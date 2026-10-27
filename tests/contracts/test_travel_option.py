"""Tests for the shared travel-option contract."""

from __future__ import annotations

import copy
import math
import pickle
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from routesmart.contracts import (
    MAX_AMOUNT_EXCLUSIVE,
    MAX_DURATION,
    MAX_METADATA_ENTRIES,
    MAX_METADATA_TEXT_LENGTH,
    AvailabilityStatus,
    DataOrigin,
    Freshness,
    FrozenMapping,
    Money,
    Provenance,
    TravelMode,
    TravelOption,
    UnavailableReason,
)

IST = timezone(timedelta(hours=5, minutes=30))
DEPART = datetime(2026, 11, 2, 6, 0, tzinfo=IST)
ARRIVE = datetime(2026, 11, 2, 7, 5, tzinfo=IST)
RETRIEVED = datetime(2026, 10, 27, 0, 0, tzinfo=UTC)


def sample_provenance(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "origin": "sample",
        "source": "sample",
        "retrieved_at": RETRIEVED,
    }
    data.update(overrides)
    return data


def option_data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "option_id": "flight-sample-1",
        "mode": "flight",
        "origin": "BLR",
        "destination": "MAA",
        "operator": "Sample Air",
        "departure_at": DEPART,
        "arrival_at": ARRIVE,
        "duration": ARRIVE - DEPART,
        "total_cost": {"amount": "4250.00", "currency": "INR"},
        "availability": "available",
        "provenance": sample_provenance(),
    }
    data.update(overrides)
    return data


# --- valid data ------------------------------------------------------------


def test_valid_complete_option() -> None:
    option = TravelOption.model_validate(option_data())
    assert option.mode is TravelMode.FLIGHT
    assert option.total_cost == Money(amount=Decimal("4250.00"), currency="INR")
    assert option.duration == timedelta(hours=1, minutes=5)
    assert option.schema_version == 1
    assert option.is_sample


@pytest.mark.parametrize("mode", list(TravelMode))
def test_every_mode_is_accepted(mode: TravelMode) -> None:
    assert TravelOption.model_validate(option_data(mode=mode.value)).mode is mode


def test_json_round_trip_preserves_values() -> None:
    option = TravelOption.model_validate(option_data())
    restored = TravelOption.model_validate_json(option.model_dump_json())
    assert restored == option


def test_json_uses_iso_duration_and_offset_timestamps() -> None:
    dumped = TravelOption.model_validate(option_data()).model_dump(mode="json")
    assert dumped["duration"] == "PT1H5M"
    assert dumped["departure_at"] == "2026-11-02T06:00:00+05:30"
    assert dumped["total_cost"] == {"amount": "4250.00", "currency": "INR"}


def test_option_is_immutable() -> None:
    option = TravelOption.model_validate(option_data())
    with pytest.raises(ValidationError):
        option.mode = TravelMode.BUS  # type: ignore[misc]


def test_whitespace_is_stripped() -> None:
    option = TravelOption.model_validate(option_data(origin="  BLR  "))
    assert option.origin == "BLR"


# --- required fields -------------------------------------------------------


@pytest.mark.parametrize("field", ["option_id", "mode", "origin", "destination", "provenance"])
def test_required_field_missing_is_rejected(field: str) -> None:
    data = option_data()
    del data[field]
    with pytest.raises(ValidationError, match=field):
        TravelOption.model_validate(data)


@pytest.mark.parametrize("field", ["option_id", "origin", "destination"])
def test_required_string_cannot_be_blank(field: str) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(**{field: "   "}))


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError, match="extra"):
        TravelOption.model_validate(option_data(price=100))


def test_unknown_mode_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(mode="teleport"))


def test_unsupported_schema_version_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(schema_version=2))


@pytest.mark.parametrize("place", ["MAA", "maa", " Maa "])
def test_origin_equal_to_destination_is_rejected(place: str) -> None:
    with pytest.raises(ValidationError, match="must differ"):
        TravelOption.model_validate(option_data(origin=place, destination="MAA"))


def test_place_name_length_boundary() -> None:
    assert TravelOption.model_validate(option_data(origin="B" * 64)).origin == "B" * 64
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(origin="B" * 65))


