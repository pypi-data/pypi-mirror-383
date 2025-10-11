from __future__ import annotations

from typing import Any

from ..models import ApiKey, ApiKeyToken
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class ApiKeysResource(SyncResource):
    def list(self) -> list[ApiKey]:
        response = self._get("/keys")
        data = extract_data(response.json())
        return [ApiKey.model_validate(item) for item in data]

    def create(self, **payload: Any) -> ApiKeyToken:
        response = self._post("/keys", json=payload)
        return ApiKeyToken.model_validate(extract_data(response.json()))

    def update(self, api_key_id: int, **payload: Any) -> ApiKey:
        response = self._put(f"/keys/{api_key_id}", json=payload)
        return ApiKey.model_validate(extract_data(response.json()))

    def usage(self, api_key_id: int) -> dict[str, Any]:
        response = self._get(f"/keys/{api_key_id}/usage")
        return extract_data(response.json())

    def delete(self, api_key_id: int) -> None:
        self._delete(f"/keys/{api_key_id}")


class AsyncApiKeysResource(AsyncResource):
    async def list(self) -> list[ApiKey]:
        response = await self._get("/keys")
        data = extract_data(response.json())
        return [ApiKey.model_validate(item) for item in data]

    async def create(self, **payload: Any) -> ApiKeyToken:
        response = await self._post("/keys", json=payload)
        return ApiKeyToken.model_validate(extract_data(response.json()))

    async def update(self, api_key_id: int, **payload: Any) -> ApiKey:
        response = await self._put(f"/keys/{api_key_id}", json=payload)
        return ApiKey.model_validate(extract_data(response.json()))

    async def usage(self, api_key_id: int) -> dict[str, Any]:
        response = await self._get(f"/keys/{api_key_id}/usage")
        return extract_data(response.json())

    async def delete(self, api_key_id: int) -> None:
        await self._delete(f"/keys/{api_key_id}")
