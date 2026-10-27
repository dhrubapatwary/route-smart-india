"""Provider-neutral travel-option contract shared by all travel modes.

Flight, rail, car, cab and bus modules map their provider data into
``TravelOption``. Scoring, the API and the UI consume only this contract. See
``docs/TRAVEL_OPTION_CONTRACT.md`` for the design rationale.

Validated instances cannot be changed through their public API or ordinary
attribute access, and they are hashable. Nested ``Money``/``Provenance``
instances are always revalidated. ``model_construct()`` and
``model_copy(update=...)`` still skip validation (Pydantic behaviour) and must not
be used to build options from untrusted or provider data.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterator, Mapping
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import Annotated, Any, Final, Literal, Self, override

from pydantic import (
    AfterValidator,
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    StringConstraints,
    field_validator,
    model_validator,
)

SCHEMA_VERSION: Final = 1
MAX_DURATION: Final = timedelta(days=7)
MAX_METADATA_ENTRIES: Final = 32
MAX_METADATA_TEXT_LENGTH: Final = 256
MAX_AMOUNT_EXCLUSIVE: Final = Decimal("1000000000000")  # 10**12: technical sanity bound
_CENT: Final = Decimal("0.01")

_ISO_DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
_ISO_DURATION = re.compile(r"^-?P")


class FrozenMapping[K, V](Mapping[K, V]):
    """Immutable, hashable mapping used for the contract's mapping fields.

    * The items live in a read-only ``MappingProxyType`` over a private copy, and
      attribute assignment and deletion raise ``AttributeError``. The contents
      and the hash therefore cannot change through the public API or ordinary
      attribute access. Deliberate interpreter-level tampering (e.g.
      ``object.__setattr__``) is out of scope, as for any Python object.
    * Equality is **type-aware** for values: ``{"x": 1}``, ``{"x": True}`` and
      ``{"x": 1.0}`` are all different. They serialise differently, so equality
      matches the JSON form. A ``FrozenMapping`` equals any ``Mapping``, including
      a ``dict``, with the same keys and the same value types and values.
    * Hashing requires hashable values and is consistent with equality.
    """

    __slots__ = ("_data",)
    _data: MappingProxyType[K, V]

    def __init__(self, data: Mapping[K, V] | None = None) -> None:
        """Copy ``data`` into a new immutable mapping."""
        object.__setattr__(self, "_data", MappingProxyType(dict(data) if data is not None else {}))

    @override
    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("FrozenMapping is immutable")

    @override
    def __delattr__(self, name: str) -> None:
        raise AttributeError("FrozenMapping is immutable")

    @override
    def __reduce__(self) -> tuple[type[FrozenMapping[K, V]], tuple[dict[K, V]]]:
        return (type(self), (dict(self._data),))

    @override
    def __getitem__(self, key: K) -> V:
        return self._data[key]

    @override
    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    @override
    def __len__(self) -> int:
        return len(self._data)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return NotImplemented
        if len(other) != len(self._data):
            return False
        for key, value in self._data.items():
            if key not in other:
                return False
            theirs = other[key]
            if type(theirs) is not type(value) or not (theirs is value or theirs == value):
                return False
        return True

    @override
    def __hash__(self) -> int:
        return hash(frozenset((key, type(value), value) for key, value in self._data.items()))

    @override
    def __repr__(self) -> str:
        return f"FrozenMapping({dict(self._data)!r})"


def _freeze[K, V](value: Mapping[K, V]) -> FrozenMapping[K, V]:
    return FrozenMapping(value)


def _thaw(value: Mapping[Any, Any]) -> dict[Any, Any]:
    return dict(value)


def _reject_ambiguous_datetime(value: object) -> object:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and _ISO_DATETIME.match(value.strip()):
        return value.strip()
    raise ValueError(
        "timestamps must be datetime objects or ISO 8601 date-time strings with an offset; "
        "numeric epoch values are ambiguous"
    )


def _reject_ambiguous_duration(value: object) -> object:
    if isinstance(value, timedelta):
        return value
    if isinstance(value, str) and _ISO_DURATION.match(value.strip()):
        return value.strip()
    raise ValueError(
        "durations must be timedelta objects or ISO 8601 duration strings (e.g. PT1H5M)"
    )


def _reject_float_amount(value: object) -> object:
    if isinstance(value, bool | float):
        raise ValueError(
            "amount must be a Decimal, an integer or a decimal string, not a float or bool"
        )
    return value


def _canonical_amount(value: Decimal) -> Decimal:
    if value >= MAX_AMOUNT_EXCLUSIVE:
        raise ValueError(f"amount must be less than {MAX_AMOUNT_EXCLUSIVE}")
    quantized = value.quantize(_CENT)
    if quantized != value:
        raise ValueError("amount must have at most 2 decimal places")
    return quantized if quantized != 0 else Decimal("0.00")


def _reject_non_finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("metadata numbers must be finite")
    return value


def _reject_bool(value: object) -> object:
    if isinstance(value, bool):
        raise ValueError("booleans are not accepted here")
    return value


Slug = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]
PlaceName = Annotated[str, StringConstraints(min_length=1, max_length=64)]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
Timestamp = Annotated[AwareDatetime, BeforeValidator(_reject_ambiguous_datetime)]
Duration = Annotated[timedelta, BeforeValidator(_reject_ambiguous_duration)]
Amount = Annotated[
    Decimal,
    BeforeValidator(_reject_float_amount),
    Field(ge=0, allow_inf_nan=False),
    AfterValidator(_canonical_amount),
]
MetadataValue = (
    Annotated[str, StringConstraints(max_length=MAX_METADATA_TEXT_LENGTH)]
    | bool
    | int
    | Annotated[float, AfterValidator(_reject_non_finite)]
    | None
)


class TravelMode(StrEnum):
    """Mode of transport an option represents."""

    FLIGHT = "flight"
    RAIL = "rail"
    CAR = "car"
    CAB = "cab"
    BUS = "bus"


class DataOrigin(StrEnum):
    """Where an option's data came from."""

    SAMPLE = "sample"
    LIVE = "live"


