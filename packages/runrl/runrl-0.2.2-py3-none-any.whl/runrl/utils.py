from __future__ import annotations

from typing import Any, Dict


def extract_data(payload: Dict[str, Any]) -> Any:
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def success(payload: Dict[str, Any]) -> bool:
    return bool(payload.get("success", True))


__all__ = ["extract_data", "success"]
