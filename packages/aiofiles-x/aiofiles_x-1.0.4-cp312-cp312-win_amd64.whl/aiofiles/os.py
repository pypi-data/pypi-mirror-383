"""Async OS operations."""

import asyncio
import os as _os
from functools import partial, wraps


def _wrap_os_func(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    return wrapper


stat = _wrap_os_func(_os.stat)
rename = _wrap_os_func(_os.rename)
renames = _wrap_os_func(_os.renames)
replace = _wrap_os_func(_os.replace)
remove = _wrap_os_func(_os.remove)
unlink = _wrap_os_func(_os.unlink)
mkdir = _wrap_os_func(_os.mkdir)
makedirs = _wrap_os_func(_os.makedirs)
rmdir = _wrap_os_func(_os.rmdir)
removedirs = _wrap_os_func(_os.removedirs)
link = _wrap_os_func(_os.link)
symlink = _wrap_os_func(_os.symlink)
readlink = _wrap_os_func(_os.readlink)
listdir = _wrap_os_func(_os.listdir)
access = _wrap_os_func(_os.access)
getcwd = _wrap_os_func(_os.getcwd)

if hasattr(_os, "sendfile"):
    sendfile = _wrap_os_func(_os.sendfile)

if hasattr(_os, "statvfs"):
    statvfs = _wrap_os_func(_os.statvfs)

if hasattr(_os, "scandir"):
    scandir = _wrap_os_func(_os.scandir)


class PathModule:
    @staticmethod
    async def exists(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.exists, path)

    @staticmethod
    async def isfile(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.isfile, path)

    @staticmethod
    async def isdir(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.isdir, path)

    @staticmethod
    async def islink(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.islink, path)

    @staticmethod
    async def ismount(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.ismount, path)

    @staticmethod
    async def getsize(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.getsize, path)

    @staticmethod
    async def getatime(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.getatime, path)

    @staticmethod
    async def getmtime(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.getmtime, path)

    @staticmethod
    async def getctime(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.getctime, path)

    @staticmethod
    async def samefile(path1, path2):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.samefile, path1, path2)

    @staticmethod
    async def sameopenfile(fp1, fp2):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.sameopenfile, fp1, fp2)

    @staticmethod
    async def abspath(path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _os.path.abspath, path)


path = PathModule()


__all__ = [
    "stat",
    "rename",
    "renames",
    "replace",
    "remove",
    "unlink",
    "mkdir",
    "makedirs",
    "rmdir",
    "removedirs",
    "link",
    "symlink",
    "readlink",
    "listdir",
    "access",
    "getcwd",
    "path",
]

if hasattr(_os, "sendfile"):
    sendfile = _wrap_os_func(_os.sendfile)
    __all__.append("sendfile")
if hasattr(_os, "statvfs"):
    statvfs = _wrap_os_func(_os.statvfs)
    __all__.append("statvfs")
if hasattr(_os, "scandir"):
    scandir = _wrap_os_func(_os.scandir)
    __all__.append("scandir")