# --- optional and unavailable data -----------------------------------------


def test_missing_optional_operator_is_allowed() -> None:
    data = option_data()
    del data["operator"]
    assert TravelOption.model_validate(data).operator is None


def test_availability_defaults_to_unknown() -> None:
    data = option_data()
    del data["availability"]
    assert TravelOption.model_validate(data).availability is AvailabilityStatus.UNKNOWN


def test_metadata_defaults_to_empty() -> None:
    option = TravelOption.model_validate(option_data())
    assert option.provider_metadata == {}
    assert option.unavailable == {}


@pytest.mark.parametrize("field", ["departure_at", "arrival_at", "duration", "total_cost"])
def test_missing_measurable_field_must_be_declared(field: str) -> None:
    data = option_data()
    del data[field]
    with pytest.raises(ValidationError, match=f"{field} is missing"):
        TravelOption.model_validate(data)


@pytest.mark.parametrize("field", ["departure_at", "arrival_at", "duration", "total_cost"])
def test_declared_unavailable_field_is_accepted(field: str) -> None:
    data = option_data(unavailable={field: "provider_error"})
    data[field] = None
    option = TravelOption.model_validate(data)
    assert getattr(option, field) is None
    assert option.unavailable == {field: UnavailableReason.PROVIDER_ERROR}


def test_road_option_with_only_duration_and_cost() -> None:
    option = TravelOption.model_validate(
        option_data(
            option_id="car-sample-1",
            mode="car",
            origin="Bengaluru",
            destination="Chennai",
            operator=None,
            departure_at=None,
            arrival_at=None,
            duration="PT5H30M",
            unavailable={"departure_at": "not_applicable", "arrival_at": "not_applicable"},
        )
    )
    assert option.duration == timedelta(hours=5, minutes=30)


def test_entirely_unavailable_measurements() -> None:
    reasons = dict.fromkeys(
        ["departure_at", "arrival_at", "duration", "total_cost"], "not_provided"
    )
    data = option_data(unavailable=reasons)
    for field in reasons:
        data[field] = None
    assert len(TravelOption.model_validate(data).unavailable) == 4


def test_field_with_value_cannot_be_declared_unavailable() -> None:
    with pytest.raises(ValidationError, match="declared unavailable"):
        TravelOption.model_validate(option_data(unavailable={"total_cost": "not_provided"}))


def test_unknown_unavailable_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(unavailable={"operator": "not_provided"}))


def test_unknown_unavailable_reason_is_rejected() -> None:
    data = option_data(unavailable={"total_cost": "because"})
    data["total_cost"] = None
    with pytest.raises(ValidationError):
        TravelOption.model_validate(data)


# --- currency --------------------------------------------------------------


@pytest.mark.parametrize("amount", ["0", "0.00", "0.01", "4250.5", 4250])
def test_valid_amounts(amount: object) -> None:
    assert Money.model_validate({"amount": amount, "currency": "INR"}).amount >= 0


@pytest.mark.parametrize(
    "amount", ["-0.01", "1.001", "NaN", "Infinity", "-Infinity", "abc", "", None, 4250.5, 0.0, True]
)
def test_invalid_amounts(amount: object) -> None:
    with pytest.raises(ValidationError):
        Money.model_validate({"amount": amount, "currency": "INR"})


@pytest.mark.parametrize("currency", ["inr", "IN", "INRR", "", "₹", None])
def test_invalid_currency_codes(currency: object) -> None:
    with pytest.raises(ValidationError):
        Money.model_validate({"amount": "1.00", "currency": currency})


def test_currency_is_required() -> None:
    with pytest.raises(ValidationError, match="currency"):
        Money.model_validate({"amount": "1.00"})


def test_non_inr_currency_is_representable() -> None:
    assert Money.model_validate({"amount": "10.00", "currency": "USD"}).currency == "USD"


# --- durations and timestamps ----------------------------------------------


@pytest.mark.parametrize("timestamp", [datetime(2026, 11, 2, 6, 0), "2026-11-02T06:00:00"])  # noqa: DTZ001
def test_naive_timestamps_are_rejected(timestamp: object) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(departure_at=timestamp))


