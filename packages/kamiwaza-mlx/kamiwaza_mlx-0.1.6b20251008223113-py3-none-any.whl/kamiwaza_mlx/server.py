#!/usr/bin/env python3
"""
**Internal copy of `server.py`** packaged under `kamiwaza_mlx` so end-users can
simply run:

    python -m kamiwaza_mlx.server -m <model> [--port 1234]

The body of the file is identical to the original standalone script (save for
this prologue) to avoid any behavioural changes during the move.
"""

from __future__ import annotations

import argparse, base64, io, json, logging, math, re, time, uuid, asyncio, os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Optional

import requests, uvicorn, mlx.core as mx
from PIL import Image
from fastapi import FastAPI, Request
from fastapi import HTTPException
import shutil as _shutil
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, model_validator

# Import for prompt caching
from mlx_lm.models.cache import make_prompt_cache, save_prompt_cache, load_prompt_cache
from mlx_lm.models.cache import RotatingKVCache, QuantizedKVCache, KVCache
from mlx_lm.models.cache import can_trim_prompt_cache, trim_prompt_cache

# ────────────────────────── CLI & logging ──────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", default="mlx-community/Qwen2-VL-2B-Instruct-4bit")
parser.add_argument("--host", default="0.0.0.0")
parser.add_argument("--port", type=int, default=18_000)
parser.add_argument("-V", "--vision", action="store_true", help="Force vision pipeline; otherwise auto-detect.")
parser.add_argument("--strip-thinking", action="store_true")
parser.add_argument("--enable-prefix-caching", type=lambda x: (str(x).lower() == 'true'), default=True, help="Enable system message caching (default: True). Caches system messages for reuse across requests with the same system context.")
parser.add_argument("--prompt-cache-dir", type=str, default="./.cache/mlx_prompt_caches/", help="Directory to store/load system message cache files.")
parser.add_argument(
    "--kv-cache-max-tokens",
    type=int,
    default=0,
    help="Upper bound for KV cache tokens (0 = auto model context).",
)
parser.add_argument(
    "--kv-cache-min-tokens",
    type=int,
    default=0,
    help="Lower bound for KV cache tokens when building caches.",
)
parser.add_argument("--kv-cache-keep", type=int, default=4, help="RotatingKVCache keep tokens when trimming.")
parser.add_argument("--prefix-cache-headroom", type=int, default=64, help="Extra tokens added to system-prefix cache size.")
parser.add_argument("--disable-kv-cache", action="store_true", help="Disable all KV caching (prefix + conversation)")
parser.add_argument("--enable-conversation-cache", type=lambda x: (str(x).lower() == 'true'), default=True, help="Enable conversation-scoped KV caching (default: True)")
parser.add_argument("--conversation-kv-max-tokens", type=int, default=131072, help="Max tokens to retain per conversation KV cache (default: 128k)")
parser.add_argument("--conversation-max-convs", type=int, default=32, help="Max number of conversation caches to keep in memory")
parser.add_argument("--conversation-ttl-seconds", type=int, default=3600, help="Idle TTL for conversation caches (seconds)")
parser.add_argument("--conversation-snapshots", type=int, default=1, help="Snapshots to retain per conversation (default: 1)")
parser.add_argument("--conversation-auto-id", type=lambda x: (str(x).lower() == 'true'), default=True, help="Automatically bind requests without an explicit conversation id to a per-client conversation (default: True)")
parser.add_argument("--conversation-auto-fixed", type=str, default="_default", help="Fallback id to use if client address is unavailable and auto-id is enabled")
# Disk persistence (manual, via endpoints)
parser.add_argument("--conversation-disk-dir", type=str, default="/tmp/kamiwaza_mlx", help="Directory for conversation KV cache files (manual save/load endpoints)")
parser.add_argument("--conversation-disk-budget-mb", type=int, default=25, help="Approx total size budget (MB) for on-disk conversation caches (default: 25 MB)")
parser.add_argument("--conversation-disk-max-gb", type=int, default=200, help="Hard per-save limit for a single KV cache file (GiB)")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if args.disable_kv_cache and args.enable_prefix_caching:
    log.info("KV cache disabled; skipping prefix caching setup.")
    args.enable_prefix_caching = False

# ───────────────────────── timers / tiny helpers ─────────────────────────

class _Timer:  # noqa: D101 – internal util
    __slots__ = ("start", "in_tok")

    def __init__(self, in_tok: int):
        self.start = time.perf_counter()
        self.in_tok = in_tok
        logging.info("Starting generation with %d input tokens", in_tok)

    def done(self, out_tok: int):
        dt = time.perf_counter() - self.start
        tps = 0.0 if dt == 0 else out_tok / dt
        logging.info(
            "Generation completed: %d output tokens in %.2fs (%.2f output tokens/sec)", out_tok, dt, tps
        )


# ───────────────────────── constants / regex ───────────────────────
MAX_TOKENS = -1
PATCH_LIMIT = 1536
PATCH_SIZE = 32
THINK_RE = re.compile(r"<think>(.*?)</think>", re.S | re.I)  # capture group!

# ──────────────────────────── helpers ──────────────────────────────

def _encode(txt: str):
    if hasattr(PROCESSOR, "encode"):
        return mx.array(PROCESSOR.encode(txt))
    if hasattr(PROCESSOR, "tokenizer"):
        return mx.array(PROCESSOR.tokenizer.encode(txt))
    return mx.array(txt.split())  # fallback

def _tok_len(text: str) -> int:
    # Add safety check for None/empty text
    if text is None:
        log.warning("_tok_len received None text")
        return 0
    if not isinstance(text, str):
        log.warning("_tok_len received non-string: %s = %r", type(text), text)
        text = str(text) if text is not None else ""
    
    if hasattr(PROCESSOR, "encode"):
        return len(PROCESSOR.encode(text))
    if hasattr(PROCESSOR, "tokenizer"):
        return len(PROCESSOR.tokenizer.encode(text))
    return len(text.split())  # hopeless fallback


def _model_cfg(model) -> Dict[str, Any]:
    cfg = getattr(model, "config", {})
    return cfg if isinstance(cfg, dict) else cfg.__dict__


def _model_ctx_len(model) -> Optional[int]:
    """Best-effort detection of model context length from config."""
    cfg = _model_cfg(model)
    for k in (
        "max_position_embeddings",
        "max_sequence_length",
        "max_seq_len",
        "seq_len",
        "n_ctx",
        "context_length",
    ):
        v = cfg.get(k)
        if isinstance(v, int) and v > 0:
            return int(v)
    return None


def strip_thoughts(text: str, flag: bool) -> str:
    return THINK_RE.sub("", text) if flag else text


def _cap_image(img: Image.Image) -> Image.Image:
    w, h = img.size
    patches = math.ceil(w / PATCH_SIZE) * math.ceil(h / PATCH_SIZE)
    if patches <= PATCH_LIMIT:
        return img
    scale = math.sqrt(PATCH_LIMIT / patches)
    return img.resize((int(w * scale), int(h * scale)), Image.BICUBIC)


def load_image(ref: str) -> Image.Image:
    if ref.startswith("data:image/"):
        img = Image.open(io.BytesIO(base64.b64decode(ref.split(",", 1)[1])))
    elif ref.startswith("http"):
        img = Image.open(io.BytesIO(requests.get(ref, timeout=15).content))
    else:
        img = Image.open(ref)
    return _cap_image(img.convert("RGB"))


def _hash_tokens(toks: mx.array) -> str:
    """Return SHA256 hash of token id array (1-D view)."""
    import hashlib, numpy as _np
    # Ensure toks is an mx.array, convert to numpy, flatten, and hash
    # The .astype('uint32') is important for consistent hashing across platforms/setups
    # if the token IDs are, for instance, int64 by default from the tokenizer.
    flat_numpy_array = _np.array(toks, copy=False).astype('uint32').ravel()
    return hashlib.sha256(flat_numpy_array.tobytes()).hexdigest()


def _mx_length(arr) -> int:
    """Return total element count for an mx.array-like object."""
    if hasattr(arr, "size"):
        try:
            return int(arr.size)
        except Exception:
            pass
    if hasattr(arr, "shape"):
        try:
            return int(arr.shape[-1])
        except Exception:
            pass
    try:
        return int(len(arr))
    except Exception:
        return 0


def _iter_cache_nodes(cache_obj: Any):
    if isinstance(cache_obj, (list, tuple)):
        for item in cache_obj:
            yield from _iter_cache_nodes(item)
    else:
        yield cache_obj


def _set_rotating_keep(cache_obj: Any, keep: int) -> None:
    keep = int(keep)
    for node in _iter_cache_nodes(cache_obj):
        if isinstance(node, RotatingKVCache):
            node.keep = keep


def _positive_or_none(value: Optional[int]) -> Optional[int]:
    if value is None:
        return None
    try:
        value = int(value)
    except Exception:
        return None
    return value if value > 0 else None


def _resolve_cache_size(*, ensure: int = 0, cli_cap: Optional[int] = None) -> Optional[int]:
    """Determine the max_kv_size to request when allocating caches."""

    ensure = max(int(ensure), 0)
    min_tokens = max(int(args.kv_cache_min_tokens), 0)
    lower_bound = max(ensure, min_tokens)

    cap = _positive_or_none(cli_cap)
    try:
        ctx = _model_ctx_len(MODEL)
    except NameError:  # MODEL not yet initialised (should be rare)
        ctx = None
    limit: Optional[int] = None
    if cap is not None:
        limit = cap
    if ctx is not None and isinstance(ctx, int) and ctx > 0:
        limit = ctx if limit is None else min(limit, int(ctx))

    if limit is None:
        return lower_bound if lower_bound > 0 else None

    if lower_bound > limit:
        log.debug(
            "Requested cache lower bound %d exceeds limit %d; using limit.",
            lower_bound,
            limit,
        )
        return limit

    return max(limit, lower_bound)


def _legacy_prompt_cache(max_tokens: Optional[int], keep: int) -> List[Any]:
    try:
        num_layers = len(MODEL.layers)
    except Exception:
        cfg = _model_cfg(MODEL)
        num_layers = int(cfg.get("num_hidden_layers", 32))

    if max_tokens is None:
        log.info("Falling back to unbounded KVCache instances (legacy path).")
        return [KVCache() for _ in range(num_layers)]

    max_tokens = max(int(max_tokens), 1)
    log.info(
        "Falling back to RotatingKVCache instances (legacy path) max_size=%d keep=%d.",
        max_tokens,
        keep,
    )
    return [RotatingKVCache(max_size=max_tokens, keep=int(keep)) for _ in range(num_layers)]


def _allocate_prompt_cache(
    max_tokens: Optional[int], *, keep: int, reason: str
) -> List[Any]:
    try:
        prompt_cache = make_prompt_cache(MODEL, max_kv_size=max_tokens)
    except Exception as exc:  # noqa: BLE001 – one-off fallback
        log.warning(
            "make_prompt_cache failed for %s (%s); using legacy allocation.",
            reason,
            exc,
        )
        return _legacy_prompt_cache(max_tokens, keep)

    desc = "unbounded" if max_tokens is None else str(int(max_tokens))
    log.info("Allocating prompt cache (%s): max_size=%s, keep=%d", reason, desc, keep)
    _set_rotating_keep(prompt_cache, keep)
    return prompt_cache


