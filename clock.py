"""Generation clock.

Record-keeping timestamps (meta.lastUpdated, Bundle.timestamp, and FHIR
recording instants) default to the current wall-clock time. When a generation
runs with a seed, those timestamps are frozen to a deterministic instant so the
whole output is byte-reproducible for that seed.

The frozen instant is anchored to the current date at midnight UTC, matching the
day-level determinism the generators already have through date.today(). Seeded
output is therefore reproducible within a given day.

This lives in its own module so both the generators and the mappers can use it
without either layer importing the other.
"""
from __future__ import annotations

import contextvars
from datetime import UTC, datetime

_frozen_now: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "synthfhir_frozen_now", default=None
)


def utcnow_str() -> str:
    """Return the record-keeping timestamp, honoring a frozen instant if set."""
    frozen = _frozen_now.get()
    if frozen is not None:
        return frozen
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_midnight_utc() -> str:
    """The current date at 00:00:00 UTC, formatted as a FHIR instant."""
    return datetime.now(UTC).strftime("%Y-%m-%dT00:00:00Z")


def freeze(value: str) -> object:
    """Freeze the generation clock to a fixed instant. Returns a reset token."""
    return _frozen_now.set(value)


def unfreeze(token: object) -> None:
    """Restore the previous clock state using a token from freeze()."""
    _frozen_now.reset(token)  # type: ignore[arg-type]
