"""Base classes for aiofiles."""


class AiofilesContextManager:
    def __init__(self, coro):
        self._coro = coro
        self._obj = None

    async def __aenter__(self):
        self._obj = await self._coro
        return self._obj

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._obj is not None and hasattr(self._obj, "close"):
            await self._obj.close()
        return False

    def __await__(self):
        return self._coro.__await__()
