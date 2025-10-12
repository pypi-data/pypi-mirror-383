import urllib
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
from pydantic import AnyUrl, BaseModel, Field

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


class CDPGUIService(BaseModel):
    """A minimal client for Browserless's session API."""

    base_url: AnyUrl  # e.g. "https://browserless-gui.matthewcoulter.dev"

    def with_ws(self, ws: str) -> str:
        """Applies a ws url to the gui, ensuring the client can see that particular browser session"""
        encoded_ws = urllib.parse.quote(ws, safe="")
        return f"{self.base_url}?ws={encoded_ws}"


class PlaywrightCDPImpersonator(PlaywrightImpersonatorBase):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    tool: Literal[ImpersonatorTool.PLAYWRIGHT_CDP] = ImpersonatorTool.PLAYWRIGHT_CDP

    cdp_endpoint: str = Field(
        ...,
        description='CDP endpoint URL, e.g. "wss://your-browserless/chromium?token=..."',
    )
    cdp_headers: dict | None = Field(default=None)
    cdp_timeout: float | None = Field(default=None)
    cdp_gui_service: CDPGUIService | None = None

    @contextmanager
    @override
    def init_context(
        self,
        url: str,
    ) -> Generator[PlaywrightContext, None, None]:
        # Note: no more p.chromium.launch(...)
        with sync_playwright() as p:
            # Connect to the remote Chrome running at localhost:9222
            browser = p.chromium.connect_over_cdp(
                self.cdp_endpoint,
                timeout=self.cdp_timeout,
                headers=self.cdp_headers,
            )
            # Create a new isolated context (cookies, cache, etc.)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state("networkidle")
            try:
                yield PlaywrightContext(
                    browser=browser,
                    context=context,
                    page=page,
                )
            finally:
                # This will disconnect Playwright, not shut down the container
                browser.close()

    @asynccontextmanager
    @override
    async def init_context_async(
        self,
        url: str,
    ) -> AsyncGenerator[PlaywrightContextAsync, None]:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(
                self.cdp_endpoint,
                timeout=self.cdp_timeout,
                headers=self.cdp_headers,
            )
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
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
