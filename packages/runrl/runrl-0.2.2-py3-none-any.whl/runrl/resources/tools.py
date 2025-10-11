from __future__ import annotations

from typing import Any, Dict, Optional

from ..models import Tool, PagedResponse
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class ToolsResource(SyncResource):
    def list(self, **params: Any) -> PagedResponse:
        response = self._get("/tools", params=params)
        data = extract_data(response.json())
        items = [Tool.model_validate(item) for item in data.get("items", data)]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    def create(self, **payload: Any) -> Tool:
        response = self._post("/tools", json=payload)
        return Tool.model_validate(extract_data(response.json()))

    def get(self, tool_id: int) -> Tool:
        response = self._get(f"/tools/{tool_id}")
        return Tool.model_validate(extract_data(response.json()))

    def update(self, tool_id: int, **payload: Any) -> Tool:
        response = self._put(f"/tools/{tool_id}", json=payload)
        return Tool.model_validate(extract_data(response.json()))

    def delete(self, tool_id: int) -> None:
        self._delete(f"/tools/{tool_id}")

    def test_connection(self, mcp_url: str) -> Dict[str, Any]:
        response = self._post("/tools/test-mcp", json={"mcp_url": mcp_url})
        return extract_data(response.json())


class AsyncToolsResource(AsyncResource):
    async def list(self, **params: Any) -> PagedResponse:
        response = await self._get("/tools", params=params)
        data = extract_data(response.json())
        items = [Tool.model_validate(item) for item in data.get("items", data)]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    async def create(self, **payload: Any) -> Tool:
        response = await self._post("/tools", json=payload)
        return Tool.model_validate(extract_data(response.json()))

    async def get(self, tool_id: int) -> Tool:
        response = await self._get(f"/tools/{tool_id}")
        return Tool.model_validate(extract_data(response.json()))

    async def update(self, tool_id: int, **payload: Any) -> Tool:
        response = await self._put(f"/tools/{tool_id}", json=payload)
        return Tool.model_validate(extract_data(response.json()))

    async def delete(self, tool_id: int) -> None:
        await self._delete(f"/tools/{tool_id}")

    async def test_connection(self, mcp_url: str) -> Dict[str, Any]:
        response = await self._post("/tools/test-mcp", json={"mcp_url": mcp_url})
        return extract_data(response.json())
