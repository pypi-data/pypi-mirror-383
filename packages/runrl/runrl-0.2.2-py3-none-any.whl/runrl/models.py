from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class File(BaseModel):
    id: str = Field(alias="id")
    name: str
    original_filename: Optional[str] = None
    type: str
    file_size: Optional[int] = None
    file_size_human: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    download_url: Optional[str] = None
    content_url: Optional[str] = None
    preview_url: Optional[str] = None


class Run(BaseModel):
    id: int
    status: str
    type: str
    model: str
    parameters: Dict[str, Any]
    uses_tools: bool
    progress: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    wandb_url: Optional[str] = Field(default=None, alias="wandb_url")
    hf_name: Optional[str] = None
    prompt_file: Optional[Dict[str, Any]] = None
    reward_file: Optional[Dict[str, Any]] = None
    sft_file: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None


class Deployment(BaseModel):
    id: int
    run_id: int
    base_model: str
    api_url: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    run: Optional[Dict[str, Any]] = None


class Tool(BaseModel):
    id: int
    name: str
    description: Optional[str]
    mcp_url: str
    owner_user_id: int
    is_public: bool
    verified: bool
    usage_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SharedConfiguration(BaseModel):
    uuid: str
    name: str
    description: Optional[str]
    visibility: str
    configuration: Dict[str, Any]
    shareable_url: Optional[str]
    stats: Optional[Dict[str, Any]]
    creator: Optional[Dict[str, Any]]
    is_owner: Optional[bool]
    liked: Optional[bool]
    files: Optional[Dict[str, Any]]


class ValidationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SearchResults(BaseModel):
    runs: List[Dict[str, Any]] = []
    tools: List[Dict[str, Any]] = []
    files: List[Dict[str, Any]] = []


class ApiKey(BaseModel):
    id: int
    name: str
    scopes: List[str]
    masked_key: Optional[str] = None
    active: bool
    requests_per_hour: int
    remaining_requests: Optional[int] = None
    total_requests: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ApiKeyToken(BaseModel):
    api_key: ApiKey
    token: str
    warning: Optional[str]


class PagedResponse(BaseModel):
    items: List[Any]
    pagination: Dict[str, Any]

    def iter_pages(self) -> List[List[Any]]:
        return [self.items]


__all__ = [
    "File",
    "Run",
    "Deployment",
    "Tool",
    "SharedConfiguration",
    "ValidationResponse",
    "SearchResults",
    "ApiKey",
    "ApiKeyToken",
    "PagedResponse",
]
