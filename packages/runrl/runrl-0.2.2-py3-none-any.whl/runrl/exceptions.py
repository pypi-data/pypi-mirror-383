from __future__ import annotations

from typing import Optional


class RunRLException(RuntimeError):
    """Base exception for SDK errors."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class AuthenticationError(RunRLException):
    pass


class AuthorizationError(RunRLException):
    pass


class NotFoundError(RunRLException):
    pass


class ValidationError(RunRLException):
    pass


class RateLimitError(RunRLException):
    pass


class ServerError(RunRLException):
    pass


class RunFailedError(RunRLException):
    """Raised when a run completes in a non-success state."""

    def __init__(self, message: str, run: dict):
        super().__init__(message, payload={"run": run})
        self.run = run


class TimeoutError(RunRLException):
    pass
