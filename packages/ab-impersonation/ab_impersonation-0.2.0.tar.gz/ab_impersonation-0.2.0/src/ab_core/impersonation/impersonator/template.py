from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import (
    Literal,
    override,
)

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
    ImpersonationExchangeRequest,
    ImpersonationExchangeResponse,
)
from ab_core.impersonation.schema.impersonation_tool import (
    ImpersonatorTool,
)
from ab_core.impersonation.schema.intercept_event import InterceptEvent

from .base import ImpersonatorBase


class TemplateContext: ...


class TemplateContextAsync: ...


class TemplateImpersonator(ImpersonatorBase[TemplateContext, TemplateContextAsync]):
    """Automate browser login to capture auth code via OIDC with PKCE."""

    tool: Literal[ImpersonatorTool.TEMPLATE] = ImpersonatorTool.TEMPLATE

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[TemplateContext, None, None]:
        raise NotImplementedError()

    @asynccontextmanager
    @override
    async def init_context_async(
        self,
        url: str,
    ) -> AsyncGenerator[TemplateContext, None]:
        raise NotImplementedError()

    @override
    def init_interaction(
        self,
        context: TemplateContext,
    ) -> ImpersonationExchangeInteract | None:
        raise NotImplementedError()

    @override
    async def init_interaction_async(
        self,
        context: TemplateContext,
    ) -> ImpersonationExchangeInteract | None:
        raise NotImplementedError()

    @contextmanager
    @override
    def make_request(
        self,
        context: TemplateContext,
        request: ImpersonationExchangeRequest,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        raise NotImplementedError()

    @override
    async def make_request_async(
        self,
        context: TemplateContext,
        request: ImpersonationExchangeRequest,
    ) -> AsyncGenerator[ImpersonationExchangeResponse, None]:
        raise NotImplementedError()

    @contextmanager
    @override
    def intercept(
        self,
        context: TemplateContext,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchangeResponse], bool] | None = None,
        timeout: int | None = None,
    ) -> Generator[ImpersonationExchangeResponse, None, None]:
        raise NotImplementedError()

    @asynccontextmanager
    @override
    async def intercept_async(
        self,
        context: TemplateContext,
        event: InterceptEvent = "response",
        cond: Callable[[ImpersonationExchangeResponse], bool] | None = None,
        timeout: int | None = None,
    ) -> AsyncGenerator[ImpersonationExchangeResponse, None]:
        raise NotImplementedError()