def _prepare_cache_for_system_only(
    req: ChatReq,
    global_prompt_cache: Optional[List[Any]],
    cached_prefix_len: int,
    cache_prefix_hash: str,
    is_vision_model: bool,
    enable_prefix_caching_arg: bool,
    func_name_for_log: str
) -> Tuple[Optional[List[Any]], int, mx.array]:
    """Prepare cache and suffix for system-only caching approach."""
    
    if is_vision_model or not enable_prefix_caching_arg:
        # No caching for vision models
        prompt_str = build_prompt(req, 0)
        prompt_ids = _encode(prompt_str)
        return None, 0, prompt_ids
    
    # Check if we have system messages
    system_prompt_str = build_system_prompt(req)
    if not system_prompt_str:
        # No system messages, can't use cache
        prompt_str = build_prompt(req, 0)
        prompt_ids = _encode(prompt_str)
        return None, 0, prompt_ids
    
    # Check if cache is valid for current system prompt
    system_ids = _encode(system_prompt_str)
    system_hash = _hash_tokens(system_ids)
    
    cache_to_use = None
    actual_cached_len = 0
    
    if (global_prompt_cache is not None and 
        cached_prefix_len > 0 and 
        cache_prefix_hash == system_hash):
        # Cache is valid for this system prompt
        cache_to_use = LATE_def_copy_mlx_lm_kv_cache(global_prompt_cache)
        actual_cached_len = cached_prefix_len
        log.info(f"✅ Using cached system prompt ({actual_cached_len} tokens) in {func_name_for_log}")
        
        # Get the user/assistant portion only
        user_assistant_prompt = build_user_and_assistant_prompt(req, 0)
        suffix_ids = _encode(user_assistant_prompt)
    else:
        # Cache doesn't match or doesn't exist
        if global_prompt_cache is not None:
            log.info(f"❌ System prompt hash mismatch in {func_name_for_log}, not using cache")
        
        # Use full prompt
        prompt_str = build_prompt(req, 0)
        suffix_ids = _encode(prompt_str)
    
    # Ensure suffix is not empty
    if suffix_ids.ndim == 1 and len(suffix_ids) == 0:
        # This shouldn't happen with properly formed prompts, but just in case
        log.warning(f"Empty suffix in {func_name_for_log}, using full prompt")
        prompt_str = build_prompt(req, 0)
        suffix_ids = _encode(prompt_str)
        cache_to_use = None
        actual_cached_len = 0
    
    return cache_to_use, actual_cached_len, suffix_ids


def _usage_dict(in_tok: int, out_tok: int, dur: float, reasoning_tok: int, cached_tok: int) -> Dict[str, Any]:
    """Return an OpenAI-style `usage` dict including optional reasoning tokens."""

    return {
        "input_tokens": in_tok,
        "input_tokens_details": {"cached_tokens": int(cached_tok)},
        "output_tokens": out_tok,
        "output_tokens_details": {"reasoning_tokens": reasoning_tok},
        "total_tokens": in_tok + out_tok,
        "tokens_per_second": (in_tok + out_tok) / max(dur, 1e-6),  # never ÷0
    }


def load_model(repo: str) -> Tuple[Any, Any, bool]:
    want_vl = args.vision or "vl" in Path(repo).name.lower()
    if want_vl:
        try:
            from mlx_vlm import load as vlm_load
            # // Do NOT pass HF config dict into mlx_vlm.load(); it reads the repo itself.
            model, proc = vlm_load(repo)
            log.info("🖼️  vision model loaded via mlx-vlm")
            return model, proc, True
        except Exception as e:  # noqa: BLE001 – blanket log here is fine
            msg = str(e)
            if "AutoVideoProcessor requires the Torchvision" in msg:
                log.error("GLM-V video preprocessor present but torchvision missing.")
                log.error("Either install torchvision (to keep video) or remove "
                          "video_preprocessor_config.json (image-only).")
                raise  # don't drop to LM for glm4v_moe
            log.warning("vision load failed (%s) – falling back to LM", e)

    from mlx_lm import load as lm_load

    # Use lazy=True to avoid materializing parameters immediately; reduces peak mem at startup
    model, tok = lm_load(repo, lazy=True)
    log.info("💬  language model loaded via mlx-lm")
    return model, tok, False


MODEL, PROCESSOR, IS_VISION = load_model(args.model)
MODEL_NAME = Path(args.model).name
MODEL_CREATED = int(time.time())

# Global variables for system message caching
GLOBAL_PROMPT_CACHE = None
GLOBAL_CACHE_FILE_PATH: str | None = None
CACHE_PRIMED_THIS_SESSION = False
CACHED_PREFIX_LEN = 0
CACHE_PREFIX_HASH = ""

