from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    RunRLException,
    ServerError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _raise_for_status(response: httpx.Response) -> None:
    if 200 <= response.status_code < 300:
        return

    payload: Dict[str, Any]
    try:
        payload = response.json()
    except Exception:  # pragma: no cover - fallback if body is not JSON
        payload = {"message": response.text}

    message = payload.get("message") or payload.get("error") or response.text

    if response.status_code == 401:
        raise AuthenticationError(message, status_code=response.status_code, payload=payload)
    if response.status_code == 403:
        raise AuthorizationError(message, status_code=response.status_code, payload=payload)
    if response.status_code == 404:
        raise NotFoundError(message, status_code=response.status_code, payload=payload)
    if response.status_code == 422:
        raise ValidationError(message, status_code=response.status_code, payload=payload)
    if response.status_code == 429:
        raise RateLimitError(message, status_code=response.status_code, payload=payload)
    if 500 <= response.status_code < 600:
        raise ServerError(message, status_code=response.status_code, payload=payload)

    raise RunRLException(message, status_code=response.status_code, payload=payload)


def _headers(api_key: str, user_agent: str) -> Dict[str, str]:
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


class SyncSession:
    def __init__(self, base_url: str, api_key: str, timeout: float, user_agent: str):
        self._client = httpx.Client(base_url=base_url, timeout=timeout, headers=_headers(api_key, user_agent))

    def close(self) -> None:
        self._client.close()

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempts = 5
        backoff = 1.0
        for attempt in range(1, attempts + 1):
            try:
                logger.debug("HTTP %s %s", method, url)
                response = self._client.request(method, url, **kwargs)
                _raise_for_status(response)
                return response
            except (httpx.RequestError, RateLimitError, ServerError) as exc:
                if attempt == attempts:
                    raise
                sleep_for = backoff + random.uniform(0, 0.5)
                time.sleep(sleep_for)
                backoff = min(backoff * 2, 10)
                continue


class AsyncSession:
    def __init__(self, base_url: str, api_key: str, timeout: float, user_agent: str):
        self._client = httpx.AsyncClient(
            base_url=base_url, timeout=timeout, headers=_headers(api_key, user_agent)
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        logger.debug("HTTP %s %s", method, url)
        attempts = 5
        backoff = 1.0
        for attempt in range(1, attempts + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                _raise_for_status(response)
                return response
            except (httpx.RequestError, RateLimitError, ServerError) as exc:
                if attempt == attempts:
                    raise RunRLException(str(exc)) from exc
                sleep_for = backoff + random.uniform(0, 0.5)
                import asyncio

                await asyncio.sleep(sleep_for)
                backoff = min(backoff * 2, 10)
                continue
