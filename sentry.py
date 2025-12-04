from __future__ import annotations

import os

from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk import Hub

load_dotenv() 

_DSN: str | None = os.getenv("SENTRY_DSN")
_ENV: str = os.getenv("SENTRY_ENV", "development")
_TRACES_RATE: float = float(
    os.getenv("SENTRY_TRACES", "0.0"))


def init_sentry() -> None:

    if not _DSN:
        return

    sentry_sdk.init(
        dsn=_DSN,
        environment=_ENV,
        send_default_pii=True,          # envoie IP, User‑Agent, etc.
        traces_sample_rate=_TRACES_RATE,
        enable_tracing=_TRACES_RATE > 0.0,
    )


def _is_enabled() -> bool:
    hub = Hub.current
    client = getattr(hub, "client", None)
    return bool(client)


def report_exception(exc: Exception) -> None:
    if not _is_enabled():
        return
    sentry_sdk.capture_exception(exc)

