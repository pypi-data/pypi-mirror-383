"""Base classes for aiofiles."""


class AiofilesContextManager:
    """Async context manager for file operations."""

    def __init__(self, coro):
        """Initialize with coroutine."""
        self._coro = coro
        self._obj = None

    async def __aenter__(self):
        """Async enter."""
        self._obj = await self._coro
        return self._obj

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit."""
        if self._obj is not None and hasattr(self._obj, "close"):
            await self._obj.close()
        return False

    def __await__(self):
        """Make awaitable."""
        return self._coro.__await__()
