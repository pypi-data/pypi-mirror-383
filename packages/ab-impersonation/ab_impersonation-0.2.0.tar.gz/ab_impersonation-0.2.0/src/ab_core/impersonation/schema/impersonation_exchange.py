from abc import ABC
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator


class ImpersonationExchangeType(StrEnum):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    INTERACT = "INTERACT"


class ImpersonationExchangeBase(BaseModel, ABC): ...


class ImpersonationExchangeInteract(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.INTERACT] = ImpersonationExchangeType.INTERACT

    ws_url: str
    gui_url: str | None


class ImpersonationExchangeRequest(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.REQUEST] = ImpersonationExchangeType.REQUEST

    url: str
    method: str
    headers: dict[str, str]
    body: bytes | None = None


class ImpersonationExchangeResponse(ImpersonationExchangeBase):
    event: Literal[ImpersonationExchangeType.RESPONSE] = ImpersonationExchangeType.RESPONSE

    request: ImpersonationExchangeRequest

    url: str
    ok: bool
    status: int
    status_text: str
    headers: dict[str, str]
    body: bytes | None = None


ImpersonationExchange = Annotated[
    tuple[
        ImpersonationExchangeRequest,
        ImpersonationExchangeResponse,
    ],
    Discriminator("event"),
]
