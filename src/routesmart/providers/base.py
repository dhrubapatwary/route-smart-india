"""Typed asynchronous interface implemented by every option provider."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from routesmart.contracts import TravelMode, TravelOption
from routesmart.providers.query import TravelQuery


class OptionProvider(Protocol):
    """Source of ``TravelOption`` values for one travel mode.

    Providers map their data into the shared contract and return it unchanged.
    They report failure by raising; the collector turns exceptions and timeouts
    into per-provider outcomes, so one failing provider never hides another's
    results.
    """

    @property
    def name(self) -> str:
        """Stable lower-case identifier used in outcomes and logs."""
        ...

    @property
    def mode(self) -> TravelMode:
        """The single travel mode this provider returns."""
        ...

    async def fetch_options(self, query: TravelQuery) -> Sequence[TravelOption]:
        """Return the options for ``query``; an empty sequence means none were found."""
        ...
