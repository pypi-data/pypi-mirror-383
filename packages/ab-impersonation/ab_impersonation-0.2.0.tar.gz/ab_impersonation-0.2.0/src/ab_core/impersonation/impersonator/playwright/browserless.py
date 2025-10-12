from typing import Literal, override
from urllib.parse import urljoin, urlparse

import httpx
import requests
from pydantic import AnyUrl, BaseModel, computed_field

from ab_core.impersonation.schema.impersonation_exchange import (
    ImpersonationExchangeInteract,
)
from ab_core.impersonation.schema.impersonation_tool import (
    ImpersonatorTool,
)

from .base import PlaywrightContext, PlaywrightContextAsync
from .cdp import PlaywrightCDPImpersonator


class BrowserlessService(BaseModel):
    """A minimal client for Browserless's session API."""

    base_url: AnyUrl  # e.g. "https://browserless.matthewcoulter.dev"

    @computed_field
    @property
    def sessions_url(self) -> str:
        """The JSON endpoint to list active sessions."""
        return urljoin(str(self.base_url), "sessions")

    @computed_field
    @property
    def ws_url_prefix(self) -> str:
        """Compute the WebSocket host prefix (wss://hostname) from base_url."""
        base = urlparse(str(self.base_url))
        scheme = "wss" if base.scheme == "https" else "ws"
        return f"{scheme}://{base.netloc}"

    def fetch_sessions(self) -> list[dict]:
        """GET /sessions → list of all active pages/tabs."""
        resp = requests.get(self.sessions_url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    async def fetch_sessions_async(self) -> list[dict]:
        """GET /sessions → list of all active pages/tabs. (async)"""
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(self.sessions_url)
            resp.raise_for_status()
            return resp.json()

    def get_session_by_page_url(self, page_url: str) -> dict:
        """Find the raw session entry whose `url` exactly matches `page_url`.
        Raises ValueError if none found.
        """
        for s in self.fetch_sessions():
            if s.get("url") == page_url:
                return s
        raise ValueError(f"No Browserless session found for page URL: {page_url}")

    async def get_session_by_page_url_async(self, page_url: str) -> dict:
        """Find the raw session entry whose `url` exactly matches `page_url`. (async)
        Raises ValueError if none found.
        """
        for s in await self.fetch_sessions_async():
            if s.get("url") == page_url:
                return s
        raise ValueError(f"No Browserless session found for page URL: {page_url}")

    def get_page_ws_url(self, page_url: str, public: bool = False) -> str:
        """High-level helper: lookup the session for `page_url`
        and return its WebSocket URL.

        By default returns the internal URL; set public=True to rewrite it
        against base_url.
        """
        session = self.get_session_by_page_url(page_url)
        ws = session.get("webSocketDebuggerUrl")
        if not ws:
            raise ValueError(f"Session has no WebSocket URL: {session}")
        return self.as_public_ws_url(ws) if public else ws

    async def get_page_ws_url_async(self, page_url: str, public: bool = False) -> str:
        """Lookup the session for `page_url` and return its WebSocket URL. (async)
        By default returns the internal URL; set public=True to rewrite it
        against base_url using `as_public_ws_url`.
        """
        session = await self.get_session_by_page_url_async(page_url)
        ws = session.get("webSocketDebuggerUrl")
        if not ws:
            raise ValueError(f"Session has no WebSocket URL: {session}")
        return self.as_public_ws_url(ws) if public else ws

    def as_public_ws_url(self, internal_ws: str) -> str:
        """Rewrite an internal ws://0.0.0.0:port/... URL
        to your public hostname using ws_url_prefix and the same path/query.
        """
        p = urlparse(internal_ws)
        path_q = p.path + (f"?{p.query}" if p.query else "")
        return f"{self.ws_url_prefix}{path_q}"


class PlaywrightCDPBrowserlessImpersonator(PlaywrightCDPImpersonator):
    """Automate browser login to capture auth code via OIDC with PKCE. Good For CLIs, but"""

    tool: Literal[ImpersonatorTool.PLAYWRIGHT_CDP_BROWSERLESS] = ImpersonatorTool.PLAYWRIGHT_CDP_BROWSERLESS

    browserless_service: BrowserlessService

    @override
    def init_interaction(
        self,
        context: PlaywrightContext,
    ) -> ImpersonationExchangeInteract | None:
        # 1️⃣ Get the URL the user is currently at
        page_url = context.page.url

        # get the websocket url
        public_ws_url = self.browserless_service.get_page_ws_url(page_url, public=True)

        # get a gui url for that web socket if available
        public_gui_url = None
        if self.cdp_gui_service is not None:
            public_gui_url = self.cdp_gui_service.with_ws(public_ws_url)

        return ImpersonationExchangeInteract(
            ws_url=public_ws_url,
            gui_url=public_gui_url,
        )

    @override
    async def init_interaction_async(
        self,
        context: PlaywrightContextAsync,
    ) -> ImpersonationExchangeInteract | None:
        # current page URL
        page_url = context.page.url  # property access is sync

        # resolve public WebSocket for that page (async)
        public_ws_url = await self.browserless_service.get_page_ws_url_async(page_url, public=True)

        # optional GUI URL
        public_gui_url = None
        if self.cdp_gui_service is not None:
            public_gui_url = self.cdp_gui_service.with_ws(public_ws_url)

        return ImpersonationExchangeInteract(
            ws_url=public_ws_url,
            gui_url=public_gui_url,
        )
