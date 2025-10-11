from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..config import DEFAULT_POLL_INTERVAL, DEFAULT_MAX_POLL_TIMEOUT
from ..futures import FutureState, RunRLPollingFuture, AsyncRunRLPollingFuture
from ..models import Deployment, PagedResponse
from ..utils import extract_data
from .base import AsyncResource, SyncResource

TERMINAL = {"active", "failed", "deleted"}
SUCCESS = {"active"}


class DeploymentsResource(SyncResource):
    def __init__(self, session, poll_interval: float = DEFAULT_POLL_INTERVAL, max_timeout: float = DEFAULT_MAX_POLL_TIMEOUT):
        super().__init__(session)
        self._poll_interval = poll_interval
        self._max_timeout = max_timeout

    def list(self, **params: Any) -> PagedResponse:
        response = self._get("/deployments", params=params)
        data = extract_data(response.json())
        items = [Deployment.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    def get(self, deployment_id: int) -> Deployment:
        response = self._get(f"/deployments/{deployment_id}")
        return Deployment.model_validate(extract_data(response.json()))

    def check(self, run_id: int) -> Dict[str, Any]:
        response = self._post("/deployments/check", json={"run_id": run_id})
        return extract_data(response.json())

    def create(self, run_id: int, *, poll_interval: Optional[float] = None, max_timeout: Optional[float] = None) -> RunRLPollingFuture[Deployment]:
        response = self._post("/deployments", json={"run_id": run_id})
        deployment = Deployment.model_validate(extract_data(response.json()))

        def poller() -> Deployment:
            return self.get(deployment.id)

        state = FutureState[
            Deployment
        ](
            initial=deployment,
            poller=poller,
            is_terminal=lambda d: d.status in TERMINAL,
            is_success=lambda d: d.status in SUCCESS,
            on_cancel=lambda: self.delete(deployment.id),
            poll_interval=poll_interval or self._poll_interval,
            max_timeout=max_timeout or self._max_timeout,
        )
        return RunRLPollingFuture(state)

    def delete(self, deployment_id: int) -> None:
        self._delete(f"/deployments/{deployment_id}")


class AsyncDeploymentsResource(AsyncResource):
    def __init__(self, session, poll_interval: float = DEFAULT_POLL_INTERVAL, max_timeout: float = DEFAULT_MAX_POLL_TIMEOUT):
        super().__init__(session)
        self._poll_interval = poll_interval
        self._max_timeout = max_timeout

    async def list(self, **params: Any) -> PagedResponse:
        response = await self._get("/deployments", params=params)
        data = extract_data(response.json())
        items = [Deployment.model_validate(item) for item in data["items"]]
        return PagedResponse(items=items, pagination=data.get("pagination", {}))

    async def get(self, deployment_id: int) -> Deployment:
        response = await self._get(f"/deployments/{deployment_id}")
        return Deployment.model_validate(extract_data(response.json()))

    async def check(self, run_id: int) -> Dict[str, Any]:
        response = await self._post("/deployments/check", json={"run_id": run_id})
        return extract_data(response.json())

    async def create(
        self, run_id: int, *, poll_interval: Optional[float] = None, max_timeout: Optional[float] = None
    ) -> AsyncRunRLPollingFuture[Deployment]:
        response = await self._post("/deployments", json={"run_id": run_id})
        deployment = Deployment.model_validate(extract_data(response.json()))

        async def poller() -> Deployment:
            return await self.get(deployment.id)

        async def on_cancel() -> None:
            await self.delete(deployment.id)

        state = FutureState[
            Deployment
        ](
            initial=deployment,
            poller=poller,
            is_terminal=lambda d: d.status in TERMINAL,
            is_success=lambda d: d.status in SUCCESS,
            on_cancel=on_cancel,
            poll_interval=poll_interval or self._poll_interval,
            max_timeout=max_timeout or self._max_timeout,
        )
        return AsyncRunRLPollingFuture(state)

    async def delete(self, deployment_id: int) -> None:
        await self._delete(f"/deployments/{deployment_id}")
