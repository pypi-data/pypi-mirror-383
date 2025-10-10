"""
Kamiwaza-MLX – unified server & CLI wrappers around the mlx-lm / mlx-vlm stack.

Exposes the same public API as the original scripts but packaged so it can be
installed from PyPI and run with e.g.  `python -m kamiwaza_mlx.server`.
"""

from __future__ import annotations

import importlib.metadata as _ilmd

try:
    __version__: str = _ilmd.version(__name__)
except _ilmd.PackageNotFoundError:  # pragma: no cover – during editable installs
    # When run from source before the package is built/installed.
    __version__ = "0.0.0.dev0"

del _ilmd

# Re-export the two main sub-modules so users can do e.g.
# >>> from kamiwaza_mlx import infer, server
# without having to import the package twice.

from . import infer  # noqa: E402  (import after __version__ definition)
from . import server  # noqa: E402

__all__: list[str] = ["infer", "server", "__version__"] 
