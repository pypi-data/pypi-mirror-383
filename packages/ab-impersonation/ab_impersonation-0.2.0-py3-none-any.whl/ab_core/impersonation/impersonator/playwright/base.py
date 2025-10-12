import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import field
from typing import (
    Any,
    TypeVar,
    override,
)

from playwright.async_api import (
    Browser as AsyncBrowser,
)
from playwright.async_api import (
    BrowserContext as AsyncBrowserContext,
)
from playwright.async_api import (
    Page as AsyncPage,
)
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
)
from pydantic import BaseModel
from uuid_extensions import uuid7

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
    ImpersonationExchange,
)
from ab_core.impersonation.schema.intercept_event import InterceptEvent

from ..base import ImpersonatorBase

logger = logging.getLogger(__name__)


class PlaywrightContext(BaseModel):
    id: str = field(default_factory=lambda: str(uuid7()))

    browser: Browser
    context: BrowserContext
    page: Page

    class Config:
        arbitrary_types_allowed = True


class PlaywrightContextAsync(BaseModel):
    id: str = field(default_factory=lambda: str(uuid7()))
    browser: AsyncBrowser
    context: AsyncBrowserContext
    page: AsyncPage

    class Config:
        arbitrary_types_allowed = True


PLAYWRIGHT_CONTEXT_T = TypeVar("PLAYWRIGHT_CONTEXT_T", bound=PlaywrightContext)
PLAYWRIGHT_CONTEXT_ASYNC_T = TypeVar("PLAYWRIGHT_CONTEXT_ASYNC_T", bound=PlaywrightContextAsync)


class PlaywrightImpersonatorBase(ImpersonatorBase[PLAYWRIGHT_CONTEXT_T, PLAYWRIGHT_CONTEXT_ASYNC_T], ABC):
    """Impersonate client HTTP request via playwright."""

    @contextmanager
    @abstractmethod
    def init_context(
        self,
        url: str,
    ) -> Generator[PLAYWRIGHT_CONTEXT_T, None, None]: ...

    @asynccontextmanager
    @abstractmethod
    async def init_context_async(
        self,
        url: str,
    ) -> AsyncGenerator[PLAYWRIGHT_CONTEXT_ASYNC_T, None]: ...

    @abstractmethod
    def init_interaction(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
    ) -> ImpersonationExchangeInteract | None: ...

    @abstractmethod
    async def init_interaction_async(
        self,
        context: PLAYWRIGHT_CONTEXT_ASYNC_T,
    ) -> ImpersonationExchangeInteract | None: ...

    @override
    def make_request(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        api_request = context.context.request
        response = api_request.fetch(
            url=request.url,
            method=request.method,
            headers=request.headers,
            data=request.body,
        )
        yield self._cast_response(response)

    @override
    async def make_request_async(
        self,
        context: PlaywrightContextAsync,  # explicit to avoid circular types
        request: ImpersonationExchangeRequest,
    ) -> AsyncGenerator[ImpersonationExchangeResponse, None]:
        api_request = context.context.request
        resp = await api_request.fetch(
            url=request.url,
            method=request.method,
            headers=request.headers,
            data=request.body,
        )
        yield await self._cast_response_async(resp)

    @contextmanager
    @override
    def intercept(
        self,
        context: PLAYWRIGHT_CONTEXT_T,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchange], bool] | None = None,
        timeout: int | None = None,
    ) -> Generator[ImpersonationExchange, None, None]:
        playwright_event = context.context.wait_for_event(
            event,
            predicate=lambda e: cond(self._cast(event, e)),
            timeout=timeout,
        )
        yield self._cast(event, playwright_event)

    @asynccontextmanager
    async def intercept_async(
        self,
        context: PlaywrightContextAsync,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchange], bool] | None = None,
        timeout: int | None = None,
    ) -> AsyncGenerator[ImpersonationExchange, None]:
        # predicate must be sync
        playwright_event = await context.context.wait_for_event(
            event,
            predicate=lambda e: cond(self._cast(event, e)),
            timeout=timeout,
        )
        yield self._cast(event, playwright_event)

    def _cast(self, event: InterceptEvent, e: Any):
        if event == "request":
            return self._cast_request(e)
        if event == "response":
            return self._cast_response(e)
        raise NotImplementedError(f"{repr(self)} does not support event {event}")

    def _cast_request(self, request: Any) -> ImpersonationExchangeRequest:
        return ImpersonationExchangeRequest(
            url=str(request.url),
            headers=dict(request.headers),
            body=request.post_data_buffer,
            method=request.method,
        )

    def _cast_response(self, response: Any) -> ImpersonationExchangeResponse:
        return ImpersonationExchangeResponse(
            request=self._cast_request(response.request),
            url=str(response.url),
            headers=dict(response.headers),
            ok=response.ok,
            status=response.status,
            status_text=response.status_text,
        )
