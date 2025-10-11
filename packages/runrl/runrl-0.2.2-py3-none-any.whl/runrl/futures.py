from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Generic, Iterable, List, Optional, TypeVar

from .exceptions import RunFailedError, TimeoutError

T = TypeVar("T")


@dataclass
class FutureState(Generic[T]):
    initial: T
    poller: Callable[[], T]
    is_terminal: Callable[[T], bool]
    is_success: Callable[[T], bool]
    on_cancel: Optional[Callable[[], Any]] = None
    poll_interval: float = 5.0
    max_timeout: float = 60 * 60


class RunRLPollingFuture(Generic[T]):
    """Synchronously poll a resource until it reaches a terminal state."""

    def __init__(self, state: FutureState[T]):
        self._state = state
        self._done_event = threading.Event()
        self._result: Optional[T] = None
        self._exception: Optional[Exception] = None
        self._callbacks: List[Callable[["RunRLPollingFuture[T]"], None]] = []

    @property
    def initial(self) -> T:
        return self._state.initial

    def status(self) -> T:
        return self._state.poller()

    def cancel(self) -> None:
        if self._state.on_cancel:
            self._state.on_cancel()
        self._done(success=False, result=None, exception=TimeoutError("Operation cancelled."))

    def add_done_callback(self, fn: Callable[["RunRLPollingFuture[T]"], None]) -> None:
        if self._done_event.is_set():
            fn(self)
        else:
            self._callbacks.append(fn)

    def result(self, timeout: Optional[float] = None) -> T:
        if self._done_event.is_set():
            if self._exception:
                raise self._exception
            return self._result  # type: ignore

        deadline = time.time() + (timeout if timeout is not None else self._state.max_timeout)
        current = self._state.initial

        while True:
            if self._state.is_terminal(current):
                if self._state.is_success(current):
                    self._done(True, current, None)
                    return current
                error = RunFailedError("Operation finished unsuccessfully", run=current)  # type: ignore[arg-type]
                self._done(False, current, error)
                raise error

            if time.time() >= deadline:
                error = TimeoutError("Timed out waiting for completion")
                self._done(False, current, error)
                raise error

            time.sleep(self._state.poll_interval)
            current = self._state.poller()

    def _done(self, success: bool, result: Optional[T], exception: Optional[Exception]) -> None:
        self._result = result
        self._exception = exception
        self._done_event.set()
        for fn in self._callbacks:
            try:
                fn(self)
            except Exception:  # pragma: no cover
                pass


class AsyncRunRLPollingFuture(Generic[T]):
    """Asynchronous polling future."""

    def __init__(self, state: FutureState[T]):
        self._state = state
        self._done = False
        self._result: Optional[T] = None
        self._exception: Optional[Exception] = None
        self._callbacks: List[Callable[["AsyncRunRLPollingFuture[T]"], None]] = []

    @property
    def initial(self) -> T:
        return self._state.initial

    def add_done_callback(self, fn: Callable[["AsyncRunRLPollingFuture[T]"], None]) -> None:
        if self._done:
            fn(self)
        else:
            self._callbacks.append(fn)

    def __await__(self):  # type: ignore[override]
        return self.result().__await__()

    async def result(self, timeout: Optional[float] = None):
        import asyncio

        if self._done:
            if self._exception:
                raise self._exception
            return self._result

        deadline = asyncio.get_event_loop().time() + (
            timeout if timeout is not None else self._state.max_timeout
        )
        current = self._state.initial

        while True:
            if self._state.is_terminal(current):
                if self._state.is_success(current):
                    self._set_done(current, None)
                    return current
                error = RunFailedError("Operation finished unsuccessfully", run=current)  # type: ignore[arg-type]
                self._set_done(current, error)
                raise error

            now = asyncio.get_event_loop().time()
            if now >= deadline:
                error = TimeoutError("Timed out waiting for completion")
                self._set_done(current, error)
                raise error

            await asyncio.sleep(self._state.poll_interval)
            poller = self._state.poller
            value = poller()
            current = await value if isinstance(value, Awaitable) else value  # type: ignore[arg-type]

    async def status(self):
        poller = self._state.poller
        value = poller()
        return await value if isinstance(value, Awaitable) else value

    async def cancel(self) -> None:
        if self._state.on_cancel:
            maybe = self._state.on_cancel()
            if isinstance(maybe, Awaitable):
                await maybe
        self._set_done(None, TimeoutError("Operation cancelled."))

    def _set_done(self, result: Optional[T], exception: Optional[Exception]) -> None:
        self._done = True
        self._result = result
        self._exception = exception
        for fn in self._callbacks:
            try:
                fn(self)
            except Exception:  # pragma: no cover
                pass


def wait_all(futures: Iterable[RunRLPollingFuture[T]]) -> List[T]:
    return [future.result() for future in futures]


__all__ = [
    "RunRLPollingFuture",
    "AsyncRunRLPollingFuture",
    "FutureState",
    "wait_all",
]