class Freshness(StrEnum):
    """Derived freshness of an option's data at a given instant."""

    SAMPLE = "sample"
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


class AvailabilityStatus(StrEnum):
    """Seat or service availability as reported by the source."""

    AVAILABLE = "available"
    LIMITED = "limited"
    WAITLISTED = "waitlisted"
    SOLD_OUT = "sold_out"
    UNKNOWN = "unknown"


class UnavailableReason(StrEnum):
    """Why a measurable field has no value."""

    NOT_PROVIDED = "not_provided"
    PROVIDER_ERROR = "provider_error"
    NOT_APPLICABLE = "not_applicable"
    NOT_SUPPORTED = "not_supported"


OptionalField = Literal["departure_at", "arrival_at", "duration", "total_cost"]
_OPTIONAL_FIELDS: Final[tuple[OptionalField, ...]] = (
    "departure_at",
    "arrival_at",
    "duration",
    "total_cost",
)

UnavailableMap = Annotated[
    Mapping[OptionalField, UnavailableReason],
    AfterValidator(_freeze),
    PlainSerializer(_thaw, return_type=dict[OptionalField, UnavailableReason]),
]
MetadataMap = Annotated[
    Mapping[Slug, MetadataValue],
    Field(max_length=MAX_METADATA_ENTRIES),
    AfterValidator(_freeze),
    PlainSerializer(_thaw, return_type=dict[Slug, MetadataValue]),
]


