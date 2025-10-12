from collections.abc import AsyncGenerator, Generator
from contextlib import (
    asynccontextmanager,  # (import ok to add)
    contextmanager,
)
from typing import (
    Literal,
    override,
)

from playwright.async_api import async_playwright  # (import ok to add)
from playwright.sync_api import sync_playwright

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
)
from ab_core.impersonation.schema.impersonation_tool import (
    ImpersonatorTool,
)

from .base import (
    PlaywrightContext,
    PlaywrightContextAsync,
    PlaywrightImpersonatorBase,
)


class PlaywrightImpersonator(PlaywrightImpersonatorBase):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    tool: Literal[ImpersonatorTool.PLAYWRIGHT] = ImpersonatorTool.PLAYWRIGHT
    browser_channel: str = "chrome"

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[PlaywrightContext, None, None]:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel=self.browser_channel,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            try:
                yield PlaywrightContext(
                    context=context,
                    page=page,
                )
            finally:
                browser.close()

    @asynccontextmanager
    @override
    async def init_context_async(
        self,
        url: str,
    ) -> AsyncGenerator[PlaywrightContextAsync, None]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel=self.browser_channel,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            try:
                yield PlaywrightContextAsync(
                    browser=browser,
                    context=context,
                    page=page,
                )
            finally:
                await browser.close()

    @override
    def init_interaction(
        self,
        context: PlaywrightContext,
    ) -> ImpersonationExchangeInteract | None:
        return None  # browser opens in client, no interaction preparation needed

    @override
    async def init_interaction_async(
        self,
        context: PlaywrightContextAsync,
    ) -> ImpersonationExchangeInteract | None:
        # No special prep needed; mirror sync behaviour
        return None
