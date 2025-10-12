from typing import Literal

InterceptEvent = Literal[
    "close",
    "console",
    "crash",
    "dialog",
    "domcontentloaded",
    "download",
    "filechooser",
    "frameattached",
    "framedetached",
    "framenavigated",
    "load",
    "pageerror",
    "popup",
    "request",
    "requestfailed",
    "requestfinished",
    "response",
    "websocket",
    "worker",
]