def test_naive_retrieved_at_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Provenance.model_validate(sample_provenance(retrieved_at="2026-10-27T00:00:00"))


def test_equivalent_instants_in_different_offsets_are_consistent() -> None:
    option = TravelOption.model_validate(
        option_data(arrival_at=ARRIVE.astimezone(UTC), duration=ARRIVE - DEPART)
    )
    assert option.arrival_at == ARRIVE


@pytest.mark.parametrize("arrival", [DEPART, DEPART - timedelta(minutes=1)])
def test_arrival_not_after_departure_is_rejected(arrival: datetime) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(arrival_at=arrival))


def test_duration_must_match_timestamps() -> None:
    with pytest.raises(ValidationError, match="duration must equal"):
        TravelOption.model_validate(option_data(duration=timedelta(hours=2)))


@pytest.mark.parametrize(
    "duration", [timedelta(0), timedelta(seconds=-1), MAX_DURATION + timedelta(seconds=1)]
)
def test_out_of_range_durations_are_rejected(duration: timedelta) -> None:
    with pytest.raises(ValidationError, match="duration must be positive"):
        TravelOption.model_validate(
            option_data(
                departure_at=None,
                arrival_at=None,
                duration=duration,
                unavailable={"departure_at": "not_applicable", "arrival_at": "not_applicable"},
            )
        )


@pytest.mark.parametrize("duration", [timedelta(seconds=1), MAX_DURATION])
def test_duration_boundaries_are_accepted(duration: timedelta) -> None:
    option = TravelOption.model_validate(
        option_data(
            departure_at=None,
            arrival_at=None,
            duration=duration,
            unavailable={"departure_at": "not_applicable", "arrival_at": "not_applicable"},
        )
    )
    assert option.duration == duration


# --- availability ------------------------------------------------------------


def test_waitlisted_option_with_position() -> None:
    option = TravelOption.model_validate(
        option_data(mode="rail", availability="waitlisted", waitlist_position=1)
    )
    assert option.waitlist_position == 1


def test_waitlisted_without_position_is_allowed() -> None:
    option = TravelOption.model_validate(option_data(mode="rail", availability="waitlisted"))
    assert option.waitlist_position is None


@pytest.mark.parametrize("position", [0, -3])
def test_non_positive_waitlist_position_is_rejected(position: int) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(
            option_data(availability="waitlisted", waitlist_position=position)
        )


def test_waitlist_position_requires_waitlisted_status() -> None:
    with pytest.raises(ValidationError, match="waitlisted"):
        TravelOption.model_validate(option_data(availability="available", waitlist_position=4))


# --- provenance and freshness -------------------------------------------------


def test_sample_data_is_never_fresh() -> None:
    provenance = Provenance.model_validate(
        sample_provenance(expires_at=RETRIEVED + timedelta(days=365))
    )
    assert provenance.freshness(RETRIEVED + timedelta(minutes=1)) is Freshness.SAMPLE


def test_live_data_freshness_boundary() -> None:
    expires = RETRIEVED + timedelta(minutes=15)
    provenance = Provenance(
        origin=DataOrigin.LIVE,
        source="example_provider",
        retrieved_at=RETRIEVED,
        expires_at=expires,
    )
    assert provenance.freshness(expires - timedelta(microseconds=1)) is Freshness.FRESH
    assert provenance.freshness(expires) is Freshness.STALE
    assert provenance.freshness(expires + timedelta(days=1)) is Freshness.STALE


def test_live_data_without_expiry_is_unknown() -> None:
    provenance = Provenance(
        origin=DataOrigin.LIVE, source="example_provider", retrieved_at=RETRIEVED
    )
    assert provenance.freshness(RETRIEVED) is Freshness.UNKNOWN


def test_freshness_requires_aware_instant() -> None:
    provenance = Provenance.model_validate(sample_provenance())
    with pytest.raises(ValueError, match="timezone-aware"):
        provenance.freshness(datetime(2026, 10, 27))  # noqa: DTZ001


def test_live_origin_cannot_claim_sample_source() -> None:
    with pytest.raises(ValidationError, match="live data"):
        Provenance.model_validate(sample_provenance(origin="live"))


