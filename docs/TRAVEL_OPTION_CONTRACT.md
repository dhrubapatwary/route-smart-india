# Travel-Option Contract (schema version 1)

- **Code:** `src/routesmart/contracts/travel_option.py`
- **Tests:** `tests/contracts/test_travel_option.py`
- **Status:** Minimal foundation created in Task 002. **Direction approved** by the owner on 2026-10-27 (D-IMPL-03). The **final schema remains a Phase 2 approval gate**; this approval does not cover the scoring formula or every field. ROADMAP Phase 2 must extend and approve it before live provider data is used.

## Purpose

Every travel mode maps its source data into one provider-neutral `TravelOption`:

- flight (`flight`)
- rail (`rail`)
- self-drive (`car`)
- cab (`cab`)
- bus (`bus`)

Scoring, the backend API and the PWA consume **only** this contract. Provider adapters own the mapping from provider formats, and nothing downstream sees a provider's raw response.

## Fields

| Field | Required | Type / rule | Owner |
|---|---|---|---|
| `schema_version` | defaulted | `1`. Any other value, including boolean `true`, is rejected. | contract |
| `option_id` | yes | 1–128 characters; unique within one result set (not enforced here) | adapter |
| `mode` | yes | `flight` \| `rail` \| `car` \| `cab` \| `bus` | adapter |
| `origin`, `destination` | yes | 1–64 characters, stripped. They must differ, compared case-insensitively. | adapter |
| `operator` | no | e.g. carrier name; `None` when not meaningful | adapter |
| `departure_at`, `arrival_at` | measurable* | **timezone-aware** datetimes. Input must be a `datetime` object or an ISO 8601 date-time string with an offset (see Time and units). Arrival must be after departure. | adapter |
| `duration` | measurable* | `timedelta` > 0 and ≤ 7 days. Input must be a `timedelta` or an ISO 8601 duration string. It must equal `arrival_at − departure_at` when both are present. | adapter |
| `total_cost` | measurable* | `Money` | adapter |
| `availability` | defaulted | `available` \| `limited` \| `waitlisted` \| `sold_out` \| `unknown` (default `unknown`) | adapter |
| `waitlist_position` | no | strict integer ≥ 1. Booleans, strings and floats are rejected. Only allowed when `availability = waitlisted`. | adapter |
| `unavailable` | defaulted | **immutable** mapping from a measurable field name to a reason: `not_provided` \| `provider_error` \| `not_applicable` \| `not_supported` | adapter |
| `provenance` | yes | `Provenance` (below) | adapter |
| `provider_metadata` | defaulted | **immutable** flat mapping of slug keys to scalar values: `str` (≤ 256 characters), `int`, finite `float`, `bool` or `None`. At most 32 entries. | adapter (opaque) |

\* **Measurable fields must be explained when missing.** If `departure_at`, `arrival_at`, `duration` or `total_cost` is `None`, it must appear in `unavailable` with a reason. A field that has a value must not appear there. This makes incomplete data explicit, so it is never silently absent. For example, a self-drive `car` option declares `departure_at` and `arrival_at` as `not_applicable`.

## Money and currency

`Money` has two fields:

- `amount`: a `Decimal` that is ≥ 0 and < 10¹² (`MAX_AMOUNT_EXCLUSIVE`).
  - **Canonical form:** it is quantised to exactly two decimal places, so `"4250.5"` becomes `4250.50`, `"1E+2"` becomes `100.00` and `"-0"` becomes `0.00`. It always serialises in JSON as a two-decimal string.
  - Input with more than two *significant* decimal places (`"1.001"`) is rejected.
  - **Accepted input:** a `Decimal`, an `int`, or a decimal string. JSON clients must send amounts as strings, as the contract itself serialises them, or as integers.
  - **Rejected input:** floats, including JSON fractional numbers, which are binary and ambiguous; booleans; NaN; and Infinity.
- `currency`: checked for ISO 4217 alphabetic-code **format** only (three upper-case letters). Membership in the ISO 4217 registry is **not** validated (`XYZ` is accepted). This is a deliberately narrower guarantee: the standard library ships no registry, and a hand-maintained list would go stale. Revisit at the Phase 2 schema gate if needed.

**Why the upper bound:** it is a technical sanity bound, not a business rule. It keeps values far below `Decimal`'s 28-digit context precision (quantising 10³⁰ would otherwise raise) and rejects obviously corrupt input. It sits several orders of magnitude above any plausible travel fare in any currency.

Amounts are never floats, which avoids binary rounding errors. INR is the expected pilot currency, but the contract does not assume it. Currency conversion is out of scope, and scoring must not compare amounts in different currencies.

