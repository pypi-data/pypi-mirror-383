"""Async tempfile operations."""

import asyncio
import tempfile as _tempfile
from functools import partial

from .threadpool import AsyncFileWrapper


class TemporaryFile:
    def __init__(
        self,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
        *,
        loop=None,
        executor=None,
    ):
        self._mode = mode
        self._buffering = buffering
        self._encoding = encoding
        self._newline = newline
        self._suffix = suffix
        self._prefix = prefix
        self._dir = dir
        self._loop = loop
        self._executor = executor
        self._file = None

    async def __aenter__(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._file = await self._loop.run_in_executor(
            self._executor,
            partial(
                _tempfile.TemporaryFile,
                mode=self._mode,
                buffering=self._buffering,
                encoding=self._encoding,
                newline=self._newline,
                suffix=self._suffix,
                prefix=self._prefix,
                dir=self._dir,
            ),
        )
        return AsyncFileWrapper(self._file, loop=self._loop, executor=self._executor)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            await self._loop.run_in_executor(self._executor, self._file.close)
        return False


class NamedTemporaryFile:
    def __init__(
        self,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
        delete=True,
        *,
        loop=None,
        executor=None,
    ):
        self._mode = mode
        self._buffering = buffering
        self._encoding = encoding
        self._newline = newline
        self._suffix = suffix
        self._prefix = prefix
        self._dir = dir
        self._delete = delete
        self._loop = loop
        self._executor = executor
        self._file = None

    async def __aenter__(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._file = await self._loop.run_in_executor(
            self._executor,
            partial(
                _tempfile.NamedTemporaryFile,
                mode=self._mode,
                buffering=self._buffering,
                encoding=self._encoding,
                newline=self._newline,
                suffix=self._suffix,
                prefix=self._prefix,
                dir=self._dir,
                delete=self._delete,
            ),
        )
        wrapper = AsyncFileWrapper(self._file, loop=self._loop, executor=self._executor)
        wrapper.name = self._file.name
        return wrapper

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            await self._loop.run_in_executor(self._executor, self._file.close)
        return False


class SpooledTemporaryFile:
    def __init__(
        self,
        max_size=0,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
        *,
        loop=None,
        executor=None,
    ):
        self._max_size = max_size
        self._mode = mode
        self._buffering = buffering
        self._encoding = encoding
        self._newline = newline
        self._suffix = suffix
        self._prefix = prefix
        self._dir = dir
        self._loop = loop
        self._executor = executor
        self._file = None

    async def __aenter__(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._file = await self._loop.run_in_executor(
            self._executor,
            partial(
                _tempfile.SpooledTemporaryFile,
                max_size=self._max_size,
                mode=self._mode,
                buffering=self._buffering,
                encoding=self._encoding,
                newline=self._newline,
                suffix=self._suffix,
                prefix=self._prefix,
                dir=self._dir,
            ),
        )
        return AsyncFileWrapper(self._file, loop=self._loop, executor=self._executor)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._file:
            await self._loop.run_in_executor(self._executor, self._file.close)
        return False


class TemporaryDirectory:
    def __init__(self, suffix=None, prefix=None, dir=None, *, loop=None, executor=None):
        self._suffix = suffix
        self._prefix = prefix
        self._dir = dir
        self._loop = loop
        self._executor = executor
        self._tmpdir = None

    async def __aenter__(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        self._tmpdir = await self._loop.run_in_executor(
            self._executor,
            partial(
                _tempfile.TemporaryDirectory,
                suffix=self._suffix,
                prefix=self._prefix,
                dir=self._dir,
            ),
        )
        return self._tmpdir.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._tmpdir:
            await self._loop.run_in_executor(
                self._executor,
                partial(self._tmpdir.__exit__, exc_type, exc_val, exc_tb),
            )
        return False


__all__ = [
    "TemporaryFile",
    "NamedTemporaryFile",
    "SpooledTemporaryFile",
    "TemporaryDirectory",
]