@pytest.mark.parametrize("offset", [timedelta(0), timedelta(seconds=-1)])
def test_expiry_must_follow_retrieval(offset: timedelta) -> None:
    with pytest.raises(ValidationError, match="expires_at"):
        Provenance.model_validate(sample_provenance(expires_at=RETRIEVED + offset))


@pytest.mark.parametrize("source", ["", "Sample", "has space", "1provider", "a" * 65])
def test_invalid_source_slugs(source: str) -> None:
    with pytest.raises(ValidationError):
        Provenance.model_validate(sample_provenance(source=source))


def test_unknown_origin_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Provenance.model_validate(sample_provenance(origin="cached"))


def test_live_option_is_not_sample() -> None:
    provenance = sample_provenance(origin="live", source="example_provider")
    assert not TravelOption.model_validate(option_data(provenance=provenance)).is_sample


# --- provider metadata ----------------------------------------------------------


def test_flat_metadata_is_accepted() -> None:
    metadata = {"fare_class": "Y", "stops": 0, "co2_kg": 41.5, "refundable": False, "note": None}
    option = TravelOption.model_validate(option_data(provider_metadata=metadata))
    assert option.provider_metadata == metadata


def test_nested_metadata_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(provider_metadata={"legs": [{"from": "BLR"}]}))


@pytest.mark.parametrize("key", ["", "Upper", "with space"])
def test_invalid_metadata_keys_are_rejected(key: str) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(provider_metadata={key: 1}))


def test_metadata_entry_limit_boundary() -> None:
    at_limit = {f"k{i}": i for i in range(MAX_METADATA_ENTRIES)}
    assert (
        len(TravelOption.model_validate(option_data(provider_metadata=at_limit)).provider_metadata)
        == MAX_METADATA_ENTRIES
    )
    over_limit = {f"k{i}": i for i in range(MAX_METADATA_ENTRIES + 1)}
    with pytest.raises(ValidationError, match="at most"):
        TravelOption.model_validate(option_data(provider_metadata=over_limit))


# --- immutability, hashing and serialisation (H4) ----------------------------


def test_unavailable_cannot_be_mutated_after_validation() -> None:
    data = option_data(unavailable={"total_cost": "not_provided"})
    data["total_cost"] = None
    option = TravelOption.model_validate(data)
    with pytest.raises(TypeError):
        option.unavailable["departure_at"] = UnavailableReason.NOT_PROVIDED  # type: ignore[index]
    with pytest.raises(TypeError):
        del option.unavailable["total_cost"]  # type: ignore[attr-defined]
    assert not hasattr(option.unavailable, "update")
    assert not hasattr(option.unavailable, "pop")
    assert dict(option.unavailable) == {"total_cost": UnavailableReason.NOT_PROVIDED}


def test_metadata_limit_cannot_be_bypassed_after_validation() -> None:
    option = TravelOption.model_validate(option_data(provider_metadata={"k0": 0}))
    with pytest.raises(TypeError):
        option.provider_metadata["k1"] = 1  # type: ignore[index]
    assert not hasattr(option.provider_metadata, "clear")
    assert len(option.provider_metadata) == 1


def test_input_dict_changes_do_not_leak_into_option() -> None:
    metadata: dict[str, object] = {"stops": 0}
    option = TravelOption.model_validate(option_data(provider_metadata=metadata))
    metadata["stops"] = 99
    metadata["extra"] = "x"
    assert option.provider_metadata == {"stops": 0}


def test_mapping_fields_are_frozen_mappings() -> None:
    option = TravelOption.model_validate(option_data(provider_metadata={"stops": 0}))
    assert isinstance(option.unavailable, FrozenMapping)
    assert isinstance(option.provider_metadata, FrozenMapping)


def test_model_dump_returns_plain_dicts() -> None:
    dumped = TravelOption.model_validate(option_data(provider_metadata={"stops": 0})).model_dump()
    assert type(dumped["provider_metadata"]) is dict
    assert type(dumped["unavailable"]) is dict