if args.enable_prefix_caching and not IS_VISION:
    try:
        # Sanitize model name for use as a filename
        sanitized_model_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', MODEL_NAME)
        cache_dir = Path(args.prompt_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        GLOBAL_CACHE_FILE_PATH = str(cache_dir / f"{sanitized_model_name}.safetensors")
        log.info(f"System message cache path set to: {GLOBAL_CACHE_FILE_PATH}")

        if os.path.exists(GLOBAL_CACHE_FILE_PATH):
            log.info(f"Attempting to load system message cache from {GLOBAL_CACHE_FILE_PATH}...")
            GLOBAL_PROMPT_CACHE = load_prompt_cache(GLOBAL_CACHE_FILE_PATH) 
            log.info("System message cache loaded successfully.")
            CACHE_PRIMED_THIS_SESSION = True # If loaded, it's already primed
            # load len
            len_path = GLOBAL_CACHE_FILE_PATH + ".len"
            if os.path.exists(len_path):
                try:
                    CACHED_PREFIX_LEN = int(Path(len_path).read_text())
                except Exception:
                    CACHED_PREFIX_LEN = 0
            # load hash
            hash_path = GLOBAL_CACHE_FILE_PATH + ".hash"
            if os.path.exists(hash_path):
                try:
                    CACHE_PREFIX_HASH = Path(hash_path).read_text().strip()
                except Exception:
                    CACHE_PREFIX_HASH = ""
        else:
            log.info(f"System message cache file not found at {GLOBAL_CACHE_FILE_PATH}. Will be created on first request with a system message.")
    except Exception as e:
        log.error(f"Error during system message cache setup: {e}. Caching might not work.")

# ─────────────────── Pydantic request / schema ────────────────────

class MsgPart(BaseModel):
    type: str
    text: str | None = None
    image_url: Dict[str, str] | None = None


class ToolFunctionSpec(BaseModel):
    name: str
    description: str | None = None
    parameters: Dict[str, Any] | None = None


class ToolSpec(BaseModel):
    type: str  # Only 'function' is supported
    function: ToolFunctionSpec


class ToolCallFunction(BaseModel):
    name: str
    # OpenAI returns arguments as a JSON string; accept dict and stringify later
    arguments: Union[str, Dict[str, Any]]


class ToolCall(BaseModel):
    id: str | None = None
    type: str = "function"
    function: ToolCallFunction


class ChatMsg(BaseModel):
    role: str
    # Allow None when assistant emits tool_calls
    content: Union[str, List[MsgPart], None]
    # Optional OpenAI-compatible tool fields
    tool_calls: List[ToolCall] | None = None
    name: str | None = None          # for role=='tool'
    tool_call_id: str | None = None  # for role=='tool'


class ChatReq(BaseModel):
    model: str = MODEL_NAME
    messages: List[ChatMsg]
    images: List[str] | None = None
    max_tokens: int = MAX_TOKENS
    temperature: float = 1.0
    top_p: float = 1.0
    stream: bool = False
    strip_thinking: bool | None = None
    # Tool-calling (OpenAI-compatible) inputs
    tools: List[ToolSpec] | None = None
    tool_choice: Union[str, Dict[str, Any], None] = None
    parallel_tool_calls: bool | None = True
    # Conversation KV caching
    conversation: str | None = None
    conversation_id: str | None = None
    reset_conversation: bool | None = None

    @model_validator(mode="after")
    def _flatten(self):  # noqa: D401
        imgs, flat = list(self.images or []), []
        for m in self.messages:
            if isinstance(m.content, list):
                buf = []
                for p in m.content:
                    if p.type == "text" and p.text:
                        buf.append(p.text)
                    elif p.type == "image_url" and p.image_url:
                        imgs.append(p.image_url["url"])
                m.content = "\n".join(buf)
            # Normalize None content
            if m.content is None:
                m.content = ""
            # Map tool messages into user-visible text for models that don't know 'tool' role
            if m.role == "tool":
                tool_name = m.name or "tool"
                tool_id = m.tool_call_id or ""
                wrapped = f"<tool_result name=\"{tool_name}\" id=\"{tool_id}\">\n{m.content}\n</tool_result>"
                flat.append({"role": "user", "content": wrapped})
                continue
            # If assistant message has tool_calls, serialize as text markers so the model sees them in-context
            if m.role == "assistant" and m.tool_calls:
                chunks = []
                for i, call in enumerate(m.tool_calls):
                    cid = call.id or f"call_{i+1}"
                    args = call.function.arguments
                    if not isinstance(args, str):
                        try:
                            args = json.dumps(args, ensure_ascii=False)
                        except Exception:
                            args = str(args)
                    chunks.append(
                        f"<tool_call id=\"{cid}\" name=\"{call.function.name}\">\n{args}\n</tool_call>"
                    )
                # Preserve any free-form assistant content around tool calls (rare)
                if m.content:
                    chunks.append(str(m.content))
                flat.append({"role": "assistant", "content": "\n".join(chunks)})
                continue
            flat.append({"role": m.role, "content": m.content})
        self.__dict__["flat"] = flat
        self.__dict__["all_images"] = imgs
        return self


class _ThinkFilter:  # noqa: D401 – simple state machine
    def __init__(self):
        self.state, self.buf = "NORMAL", ""

    def feed(self, s: str) -> str | None:  # noqa: C901 – tiny FSM, keep inline
        self.buf += s
        out = ""
        while True:
            if self.state == "NORMAL":
                i = self.buf.find("<think>")
                if i == -1:
                    out, self.buf = self.buf, ""
                    return out
                out += self.buf[:i]
                self.buf = self.buf[i + 7 :]
                self.state = "IN"
            elif self.state == "IN":
                j = self.buf.find("</think>")
                if j == -1:
                    return None
                self.buf = self.buf[j + 8 :]
                self.state = "STRIP_NL"
            elif self.state == "STRIP_NL":
                self.buf = self.buf.lstrip("\n")
                self.state = "NORMAL"


def build_prompt(req: ChatReq, n_imgs: int) -> str:
    if IS_VISION:
        from mlx_vlm import apply_chat_template

        return apply_chat_template(PROCESSOR, config=_model_cfg(MODEL), prompt=req.flat, num_images=n_imgs)
    if getattr(PROCESSOR, "chat_template", None):
        return PROCESSOR.apply_chat_template(req.flat, tokenize=False, add_generation_prompt=True)
    chunks = [f"<|{m['role']}|>\n{m['content']}</s>" for m in req.flat]
    chunks.append("<|assistant|>\n")
    return "\n".join(chunks)


def build_system_prompt(req: ChatReq) -> str:
    """Build prompt containing only system message(s) for caching."""
    # Extract only system messages
    system_messages = [m for m in req.flat if m['role'] == 'system']
    
    if not system_messages:
        return ""
    
    if IS_VISION:
        # For vision models, we can't easily separate system from user in the template
        # So we'll return empty string and not cache for vision models
        return ""
    
    if getattr(PROCESSOR, "chat_template", None):
        # Apply chat template to system messages only
        # Don't add generation prompt since we're not generating yet
        return PROCESSOR.apply_chat_template(system_messages, tokenize=False, add_generation_prompt=False)
    
    # Manual template formatting for system messages only
    chunks = [f"<|{m['role']}|>\n{m['content']}</s>" for m in system_messages]
    return "\n".join(chunks)


def build_user_and_assistant_prompt(req: ChatReq, n_imgs: int) -> str:
    """Build prompt containing everything after system messages."""
    # Extract non-system messages
    non_system_messages = [m for m in req.flat if m['role'] != 'system']
    
    if not non_system_messages:
        # If only system messages, return just the assistant prompt
        if getattr(PROCESSOR, "chat_template", None):
            return PROCESSOR.apply_chat_template([], tokenize=False, add_generation_prompt=True)
        return "<|assistant|>\n"
    
    if IS_VISION:
        from mlx_vlm import apply_chat_template
        # For vision, we need to include all messages
        return apply_chat_template(PROCESSOR, config=_model_cfg(MODEL), prompt=req.flat, num_images=n_imgs)
    
    if getattr(PROCESSOR, "chat_template", None):
        # Apply chat template to non-system messages and add generation prompt
        return PROCESSOR.apply_chat_template(non_system_messages, tokenize=False, add_generation_prompt=True)
    
    # Manual template formatting
    chunks = [f"<|{m['role']}|>\n{m['content']}</s>" for m in non_system_messages]
    chunks.append("<|assistant|>\n")
    return "\n".join(chunks)


def build_base_prompt(req: ChatReq, n_imgs: int) -> str:
    """Build prompt without the generation prompt (assistant header).
    Used to compute stable string prefixes for incremental tokenization.
    """
    if IS_VISION:
        # Vision path does not currently support base vs full separation.
        from mlx_vlm import apply_chat_template
        return apply_chat_template(PROCESSOR, config=_model_cfg(MODEL), prompt=req.flat, num_images=n_imgs)
    if getattr(PROCESSOR, "chat_template", None):
        return PROCESSOR.apply_chat_template(req.flat, tokenize=False, add_generation_prompt=False)
    # Manual template formatting without the trailing assistant cue
    chunks = [f"<|{m['role']}|>\n{m['content']}</s>" for m in req.flat]
    return "\n".join(chunks)


def build_base_prompt_for_flat(flat_msgs: List[Dict[str, str]], n_imgs: int) -> str:
    """Build base prompt (no generation prompt) for a provided flat message list."""
    if IS_VISION:
        from mlx_vlm import apply_chat_template
        return apply_chat_template(PROCESSOR, config=_model_cfg(MODEL), prompt=flat_msgs, num_images=n_imgs)
    if getattr(PROCESSOR, "chat_template", None):
        return PROCESSOR.apply_chat_template(flat_msgs, tokenize=False, add_generation_prompt=False)
    chunks = [f"<|{m['role']}|>\n{m['content']}</s>" for m in flat_msgs]
    return "\n".join(chunks)


def _msg_hash(role: str, content: str) -> str:
    import hashlib
    s = (role + "\n" + (content or "")).encode("utf-8", errors="ignore")
    return hashlib.sha1(s).hexdigest()[:16]


def _boundary_offsets_for_flat(flat_msgs: List[Dict[str, str]], n_imgs: int) -> List[int]:
    """Compute cumulative token offsets at the end of each message in flat_msgs.
    Uses incremental delta tokenization of the base prompt to avoid re-encoding
    the entire prefix multiple times.
    """
    offsets: List[int] = []
    prev_base = ""
    total = 0
    for i in range(len(flat_msgs)):
        base_i = build_base_prompt_for_flat(flat_msgs[: i + 1], n_imgs)
        delta = base_i[len(prev_base):]
        ids = _encode(delta)
        dn = int(ids.shape[-1] if getattr(ids, 'ndim', 1) != 1 else len(ids))
        total += dn
        offsets.append(total)
        prev_base = base_i
    return offsets


# ─────────────────── generation (vision / language) ───────────────

# ─────────────── tool support helpers (prompt + parsing) ───────────────

def _tools_instruction(tools: List[ToolSpec], tool_choice: Union[str, Dict[str, Any], None], parallel: bool | None) -> str:
    names = ", ".join(t.function.name for t in tools if t.type == "function")
    choice_txt = "auto" if tool_choice in (None, "auto") else json.dumps(tool_choice)
    parallel_txt = "true" if (parallel is None or parallel) else "false"
    specs = []
    for t in tools:
        if t.type != "function":
            continue
        specs.append({
            "name": t.function.name,
            "description": t.function.description or "",
            "parameters": t.function.parameters or {}
        })
    instruction = (
        "You can call external tools to help answer. "
        f"Available function tools: {names}. "
        f"tool_choice={choice_txt}, parallel_tool_calls={parallel_txt}.\n"
        "When you decide to call tool(s), reply with ONLY a JSON object on a single line of the form:\n"
        '{"tool_calls":[{"id":"call_1","type":"function","function":{"name":"<name>","arguments":{...}}}]}'
        " (no extra commentary). Arguments must be valid JSON. If no tool is needed, reply normally.\n"
        "Tool specs (name, description, parameters JSON Schema):\n" + json.dumps(specs, ensure_ascii=False)
    )
    return instruction


def _maybe_parse_tool_calls(text: str) -> List[Dict[str, Any]] | None:
    """Try to parse a top-level JSON with tool_calls from model output.
    Accepts plain JSON or fenced ```json blocks. Returns OpenAI-style tool_calls list or None.
    """
    s = text.strip()
    # Try to extract fenced json first
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1)
    # If content has leading junk before {, trim to first {
    if "{" in s and not s.lstrip().startswith("{"):
        s = s[s.find("{"):]
    try:
        obj = json.loads(s)
    except Exception:
        return None
    calls = None
    if isinstance(obj, dict):
        if "tool_calls" in obj and isinstance(obj["tool_calls"], list):
            calls = obj["tool_calls"]
        elif "function_call" in obj and isinstance(obj["function_call"], dict):
            fc = obj["function_call"]
            calls = [{
                "id": f"call_1",
                "type": "function",
                "function": {
                    "name": fc.get("name", ""),
                    "arguments": fc.get("arguments", {})
                }
            }]
    if not calls:
        return None
    # Normalize: ensure arguments are strings per OpenAI, ids present
    normd = []
    for i, c in enumerate(calls):
        fn = c.get("function", {})
        args = fn.get("arguments", {})
        if not isinstance(args, str):
            try:
                args = json.dumps(args, ensure_ascii=False)
            except Exception:
                args = str(args)
        cid = c.get("id") or f"call_{i+1}"
        normd.append({
            "id": cid,
            "type": "function",
            "function": {"name": fn.get("name", ""), "arguments": args},
        })
    return normd


def _get_forced_tool_name(tool_choice: Union[str, Dict[str, Any], None]) -> Optional[str]:
    if isinstance(tool_choice, dict):
        fn = tool_choice.get("function") or {}
        name = fn.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _forced_tool_instruction(tools: List[ToolSpec], forced_name: str) -> str:
    spec = None
    for t in tools or []:
        if t.type == "function" and t.function.name == forced_name:
            spec = t
            break
    schema = (spec.function.parameters if spec and spec.function.parameters else {})
    example = "{}"
    try:
        # crude example using required fields if present
        req = (schema or {}).get("required") or []
        props = (schema or {}).get("properties") or {}
        ex = {k: ("string" if (props.get(k, {}).get("type") == "string") else 0) for k in req}
        example = json.dumps(ex) if ex else "{}"
    except Exception:
        pass
    instruction = (
        f"You MUST call the function '{forced_name}'.\n"
        "Reply with ONLY the JSON arguments object for that function on a single line, no code fences, no commentary.\n"
        f"Example: {example}\n"
        "JSON Schema for arguments: " + json.dumps(schema, ensure_ascii=False)
    )
    return instruction