class Money(BaseModel):
    """A non-negative monetary amount with an explicit currency code.

    ``amount`` is canonicalised to exactly two decimal places. ``currency`` is
    checked for ISO 4217 alphabetic-code *format* (three upper-case letters);
    membership in the ISO 4217 registry is not validated.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", str_strip_whitespace=True, revalidate_instances="always"
    )

    amount: Amount
    currency: CurrencyCode


class Provenance(BaseModel):
    """Source and timing of the data behind an option."""

    model_config = ConfigDict(
        frozen=True, extra="forbid", str_strip_whitespace=True, revalidate_instances="always"
    )

    origin: DataOrigin
    source: Slug
    retrieved_at: Timestamp
    expires_at: Timestamp | None = None

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.origin is DataOrigin.LIVE and self.source == "sample":
            raise ValueError("live data cannot name 'sample' as its source")
        if self.expires_at is not None and self.expires_at <= self.retrieved_at:
            raise ValueError("expires_at must be later than retrieved_at")
        return self

    def freshness(self, at: datetime) -> Freshness:
        """Classify the data's freshness at instant ``at``.

        Sample data is always ``SAMPLE``, so it can never be reported as fresh
        live data. Live data without an expiry is ``UNKNOWN``.

        Args:
            at: Timezone-aware instant to evaluate against.

        Returns:
            The derived freshness.

        Raises:
            ValueError: If ``at`` is naive.
        """
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("freshness requires a timezone-aware datetime")
        if self.origin is DataOrigin.SAMPLE:
            return Freshness.SAMPLE
        if self.expires_at is None:
            return Freshness.UNKNOWN
        return Freshness.FRESH if at < self.expires_at else Freshness.STALE


class TravelOption(BaseModel):
    """One candidate way to travel between two places.

    Measurable fields (``departure_at``, ``arrival_at``, ``duration``,
    ``total_cost``) are optional, but a missing value must be declared in
    ``unavailable`` with a reason. Nothing is silently absent.
    """

    model_config = ConfigDict(
        frozen=True, extra="forbid", str_strip_whitespace=True, revalidate_instances="always"
    )

    schema_version: Annotated[Literal[1], BeforeValidator(_reject_bool)] = SCHEMA_VERSION
    option_id: Annotated[str, StringConstraints(min_length=1, max_length=128)]
    mode: TravelMode
    origin: PlaceName
    destination: PlaceName
    operator: Annotated[str, StringConstraints(min_length=1, max_length=128)] | None = None
    departure_at: Timestamp | None = None
    arrival_at: Timestamp | None = None
    duration: Duration | None = None
    total_cost: Money | None = None
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    waitlist_position: Annotated[int, Field(ge=1, strict=True)] | None = None
    unavailable: UnavailableMap = Field(default_factory=FrozenMapping)
    provenance: Provenance
    provider_metadata: MetadataMap = Field(default_factory=FrozenMapping)

    @field_validator("duration")
    @classmethod
    def _check_duration(cls, value: timedelta | None) -> timedelta | None:
        if value is not None and not timedelta(0) < value <= MAX_DURATION:
            raise ValueError(f"duration must be positive and at most {MAX_DURATION}")
        return value

    @model_validator(mode="after")
    def _check_consistency(self) -> Self:
        if self.origin.casefold() == self.destination.casefold():
            raise ValueError("origin and destination must differ")

        for name in _OPTIONAL_FIELDS:
            missing = getattr(self, name) is None
            declared = name in self.unavailable
            if missing and not declared:
                raise ValueError(f"{name} is missing; declare it in 'unavailable' with a reason")
            if declared and not missing:
                raise ValueError(f"{name} has a value but is declared unavailable")

        if self.departure_at is not None and self.arrival_at is not None:
            elapsed = self.arrival_at - self.departure_at
            if elapsed <= timedelta(0):
                raise ValueError("arrival_at must be later than departure_at")
            if self.duration is not None and self.duration != elapsed:
                raise ValueError("duration must equal arrival_at - departure_at")

        is_waitlisted = self.availability is AvailabilityStatus.WAITLISTED
        if self.waitlist_position is not None and not is_waitlisted:
            raise ValueError("waitlist_position requires availability 'waitlisted'")
        return self

    @property
    def is_sample(self) -> bool:
        """Whether this option is built from sample (non-live) data."""
        return self.provenance.origin is DataOrigin.SAMPLE