def test_validated_option_is_hashable_and_hash_is_stable_across_round_trip() -> None:
    option = TravelOption.model_validate(option_data(provider_metadata={"stops": 0, "y": None}))
    restored = TravelOption.model_validate_json(option.model_dump_json())
    assert restored == option
    assert hash(restored) == hash(option)
    assert len({option, restored}) == 1


def test_option_survives_pickle_and_deepcopy() -> None:
    option = TravelOption.model_validate(option_data(provider_metadata={"stops": 0}))
    assert pickle.loads(pickle.dumps(option)) == option  # noqa: S301 (own trusted data)
    assert copy.deepcopy(option) == option
    assert option.model_copy(deep=True) == option


def test_frozen_mapping_semantics() -> None:
    mapping = FrozenMapping({"a": 1, "b": 2})
    assert mapping == {"a": 1, "b": 2}
    assert mapping != {"a": 1}
    assert len(mapping) == 2
    assert list(mapping) == ["a", "b"]
    assert mapping["a"] == 1
    assert hash(mapping) == hash(FrozenMapping({"b": 2, "a": 1}))
    assert FrozenMapping() == {}
    assert repr(mapping) == "FrozenMapping({'a': 1, 'b': 2})"
    with pytest.raises(KeyError):
        mapping["missing"]


def test_serialisation_schema_keeps_mapping_detail() -> None:
    schema = TravelOption.model_json_schema(mode="serialization")["properties"]
    assert schema["unavailable"]["propertyNames"]["enum"] == [
        "departure_at",
        "arrival_at",
        "duration",
        "total_cost",
    ]
    assert "^[a-z][a-z0-9_-]{0,63}$" in schema["provider_metadata"]["patternProperties"]
    validation = TravelOption.model_json_schema(mode="validation")["properties"]
    assert validation["provider_metadata"]["maxProperties"] == MAX_METADATA_ENTRIES


# --- unambiguous inputs (M1) ----------------------------------------------------

_NO_TIMES = {"departure_at": "not_applicable", "arrival_at": "not_applicable"}


@pytest.mark.parametrize("duration", [3900, 3900.5, True, "3900", "1:05:00", "65 minutes", ""])
def test_ambiguous_durations_are_rejected(duration: object) -> None:
    with pytest.raises(ValidationError, match="ISO 8601"):
        TravelOption.model_validate(
            option_data(
                departure_at=None, arrival_at=None, duration=duration, unavailable=_NO_TIMES
            )
        )


@pytest.mark.parametrize(
    ("duration", "expected"),
    [("PT1H5M", timedelta(hours=1, minutes=5)), (" P1DT2H ", timedelta(days=1, hours=2))],
)
def test_iso_durations_are_accepted(duration: str, expected: timedelta) -> None:
    option = TravelOption.model_validate(
        option_data(departure_at=None, arrival_at=None, duration=duration, unavailable=_NO_TIMES)
    )
    assert option.duration == expected


def test_negative_iso_duration_is_rejected() -> None:
    with pytest.raises(ValidationError, match="duration must be positive"):
        TravelOption.model_validate(
            option_data(departure_at=None, arrival_at=None, duration="-PT1H", unavailable=_NO_TIMES)
        )


@pytest.mark.parametrize(
    "timestamp", [1793580000, 1793580000.5, True, "1793580000", "2026-11-02", date(2026, 11, 2)]
)
def test_ambiguous_timestamps_are_rejected(timestamp: object) -> None:
    with pytest.raises(ValidationError, match="ISO 8601"):
        TravelOption.model_validate(option_data(departure_at=timestamp))


@pytest.mark.parametrize("field", ["retrieved_at", "expires_at"])
def test_ambiguous_provenance_timestamps_are_rejected(field: str) -> None:
    with pytest.raises(ValidationError, match="ISO 8601"):
        Provenance.model_validate(sample_provenance(**{field: 1793580000}))


def test_iso_timestamp_with_z_and_offset_is_accepted() -> None:
    option = TravelOption.model_validate(
        option_data(departure_at="2026-11-02T00:30:00Z", arrival_at="2026-11-02T07:05:00+05:30")
    )
    assert option.departure_at == DEPART
    assert option.duration == timedelta(hours=1, minutes=5)


