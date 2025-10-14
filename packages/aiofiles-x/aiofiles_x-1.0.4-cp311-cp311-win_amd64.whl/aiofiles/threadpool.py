"""Async file operations with C++ backend."""

import asyncio
import sys
from functools import partial
from typing import Optional, Union, List, Any
from .base import AiofilesContextManager


class _DirectReturn:
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
    def __init__(self, cpp_file, loop=None, executor=None):
        self._cpp_file = cpp_file
        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor
        self._use_executor_threshold = 1024 * 1024  # 1MB

    def close(self):
        return _DirectReturn(self._cpp_file.close())

    def flush(self):
        return _DirectReturn(self._cpp_file.flush())

    def isatty(self):
        return _DirectReturn(self._cpp_file.isatty())

    def read(self, size: Optional[int] = None):
        if size is None:
            return _DirectReturn(self._cpp_file.read())
        else:
            return _DirectReturn(self._cpp_file.read(size))

    def readall(self):
        return _DirectReturn(self._cpp_file.readall())

    def read1(self, size: Optional[int] = None):
        if size is None:
            return _DirectReturn(self._cpp_file.read1())
        else:
            return _DirectReturn(self._cpp_file.read1(size))

    def readinto(self, buffer):
        return _DirectReturn(self._cpp_file.readinto(buffer))

    def readline(self, size: Optional[int] = None):
        return _DirectReturn(self._cpp_file.readline(size))

    def readlines(self, hint: Optional[int] = None):
        return _DirectReturn(self._cpp_file.readlines(hint))

    def seek(self, offset: int, whence: int = 0):
        return _DirectReturn(self._cpp_file.seek(offset, whence))

    def tell(self):
        return _DirectReturn(self._cpp_file.tell())

    def truncate(self, size: Optional[int] = None):
        return _DirectReturn(self._cpp_file.truncate(size))

    def write(self, data: Union[str, bytes]):
        return _DirectReturn(self._cpp_file.write(data))

    def writelines(self, lines: List[Union[str, bytes]]):
        return _DirectReturn(self._cpp_file.writelines(lines))

    def seekable(self):
        if hasattr(self._cpp_file, "seekable"):
            return self._cpp_file.seekable()
        return True

    def writable(self):
        if hasattr(self._cpp_file, "writable"):
            return self._cpp_file.writable()
        mode = getattr(self._cpp_file, "mode", "r")
        return "w" in mode or "a" in mode or "+" in mode

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        if hasattr(self._cpp_file, "name"):
            return self._cpp_file.name
        return None

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def mode(self):
        if hasattr(self._cpp_file, "mode"):
            return self._cpp_file.mode
        return getattr(self._cpp_file, "mode", None)

    def __aiter__(self):
        return self

    async def __anext__(self):
        line = await self.readline()
        if not line:
            raise StopAsyncIteration
        return line

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
    def __init__(self, stream):
        self._stream = stream
        self._loop = None

    async def read(self, size: Optional[int] = None):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        if size is None:
            return await self._loop.run_in_executor(None, self._stream.read)
        return await self._loop.run_in_executor(None, self._stream.read, size)

    async def readline(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._stream.readline)

    async def write(self, data: str):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()
        return await self._loop.run_in_executor(None, self._stream.write, data)

    async def flush(self):
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