def _maybe_parse_arguments_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract a top-level JSON object from text and return it as a dict."""
    s = text.strip()
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1)
    # Trim to first '{'
    if "{" in s and not s.lstrip().startswith("{"):
        s = s[s.find("{"):]
    # Try full-string parse first
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # Attempt to find the first balanced JSON object
    # Simple brace matching ignoring braces inside quotes
    in_str = False
    esc = False
    depth = 0
    start = None
    for i, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    candidate = s[start : i + 1]
                    try:
                        obj = json.loads(candidate)
                        if isinstance(obj, dict):
                            return obj
                    except Exception:
                        pass
    return None

if IS_VISION:  # ──────────── VISION PATH ────────────
    # mlx-vlm API compatibility: generate/stream_generate moved from utils → generate in newer versions
    try:
        from mlx_vlm.utils import generate as vlm_gen, stream_generate as vlm_stream  # older mlx-vlm
    except Exception:  # ImportError or missing attributes
        try:
            from mlx_vlm.generate import generate as vlm_gen, stream_generate as vlm_stream  # newer mlx-vlm
        except Exception:
            # Last-resort granular fallbacks to handle mixed versions
            from mlx_vlm.generate import generate as vlm_gen  # type: ignore
            try:
                from mlx_vlm.generate import stream_generate as vlm_stream  # type: ignore
            except Exception:
                from mlx_vlm.utils import stream_generate as vlm_stream  # type: ignore

    def sync_gen(prompt: str, imgs, req: ChatReq) -> str:  # noqa: D401
        timer = _Timer(len(prompt))
        result = vlm_gen(
            MODEL,
            PROCESSOR,
            prompt,
            image=imgs,
            max_tokens=req.max_tokens,
            temp=req.temperature,
            top_p=req.top_p,
            verbose=False,
        )
        # Normalize return across mlx-vlm versions: GenerationResult | (text, stats) | str
        if hasattr(result, "text"):
            txt = result.text
        elif isinstance(result, tuple):
            txt = result[0]
        else:
            txt = str(result)
        timer.done(_tok_len(txt))
        return txt

    def stream_chunks(prompt: str, imgs, req: ChatReq):  # noqa: C901 – ported as-is
        rid, created, first = f"chatcmpl-{uuid.uuid4()}", int(time.time()), False
        should_strip = args.strip_thinking if req.strip_thinking is None else req.strip_thinking
        timer = _Timer(len(prompt))
        out_tok = 0

        def _emit(chunk: str):
            nonlocal first, out_tok
            if not chunk:
                return
            out_tok += _tok_len(chunk)
            delta = {"content": chunk}
            if not first:
                delta["role"] = "assistant"  # ← add the value!
                first = True
            return _sse_chunk(rid, created, delta)

        if not should_strip:
            for r in vlm_stream(
                MODEL,
                PROCESSOR,
                prompt,
                image=imgs,
                max_tokens=req.max_tokens,
                temp=req.temperature,
                top_p=req.top_p,
            ):
                if r.text:
                    yield _emit(r.text)
            yield "data: [DONE]\n\n"
            final = {
                "id": rid,
                "object": "chat.completion.chunk",
                "created": created,
                "model": MODEL_NAME,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final)}\n\n"
            timer.done(out_tok)
            yield "data: [DONE]\n\n"

        state, buf = "NORMAL", ""
        for r in vlm_stream(
            MODEL,
            PROCESSOR,
            prompt,
            image=imgs,
            max_tokens=req.max_tokens,
            temp=req.temperature,
            top_p=req.top_p,
        ):
            if not r.text:
                continue
            buf += r.text
            while True:
                if state == "NORMAL":
                    k = buf.find("<think>")
                    if k == -1:
                        chunk, buf = buf, ""
                    else:
                        chunk, buf, state = buf[:k], buf[k + 7 :], "IN_THINK"
                    if chunk:
                        yield _emit(chunk)
                    if k == -1:
                        break
                elif state == "IN_THINK":
                    k = buf.find("</think>")
                    if k == -1:
                        buf = ""
                        break
                    buf, state = buf[k + 8 :], "STRIP"
                elif state == "STRIP":
                    buf = buf.lstrip("\n")
                    state = "NORMAL"
        if buf:
            yield _emit(buf)
        final = {
            "id": rid,
            "object": "chat.completion.chunk",
            "created": created,
            "model": MODEL_NAME,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final)}\n\n"
        timer.done(out_tok)
        yield "data: [DONE]\n\n"

else:  # ──────────── TEXT-ONLY PATH ────────────
    from mlx_lm.generate import stream_generate as lm_stream
    from mlx_lm.sample_utils import make_sampler

    def _sampler(req: ChatReq):
        return make_sampler(temp=req.temperature, top_p=req.top_p, min_p=0.0, min_tokens_to_keep=1)

    def sync_gen(prompt: str, _imgs, req: ChatReq) -> str:  # noqa: C901, D401
        global GLOBAL_PROMPT_CACHE, CACHED_PREFIX_LEN, CACHE_PREFIX_HASH
        sampler = _sampler(req)
        
        pre = req.__dict__.get("_precomputed_cache")
        if pre is not None:
            cache_to_use, actual_cached_len, suffix_ids_val = pre[0], pre[1], pre[2]
        else:
            cache_to_use, actual_cached_len, suffix_ids_val = _prepare_cache_for_system_only(
                req,
                GLOBAL_PROMPT_CACHE,
                CACHED_PREFIX_LEN,
                CACHE_PREFIX_HASH,
                IS_VISION,
                (args.enable_prefix_caching and not args.disable_kv_cache),
                "sync_gen"
            )
        # Fallback: ensure a bounded KV cache exists to cap memory
        if cache_to_use is None and not IS_VISION and not args.disable_kv_cache:
            suffix_len = _mx_length(suffix_ids_val)
            required = suffix_len + int(args.prefix_cache_headroom)
            max_size = _resolve_cache_size(
                ensure=required,
                cli_cap=args.kv_cache_max_tokens,
            )
            cache_to_use = _allocate_prompt_cache(
                max_size,
                keep=args.kv_cache_keep,
                reason="generation",
            )
        
        # Calculate total prompt length for reporting
        full_prompt_len = len(_encode(prompt))
        suffix_len = len(suffix_ids_val) if suffix_ids_val.ndim == 1 else suffix_ids_val.shape[-1]
        
        log.info("🪟 Using cache? %s | full prompt %d tokens | processing %d tokens (cached system: %d)", 
                 cache_to_use is not None, full_prompt_len, suffix_len, actual_cached_len)

        timer = _Timer(suffix_len)
        out, comp_tok, think_tok_count_if_stripped = [], 0, 0
        t0 = time.perf_counter()

        first_iter = True
        for r in lm_stream(
            model=MODEL,
            tokenizer=PROCESSOR,
            prompt=suffix_ids_val,
            max_tokens=req.max_tokens,
            sampler=sampler,
            prompt_cache=cache_to_use
        ):
            if first_iter:
                start_pos = getattr(r, "pos", getattr(r, "position", -1))
                log.debug("🔍 First step model start_pos = %s", start_pos)
                first_iter = False
            if r.token == PROCESSOR.eos_token_id:
                break
            out.append(r.text)
            comp_tok += 1
            # This counts tokens inside <think> tags if they were to be stripped.
            # The actual reasoning_tok for usage depends on whether stripping happens.
            if "<think>" in r.text:
                 think_tok_count_if_stripped += len(PROCESSOR.encode("".join(THINK_RE.findall(r.text))))
        dt = time.perf_counter() - t0

        full = "".join(out)
        # Calculate actual reasoning tokens based on the final full string and stripping choice
        final_reasoning_tok = 0
        if not (req.strip_thinking or args.strip_thinking):
            inner_thoughts = THINK_RE.findall(full)
            final_reasoning_tok = sum(len(PROCESSOR.encode(seg)) for seg in inner_thoughts)
        
        total_input = suffix_len + int(actual_cached_len)
        req.__dict__["_usage"] = _usage_dict(total_input, comp_tok, dt, final_reasoning_tok, int(actual_cached_len))

        timer.done(comp_tok)

        return full if not (req.strip_thinking or args.strip_thinking) else strip_thoughts(full, True)

    def stream_chunks(prompt: str, _imgs, req: ChatReq):  # noqa: C901
        global GLOBAL_PROMPT_CACHE, CACHED_PREFIX_LEN, CACHE_PREFIX_HASH
        rid, created, sent_role = f"chatcmpl-{uuid.uuid4()}", int(time.time()), False
        sampler = _sampler(req)

        pre = req.__dict__.get("_precomputed_cache")
        if pre is not None:
            cache_to_use, actual_cached_len, suffix_ids_val = pre[0], pre[1], pre[2]
        else:
            cache_to_use, actual_cached_len, suffix_ids_val = _prepare_cache_for_system_only(
                req,
                GLOBAL_PROMPT_CACHE,
                CACHED_PREFIX_LEN,
                CACHE_PREFIX_HASH,
                IS_VISION,
                (args.enable_prefix_caching and not args.disable_kv_cache),
                "stream_chunks"
            )
        # Fallback: ensure a bounded KV cache exists to cap memory
        if cache_to_use is None and not IS_VISION and not args.disable_kv_cache:
            suffix_len = _mx_length(suffix_ids_val)
            required = suffix_len + int(args.prefix_cache_headroom)
            max_size = _resolve_cache_size(
                ensure=required,
                cli_cap=args.kv_cache_max_tokens,
            )
            cache_to_use = _allocate_prompt_cache(
                max_size,
                keep=args.kv_cache_keep,
                reason="generation-stream",
            )
        
        # Calculate total prompt length for reporting
        full_prompt_len = len(_encode(prompt))
        suffix_len = len(suffix_ids_val) if suffix_ids_val.ndim == 1 else suffix_ids_val.shape[-1]
        
        log.info("🪟 Using cache? %s | full prompt %d tokens | processing %d tokens (cached system: %d) (stream)", 
                 cache_to_use is not None, full_prompt_len, suffix_len, actual_cached_len)

        timer = _Timer(suffix_len)
        # reasoning_tok for streaming is harder to calculate accurately upfront if stripping thoughts.
        # The _ThinkFilter handles stripping, and final usage might not be easily available here.
        # For simplicity, we'll set it to 0 here or acknowledge it's an approximation for streaming.

        think = _ThinkFilter()
        strip_it = args.strip_thinking if req.strip_thinking is None else req.strip_thinking
        SYNC_EVERY, tok_ctr, out_tok = 16, 0, 0

        first_iter = True
        for r in lm_stream(
            model=MODEL,
            tokenizer=PROCESSOR,
            prompt=suffix_ids_val,
            max_tokens=req.max_tokens,
            sampler=sampler,
            prompt_cache=cache_to_use
        ):
            if first_iter:
                start_pos = getattr(r, "pos", getattr(r, "position", -1))
                log.debug("🔍 First step model start_pos = %s (stream)", start_pos)
                first_iter = False
            if r.token == PROCESSOR.eos_token_id:
                break
            piece = r.text
            if strip_it:
                stripped_piece = think.feed(piece)
                if stripped_piece is None:
                    tok_ctr += 1
                    if tok_ctr % SYNC_EVERY == 0:
                        mx.synchronize()
                    continue
                piece = stripped_piece
            
            if piece == "" and r.text:
                 piece = "\n"
            elif piece == "" and not r.text:
                 continue

            delta = {"content": piece}
            if not sent_role:
                delta["role"] = "assistant"
                sent_role = True
            out_tok += 1
            yield _sse_chunk(rid, created, delta)
            tok_ctr += 1
            if tok_ctr % SYNC_EVERY == 0:
                mx.synchronize()

        timer.done(out_tok)
        final = {
            "id": rid,
            "object": "chat.completion.chunk",
            "created": created,
            "model": MODEL_NAME,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final)}\n\n"
        yield "data: [DONE]\n\n"


# ───────────────────────── SSE helper ─────────────────────────────

def _sse_chunk(rid: str, created: int, delta: Dict[str, str]) -> str:
    payload = {
        "id": rid,
        "object": "chat.completion.chunk",
        "created": created,
        "model": MODEL_NAME,
        "choices": [{"index": 0, "delta": delta, "finish_reason": None}],
    }
    return f"data: {json.dumps(payload)}\n\n"


# ─────────────────────────── FastAPI app ─────────────────────────
app = FastAPI()

# ─────────────────── KVCache Copy Helper ───────────────────
def LATE_def_copy_mlx_lm_kv_cache(original_cache: Any) -> Any:
    """Deep-copy an mlx-lm prompt cache preserving structure.

    Handles nested containers (list/tuple) and known cache types
    (KVCache, RotatingKVCache, QuantizedKVCache). Arrays are copied to
    avoid mutating the original cache across requests.
    """
    if original_cache is None:
        return None

    # Recurse containers
    if isinstance(original_cache, (list, tuple)):
        return type(original_cache)(LATE_def_copy_mlx_lm_kv_cache(x) for x in original_cache)

    item_cache = original_cache
    try:
        new_item_cache = type(item_cache)()  # Create new instance of the same type
    except Exception:
        # Unknown type; return as-is
        return item_cache

    # Copy common attributes like offset and step
    if hasattr(item_cache, 'offset'):
        new_item_cache.offset = item_cache.offset
    if hasattr(item_cache, 'step'):
        new_item_cache.step = item_cache.step

    # Handle .keys and .values (may be mx.array or list/tuple of mx.arrays)
    for attr_name in ["keys", "values"]:
        original_attr_val = getattr(item_cache, attr_name, None)
        if original_attr_val is None:
            setattr(new_item_cache, attr_name, None)
        elif isinstance(original_attr_val, mx.array):
            setattr(new_item_cache, attr_name, mx.array(original_attr_val))
        elif isinstance(original_attr_val, (list, tuple)):
            copied = [mx.array(arr) if isinstance(arr, mx.array) else arr for arr in original_attr_val]
            setattr(new_item_cache, attr_name, type(original_attr_val)(copied))
        else:
            setattr(new_item_cache, attr_name, original_attr_val)

    # Specific attributes for RotatingKVCache
    if isinstance(item_cache, RotatingKVCache):
        if hasattr(item_cache, 'max_size'):
            new_item_cache.max_size = item_cache.max_size
        if hasattr(item_cache, 'keep'):
            new_item_cache.keep = item_cache.keep
        if hasattr(item_cache, '_idx'):
            new_item_cache._idx = item_cache._idx

    # Specific attributes for QuantizedKVCache
    if isinstance(item_cache, QuantizedKVCache):
        if hasattr(item_cache, 'group_size'):
            new_item_cache.group_size = item_cache.group_size
        if hasattr(item_cache, 'bits'):
            new_item_cache.bits = item_cache.bits

    return new_item_cache


# ─────────────────── Conversation KV manager ───────────────────
import time as _time
from collections import OrderedDict


class _ConvRec:
    __slots__ = ("cache", "tokens", "text", "base_text", "boundary_offsets", "message_hashes", "messages", "ts", "snapshots")

    def __init__(self, cache: Any, tokens, text: str = "", base_text: str = ""):
        self.cache = cache
        self.tokens = tokens  # numpy array (uint32) 1-D
        self.text = text      # full prompt string corresponding to tokens
        self.base_text = base_text  # prompt without generation prompt
        self.boundary_offsets: List[int] | None = None  # token offsets after each message
        self.message_hashes: List[str] | None = None    # hash per message
        self.messages: List[Dict[str, str]] | None = None  # flat messages used for this cache
        self.ts = _time.time()
        # snapshots: recent prior states for rollback/prefix match
        # elements: {"tokens": np.ndarray, "text": str, "cache": Any}
        self.snapshots: List[Dict[str, Any]] = []


class ConversationKV:
    def __init__(self, max_convs: int, ttl: int):
        self.max_convs = max_convs
        self.ttl = ttl
        self._map: "OrderedDict[str, _ConvRec]" = OrderedDict()

    def _evict(self):
        # Evict LRU beyond capacity or stale by TTL
        now = _time.time()
        # Drop expired
        keys_to_drop = [k for k, rec in self._map.items() if self.ttl > 0 and (now - rec.ts) > self.ttl]
        for k in keys_to_drop:
            self._map.pop(k, None)
        # Enforce max size
        while len(self._map) > self.max_convs:
            self._map.popitem(last=False)

    def get(self, cid: str) -> Optional[_ConvRec]:
        rec = self._map.get(cid)
        if rec is None:
            return None
        # touch LRU
        rec.ts = _time.time()
        self._map.move_to_end(cid, last=True)
        return rec

    def put(self, cid: str, cache: Any, tokens, text: str = "", base_text: str = ""):
        rec = _ConvRec(cache, tokens, text, base_text)
        self._map[cid] = rec
        self._map.move_to_end(cid, last=True)
        self._evict()

# ─────────────────── Disk persistence for conversation KV (manual) ───────────────────
def _sanitize_id(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", s or "")


def _ensure_disk_dir() -> Path:
    d = Path(args.conversation_disk_dir)
    try:
        d.mkdir(parents=True, exist_ok=True)
        d.chmod(0o700)
    except Exception:
        pass
    return d


def _conv_disk_paths(conv_id: str) -> Dict[str, Path]:
    base = _sanitize_id(MODEL_NAME) + "__" + _sanitize_id(conv_id)
    d = _ensure_disk_dir()
    return {
        "cache": d / f"{base}.safetensors",
        "meta": d / f"{base}.meta.json",
    }


def _conv_disk_save(conv_id: str, rec: _ConvRec, *, title: Optional[str] = None, override_limit: bool = False) -> Dict[str, Any]:
    import numpy as _np
    info = {"written_bytes": 0, "meta_bytes": 0, "path": "", "error": None}
    paths = _conv_disk_paths(conv_id)
    try:
        d = paths["cache"].parent
        d.mkdir(parents=True, exist_ok=True)
        d.chmod(0o700)
        tmp_cache = d / (paths["cache"].name + ".tmp")
        tmp_meta = d / (paths["meta"].name + ".tmp")
        # Write cache to tmp
        if tmp_cache.exists():
            tmp_cache.unlink()
        save_prompt_cache(str(tmp_cache), rec.cache)
        size = int(tmp_cache.stat().st_size)
        # Check per-save max size (GiB)
        max_bytes = int(args.conversation_disk_max_gb) * (1024**3)
        if size > max_bytes and not override_limit:
            tmp_cache.unlink(missing_ok=True)
            info["error"] = f"cache size {size} exceeds max {max_bytes}"
            return info
        # Check disk occupancy threshold (90%) before committing
        usage = _shutil.disk_usage(str(d))
        after_used = usage.used + size
        if after_used / usage.total > 0.90:
            tmp_cache.unlink(missing_ok=True)
            info["error"] = "disk occupancy would exceed 90%"
            return info
        # Write meta tmp
        meta = {
            "v": 2,
            "model": MODEL_NAME,
            "conversation_id": conv_id,
            "ts": int(time.time()),
            "title": title or "",
            "tokens": list(map(int, _np.array(rec.tokens, copy=False).astype('uint32').ravel())) if rec.tokens is not None else [],
            "boundary_offsets": list(map(int, rec.boundary_offsets or [])) if getattr(rec, 'boundary_offsets', None) else None,
            "message_hashes": list(rec.message_hashes or []),
            "messages": list(rec.messages or []),
            "prefix": (rec.base_text or rec.text or "")[:500],
            "path": str(paths["cache"]),
        }
        tmp_meta.write_text(json.dumps(meta), encoding="utf-8")
        # Move into place atomically
        if paths["cache"].exists():
            paths["cache"].unlink()
        tmp_cache.rename(paths["cache"])
        if paths["meta"].exists():
            paths["meta"].unlink()
        tmp_meta.rename(paths["meta"])
        # Permissions
        try:
            paths["cache"].chmod(0o600)
            paths["meta"].chmod(0o600)
        except Exception:
            pass
        info["written_bytes"] = size
        info["meta_bytes"] = int(paths["meta"].stat().st_size)
        info["path"] = str(paths["cache"])
        return info
    except Exception as e:
        log.warning(f"Conversation disk save failed for '{conv_id}': {e}")
        try:
            tmp_cache.unlink(missing_ok=True)
            tmp_meta.unlink(missing_ok=True)
        except Exception:
            pass
        info["error"] = str(e)
        return info


def _conv_disk_load(conv_id: str) -> Tuple[Any, Optional[List[int]], Optional[List[int]], Optional[List[str]]]:
    import numpy as _np
    paths = _conv_disk_paths(conv_id)
    if not (paths["cache"].exists() and paths["meta"].exists()):
        return None, None, None, None
    try:
        cache = load_prompt_cache(str(paths["cache"]))
        meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
        toks = meta.get("tokens") or []
        offs = meta.get("boundary_offsets") or None
        hashes = meta.get("message_hashes") or None
        return cache, toks, offs, hashes
    except Exception as e:
        log.warning(f"Conversation disk load failed for '{conv_id}': {e}")
        return None, None, None, None


def _conv_disk_enforce_budget() -> None:
    budget = int(args.conversation_disk_budget_mb) * 1024 * 1024
    d = _ensure_disk_dir()
    try:
        entries = []
        total = 0
        prefix = _sanitize_id(MODEL_NAME) + "__"
        for meta_p in d.glob(f"{prefix}*.meta.json"):
            try:
                cache_p = Path(str(meta_p).replace('.meta.json', '.safetensors'))
                size = (meta_p.stat().st_size if meta_p.exists() else 0) + (cache_p.stat().st_size if cache_p.exists() else 0)
                ts = 0
                try:
                    m = json.loads(meta_p.read_text(encoding='utf-8'))
                    ts = int(m.get('ts') or 0)
                except Exception:
                    pass
                entries.append((ts, size, meta_p, cache_p))
                total += size
            except Exception:
                continue
        if total <= budget:
            return
        entries.sort(key=lambda x: x[0])
        for ts, size, meta_p, cache_p in entries:
            try:
                if cache_p.exists():
                    cache_p.unlink()
                if meta_p.exists():
                    meta_p.unlink()
            except Exception:
                pass
            total -= size
            if total <= budget:
                break
    except Exception as e:
        log.warning(f"Disk budget enforcement failed: {e}")


# ──────────────────────────── Save/Load Endpoints ───────────────────────────

class _ConvIOReq(BaseModel):
    conversation: Optional[str] = None
    conversation_id: Optional[str] = None
    budget_mb: Optional[int] = None
    title: Optional[str] = None
    override_limit: Optional[bool] = None


@app.post("/v1/conv_kv/save")
async def save_conversation(body: _ConvIOReq):
    cid = (body.conversation or body.conversation_id or "").strip()
    if not cid:
        raise HTTPException(status_code=400, detail="conversation or conversation_id required")
    rec = CONV_KV.get(cid)
    if rec is None or rec.cache is None:
        raise HTTPException(status_code=404, detail="conversation not found or no cache in memory")
    # Ensure boundary metadata is present
    if rec.boundary_offsets is None and not IS_VISION:
        try:
            # We cannot reconstruct message list here; leave None if unknown
            pass
        except Exception:
            pass
    info = _conv_disk_save(cid, rec, title=body.title, override_limit=bool(body.override_limit))
    if info.get("error"):
        raise HTTPException(status_code=413, detail=info["error"])  # 413 Payload Too Large / over limit
    if body.budget_mb is not None:
        try:
            old = args.conversation_disk_budget_mb
            args.conversation_disk_budget_mb = int(body.budget_mb)
            _conv_disk_enforce_budget()
            args.conversation_disk_budget_mb = old
        except Exception:
            _conv_disk_enforce_budget()
    else:
        _conv_disk_enforce_budget()
    return {
        "status": "saved",
        "id": cid,
        "path": info.get("path"),
        "bytes": info.get("written_bytes", 0),
        "meta_bytes": info.get("meta_bytes", 0),
        "tokens": int(len(rec.tokens) if rec.tokens is not None else 0),
    }


@app.post("/v1/conv_kv/load")
async def load_conversation(body: _ConvIOReq):
    import numpy as _np
    cid = (body.conversation or body.conversation_id or "").strip()
    if not cid:
        raise HTTPException(status_code=400, detail="conversation or conversation_id required")
    cache, toks, offs, hashes = _conv_disk_load(cid)
    if cache is None:
        raise HTTPException(status_code=404, detail="conversation cache not found on disk")
    # Install or update record
    toks_np = _np.array(toks or [], dtype='uint32')
    rec = CONV_KV.get(cid)
    if rec is not None:
        rec.cache = cache
        rec.tokens = toks_np
        rec.boundary_offsets = list(map(int, offs or [])) if offs else None
        rec.message_hashes = list(hashes or []) if hashes else None
    else:
        CONV_KV.put(cid, cache, toks_np, text="", base_text="")
        rec2 = CONV_KV.get(cid)
        if rec2 is not None:
            rec2.boundary_offsets = list(map(int, offs or [])) if offs else None
            rec2.message_hashes = list(hashes or []) if hashes else None
    return {
        "status": "loaded",
        "id": cid,
        "tokens": int(len(toks or [])),
        "has_boundary": bool(offs),
        "has_hashes": bool(hashes),
    }


@app.get("/v1/conv_kv/stats")
async def list_conversation_stats():
    d = _ensure_disk_dir()
    prefix = _sanitize_id(MODEL_NAME) + "__"
    items = []
    try:
        for meta_p in d.glob(f"{prefix}*.meta.json"):
            try:
                cache_p = Path(str(meta_p).replace('.meta.json', '.safetensors'))
                meta = json.loads(meta_p.read_text(encoding='utf-8'))
                size = (meta_p.stat().st_size if meta_p.exists() else 0) + (cache_p.stat().st_size if cache_p.exists() else 0)
                items.append({
                    "id": meta.get("conversation_id") or meta_p.stem.split("__",1)[-1].replace('.meta',''),
                    "title": meta.get("title") or "",
                    "tokens": len(meta.get("tokens") or []),
                    "ts": meta.get("ts") or 0,
                    "size_bytes": int(size),
                    "path": str(cache_p),
                    "prefix": meta.get("prefix") or "",
                })
            except Exception:
                continue
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"items": items}


@app.delete("/v1/conv_kv/{cid}")
async def delete_conversation(cid: str):
    paths = _conv_disk_paths(cid)
    deleted = False
    try:
        if paths["cache"].exists():
            paths["cache"].unlink()
            deleted = True
        if paths["meta"].exists():
            paths["meta"].unlink()
            deleted = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "deleted" if deleted else "not_found", "id": cid}


CONV_KV = ConversationKV(max_convs=int(32), ttl=int(3600))

@app.get("/v1/models")
async def list_models() -> dict:
    """Return the single loaded model in OpenAI's `/v1/models` schema."""

    model_info = {
        "id": MODEL_NAME,
        "object": "model",
        "created": MODEL_CREATED,
        "owned_by": "kamiwaza",
    }
    return {"object": "list", "data": [model_info]}