@pytest.mark.parametrize("position", [True, False, "3", 3.0])
def test_non_integer_waitlist_positions_are_rejected(position: object) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(
            option_data(availability="waitlisted", waitlist_position=position)
        )


def test_boolean_schema_version_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(schema_version=True))


# --- money canonicalisation and bounds (M2) --------------------------------------


@pytest.mark.parametrize(
    ("raw", "canonical"),
    [
        ("4250.5", "4250.50"),
        ("1E+2", "100.00"),
        ("1.100", "1.10"),
        ("-0", "0.00"),
        (0, "0.00"),
        (Decimal("7"), "7.00"),
        ("999999999999.99", "999999999999.99"),
    ],
)
def test_amounts_are_canonicalised_to_two_places(raw: object, canonical: str) -> None:
    money = Money.model_validate({"amount": raw, "currency": "INR"})
    assert str(money.amount) == canonical
    assert money.model_dump(mode="json")["amount"] == canonical


@pytest.mark.parametrize("raw", [str(MAX_AMOUNT_EXCLUSIVE), "1e30", 10**12])
def test_amount_upper_bound(raw: object) -> None:
    with pytest.raises(ValidationError, match="less than"):
        Money.model_validate({"amount": raw, "currency": "INR"})


@pytest.mark.parametrize(
    ("payload", "accepted"),
    [
        ('{"amount": "4250.50", "currency": "INR"}', True),
        ('{"amount": 4250, "currency": "INR"}', True),
        ('{"amount": 4250.5, "currency": "INR"}', False),
        ('{"amount": "NaN", "currency": "INR"}', False),
    ],
)
def test_json_amount_inputs(payload: str, accepted: bool) -> None:
    if accepted:
        Money.model_validate_json(payload)
    else:
        with pytest.raises(ValidationError):
            Money.model_validate_json(payload)


def test_currency_check_is_format_only() -> None:
    # Documented narrower guarantee: ISO 4217 code *format*, not registry membership.
    assert Money.model_validate({"amount": "1", "currency": "XYZ"}).currency == "XYZ"


# --- metadata bounds and documented behaviours (L4) -------------------------------


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_metadata_numbers_are_rejected(value: float) -> None:
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(provider_metadata={"x": value}))


def test_metadata_text_length_boundary() -> None:
    at_limit = "a" * MAX_METADATA_TEXT_LENGTH
    option = TravelOption.model_validate(option_data(provider_metadata={"x": at_limit}))
    assert option.provider_metadata["x"] == at_limit
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(provider_metadata={"x": at_limit + "a"}))


def test_metadata_scalar_types_are_preserved() -> None:
    metadata = {"s": "1", "b": True, "i": 1, "f": 1.5, "n": None}
    option = TravelOption.model_validate(option_data(provider_metadata=metadata))
    assert {k: type(v) for k, v in option.provider_metadata.items()} == {
        "s": str,
        "b": bool,
        "i": int,
        "f": float,
        "n": type(None),
    }


def test_future_retrieval_timestamp_is_accepted_by_design() -> None:
    # Documented decision: validation stays clock-independent; adapters stamp retrieved_at.
    provenance = Provenance.model_validate(sample_provenance(retrieved_at="2099-01-01T00:00:00Z"))
    assert provenance.retrieved_at.year == 2099


def test_model_construct_skips_validation_as_documented() -> None:
    unchecked = TravelOption.model_construct(
        option_id="x",
        mode=TravelMode.CAR,
        origin="MAA",
        destination="MAA",
        provenance=Provenance.model_validate(sample_provenance()),
    )
    assert unchecked.origin == unchecked.destination


# --- Round 2 review regressions: N3 (nested revalidation) ------------------------


def test_nested_money_built_with_model_construct_is_revalidated() -> None:
    bad_money = Money.model_construct(amount=Decimal("-5"), currency="rupees")
    with pytest.raises(ValidationError) as excinfo:
        TravelOption.model_validate(option_data(total_cost=bad_money))
    locations = {err["loc"] for err in excinfo.value.errors()}
    assert ("total_cost", "amount") in locations
    assert ("total_cost", "currency") in locations