## Time and units

- **Timestamp input:** `datetime` objects, or ISO 8601 date-time strings such as `2026-11-02T06:00:00+05:30` or `…Z`. A UTC offset is required, because naive values are rejected.
- **Rejected timestamp input:** numeric epoch values (int, float, numeric strings), booleans, `date` objects and date-only strings. Epoch values are ambiguous: seconds or milliseconds, and no offset.
- **Duration input:** `timedelta` objects or ISO 8601 duration strings (`PT1H5M`, `P1DT2H`).
- **Rejected duration input:** plain numbers ("seconds?"), `HH:MM:SS` strings and booleans.
- Surrounding whitespace is stripped from both.
- Timestamps keep the source's UTC offset (e.g. `+05:30`) and serialise as ISO 8601.
- Equal instants in different offsets compare equal.
- Durations serialise as ISO 8601 durations (e.g. `PT1H5M`).

## Provenance and freshness

`Provenance` has four fields:

- `origin`: `sample` or `live`.
- `source`: a lower-case slug such as `sample` or a provider id. Live data may not name `sample` as its source.
- `retrieved_at`: an aware timestamp. A timestamp in the future is **accepted by design**, so that validation stays deterministic and clock-independent. Adapters must stamp `retrieved_at` from the system clock themselves, and Phase 3 may add a clock-skew check at the adapter boundary.
- `expires_at`: optional and aware. It must be later than `retrieved_at`.

`Provenance.freshness(at)` derives the freshness at a given aware instant:

| Data | Result |
|---|---|
| `sample` data | Always `SAMPLE`, so sample data can never be presented as fresh or current. |
| `live` data without `expires_at` | `UNKNOWN` |
| `live` data before `expires_at` | `FRESH` |
| `live` data at or after `expires_at` | `STALE` |

`TravelOption.is_sample` is a convenience flag for the UI to label simulated data.

## Immutability, hashing and serialisation

- Validated `Money`, `Provenance` and `TravelOption` instances **cannot be changed through their public API or ordinary attribute access**:
  - Assigning to a field raises an error.
  - `unavailable` and `provider_metadata` are `FrozenMapping` instances, which have no `__setitem__`, `update`, `pop` or `clear`.
  - A `FrozenMapping` keeps its items in a read-only `MappingProxyType` over a private copy, and rejects attribute assignment and deletion. Even its private `_data` cannot be written through, so the metadata cap and the hash cannot be bypassed that way. This is covered by tests.
  - Validation copies its input, so later changes to the caller's dict do not leak in.
  - Nested values are immutable: enums, scalars, frozen models.
  - Deliberate interpreter-level tampering, such as `object.__setattr__` or the `gc` module, is out of scope, as for any Python object.
- **Nested instances are always revalidated** (`revalidate_instances="always"`). A `Money` or `Provenance` built with `model_construct()`, or an unchecked `TravelOption`, is fully revalidated when passed to `TravelOption.model_validate()`. Invalid nested values, such as a negative amount, a non-ISO currency, a naive timestamp, or `live` with source `sample`, are rejected. This is covered by tests.
- Validated instances are **hashable**. Equality and hashing are consistent, including after a JSON round trip. This is covered by tests.
- **Equality is type-aware and matches serialisation.**
  - Metadata values `1`, `True` and `1.0` (and `0`/`False`, `"1"`/`1`) are different values, because they serialise differently. Two options are equal exactly when their JSON is equal; tests check this across a value matrix.
  - A `FrozenMapping` equals a `dict` with the same keys, value types and values.
- `model_dump()` and `model_dump_json()` emit plain `dict`/JSON objects.
- The JSON schema in both validation and serialisation modes keeps the key and value constraints. `maxProperties` appears in the validation schema.
- Pickle, `copy.deepcopy` and `model_copy(deep=True)` work.
- **Remaining validation bypass (documented Pydantic behaviour):** calling `model_construct()` or `model_copy(update=...)` *directly* produces an unvalidated object. Never use them to build options from provider or user data. Passing such an object through `model_validate()` revalidates it (see above).

## Provider-specific metadata

`provider_metadata` holds provider extras, such as a fare class or RAC details, for display and debugging. **Scoring and API logic must not depend on it.** If a value becomes necessary for scoring, promote it to a typed common field in a new schema version.

## Deliberately deferred (Phase 2+)

These are not part of schema version 1:

- cost breakdown (fare, tolls, fuel, EV charging)
- risk inputs
- transfers or multi-leg journeys
- place-code typing (IATA, station code, city)
- a backend API envelope
- JSON-schema publication
- cross-currency handling
