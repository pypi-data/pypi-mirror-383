from __future__ import annotations

from typing import Any, Dict

from ..http import SyncSession, AsyncSession


class SyncResource:
    def __init__(self, session: SyncSession):
        self._session = session

    def _get(self, path: str, **kwargs: Any):
        return self._session.request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any):
        return self._session.request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs: Any):
        return self._session.request("PUT", path, **kwargs)

    def _delete(self, path: str, **kwargs: Any):
        return self._session.request("DELETE", path, **kwargs)


class AsyncResource:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get(self, path: str, **kwargs: Any):
        return await self._session.request("GET", path, **kwargs)

    async def _post(self, path: str, **kwargs: Any):
        return await self._session.request("POST", path, **kwargs)

    async def _put(self, path: str, **kwargs: Any):
        return await self._session.request("PUT", path, **kwargs)

    async def _delete(self, path: str, **kwargs: Any):
        return await self._session.request("DELETE", path, **kwargs)
