"""Deterministic sample-data providers for the five travel modes (Task 003).

Everything here is **sample data** (DECISIONS.md D-PROP-01..04): operator names
are fictional, and prices and times are illustrative. Nothing implies live
availability or bookability. Every option carries ``DataOrigin.SAMPLE``
provenance with source ``"sample"`` and the fixed ``SAMPLE_RETRIEVED_AT`` of the
fixture version, never the system clock, so identical queries produce identical
options.

All options use the query's city-level codes as origin and destination
(P2-PROP-03). Scheduled times are placed on the query's travel day in the UTC
offset of ``travel_date`` (P2-PROP-02); arrivals may fall on the next day.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta, timezone
from decimal import Decimal
from types import MappingProxyType
from typing import Final

from routesmart.contracts import (
    AvailabilityStatus,
    DataOrigin,
    Money,
    Provenance,
    TravelMode,
    TravelOption,
    UnavailableReason,
)
from routesmart.contracts.travel_option import OptionalField
from routesmart.providers.query import TravelQuery

SAMPLE_FIXTURE_VERSION: Final = "2026-10-27.1"
SAMPLE_RETRIEVED_AT: Final = datetime(2026, 10, 27, 0, 0, tzinfo=UTC)
SAMPLE_SOURCE: Final = "sample"

_NA: Final = UnavailableReason.NOT_APPLICABLE
_NOT_PROVIDED: Final = UnavailableReason.NOT_PROVIDED


@dataclass(frozen=True)
class SampleFixture:
    """One fixed sample option, independent of the travel day.

    ``departure`` is a local time on the travel day. ``None`` means the option
    has no fixed schedule (road travel), and the departure and arrival must then
    be declared in ``unavailable``. ``fare_inr`` ``None`` must likewise be
    declared.
    """

    key: str
    operator: str | None
    departure: time | None
    duration: timedelta | None
    fare_inr: str | None
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    waitlist_position: int | None = None
    unavailable: Mapping[OptionalField, UnavailableReason] = field(default_factory=dict)
    note: str | None = None


SAMPLE_FIXTURES: Final[Mapping[TravelMode, tuple[SampleFixture, ...]]] = MappingProxyType(
    {
        TravelMode.FLIGHT: (
            SampleFixture(
                key="morning",
                operator="Demo Skyways",
                departure=time(6, 10),
                duration=timedelta(hours=1, minutes=5),
                fare_inr="4850.00",
                availability=AvailabilityStatus.AVAILABLE,
            ),
            SampleFixture(
                key="evening",
                operator="Sample Air",
                departure=time(18, 40),
                duration=timedelta(hours=1, minutes=10),
                fare_inr=None,
                availability=AvailabilityStatus.LIMITED,
                unavailable={"total_cost": _NOT_PROVIDED},
                note="fare not included in the sample fixture",
            ),
        ),
        TravelMode.RAIL: (
            SampleFixture(
                key="day-express",
                operator="Example Rail Express",
                departure=time(6, 0),
                duration=timedelta(hours=5),
                fare_inr="1215.00",
                availability=AvailabilityStatus.WAITLISTED,
                waitlist_position=12,
                note="sample waitlist position; not a confirmation forecast",
            ),
            SampleFixture(
                key="afternoon-intercity",
                operator="Example Intercity",
                departure=time(14, 30),
                duration=timedelta(hours=6, minutes=15),
                fare_inr="745.00",
                availability=AvailabilityStatus.AVAILABLE,
            ),
        ),
        TravelMode.CAR: (
            SampleFixture(
                key="self-drive",
                operator=None,
                departure=None,
                duration=timedelta(hours=5, minutes=45),
                fare_inr="3900.00",
                unavailable={"departure_at": _NA, "arrival_at": _NA},
                note="self-drive; illustrative fuel and toll estimate; departure is user-chosen",
            ),
        ),
        TravelMode.CAB: (
            SampleFixture(
                key="outstation-sedan",
                operator="Placeholder Cabs",
                departure=None,
                duration=timedelta(hours=6),
                fare_inr="6500.00",
                unavailable={"departure_at": _NA, "arrival_at": _NA},
                note="simulated on-demand cab; departure is user-chosen",
            ),
        ),
        TravelMode.BUS: (
            SampleFixture(
                key="overnight-sleeper",
                operator="Demo Travels",
                departure=time(22, 30),
                duration=timedelta(hours=7),
                fare_inr="950.00",
                availability=AvailabilityStatus.LIMITED,
                note="simulated sleeper bus; arrives the next day",
            ),
            SampleFixture(
                key="morning-seater",
                operator="Example Roadways",
                departure=time(7, 0),
                duration=timedelta(hours=6, minutes=15),
                fare_inr="620.00",
                availability=AvailabilityStatus.AVAILABLE,
            ),
        ),
    }
)


def build_sample_option(
    mode: TravelMode, fixture: SampleFixture, query: TravelQuery
) -> TravelOption:
    """Build a validated sample ``TravelOption`` for ``fixture`` on ``query``'s travel day.

    Raises:
        pydantic.ValidationError: If the fixture does not fit the contract.
    """
    offset = query.travel_date.utcoffset()
    if offset is None:  # unreachable: TravelQuery only accepts aware datetimes
        raise ValueError("travel_date must be timezone-aware")
    departure_at = arrival_at = None
    if fixture.departure is not None:
        departure_at = datetime.combine(query.travel_day, fixture.departure, timezone(offset))
        if fixture.duration is not None:
            arrival_at = departure_at + fixture.duration
    metadata: dict[str, str | bool] = {
        "fixture_version": SAMPLE_FIXTURE_VERSION,
        "simulated": True,
    }
    if fixture.note is not None:
        metadata["note"] = fixture.note
    return TravelOption(
        option_id=f"sample-{mode.value}-{fixture.key}-{query.travel_day.isoformat()}",
        mode=mode,
        origin=query.origin,
        destination=query.destination,
        operator=fixture.operator,
        departure_at=departure_at,
        arrival_at=arrival_at,
        duration=fixture.duration,
        total_cost=(
            None
            if fixture.fare_inr is None
            else Money(amount=Decimal(fixture.fare_inr), currency="INR")
        ),
        availability=fixture.availability,
        waitlist_position=fixture.waitlist_position,
        unavailable=fixture.unavailable,
        provenance=Provenance(
            origin=DataOrigin.SAMPLE, source=SAMPLE_SOURCE, retrieved_at=SAMPLE_RETRIEVED_AT
        ),
        provider_metadata=metadata,
    )


class SampleOptionProvider:
    """Deterministic ``OptionProvider`` serving the fixed sample fixtures for one mode."""

    def __init__(self, mode: TravelMode) -> None:
        """Create the sample provider for ``mode``."""
        self._mode = mode
        self._fixtures = SAMPLE_FIXTURES[mode]

    @property
    def name(self) -> str:
        """Provider identifier, e.g. ``"sample-rail"``."""
        return f"sample-{self._mode.value}"

    @property
    def mode(self) -> TravelMode:
        """The travel mode this provider serves."""
        return self._mode

    async def fetch_options(self, query: TravelQuery) -> tuple[TravelOption, ...]:
        """Return this mode's sample options for ``query`` (no I/O)."""
        return tuple(build_sample_option(self._mode, f, query) for f in self._fixtures)


def sample_providers() -> tuple[SampleOptionProvider, ...]:
    """Return one sample provider per travel mode, in ``TravelMode`` order."""
    return tuple(SampleOptionProvider(mode) for mode in TravelMode)
