from __future__ import annotations

from io import BufferedReader
from pathlib import Path
from typing import IO, Any, Dict, List, Optional

from ..futures import FutureState, RunRLPollingFuture
from ..models import File, PagedResponse
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class FilesResource(SyncResource):
    def list(
        self,
        *,
        type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
    ) -> PagedResponse:
        params = {
            "page": page,
            "per_page": per_page,
        }
        if type:
            params["type"] = type
        if search:
            params["search"] = search
        if sort:
            params["sort"] = sort
        if direction:
            params["direction"] = direction

        response = self._get("/files", params=params)
        data = extract_data(response.json())
        items = [File.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    def retrieve(self, file_id: str) -> File:
        response = self._get(f"/files/{file_id}")
        data = extract_data(response.json())
        return File.model_validate(data)

    def upload_path(self, path: str, *, file_type: str, name: Optional[str] = None) -> File:
        file_path = Path(path)
        files = {"file": (file_path.name, file_path.read_bytes())}
        data = {
            "type": file_type,
        }
        if name:
            data["name"] = name

        response = self._post("/files", files=files, data=data)
        return File.model_validate(extract_data(response.json()))

    def create_from_content(
        self,
        *,
        name: str,
        content: str,
        file_type: str,
        original_filename: Optional[str] = None,
    ) -> File:
        payload = {
            "name": name,
            "content": content,
            "type": file_type,
        }
        if original_filename:
            payload["original_filename"] = original_filename

        response = self._post("/files", json=payload)
        return File.model_validate(extract_data(response.json()))

    def content(self, file_id: str) -> str:
        response = self._get(f"/files/{file_id}/content")
        data = extract_data(response.json())
        return data["content"]

    def preview(self, file_id: str, *, lines: int = 20) -> Any:
        response = self._get(f"/files/{file_id}/preview", params={"lines": lines})
        return extract_data(response.json())

    def delete(self, file_id: str, *, force: bool = False) -> None:
        params = {"force": str(force).lower()} if force else None
        self._delete(f"/files/{file_id}", params=params)


class AsyncFilesResource(AsyncResource):
    async def list(self, **kwargs: Any) -> PagedResponse:
        response = await self._get("/files", params=kwargs)
        data = extract_data(response.json())
        items = [File.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    async def retrieve(self, file_id: str) -> File:
        response = await self._get(f"/files/{file_id}")
        return File.model_validate(extract_data(response.json()))

    async def upload_path(self, path: str, *, file_type: str, name: Optional[str] = None) -> File:
        file_path = Path(path)
        files = {"file": (file_path.name, file_path.read_bytes())}
        data = {"type": file_type}
        if name:
            data["name"] = name
        response = await self._post("/files", files=files, data=data)
        return File.model_validate(extract_data(response.json()))

    async def create_from_content(
        self,
        *,
        name: str,
        content: str,
        file_type: str,
        original_filename: Optional[str] = None,
    ) -> File:
        payload = {
            "name": name,
            "content": content,
            "type": file_type,
        }
        if original_filename:
            payload["original_filename"] = original_filename
        response = await self._post("/files", json=payload)
        return File.model_validate(extract_data(response.json()))

    async def content(self, file_id: str) -> str:
        response = await self._get(f"/files/{file_id}/content")
        data = extract_data(response.json())
        return data["content"]

    async def preview(self, file_id: str, *, lines: int = 20) -> Any:
        response = await self._get(f"/files/{file_id}/preview", params={"lines": lines})
        return extract_data(response.json())

    async def delete(self, file_id: str, *, force: bool = False) -> None:
        params = {"force": str(force).lower()} if force else None
        await self._delete(f"/files/{file_id}", params=params)
