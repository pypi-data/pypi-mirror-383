"""Utilities for asyncio-friendly file handling."""

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

__version__ = "24.0.0"
