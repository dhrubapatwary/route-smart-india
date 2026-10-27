"""Validated travel query consumed by option providers.

Travel-date semantics (DECISIONS.md P2-PROP-02, option A): both ``travel_date``
and the caller-supplied ``current_date`` must be timezone-aware. The current
instant is converted into ``travel_date``'s timezone, and the two *calendar
dates* are compared there. A travel date on that day or later is accepted; an
earlier one is rejected. Validation never reads the system clock.
"""

from __future__ import annotations

from datetime import date
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, model_validator

from routesmart.contracts.travel_option import PlaceName, Timestamp

SUPPORTED_ROUTES: Final[frozenset[tuple[str, str]]] = frozenset({("BLR", "MAA")})
"""Routes accepted in Task 003 (pilot route only, as city-level codes; P2-PROP-03)."""


class TravelQuery(BaseModel):
    """A request for travel options on one route and travel day."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", str_strip_whitespace=True, revalidate_instances="always"
    )

    origin: PlaceName
    destination: PlaceName
    travel_date: Timestamp
    current_date: Timestamp

    @model_validator(mode="after")
    def _check_query(self) -> Self:
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("origin and destination must differ")
        if (self.origin, self.destination) not in SUPPORTED_ROUTES:
            supported = ", ".join(f"{o} -> {d}" for o, d in sorted(SUPPORTED_ROUTES))
            raise ValueError(
                f"unsupported route {self.origin} -> {self.destination}; supported: {supported}"
            )
        if self.travel_day < self.current_day:
            raise ValueError(
                f"travel date {self.travel_day.isoformat()} is before the current date "
                f"{self.current_day.isoformat()} (compared in the travel date's timezone)"
            )
        return self

    @property
    def travel_day(self) -> date:
        """The travel day: ``travel_date``'s calendar date in its own timezone."""
        return self.travel_date.date()

    @property
    def current_day(self) -> date:
        """The supplied current instant's calendar date in ``travel_date``'s timezone."""
        return self.current_date.astimezone(self.travel_date.tzinfo).date()