@app.post("/v1/chat/completions")
async def completions(req: ChatReq, request: Request):  # noqa: C901 – same as original
    from fastapi import Request as _Request  # local import to avoid circulars
    # access headers by creating a dummy Request param via dependency not available here; instead FastAPI can inject if we include param
    if req.model != MODEL_NAME:
        log.warning("Requested model '%s' ≠ loaded '%s'", req.model, MODEL_NAME)

    # Inject tool instructions (as a non-system message to avoid polluting cache)
    tools_enabled = bool(getattr(req, "tools", None)) and len(req.tools or []) > 0
    forced_name = _get_forced_tool_name(getattr(req, "tool_choice", None)) if tools_enabled else None
    if tools_enabled:
        try:
            if forced_name:
                instr = _forced_tool_instruction(req.tools or [], forced_name)
            else:
                instr = _tools_instruction(req.tools or [], req.tool_choice, req.parallel_tool_calls)
            new_flat = ([{"role": "user", "content": instr}] + list(req.flat))
            req.__dict__["flat"] = new_flat
        except Exception as e:
            log.warning(f"Failed to prepare tool instructions: {e}")

    imgs = [load_image(u) for u in req.all_images] if IS_VISION else []
    prompt_str = build_prompt(req, len(imgs))

    # ───────── Conversation KV preparation ─────────
    conv_id = None
    if not args.disable_kv_cache and args.enable_conversation_cache:
        # precedence: body.conversation -> body.conversation_id -> header X-Conversation-Id
        conv_id = (req.conversation or req.conversation_id or request.headers.get("X-Conversation-Id"))
        if conv_id is not None:
            conv_id = conv_id.strip() or None
        # Auto-bind to a per-client conversation if enabled and none provided
        if conv_id is None and args.conversation_auto_id:
            client_id = None
            try:
                if request.client and request.client.host:
                    client_id = f"client:{request.client.host}"
            except Exception:
                client_id = None
            conv_id = client_id or str(args.conversation_auto_fixed)

    full_ids_for_conv = None
    conv_diag = {"id": conv_id or "", "mode": "disabled" if (args.disable_kv_cache or not args.enable_conversation_cache) else ("none" if not conv_id else "unknown"), "cached": 0, "processing": 0}
    if conv_id and not req.reset_conversation:
        try:
            full_ids_for_conv = _encode(prompt_str)
            # flatten to 1-D if needed
            if getattr(full_ids_for_conv, 'ndim', 1) != 1:
                full_ids_for_conv = full_ids_for_conv.ravel()
        except Exception as e:
            log.warning(f"Conversation encode failed: {e}")
            full_ids_for_conv = None

    precomp_cache = None
    if conv_id and not req.reset_conversation:
        import numpy as _np
        # Try incremental tokenization: if new prompt_str starts with stored text,
        # only encode the tail and concatenate tokens.
        cand = None
        CONV_KV.max_convs = int(args.conversation_max_convs)
        CONV_KV.ttl = int(args.conversation_ttl_seconds)
        rec = CONV_KV.get(conv_id)
        if rec is not None:
            try:
                prev = _np.array(rec.tokens, copy=False).astype('uint32').ravel()
                # Before matching, optionally snapshot current rec for rollback
                try:
                    max_snaps = int(getattr(args, 'conversation_snapshots', 1))
                except Exception:
                    max_snaps = 1
                if max_snaps > 0:
                    try:
                        snap_cache = LATE_def_copy_mlx_lm_kv_cache(rec.cache)
                        rec.snapshots.append({"tokens": prev.copy(), "text": (rec.text or ""), "cache": snap_cache})
                        # Cap snapshots per conversation
                        if len(rec.snapshots) > max_snaps:
                            rec.snapshots = rec.snapshots[-max_snaps:]
                    except Exception as e:
                        log.warning(f"Conversation snapshot copy failed: {e}")

                # Prefer boundary-aware matching by message hashes and token offsets
                text = prompt_str
                prev = _np.array(rec.tokens, copy=False).astype('uint32').ravel()
                prev_hashes = list(rec.message_hashes or [])
                new_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                base_prev = rec.base_text or ""
                k = 0
                max_k = min(len(prev_hashes), len(new_hashes))
                while k < max_k and prev_hashes[k] == new_hashes[k]:
                    k += 1
                if rec.boundary_offsets and k > 0:
                    off = list(rec.boundary_offsets or [])
                    k = min(k, len(off))
                    base_prev_tok = int(off[k-1]) if k > 0 else 0
                    # Trim cache back to boundary
                    trailer_tok = int(len(prev) - base_prev_tok)
                    if trailer_tok > 0 and can_trim_prompt_cache(rec.cache):
                        try:
                            trim_prompt_cache(rec.cache, trailer_tok)
                            prev = prev[:base_prev_tok]
                        except Exception as e:
                            log.warning(f"KV trim failed (boundary LCP): {e}")
                    # Build incremental tails per added message
                    base_str_k = build_base_prompt_for_flat(req.flat[:k], len(imgs))
                    tail_arrays = []
                    boundary_offsets_new = off[:k]
                    cur_tok = base_prev_tok
                    for i in range(k, len(req.flat)):
                        base_i = build_base_prompt_for_flat(req.flat[: i + 1], len(imgs))
                        delta = base_i[len(base_str_k):]
                        delta_ids = _encode(delta)
                        delta_ids = delta_ids if getattr(delta_ids, 'ndim', 1) == 1 else delta_ids.ravel()
                        dn = _np.array(delta_ids, copy=False).astype('uint32').ravel()
                        if len(dn) > 0:
                            tail_arrays.append(dn)
                        cur_tok += int(len(dn))
                        boundary_offsets_new.append(cur_tok)
                        base_str_k = base_i
                    # Append generation prompt for new full prompt
                    gen_str = text[len(base_str_k):]
                    gen_ids = _encode(gen_str)
                    gen_ids = gen_ids if getattr(gen_ids, 'ndim', 1) == 1 else gen_ids.ravel()
                    gen_np = _np.array(gen_ids, copy=False).astype('uint32').ravel()
                    suffix_cat = gen_np if len(tail_arrays) == 0 else _np.concatenate(tail_arrays + [gen_np])
                    suffix_ids = mx.array(suffix_cat)
                    precomp_cache = (rec.cache, base_prev_tok, suffix_ids)
                    cand = prev if len(suffix_cat) == 0 else _np.concatenate([prev, suffix_cat])
                    conv_diag.update({"mode": "hit", "cached": base_prev_tok, "processing": int(len(suffix_cat))})
                    # Stash for commit
                    req.__dict__["_boundary_offsets_new"] = boundary_offsets_new
                    req.__dict__["_message_hashes_new"] = new_hashes
                if precomp_cache is None:
                    if base_prev and text.startswith(base_prev):
                        base_new = build_base_prompt(req, len(imgs))
                        if not text.startswith(base_new):
                            # rebuild prompt to ensure consistency
                            base_new = build_base_prompt(req, len(imgs))
                        # Compute trailer tokens to trim existing cache back to base_prev
                        trailer_prev_str = (rec.text or "")[len(base_prev):]
                        trailer_prev_ids = _encode(trailer_prev_str)
                        trailer_prev_tok = int(trailer_prev_ids.shape[-1] if getattr(trailer_prev_ids, 'ndim', 1) != 1 else len(trailer_prev_ids))
                        if trailer_prev_tok > 0 and can_trim_prompt_cache(rec.cache):
                            try:
                                trim_prompt_cache(rec.cache, trailer_prev_tok)
                            except Exception as e:
                                log.warning(f"KV trim failed: {e}")
                        # Tail between base_prev and base_new
                        tail = base_new[len(base_prev):]
                        tail_ids = _encode(tail)
                        tail_ids = tail_ids if getattr(tail_ids, 'ndim', 1) == 1 else tail_ids.ravel()
                        # Append generation prompt for new full prompt
                        gen_str = text[len(base_new):]
                        gen_ids = _encode(gen_str)
                        gen_ids = gen_ids if getattr(gen_ids, 'ndim', 1) == 1 else gen_ids.ravel()
                        suffix_ids = mx.array(_np.concatenate([
                            _np.array(tail_ids, copy=False).astype('uint32').ravel(),
                            _np.array(gen_ids, copy=False).astype('uint32').ravel(),
                        ]))
                        base_prev_tok = int(len(prev) - trailer_prev_tok)
                        precomp_cache = (rec.cache, base_prev_tok, suffix_ids)
                        # Build candidate tokens for commit without full re-encode
                        tail_np = _np.array(tail_ids, copy=False).astype('uint32').ravel()
                        gen_np = _np.array(gen_ids, copy=False).astype('uint32').ravel()
                        cand = _np.concatenate([prev[:base_prev_tok], tail_np, gen_np])
                        conv_diag.update({"mode": "hit", "cached": base_prev_tok, "processing": int(len(tail_np) + len(gen_np))})
                        log.info(f"🧵 Conversation KV hit (base/string) for '{conv_id}' (cached_prefix={base_prev_tok} tokens, processing={len(tail_np)+len(gen_np)})")
                    else:
                        # Try snapshots by string
                        hit = False
                        for snap in reversed(rec.snapshots):
                            sbase = snap.get("base_text") or ""
                            stxt = snap.get("text") or ""
                            if sbase and text.startswith(sbase):
                                stoks = _np.array(snap["tokens"], copy=False).astype('uint32').ravel()
                                # Trim snapshot cache back to its base
                                trailer_snap_str = stxt[len(sbase):]
                                trailer_snap_ids = _encode(trailer_snap_str)
                                trailer_snap_tok = int(trailer_snap_ids.shape[-1] if getattr(trailer_snap_ids, 'ndim', 1) != 1 else len(trailer_snap_ids))
                                scache = snap["cache"]
                                if trailer_snap_tok > 0 and can_trim_prompt_cache(scache):
                                    try:
                                        trim_prompt_cache(scache, trailer_snap_tok)
                                    except Exception as e:
                                        log.warning(f"KV trim failed (snapshot): {e}")
                                base_new = build_base_prompt(req, len(imgs))
                                tail = base_new[len(sbase):]
                                tail_ids = _encode(tail)
                                tail_ids = tail_ids if getattr(tail_ids, 'ndim', 1) == 1 else tail_ids.ravel()
                                gen_str = text[len(base_new):]
                                gen_ids = _encode(gen_str)
                                gen_ids = gen_ids if getattr(gen_ids, 'ndim', 1) == 1 else gen_ids.ravel()
                                suffix_ids = mx.array(_np.concatenate([
                                    _np.array(tail_ids, copy=False).astype('uint32').ravel(),
                                    _np.array(gen_ids, copy=False).astype('uint32').ravel(),
                                ]))
                                base_snap_tok = int(len(stoks) - trailer_snap_tok)
                                precomp_cache = (scache, base_snap_tok, suffix_ids)
                                tail_np = _np.array(tail_ids, copy=False).astype('uint32').ravel()
                                gen_np = _np.array(gen_ids, copy=False).astype('uint32').ravel()
                                cand = _np.concatenate([stoks[:base_snap_tok], tail_np, gen_np])
                                conv_diag.update({"mode": "snapshot", "cached": base_snap_tok, "processing": int(len(tail_np)+len(gen_np))})
                                log.info(f"🧵 Conversation snapshot hit (base/string) for '{conv_id}' (cached_prefix={base_snap_tok} tokens, processing={len(tail_np)+len(gen_np)})")
                                hit = True
                                break
                        if not hit:
                            # Fallback to token-based comparison if we already encoded full prompt
                            if full_ids_for_conv is None:
                                full_ids_for_conv = _encode(prompt_str)
                                if getattr(full_ids_for_conv, 'ndim', 1) != 1:
                                    full_ids_for_conv = full_ids_for_conv.ravel()
                            cand = _np.array(full_ids_for_conv, copy=False).astype('uint32').ravel()
                            if len(prev) <= len(cand) and _np.array_equal(prev, cand[: len(prev)]):
                                match_len = int(len(prev))
                                suffix_ids = mx.array(cand[match_len:])
                                precomp_cache = (rec.cache, match_len, suffix_ids)
                                conv_diag.update({"mode": "hit", "cached": match_len, "processing": int(len(cand) - match_len)})
                                log.info(f"🧵 Conversation KV hit for '{conv_id}' (cached_prefix={match_len} tokens, processing={len(cand)-match_len})")
                            else:
                                # Token-based snapshots
                                token_hit = False
                                for snap in reversed(rec.snapshots):
                                    stoks = _np.array(snap["tokens"], copy=False).astype('uint32').ravel()
                                    if len(stoks) <= len(cand) and _np.array_equal(stoks, cand[: len(stoks)]):
                                        match_len = int(len(stoks))
                                        suffix_ids = mx.array(cand[match_len:])
                                        precomp_cache = (snap["cache"], match_len, suffix_ids)
                                        conv_diag.update({"mode": "snapshot", "cached": match_len, "processing": int(len(cand) - match_len)})
                                        log.info(f"🧵 Conversation snapshot hit for '{conv_id}' (cached_prefix={match_len} tokens, processing={len(cand)-match_len})")
                                        token_hit = True
                                        break
                                if not token_hit:
                                    log.info(f"🧵 Conversation KV miss for '{conv_id}' (prefix mismatch)")
            except Exception as e:
                log.warning(f"Conversation KV compare failed: {e}")
        if precomp_cache is None:
            # no existing record or mismatch → allocate fresh cache for this conversation
            ensure_len = 0
            if full_ids_for_conv is not None:
                ensure_len = _mx_length(full_ids_for_conv)
            conv_cap = _positive_or_none(args.conversation_kv_max_tokens)
            max_size = _resolve_cache_size(ensure=ensure_len, cli_cap=conv_cap)
            conv_cache = _allocate_prompt_cache(
                max_size,
                keep=args.kv_cache_keep,
                reason=f"conversation:{conv_id}",
            )
            # If we already computed cand (full or partial), use it; else encode now
            if cand is None:
                if full_ids_for_conv is None:
                    full_ids_for_conv = _encode(prompt_str)
                if getattr(full_ids_for_conv, 'ndim', 1) != 1:
                    full_ids_for_conv = full_ids_for_conv.ravel()
                cand = _np.array(full_ids_for_conv, copy=False).astype('uint32').ravel()
            precomp_cache = (conv_cache, 0, mx.array(cand))
            conv_diag.update({"mode": "fresh", "cached": 0, "processing": int(len(cand))})
            desc = "unbounded" if max_size is None else str(int(max_size))
            log.info(f"🧵 Conversation KV allocate for '{conv_id}' (max_size={desc})")
        # pass precomputed cache + suffix to generators via req
        req.__dict__["_precomputed_cache"] = precomp_cache
        # stash conv commit info for after generation
        req.__dict__["_conv_commit"] = {"id": conv_id, "tokens": cand}
    req.__dict__["_conv_diag"] = conv_diag
    
    # Extract system prompt for caching
    system_prompt_str = build_system_prompt(req) if not IS_VISION else ""

    global GLOBAL_PROMPT_CACHE, CACHE_PRIMED_THIS_SESSION, CACHED_PREFIX_LEN, CACHE_PREFIX_HASH  # Ensure globals are modifiable

    # ----- determine if existing cache should be discarded -----
    should_discard_cache = False
    if args.enable_prefix_caching and not IS_VISION and GLOBAL_PROMPT_CACHE is not None and system_prompt_str:
        # A cache exists and we have a system prompt. Check if the system prompt has changed.
        current_system_ids = _encode(system_prompt_str)
        current_system_hash = _hash_tokens(current_system_ids)
        
        if current_system_hash != CACHE_PREFIX_HASH:
            # System prompt has changed. Cache is not usable and should be replaced.
            log.info(
                "🔄 System prompt has changed. Discarding old cache."
            )
            should_discard_cache = True
        # else: system prompt matches -> keep cache

    if should_discard_cache:
        log.info("Executing cache discard operation.")
        GLOBAL_PROMPT_CACHE = None
        CACHED_PREFIX_LEN = 0
        CACHE_PREFIX_HASH = ""
        CACHE_PRIMED_THIS_SESSION = False
        try:
            if GLOBAL_CACHE_FILE_PATH:
                len_path = GLOBAL_CACHE_FILE_PATH + ".len"
                hash_path = GLOBAL_CACHE_FILE_PATH + ".hash"
                if os.path.exists(GLOBAL_CACHE_FILE_PATH):
                    os.remove(GLOBAL_CACHE_FILE_PATH)
                    log.info(f"Deleted cache file: {GLOBAL_CACHE_FILE_PATH}")
                if os.path.exists(len_path):
                    os.remove(len_path)
                    log.info(f"Deleted cache length file: {len_path}")
                if os.path.exists(hash_path):
                    os.remove(hash_path)
                    log.info(f"Deleted cache hash file: {hash_path}")
        except Exception as e:
            log.warning(f"Could not delete old cache files: {e}")
    # -----------------------------------------------------------------------

    # Create cache if needed and we have a system prompt (with bounded size)
    if (
        args.enable_prefix_caching
        and not args.disable_kv_cache
        and not IS_VISION
        and GLOBAL_PROMPT_CACHE is None
        and not CACHE_PRIMED_THIS_SESSION
        and GLOBAL_CACHE_FILE_PATH is not None
        and system_prompt_str
    ):
        log.info(f"Creating system message cache from current request, saving to {GLOBAL_CACHE_FILE_PATH}...")
        cache_creation_start_time = time.perf_counter()
        try:
            system_ids = _encode(system_prompt_str)
            if system_ids.ndim == 1:
                system_ids = system_ids[None, :]
            
            # Build a bounded KV cache to cap memory (prefix length + headroom, within [min,max])
            sys_len = int(system_ids.shape[-1])
            ensure_len = sys_len + int(args.prefix_cache_headroom)
            max_size = _resolve_cache_size(
                ensure=ensure_len,
                cli_cap=args.kv_cache_max_tokens,
            )
            temp_cache = _allocate_prompt_cache(
                max_size,
                keep=args.kv_cache_keep,
                reason="prefix",
            )
            MODEL(system_ids, cache=temp_cache)  # Prime the cache with system prompt only

            CACHED_PREFIX_LEN = int(system_ids.shape[-1])
            CACHE_PREFIX_HASH = _hash_tokens(system_ids)
            try:
                Path(GLOBAL_CACHE_FILE_PATH + ".len").write_text(str(CACHED_PREFIX_LEN))
                Path(GLOBAL_CACHE_FILE_PATH + ".hash").write_text(CACHE_PREFIX_HASH)
            except Exception:
                pass

            GLOBAL_PROMPT_CACHE = temp_cache
            try:
                save_prompt_cache(GLOBAL_CACHE_FILE_PATH, GLOBAL_PROMPT_CACHE)
            except Exception as e:
                log.warning(f"Could not save prompt cache: {e}")
            CACHE_PRIMED_THIS_SESSION = True
            cache_creation_duration = time.perf_counter() - cache_creation_start_time
            desc = "unbounded" if max_size is None else str(int(max_size))
            log.info(
                "System message cache created and saved (%d tokens, max_size=%s) in %.2f seconds.",
                CACHED_PREFIX_LEN,
                desc,
                cache_creation_duration,
            )
        except Exception as e:
            log.error(f"Error creating/priming system message cache: {e}")

    # The generation functions (sync_gen, stream_chunks) will use GLOBAL_PROMPT_CACHE if set

    # Prepare diagnostic headers
    diag = req.__dict__.get("_conv_diag", {}) or {}
    headers = {
        "X-Conv-Id": str(diag.get("id", "")),
        "X-Conv-KV": str(diag.get("mode", "none")),
        "X-Conv-Cached-Tokens": str(diag.get("cached", 0)),
        "X-Conv-Processing-Tokens": str(diag.get("processing", 0)),
    }

    if not req.stream:
        txt_raw = sync_gen(prompt_str, imgs, req)
        txt = strip_thoughts(txt_raw, req.strip_thinking or args.strip_thinking)

        tool_calls = None
        if tools_enabled:
            if forced_name:
                args_obj = _maybe_parse_arguments_json(txt)
                if isinstance(args_obj, dict):
                    try:
                        arg_str = json.dumps(args_obj, ensure_ascii=False)
                    except Exception:
                        arg_str = str(args_obj)
                    tool_calls = [{
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": forced_name, "arguments": arg_str},
                    }]
                else:
                    tool_calls = _maybe_parse_tool_calls(txt)
            else:
                tool_calls = _maybe_parse_tool_calls(txt)

        if IS_VISION:
            usage = _usage_dict(len(prompt_str), _tok_len(txt), 0.0, 0, 0)
        else:
            usage = req.__dict__.get("_usage")
            if not isinstance(usage, dict):
                p_tok, c_tok, dur = (len(prompt_str), len(txt), 0.0)
                usage = _usage_dict(p_tok, c_tok, dur, 0, 0)

        message: Dict[str, Any] = {"role": "assistant"}
        finish_reason = "stop"
        if tool_calls:
            message["content"] = None
            message["tool_calls"] = tool_calls
            finish_reason = "tool_calls"
        else:
            message["content"] = txt

        # Commit conversation KV (if any)
        conv_meta = req.__dict__.get("_conv_commit")
        if conv_meta and not req.reset_conversation and not args.disable_kv_cache and args.enable_conversation_cache:
            try:
                cid = conv_meta.get("id")
                tokens = conv_meta.get("tokens")
                # Use the cache object we passed to generator (updated in-place)
                cached = req.__dict__.get("_precomputed_cache")[0]
                # Update existing record if present to retain snapshots
                rec = CONV_KV.get(cid)
                if rec is not None:
                    rec.cache = cached
                    rec.tokens = tokens
                    rec.text = prompt_str
                    if not IS_VISION:
                        try:
                            rec.base_text = build_base_prompt(req, len(imgs))
                        except Exception:
                            pass
                    # Persist boundary metadata and messages snapshot
                    try:
                        offsets_new = req.__dict__.get("_boundary_offsets_new")
                        if offsets_new is None and not IS_VISION:
                            offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                        rec.boundary_offsets = offsets_new
                        rec.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                        # messages snapshot
                        rec.messages = [dict(role=m.get('role',''), content=m.get('content','') or '') for m in req.flat]
                    except Exception as e:
                        log.warning(f"Persist boundary metadata failed: {e}")
                else:
                    base_txt = ""
                    if not IS_VISION:
                        try:
                            base_txt = build_base_prompt(req, len(imgs))
                        except Exception:
                            base_txt = ""
                    CONV_KV.put(cid, cached, tokens, text=prompt_str, base_text=base_txt)
                    # Set metadata on the new record
                    try:
                        rec2 = CONV_KV.get(cid)
                        if rec2 is not None:
                            offsets_new = req.__dict__.get("_boundary_offsets_new")
                            if offsets_new is None and not IS_VISION:
                                offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                            rec2.boundary_offsets = offsets_new
                            rec2.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                            rec2.messages = [dict(role=m.get('role',''), content=m.get('content','') or '') for m in req.flat]
                    except Exception as e:
                        log.warning(f"Persist boundary metadata (new rec) failed: {e}")
                log.info(f"🧵 Conversation KV stored for '{cid}' (tokens={len(tokens)})")
            except Exception as e:
                log.warning(f"Conversation KV store failed: {e}")

        payload = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": message,
                    "finish_reason": finish_reason,
                }
            ],
            "usage": usage,
        }
        try:
            payload["metadata"] = {"conversation_id": headers.get("X-Conv-Id", "")}
        except Exception:
            payload["metadata"] = {"conversation_id": ""}
        return JSONResponse(content=payload, headers=headers)

    async def event_stream():
        # If tools are enabled, run a one-shot generation and stream a structured tool_calls delta
        if tools_enabled:
            rid, created = f"chatcmpl-{uuid.uuid4()}", int(time.time())
            txt_raw = sync_gen(prompt_str, imgs, req)
            txt = strip_thoughts(txt_raw, req.strip_thinking or args.strip_thinking)
            calls = []
            if forced_name:
                args_obj = _maybe_parse_arguments_json(txt)
                if isinstance(args_obj, dict):
                    try:
                        arg_str = json.dumps(args_obj, ensure_ascii=False)
                    except Exception:
                        arg_str = str(args_obj)
                    calls = [{"id": "call_1", "type": "function", "function": {"name": forced_name, "arguments": arg_str}}]
                else:
                    calls = _maybe_parse_tool_calls(txt) or []
            else:
                calls = _maybe_parse_tool_calls(txt) or []
            # Emit role first
            yield _sse_chunk(rid, created, {"role": "assistant"})
            if calls:
                # Emit each call in two chunks: name, then arguments
                for idx, call in enumerate(calls):
                    # Name (and id/type)
                    delta1 = {
                        "tool_calls": [
                            {
                                "index": idx,
                                "id": call.get("id"),
                                "type": "function",
                                "function": {"name": call["function"]["name"]},
                            }
                        ]
                    }
                    yield _sse_chunk(rid, created, delta1)
                    # Arguments (as a single string chunk)
                    delta2 = {
                        "tool_calls": [
                            {
                                "index": idx,
                                "function": {"arguments": call["function"]["arguments"]},
                            }
                        ]
                    }
                    yield _sse_chunk(rid, created, delta2)
                # Final chunk indicating finish by tool_calls
                final = {
                    "id": rid,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL_NAME,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}],
                }
                yield f"data: {json.dumps(final)}\n\n"
                yield "data: [DONE]\n\n"
            else:
                # No tool_calls detected; stream a single content chunk and stop
                yield _sse_chunk(rid, created, {"content": txt})
                final = {
                    "id": rid,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": MODEL_NAME,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                }
                yield f"data: {json.dumps(final)}\n\n"
                # Commit conversation KV (if any)
                conv_meta = req.__dict__.get("_conv_commit")
                if conv_meta and not req.reset_conversation and not args.disable_kv_cache and args.enable_conversation_cache:
                    try:
                        cid = conv_meta.get("id")
                        tokens = conv_meta.get("tokens")
                        cached = req.__dict__.get("_precomputed_cache")[0]
                        rec = CONV_KV.get(cid)
                        if rec is not None:
                            rec.cache = cached
                            rec.tokens = tokens
                            rec.text = prompt_str
                            if not IS_VISION:
                                try:
                                    rec.base_text = build_base_prompt(req, len(imgs))
                                except Exception:
                                    pass
                            try:
                                offsets_new = req.__dict__.get("_boundary_offsets_new")
                                if offsets_new is None and not IS_VISION:
                                    offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                                rec.boundary_offsets = offsets_new
                                rec.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                            except Exception as e:
                                log.warning(f"Persist boundary metadata failed: {e}")
                        else:
                            base_txt = ""
                            if not IS_VISION:
                                try:
                                    base_txt = build_base_prompt(req, len(imgs))
                                except Exception:
                                    base_txt = ""
                            CONV_KV.put(cid, cached, tokens, text=prompt_str, base_text=base_txt)
                            try:
                                rec2 = CONV_KV.get(cid)
                                if rec2 is not None:
                                    offsets_new = req.__dict__.get("_boundary_offsets_new")
                                    if offsets_new is None and not IS_VISION:
                                        offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                                    rec2.boundary_offsets = offsets_new
                                    rec2.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                            except Exception as e:
                                log.warning(f"Persist boundary metadata (new rec) failed: {e}")
                        log.info(f"🧵 Conversation KV stored for '{cid}' (tokens={len(tokens)})")
                    except Exception as e:
                        log.warning(f"Conversation KV store failed: {e}")
                yield "data: [DONE]\n\n"
                return
        # Default: passthrough token streaming
        for chunk in stream_chunks(prompt_str, imgs, req):
            yield chunk
            await asyncio.sleep(0)
        # Commit after streaming completes
        conv_meta = req.__dict__.get("_conv_commit")
        if conv_meta and not req.reset_conversation and not args.disable_kv_cache and args.enable_conversation_cache:
            try:
                cid = conv_meta.get("id")
                tokens = conv_meta.get("tokens")
                cached = req.__dict__.get("_precomputed_cache")[0]
                rec = CONV_KV.get(cid)
                if rec is not None:
                    rec.cache = cached
                    rec.tokens = tokens
                    rec.text = prompt_str
                    if not IS_VISION:
                        try:
                            rec.base_text = build_base_prompt(req, len(imgs))
                        except Exception:
                            pass
                    try:
                        offsets_new = req.__dict__.get("_boundary_offsets_new")
                        if offsets_new is None and not IS_VISION:
                            offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                        rec.boundary_offsets = offsets_new
                        rec.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                    except Exception as e:
                        log.warning(f"Persist boundary metadata failed: {e}")
                else:
                    base_txt = ""
                    if not IS_VISION:
                        try:
                            base_txt = build_base_prompt(req, len(imgs))
                        except Exception:
                            base_txt = ""
                    CONV_KV.put(cid, cached, tokens, text=prompt_str, base_text=base_txt)
                    try:
                        rec2 = CONV_KV.get(cid)
                        if rec2 is not None:
                            offsets_new = req.__dict__.get("_boundary_offsets_new")
                            if offsets_new is None and not IS_VISION:
                                offsets_new = _boundary_offsets_for_flat(req.flat, len(imgs))
                            rec2.boundary_offsets = offsets_new
                            rec2.message_hashes = [_msg_hash(m.get('role',''), m.get('content','') or '') for m in req.flat]
                    except Exception as e:
                        log.warning(f"Persist boundary metadata (new rec) failed: {e}")
                log.info(f"🧵 Conversation KV stored for '{cid}' (tokens={len(tokens)})")
            except Exception as e:
                log.warning(f"Conversation KV store failed: {e}")

    if req.stream:
        return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)
    else:
        if IS_VISION:
            usage = _usage_dict(len(prompt_str), _tok_len(txt), 0.0, 0, 0)
        else:
            usage = req.__dict__.get("_usage")
            if not isinstance(usage, dict):
                p_tok, c_tok, dur = (len(prompt_str), len(txt), 0.0)
                usage = _usage_dict(p_tok, c_tok, dur, 0, 0)
        payload2 = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": txt},
                    "finish_reason": "stop",
                }
            ],
            "usage": usage,
        }
        try:
            payload2["metadata"] = {"conversation_id": headers.get("X-Conv-Id", "")}
        except Exception:
            payload2["metadata"] = {"conversation_id": ""}
        return JSONResponse(content=payload2, headers=headers)

def main_entry() -> None:
    uvicorn.run(app, host=args.host, port=args.port)

# ─────────────────────────── main ────────────────────────────────
if __name__ == "__main__":
    log.info(
        "Serving %s on %s:%d  (vision=%s)", MODEL_NAME, args.host, args.port, IS_VISION
    )
    uvicorn.run(app, host=args.host, port=args.port) 