def test_nested_provenance_built_with_model_construct_is_revalidated() -> None:
    naive_live_sample = Provenance.model_construct(
        origin=DataOrigin.LIVE,
        source="sample",
        retrieved_at=datetime(2026, 1, 1),  # noqa: DTZ001 (deliberately naive)
    )
    with pytest.raises(ValidationError):
        TravelOption.model_validate(option_data(provenance=naive_live_sample))


def test_valid_nested_instances_are_accepted_and_equal_after_revalidation() -> None:
    money = Money.model_validate({"amount": "4250.00", "currency": "INR"})
    provenance = Provenance.model_validate(sample_provenance())
    option = TravelOption.model_validate(option_data(total_cost=money, provenance=provenance))
    assert option.total_cost == money
    assert option.provenance == provenance


def test_unchecked_option_is_revalidated_when_validated_again() -> None:
    unchecked = TravelOption.model_construct(
        option_id="x",
        mode=TravelMode.CAR,
        origin="MAA",
        destination="MAA",
        provenance=Provenance.model_validate(sample_provenance()),
    )
    with pytest.raises(ValidationError):
        TravelOption.model_validate(unchecked)


# --- N6: FrozenMapping internals --------------------------------------------------


def test_frozen_mapping_internal_storage_is_read_only() -> None:
    option = TravelOption.model_validate(option_data(provider_metadata={"k": 1}))
    before = hash(option)
    with pytest.raises(TypeError):
        option.provider_metadata._data["k2"] = 2  # type: ignore[attr-defined]
    assert len(option.provider_metadata) == 1
    assert hash(option) == before


def test_frozen_mapping_attributes_cannot_be_replaced_or_deleted() -> None:
    mapping = FrozenMapping({"a": 1})
    with pytest.raises(AttributeError):
        mapping._data = {"a": 2}  # type: ignore[assignment]
    with pytest.raises(AttributeError):
        del mapping._data
    with pytest.raises(AttributeError):
        mapping.extra = 1
    assert mapping == {"a": 1}


def test_metadata_cap_cannot_be_bypassed_through_internals() -> None:
    option = TravelOption.model_validate(
        option_data(provider_metadata={f"k{i}": i for i in range(MAX_METADATA_ENTRIES)})
    )
    with pytest.raises(TypeError):
        option.provider_metadata._data["extra"] = 0  # type: ignore[attr-defined]
    assert len(option.provider_metadata) == MAX_METADATA_ENTRIES


def test_frozen_mapping_copies_are_independent_and_equal() -> None:
    mapping = FrozenMapping({"a": 1})
    assert copy.copy(mapping) == mapping
    assert copy.deepcopy(mapping) == mapping
    assert pickle.loads(pickle.dumps(mapping)) == mapping  # noqa: S301 (own trusted data)


# --- N7: type-aware equality and hashing -------------------------------------------


@pytest.mark.parametrize(
    ("left", "right"),
    [(1, True), (0, False), (1, 1.0), ("1", 1), (None, 0)],
)
def test_metadata_values_of_different_types_are_not_equal(left: object, right: object) -> None:
    a = TravelOption.model_validate(option_data(provider_metadata={"f": left}))
    b = TravelOption.model_validate(option_data(provider_metadata={"f": right}))
    assert a.model_dump_json() != b.model_dump_json()
    assert a != b
    assert len({a, b}) == 2


def test_equality_matches_serialisation_and_hash_is_consistent() -> None:
    values: list[object] = [1, True, 1.0, "1", None, 0, False, 2.5]
    options = [TravelOption.model_validate(option_data(provider_metadata={"f": v})) for v in values]
    for a in options:
        for b in options:
            assert (a == b) == (a.model_dump_json() == b.model_dump_json())
            if a == b:
                assert hash(a) == hash(b)


def test_frozen_mapping_equality_against_plain_mappings() -> None:
    assert FrozenMapping({"x": 1}) == {"x": 1}
    plain = {"x": 1}
    assert plain == FrozenMapping({"x": 1})  # reflected: dict.__eq__ defers to FrozenMapping
    assert FrozenMapping({"x": 1}) != {"x": True}
    assert FrozenMapping({"x": 1}) != {"y": 1}
    assert FrozenMapping({"x": 1}) != [("x", 1)]
    assert FrozenMapping() == {}
