from __future__ import annotations

from typing import Any, Dict

from ..models import ValidationResponse
from ..utils import extract_data
from .base import AsyncResource, SyncResource


class ValidationResource(SyncResource):
    def reward_function(self, *, code: str, mode: str = "function", prompt_file_id: str | None = None) -> ValidationResponse:
        payload: Dict[str, Any] = {"functionCode": code, "mode": mode}
        if prompt_file_id:
            payload["prompt_file_id"] = prompt_file_id
        response = self._post("/validate/reward-function", json=payload)
        return ValidationResponse.model_validate(extract_data(response.json()))

    def prompt_file(self, prompt_file_id: str) -> ValidationResponse:
        response = self._post("/validate/prompt-file", json={"prompt_file_id": prompt_file_id})
        return ValidationResponse.model_validate(extract_data(response.json()))

    def sft_file(self, sft_file_id: str) -> ValidationResponse:
        response = self._post("/validate/sft-file", json={"sft_file_id": sft_file_id})
        return ValidationResponse.model_validate(extract_data(response.json()))


class AsyncValidationResource(AsyncResource):
    async def reward_function(self, *, code: str, mode: str = "function", prompt_file_id: str | None = None) -> ValidationResponse:
        payload: Dict[str, Any] = {"functionCode": code, "mode": mode}
        if prompt_file_id:
            payload["prompt_file_id"] = prompt_file_id
        response = await self._post("/validate/reward-function", json=payload)
        return ValidationResponse.model_validate(extract_data(response.json()))

    async def prompt_file(self, prompt_file_id: str) -> ValidationResponse:
        response = await self._post("/validate/prompt-file", json={"prompt_file_id": prompt_file_id})
        return ValidationResponse.model_validate(extract_data(response.json()))

    async def sft_file(self, sft_file_id: str) -> ValidationResponse:
        response = await self._post("/validate/sft-file", json={"sft_file_id": sft_file_id})
        return ValidationResponse.model_validate(extract_data(response.json()))
