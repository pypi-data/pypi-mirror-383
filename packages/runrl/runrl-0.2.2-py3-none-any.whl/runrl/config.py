from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional


DEFAULT_BASE_URL = "https://runrl.com/api/v1"
DEFAULT_POLL_INTERVAL = 5.0
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_POLL_TIMEOUT = 60 * 60  # 1 hour


@dataclass
class ClientConfig:
    """Runtime configuration for the RunRL client."""

    api_key: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    poll_interval: float = DEFAULT_POLL_INTERVAL
    max_poll_timeout: float = DEFAULT_MAX_POLL_TIMEOUT
    user_agent: str = "runrl-python/0.2.0"

    @classmethod
    def from_env(cls, **overrides) -> "ClientConfig":
        api_key = overrides.get("api_key") or os.getenv("RUNRL_API_KEY")
        base_url = overrides.get("base_url") or os.getenv("RUNRL_BASE_URL", DEFAULT_BASE_URL)
        timeout = float(overrides.get("timeout") or os.getenv("RUNRL_TIMEOUT", DEFAULT_TIMEOUT))
        poll_interval = float(
            overrides.get("poll_interval") or os.getenv("RUNRL_POLL_INTERVAL", DEFAULT_POLL_INTERVAL)
        )
        max_poll_timeout = float(
            overrides.get("max_poll_timeout")
            or os.getenv("RUNRL_MAX_POLL_TIMEOUT", DEFAULT_MAX_POLL_TIMEOUT)
        )

        return cls(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            poll_interval=poll_interval,
            max_poll_timeout=max_poll_timeout,
            user_agent=overrides.get("user_agent", os.getenv("RUNRL_USER_AGENT", "runrl-python/0.2.0")),
        )


__all__ = ["ClientConfig", "DEFAULT_BASE_URL"]
