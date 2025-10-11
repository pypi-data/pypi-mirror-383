from __future__ import annotations

from typing import Any, Dict

from ..models import PagedResponse, SharedConfiguration
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class SharedConfigurationsResource(SyncResource):
    def list(self, **params: Any) -> PagedResponse:
        response = self._get("/shared-configurations", params=params)
        data = extract_data(response.json())
        items = [SharedConfiguration.model_validate(item) for item in data]
        return PagedResponse(items=items, pagination={})

    def browse(self, **params: Any) -> PagedResponse:
        response = self._get("/shared-configurations/browse", params=params)
        data = extract_data(response.json())
        items = [SharedConfiguration.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    def get(self, uuid: str) -> SharedConfiguration:
        response = self._get(f"/shared-configurations/{uuid}")
        return SharedConfiguration.model_validate(extract_data(response.json()))

    def data(self, uuid: str) -> Dict[str, Any]:
        response = self._get(f"/shared-configurations/{uuid}/data")
        return extract_data(response.json())

    def create(self, **payload: Any) -> SharedConfiguration:
        response = self._post("/shared-configurations", json=payload)
        return SharedConfiguration.model_validate(extract_data(response.json()))

    def copy(self, uuid: str) -> Dict[str, Any]:
        response = self._post(f"/shared-configurations/{uuid}/copy")
        return extract_data(response.json())

    def like(self, uuid: str) -> Dict[str, Any]:
        response = self._post(f"/shared-configurations/{uuid}/like")
        return extract_data(response.json())

    def update(self, uuid: str, **payload: Any) -> SharedConfiguration:
        response = self._put(f"/shared-configurations/{uuid}", json=payload)
        return SharedConfiguration.model_validate(extract_data(response.json()))

    def delete(self, uuid: str) -> None:
        self._delete(f"/shared-configurations/{uuid}")


class AsyncSharedConfigurationsResource(AsyncResource):
    async def list(self, **params: Any) -> PagedResponse:
        response = await self._get("/shared-configurations", params=params)
        data = extract_data(response.json())
        items = [SharedConfiguration.model_validate(item) for item in data]
        return PagedResponse(items=items, pagination={})

    async def browse(self, **params: Any) -> PagedResponse:
        response = await self._get("/shared-configurations/browse", params=params)
        data = extract_data(response.json())
        items = [SharedConfiguration.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    async def get(self, uuid: str) -> SharedConfiguration:
        response = await self._get(f"/shared-configurations/{uuid}")
        return SharedConfiguration.model_validate(extract_data(response.json()))

    async def data(self, uuid: str) -> Dict[str, Any]:
        response = await self._get(f"/shared-configurations/{uuid}/data")
        return extract_data(response.json())

    async def create(self, **payload: Any) -> SharedConfiguration:
        response = await self._post("/shared-configurations", json=payload)
        return SharedConfiguration.model_validate(extract_data(response.json()))

    async def copy(self, uuid: str) -> Dict[str, Any]:
        response = await self._post(f"/shared-configurations/{uuid}/copy")
        return extract_data(response.json())

    async def like(self, uuid: str) -> Dict[str, Any]:
        response = await self._post(f"/shared-configurations/{uuid}/like")
        return extract_data(response.json())

    async def update(self, uuid: str, **payload: Any) -> SharedConfiguration:
        response = await self._put(f"/shared-configurations/{uuid}", json=payload)
        return SharedConfiguration.model_validate(extract_data(response.json()))

    async def delete(self, uuid: str) -> None:
        await self._delete(f"/shared-configurations/{uuid}")
