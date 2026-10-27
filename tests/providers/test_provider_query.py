"""Tests for TravelQuery validation (Task 003; travel-date semantics per P2-PROP-02 option A)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from routesmart.providers import SUPPORTED_ROUTES, TravelQuery

IST = timezone(timedelta(hours=5, minutes=30))
TRAVEL = datetime(2026, 11, 2, 0, 0, tzinfo=IST)
NAIVE = datetime(2026, 11, 2, 0, 0)  # noqa: DTZ001 (deliberately naive)


def make(**overrides: Any) -> TravelQuery:
    values: dict[str, Any] = {
        "origin": "BLR",
        "destination": "MAA",
        "travel_date": TRAVEL,
        "current_date": datetime(2026, 10, 27, 12, 0, tzinfo=IST),
    }
    values.update(overrides)
    return TravelQuery(**values)


def test_valid_pilot_query() -> None:
    query = make()
    assert (query.origin, query.destination) == ("BLR", "MAA")
    assert query.travel_day == date(2026, 11, 2)
    assert frozenset({("BLR", "MAA")}) == SUPPORTED_ROUTES


def test_same_day_later_current_time_is_accepted() -> None:
    # Option A: calendar dates are compared, so "today at 00:00" stays valid all day.
    query = make(current_date=datetime(2026, 11, 2, 23, 59, 59, tzinfo=IST))
    assert query.current_day == query.travel_day


def test_previous_day_is_rejected() -> None:
    with pytest.raises(ValidationError, match="before the current date"):
        make(current_date=datetime(2026, 11, 3, 0, 0, tzinfo=IST))


def test_current_instant_is_converted_into_travel_timezone() -> None:
    # 2026-11-01T20:00Z is 2026-11-02T01:30 in IST: same travel day, so accepted.
    assert make(current_date=datetime(2026, 11, 1, 20, 0, tzinfo=UTC)).current_day == date(
        2026, 11, 2
    )
    # 2026-11-02T19:00Z is 2026-11-03T00:30 in IST: the travel day has passed.
    with pytest.raises(ValidationError, match="before the current date"):
        make(current_date=datetime(2026, 11, 2, 19, 0, tzinfo=UTC))


def test_travel_day_uses_travel_date_own_timezone() -> None:
    # 2026-11-02T23:00-05:00 is the 2nd locally (the 3rd in UTC); the 2nd is still today.
    travel = datetime(2026, 11, 2, 23, 0, tzinfo=timezone(timedelta(hours=-5)))
    query = make(travel_date=travel, current_date=datetime(2026, 11, 3, 3, 0, tzinfo=UTC))
    assert query.travel_day == date(2026, 11, 2)
    assert query.current_day == date(2026, 11, 2)


def test_zoneinfo_timezones_are_supported() -> None:
    kolkata = ZoneInfo("Asia/Kolkata")
    query = make(
        travel_date=datetime(2026, 11, 2, 9, 0, tzinfo=kolkata),
        current_date=datetime(2026, 11, 2, 8, 0, tzinfo=kolkata),
    )
    assert query.travel_day == date(2026, 11, 2)


def test_iso_strings_with_offset_are_accepted() -> None:
    query = make(travel_date="2026-11-02T00:00:00+05:30", current_date="2026-10-27T00:00:00Z")
    assert query.travel_date == TRAVEL


@pytest.mark.parametrize("field", ["travel_date", "current_date"])
@pytest.mark.parametrize(
    "value",
    [NAIVE, "2026-11-02T00:00:00", 1793577600, date(2026, 11, 2), "2026-11-02"],
    ids=["naive-datetime", "naive-string", "epoch", "date", "date-string"],
)
def test_naive_or_ambiguous_dates_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        make(**{field: value})


@pytest.mark.parametrize(
    ("origin", "destination", "message"),
    [
        ("BLR", "BLR", "must differ"),
        ("MAA", "maa", "must differ"),
        ("MAA", "BLR", "unsupported route"),
        ("BLR", "DEL", "unsupported route"),
        ("blr", "MAA", "unsupported route"),
    ],
)
def test_invalid_routes_are_rejected(origin: str, destination: str, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        make(origin=origin, destination=destination)


@pytest.mark.parametrize("missing", ["origin", "destination", "travel_date", "current_date"])
def test_missing_fields_are_rejected(missing: str) -> None:
    values: dict[str, Any] = {
        "origin": "BLR",
        "destination": "MAA",
        "travel_date": TRAVEL,
        "current_date": TRAVEL,
    }
    del values[missing]
    with pytest.raises(ValidationError):
        TravelQuery(**values)


@pytest.mark.parametrize("bad", ["", "   ", "X" * 65])
def test_bad_place_names_are_rejected(bad: str) -> None:
    with pytest.raises(ValidationError):
        make(origin=bad)


def test_extra_fields_are_rejected_and_query_is_frozen() -> None:
    with pytest.raises(ValidationError):
        make(passengers=2)
    query = make()
    with pytest.raises(ValidationError):
        query.origin = "MAA"  # type: ignore[misc]


def test_whitespace_is_stripped() -> None:
    assert make(origin=" BLR ", destination="MAA\n").origin == "BLR"


def test_validation_uses_the_supplied_current_date_not_the_clock() -> None:
    # Accepted although both dates are long past on the real clock...
    past = make(
        travel_date=datetime(2001, 1, 2, tzinfo=IST), current_date=datetime(2001, 1, 1, tzinfo=IST)
    )
    assert past.travel_day == date(2001, 1, 2)
    # ...and rejected although both dates are far in the future on the real clock.
    with pytest.raises(ValidationError, match="before the current date"):
        make(
            travel_date=datetime(2100, 1, 1, tzinfo=IST),
            current_date=datetime(2100, 1, 2, tzinfo=IST),
        )


def test_identical_inputs_give_identical_queries() -> None:
    assert make() == make()
    assert hash(make()) == hash(make())
