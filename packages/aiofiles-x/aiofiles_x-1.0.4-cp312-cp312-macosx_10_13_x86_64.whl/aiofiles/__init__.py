"""Utilities for asyncio-friendly file handling."""

try:
    from . import tempfile, os
    from .threadpool import (
        open,
        stderr,
        stderr_bytes,
        stdin,
        stdin_bytes,
        stdout,
        stdout_bytes,
    )
except ImportError as e:
    import sys

    print(f"Error importing aiofiles submodules: {e}", file=sys.stderr)
    print("This usually means the package is not properly installed.", file=sys.stderr)
    print("Try running: pip install -e . (from the project root)", file=sys.stderr)
    raise

__all__ = [
    "open",
    "tempfile",
    "os",
    "stdin",
    "stdout",
    "stderr",
    "stdin_bytes",
    "stdout_bytes",
    "stderr_bytes",
]

__version__ = "1.0.4"
