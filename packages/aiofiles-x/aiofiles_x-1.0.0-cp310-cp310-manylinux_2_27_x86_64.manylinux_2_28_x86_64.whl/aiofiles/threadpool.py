"""High-performance async file operations using C++ backend."""

import asyncio
import sys
from functools import partial
from typing import Optional, Union, List, Any
from .base import AiofilesContextManager


class _DirectReturn:
    """Minimal awaitable that returns value immediately without suspension."""

    __slots__ = ("_value",)

    def __init__(self, value):
        self._value = value

    def __await__(self):
        yield
        return self._value

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration(self._value)


try:
    from _aiofiles_core import AsyncFile as _CppAsyncFile
except ImportError:
    _CppAsyncFile = None


class AsyncFileWrapper:
    """Async wrapper for C++ AsyncFile that provides Python async interface.

    Optimization: Direct C++ calls without executor overhead for buffered operations.
    C++ backend already handles buffering, so thread pool overhead is unnecessary.
    """

    def __init__(self, cpp_file, loop=None, executor=None):
        self._cpp_file = cpp_file
        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor
        self._use_executor_threshold = 1024 * 1024  # 1MB

    def close(self):
        """Close the file."""
        return _DirectReturn(self._cpp_file.close())

    def flush(self):
        """Flush the file."""
        return _DirectReturn(self._cpp_file.flush())

    def isatty(self):
        """Check if file is a TTY."""
        return _DirectReturn(self._cpp_file.isatty())

    def read(self, size: Optional[int] = None):
        """Read from file."""
        if size is None:
            return _DirectReturn(self._cpp_file.read())
        else:
            return _DirectReturn(self._cpp_file.read(size))

    def readline(self, size: Optional[int] = None):
        """Read a line from file."""
        return _DirectReturn(self._cpp_file.readline(size))

    def readlines(self, hint: Optional[int] = None):
        """Read lines from file."""
        return _DirectReturn(self._cpp_file.readlines(hint))

    def seek(self, offset: int, whence: int = 0):
        """Seek to position in file."""
        return _DirectReturn(self._cpp_file.seek(offset, whence))

    def tell(self):
        """Get current position in file."""
        return _DirectReturn(self._cpp_file.tell())

    def truncate(self, size: Optional[int] = None):
        """Truncate file."""
        return _DirectReturn(self._cpp_file.truncate(size))

    def write(self, data: Union[str, bytes]):
        """Write to file."""
        return _DirectReturn(self._cpp_file.write(data))

    def writelines(self, lines: List[Union[str, bytes]]):
        """Write lines to file."""
        return _DirectReturn(self._cpp_file.writelines(lines))

    def seekable(self):
        """Check if file is seekable."""
        if hasattr(self._cpp_file, "seekable"):
            return self._cpp_file.seekable()
        return True

    def writable(self):
        """Check if file is writable."""
        if hasattr(self._cpp_file, "writable"):
            return self._cpp_file.writable()
        mode = getattr(self._cpp_file, "mode", "r")
        return "w" in mode or "a" in mode or "+" in mode

    @property
    def name(self):
        """Get file name."""
        if hasattr(self, "_name"):
            return self._name
        if hasattr(self._cpp_file, "name"):
            return self._cpp_file.name
        return None

    @name.setter
    def name(self, value):
        """Set file name."""
        self._name = value

    @property
    def mode(self):
        """Get file mode."""
        if hasattr(self._cpp_file, "mode"):
            return self._cpp_file.mode
        return getattr(self._cpp_file, "mode", None)

    def __aiter__(self):
        """Async iterator."""
        return self

    async def __anext__(self):
        """Async get next line."""
        line = await self.readline()
        if not line:
            raise StopAsyncIteration
        return line

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return False


def open(
    file: Union[str, int],
    mode: str = "r",
    buffering: int = -1,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    closefd: bool = True,
    opener: Optional[Any] = None,
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    executor: Optional[Any] = None,
):
    """
    Open a file asynchronously.

    This function mirrors the built-in open() but returns an async context manager.

    Args:
        file: File path or file descriptor
        mode: File open mode (r, w, a, etc.)
        buffering: Buffering policy (-1 for default)
        encoding: Text encoding (for text mode)
        errors: Error handling strategy
        newline: Newline handling
        closefd: Whether to close file descriptor
        opener: Custom opener
        loop: Event loop to use
        executor: Executor to use for async operations

    Returns:
        AiofilesContextManager wrapping AsyncFileWrapper
    """
    return AiofilesContextManager(
        _open(
            file,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
            loop=loop,
            executor=executor,
        )
    )


async def _open(
    file: Union[str, int],
    mode: str = "r",
    buffering: int = -1,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    closefd: bool = True,
    opener: Optional[Any] = None,
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    executor: Optional[Any] = None,
):
    """Internal async open implementation."""
    if loop is None:
        loop = asyncio.get_running_loop()

    if _CppAsyncFile is not None:
        cpp_file = _CppAsyncFile(str(file), mode)
        try:
            cpp_file.open()
        except RuntimeError as e:
            err_msg = str(e)
            if "No such file" in err_msg or "cannot find" in err_msg:
                raise FileNotFoundError(err_msg) from e
            elif "Permission denied" in err_msg or "Access is denied" in err_msg:
                raise PermissionError(err_msg) from e
            else:
                raise
        return AsyncFileWrapper(cpp_file, loop=loop, executor=executor)
    else:
        cb = partial(
            __builtins__["open"],
            file,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
        )
        f = await loop.run_in_executor(executor, cb)
        return AsyncFileWrapper(f, loop=loop, executor=executor)


class AsyncTextStreamWrapper:
    """Async wrapper for standard text streams."""

    def __init__(self, stream):
        self._stream = stream
        self._loop = None

    async def read(self, size: Optional[int] = None):
        """Read from stream."""
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        if size is None:
            return await self._loop.run_in_executor(None, self._stream.read)
        return await self._loop.run_in_executor(None, self._stream.read, size)

    async def readline(self):
        """Read line from stream."""
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._stream.readline)

    async def write(self, data: str):
        """Write to stream."""
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._stream.write, data)

    async def flush(self):
        """Flush stream."""
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._stream.flush)


stdin = AsyncTextStreamWrapper(sys.stdin)
stdout = AsyncTextStreamWrapper(sys.stdout)
stderr = AsyncTextStreamWrapper(sys.stderr)
stdin_bytes = AsyncTextStreamWrapper(sys.stdin.buffer)
stdout_bytes = AsyncTextStreamWrapper(sys.stdout.buffer)
stderr_bytes = AsyncTextStreamWrapper(sys.stderr.buffer)


__all__ = [
    "open",
    "stdin",
    "stdout",
    "stderr",
    "stdin_bytes",
    "stdout_bytes",
    "stderr_bytes",
]
