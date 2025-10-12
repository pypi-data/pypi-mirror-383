from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Generic,
    TypeVar,
)

from pydantic import BaseModel

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
)
from ab_core.impersonation.schema.intercept_event import InterceptEvent

T_CONTEXT = TypeVar("T_CONTEXT")
T_CONTEXT_ASYNC = TypeVar("T_CONTEXT_ASYNC")


class ImpersonatorBase(BaseModel, Generic[T_CONTEXT, T_CONTEXT_ASYNC], ABC):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    # 1) init_context (sync)
    @contextmanager
    @abstractmethod
    def init_context(
        self,
        url: str,
    ) -> Generator[T_CONTEXT, None, None]: ...

    # 2) init_context_async (async)
    @asynccontextmanager
    @abstractmethod
    async def init_context_async(
        self,
        url: str,
    ) -> AsyncGenerator[T_CONTEXT_ASYNC, None]: ...

    # 3) init_interaction (sync)
    @abstractmethod
    def init_interaction(
        self,
        context: T_CONTEXT,
    ) -> ImpersonationExchangeInteract | None: ...

    # 4) init_interaction_async (async)
    @abstractmethod
    async def init_interaction_async(
        self,
        context: T_CONTEXT_ASYNC,
    ) -> ImpersonationExchangeInteract | None: ...

    # 5) make_request (sync)
    @abstractmethod
    def make_request(
        self,
        context: T_CONTEXT,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]: ...

    # 6) make_request_async (async)
    @abstractmethod
    async def make_request_async(
        self,
        context: T_CONTEXT_ASYNC,
        request: ImpersonationExchangeRequest,
    ) -> AsyncGenerator[ImpersonationExchangeResponse, None]: ...

    # 7) intercept_response (sync)
    @contextmanager
    @abstractmethod
    def intercept(
        self,
        context: T_CONTEXT,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchangeResponse], bool] | None = None,
        timeout: int | None = None,
    ) -> Generator[ImpersonationExchangeResponse, None, None]: ...

    # 8) intercept_async (async)
    @asynccontextmanager
    @abstractmethod
    async def intercept_async(
        self,
        context: T_CONTEXT_ASYNC,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchangeResponse], bool] | None = None,
        timeout: int | None = None,
    ) -> AsyncGenerator[ImpersonationExchangeResponse, None]: ...
