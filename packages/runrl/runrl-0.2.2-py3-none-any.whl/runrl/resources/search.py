from __future__ import annotations

from typing import Any

from ..models import SearchResults
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class SearchResource(SyncResource):
    def query(self, q: str) -> SearchResults:
        response = self._get("/search", params={"q": q})
        return SearchResults.model_validate(extract_data(response.json()))


class AsyncSearchResource(AsyncResource):
    async def query(self, q: str) -> SearchResults:
        response = await self._get("/search", params={"q": q})
        return SearchResults.model_validate(extract_data(response.json()))
