from __future__ import annotations

import os

from dotenv import load_dotenv
import sentry_sdk

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
