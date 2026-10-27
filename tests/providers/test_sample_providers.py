"""Tests for the deterministic sample providers (Task 003)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from routesmart.contracts import (
    AvailabilityStatus,
    DataOrigin,
    Freshness,
    TravelMode,
    TravelOption,
    UnavailableReason,
)
from routesmart.providers import (
    SAMPLE_FIXTURE_VERSION,
    SAMPLE_FIXTURES,
    SAMPLE_RETRIEVED_AT,
    OptionProvider,
    SampleOptionProvider,
    TravelQuery,
    sample_providers,
)

IST = timezone(timedelta(hours=5, minutes=30))


def make_query(travel: datetime | None = None) -> TravelQuery:
    return TravelQuery(
        origin="BLR",
        destination="MAA",
        travel_date=travel or datetime(2026, 11, 2, tzinfo=IST),
        current_date=datetime(2026, 10, 27, 9, 0, tzinfo=IST),
    )


async def fetch(mode: TravelMode, query: TravelQuery | None = None) -> tuple[TravelOption, ...]:
    return await SampleOptionProvider(mode).fetch_options(query or make_query())


def test_one_provider_per_mode_satisfying_the_protocol() -> None:
    providers = sample_providers()
    assert [p.mode for p in providers] == list(TravelMode)
    assert [p.name for p in providers] == [f"sample-{m.value}" for m in TravelMode]
    typed: tuple[OptionProvider, ...] = providers
    assert len(typed) == 5


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", list(TravelMode))
async def test_every_mode_returns_valid_sample_options(mode: TravelMode) -> None:
    options = await fetch(mode)
    assert len(options) == len(SAMPLE_FIXTURES[mode]) >= 1
    for option in options:
        TravelOption.model_validate(option.model_dump())  # round-trips through the contract
        assert option.mode is mode
        assert (option.origin, option.destination) == ("BLR", "MAA")
        assert option.is_sample
        assert option.provenance.origin is DataOrigin.SAMPLE
        assert option.provenance.source == "sample"
        assert option.provenance.retrieved_at == SAMPLE_RETRIEVED_AT
        assert option.provenance.expires_at is None
        assert option.provenance.freshness(datetime(2030, 1, 1, tzinfo=UTC)) is Freshness.SAMPLE
        assert option.provider_metadata["fixture_version"] == SAMPLE_FIXTURE_VERSION
        assert option.provider_metadata["simulated"] is True
        assert option.option_id.startswith(f"sample-{mode.value}-")
        assert option.option_id.endswith("-2026-11-02")
        if option.total_cost is not None:
            assert option.total_cost.currency == "INR"


@pytest.mark.asyncio
async def test_option_ids_are_unique_across_modes() -> None:
    ids = [o.option_id for mode in TravelMode for o in await fetch(mode)]
    assert len(ids) == len(set(ids))


@pytest.mark.asyncio
async def test_identical_queries_give_identical_options() -> None:
    for mode in TravelMode:
        first = await fetch(mode)
        second = await SampleOptionProvider(mode).fetch_options(make_query())
        assert first == second
        assert [o.model_dump_json() for o in first] == [o.model_dump_json() for o in second]


@pytest.mark.asyncio
async def test_scheduled_times_are_on_the_travel_day_in_its_offset() -> None:
    (morning, _evening) = await fetch(TravelMode.FLIGHT)
    assert morning.departure_at == datetime(2026, 11, 2, 6, 10, tzinfo=IST)
    assert morning.arrival_at == datetime(2026, 11, 2, 7, 15, tzinfo=IST)
    assert morning.duration == timedelta(hours=1, minutes=5)
    assert morning.total_cost is not None
    assert morning.total_cost.amount == Decimal("4850.00")


@pytest.mark.asyncio
async def test_overnight_bus_arrives_the_next_day() -> None:
    sleeper = (await fetch(TravelMode.BUS))[0]
    assert sleeper.departure_at == datetime(2026, 11, 2, 22, 30, tzinfo=IST)
    assert sleeper.arrival_at == datetime(2026, 11, 3, 5, 30, tzinfo=IST)


@pytest.mark.asyncio
async def test_travel_day_offset_is_used_for_departures() -> None:
    utc_query = make_query(datetime(2026, 11, 2, 12, 0, tzinfo=UTC))
    morning = (await fetch(TravelMode.FLIGHT, utc_query))[0]
    assert morning.departure_at == datetime(2026, 11, 2, 6, 10, tzinfo=UTC)
    assert morning.departure_at is not None
    assert morning.departure_at.utcoffset() == timedelta(0)


@pytest.mark.asyncio
async def test_options_follow_the_travel_day() -> None:
    later = await fetch(TravelMode.RAIL, make_query(datetime(2026, 12, 25, tzinfo=IST)))
    assert all(o.option_id.endswith("-2026-12-25") for o in later)
    assert all(o.departure_at and o.departure_at.date() == date(2026, 12, 25) for o in later)


@pytest.mark.asyncio
async def test_rail_includes_a_waitlisted_option() -> None:
    waitlisted = [o for o in await fetch(TravelMode.RAIL) if o.waitlist_position is not None]
    assert len(waitlisted) == 1
    assert waitlisted[0].availability is AvailabilityStatus.WAITLISTED
    assert waitlisted[0].waitlist_position == 12


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", [TravelMode.CAR, TravelMode.CAB])
async def test_road_options_declare_times_not_applicable(mode: TravelMode) -> None:
    for option in await fetch(mode):
        assert option.departure_at is None
        assert option.arrival_at is None
        assert option.duration is not None
        assert option.total_cost is not None
        assert dict(option.unavailable) == {
            "departure_at": UnavailableReason.NOT_APPLICABLE,
            "arrival_at": UnavailableReason.NOT_APPLICABLE,
        }


@pytest.mark.asyncio
async def test_missing_fare_is_declared_not_silently_absent() -> None:
    evening = (await fetch(TravelMode.FLIGHT))[1]
    assert evening.total_cost is None
    assert dict(evening.unavailable) == {"total_cost": UnavailableReason.NOT_PROVIDED}


def test_fixture_table_is_read_only() -> None:
    with pytest.raises(TypeError):
        SAMPLE_FIXTURES[TravelMode.FLIGHT] = ()  # type: ignore[index]
