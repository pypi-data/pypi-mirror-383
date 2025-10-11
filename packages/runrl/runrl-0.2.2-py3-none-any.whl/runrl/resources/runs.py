from __future__ import annotations

import json
from typing import Any, Dict, Generator, Iterable, List, Optional

from ..config import DEFAULT_POLL_INTERVAL, DEFAULT_MAX_POLL_TIMEOUT
from ..exceptions import RunRLException
from ..futures import FutureState, RunRLPollingFuture, AsyncRunRLPollingFuture
from ..models import Run, PagedResponse
from ..utils import extract_data
from .base import AsyncResource, SyncResource

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELLED"}
SUCCESS_STATUSES = {"COMPLETED"}


class RunsResource(SyncResource):
    def __init__(self, session, poll_interval: float = DEFAULT_POLL_INTERVAL, max_timeout: float = DEFAULT_MAX_POLL_TIMEOUT):
        super().__init__(session)
        self._poll_interval = poll_interval
        self._max_timeout = max_timeout

    def list(self, **params: Any) -> PagedResponse:
        response = self._get("/runs", params=params)
        data = extract_data(response.json())
        items = [Run.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    def get(self, run_id: int) -> Run:
        response = self._get(f"/runs/{run_id}")
        return Run.model_validate(extract_data(response.json()))

    def history(self, run_id: int) -> List[Dict[str, Any]]:
        response = self._get(f"/runs/{run_id}/history")
        return extract_data(response.json())["history"]

    def logs(self, run_id: int, *, last_line: int = 0, limit: int = 100) -> Dict[str, Any]:
        response = self._get(
            f"/runs/{run_id}/logs",
            params={"last_line": last_line, "limit": limit},
        )
        return extract_data(response.json())

    def stream_logs(self, run_id: int) -> Generator[str, None, None]:
        response = self._get(f"/runs/{run_id}/stream-logs")
        for line in response.iter_lines():
            if line:
                yield line

    def metrics(self, run_id: int) -> Dict[str, Any]:
        response = self._get(f"/runs/{run_id}/metrics")
        return extract_data(response.json())

    def completions(self, run_id: int) -> Dict[str, Any]:
        response = self._get(f"/runs/{run_id}/completions")
        return extract_data(response.json())

    def cancel(self, run_id: int) -> None:
        self._post(f"/runs/{run_id}/cancel")

    def create(self, *, poll_interval: Optional[float] = None, max_timeout: Optional[float] = None, **payload: Any) -> RunRLPollingFuture[Run]:
        response = self._post("/runs", json=payload)
        run = Run.model_validate(extract_data(response.json()))

        def poller() -> Run:
            return self.get(run.id)

        state = FutureState[
            Run
        ](
            initial=run,
            poller=poller,
            is_terminal=lambda r: r.status in TERMINAL_STATUSES,
            is_success=lambda r: r.status in SUCCESS_STATUSES,
            on_cancel=lambda: self.cancel(run.id),
            poll_interval=poll_interval or self._poll_interval,
            max_timeout=max_timeout or self._max_timeout,
        )
        return RunRLPollingFuture(state)


class AsyncRunsResource(AsyncResource):
    def __init__(self, session, poll_interval: float = DEFAULT_POLL_INTERVAL, max_timeout: float = DEFAULT_MAX_POLL_TIMEOUT):
        super().__init__(session)
        self._poll_interval = poll_interval
        self._max_timeout = max_timeout

    async def list(self, **params: Any) -> PagedResponse:
        response = await self._get("/runs", params=params)
        data = extract_data(response.json())
        items = [Run.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    async def get(self, run_id: int) -> Run:
        response = await self._get(f"/runs/{run_id}")
        return Run.model_validate(extract_data(response.json()))

    async def history(self, run_id: int) -> List[Dict[str, Any]]:
        response = await self._get(f"/runs/{run_id}/history")
        return extract_data(response.json())["history"]

    async def logs(self, run_id: int, *, last_line: int = 0, limit: int = 100) -> Dict[str, Any]:
        response = await self._get(
            f"/runs/{run_id}/logs",
            params={"last_line": last_line, "limit": limit},
        )
        return extract_data(response.json())

    async def metrics(self, run_id: int) -> Dict[str, Any]:
        response = await self._get(f"/runs/{run_id}/metrics")
        return extract_data(response.json())

    async def completions(self, run_id: int) -> Dict[str, Any]:
        response = await self._get(f"/runs/{run_id}/completions")
        return extract_data(response.json())

    async def cancel(self, run_id: int) -> None:
        await self._post(f"/runs/{run_id}/cancel")

    async def create(
        self,
        *,
        poll_interval: Optional[float] = None,
        max_timeout: Optional[float] = None,
        **payload: Any,
    ) -> AsyncRunRLPollingFuture[Run]:
        response = await self._post("/runs", json=payload)
        run = Run.model_validate(extract_data(response.json()))

        async def poller() -> Run:
            return await self.get(run.id)

        async def on_cancel() -> None:
            await self.cancel(run.id)

        state = FutureState[
            Run
        ](
            initial=run,
            poller=poller,
            is_terminal=lambda r: r.status in TERMINAL_STATUSES,
            is_success=lambda r: r.status in SUCCESS_STATUSES,
            on_cancel=on_cancel,
            poll_interval=poll_interval or self._poll_interval,
            max_timeout=max_timeout or self._max_timeout,
        )
        return AsyncRunRLPollingFuture(state)
