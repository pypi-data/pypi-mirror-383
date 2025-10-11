from __future__ import annotations

import logging
from typing import Any, Optional

from .config import ClientConfig
from .exceptions import AuthenticationError
from .http import AsyncSession, SyncSession
from .resources import (
    ApiKeysResource,
    AsyncApiKeysResource,
    AsyncDeploymentsResource,
    AsyncFilesResource,
    AsyncRunsResource,
    AsyncSearchResource,
    AsyncSharedConfigurationsResource,
    AsyncToolsResource,
    AsyncValidationResource,
    DeploymentsResource,
    FilesResource,
    RunsResource,
    SearchResource,
    SharedConfigurationsResource,
    ToolsResource,
    ValidationResource,
)

logger = logging.getLogger(__name__)


class RunRLClient:
    """Synchronous RunRL client."""

    def __init__(self, **config: Any):
        self._config = ClientConfig.from_env(**config)
        if not self._config.api_key:
            raise AuthenticationError("An API key is required. Set RUNRL_API_KEY or pass api_key explicitly.")
        self._session = SyncSession(
            base_url=self._config.base_url,
            api_key=self._config.api_key,
            timeout=self._config.timeout,
            user_agent=self._config.user_agent,
        )
        self.files = FilesResource(self._session)
        self.runs = RunsResource(
            self._session,
            poll_interval=self._config.poll_interval,
            max_timeout=self._config.max_poll_timeout,
        )
        self.deployments = DeploymentsResource(
            self._session,
            poll_interval=self._config.poll_interval,
            max_timeout=self._config.max_poll_timeout,
        )
        self.tools = ToolsResource(self._session)
        self.shared_configurations = SharedConfigurationsResource(self._session)
        self.validation = ValidationResource(self._session)
        self.search = SearchResource(self._session)
        self.api_keys = ApiKeysResource(self._session)

    @property
    def config(self) -> ClientConfig:
        return self._config

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "RunRLClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class AsyncRunRLClient:
    """Asynchronous RunRL client."""

    def __init__(self, **config: Any):
        self._config = ClientConfig.from_env(**config)
        if not self._config.api_key:
            raise AuthenticationError("An API key is required. Set RUNRL_API_KEY or pass api_key explicitly.")
        self._session = AsyncSession(
            base_url=self._config.base_url,
            api_key=self._config.api_key,
            timeout=self._config.timeout,
            user_agent=self._config.user_agent,
        )
        self.files = AsyncFilesResource(self._session)
        self.runs = AsyncRunsResource(
            self._session,
            poll_interval=self._config.poll_interval,
            max_timeout=self._config.max_poll_timeout,
        )
        self.deployments = AsyncDeploymentsResource(
            self._session,
            poll_interval=self._config.poll_interval,
            max_timeout=self._config.max_poll_timeout,
        )
        self.tools = AsyncToolsResource(self._session)
        self.shared_configurations = AsyncSharedConfigurationsResource(self._session)
        self.validation = AsyncValidationResource(self._session)
        self.search = AsyncSearchResource(self._session)
        self.api_keys = AsyncApiKeysResource(self._session)

    @property
    def config(self) -> ClientConfig:
        return self._config

    async def aclose(self) -> None:
        await self._session.aclose()

    async def __aenter__(self) -> "AsyncRunRLClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
