"""Search connectors. Acquisition channels, never truth engines
(docs/collection/connector-strategy.md)."""

from __future__ import annotations

from .base import SearchConnector
from .brave import BraveConnector
from .fixture import FixtureConnector


def get_connector(name: str) -> SearchConnector:
    name = (name or "").lower()
    if name in ("fixture", "offline", ""):
        return FixtureConnector()
    if name == "brave":
        return BraveConnector()
    raise ValueError(f"unknown connector: {name!r} (have: fixture, brave)")


__all__ = ["SearchConnector", "BraveConnector", "FixtureConnector", "get_connector"]
