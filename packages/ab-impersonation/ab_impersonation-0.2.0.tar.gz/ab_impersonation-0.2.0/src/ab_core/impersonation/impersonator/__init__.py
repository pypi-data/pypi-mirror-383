from typing import Annotated, Union

from pydantic import Discriminator

from .playwright.browserless import (
    PlaywrightCDPBrowserlessImpersonator,
)
from .playwright.cdp import PlaywrightCDPImpersonator
from .playwright.standard import PlaywrightImpersonator
from .template import TemplateImpersonator

Impersonator = Annotated[
    PlaywrightImpersonator | PlaywrightCDPImpersonator | PlaywrightCDPBrowserlessImpersonator | TemplateImpersonator,
    Discriminator("tool"),
]
