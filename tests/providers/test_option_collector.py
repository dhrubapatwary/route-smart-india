"""Tests for the concurrent option collector (Task 003)."""

from __future__ import annotations

import asyncio
import io
import logging
from collections.abc import Iterator, Sequence
from datetime import datetime, timedelta, timezone

import pytest

from routesmart.contracts import TravelMode, TravelOption
from routesmart.log import RedactingFormatter
from routesmart.providers import (
    INVALID_OUTPUT_ERROR,
    CollectionResult,
    OptionProvider,
    OutcomeStatus,
    SampleOptionProvider,
    TravelQuery,
    collect_options,
    sample_providers,
)

IST = timezone(timedelta(hours=5, minutes=30))
QUERY = TravelQuery(
    origin="BLR",
    destination="MAA",
    travel_date=datetime(2026, 11, 2, tzinfo=IST),
    current_date=datetime(2026, 10, 27, tzinfo=IST),
)
SENSITIVE_TEXT = "api_key=SHOULD-NOT-LEAK-123"


class FakeProvider:
    """Configurable provider double."""

    def __init__(
        self,
        name: str,
        mode: TravelMode = TravelMode.FLIGHT,
        *,
        result: object = (),
        error: BaseException | None = None,
        hang: bool = False,
    ) -> None:
        self._name = name
        self._mode = mode
        self._result = result
        self._error = error
        self._hang = hang
        self.calls = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def mode(self) -> TravelMode:
        return self._mode

    async def fetch_options(self, query: TravelQuery) -> Sequence[TravelOption]:
        self.calls += 1
        if self._hang:
            await asyncio.Event().wait()
        if self._error is not None:
            raise self._error
        return self._result  # type: ignore[return-value]


@pytest.fixture
def log_stream() -> Iterator[io.StringIO]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(RedactingFormatter())
    logger = logging.getLogger("routesmart.providers.collector")
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        yield stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)


@pytest.mark.asyncio
async def test_all_sample_providers_succeed() -> None:
    result = await collect_options(QUERY, sample_providers())
    assert [o.provider for o in result.outcomes] == [f"sample-{m.value}" for m in TravelMode]
    assert all(o.status is OutcomeStatus.SUCCESS for o in result.outcomes)
    assert all(o.error_type is None for o in result.outcomes)
    assert {o.mode for o in result.options} == set(TravelMode)
    assert all(o.is_sample for o in result.options)


@pytest.mark.asyncio
async def test_collection_is_deterministic() -> None:
    first = await collect_options(QUERY, sample_providers())
    second = await collect_options(QUERY, sample_providers())
    assert first == second
    assert [o.option_id for o in first.options] == [o.option_id for o in second.options]


@pytest.mark.asyncio
async def test_success_empty_error_and_timeout_are_distinct(log_stream: io.StringIO) -> None:
    rail = SampleOptionProvider(TravelMode.RAIL)
    providers: list[OptionProvider] = [
        rail,
        FakeProvider("empty"),
        FakeProvider("broken", error=RuntimeError(SENSITIVE_TEXT)),
        FakeProvider("slow", hang=True),
    ]
    result = await collect_options(QUERY, providers, provider_timeout=0.05)
    statuses = {o.provider: (o.status, o.error_type) for o in result.outcomes}
    assert statuses == {
        "sample-rail": (OutcomeStatus.SUCCESS, None),
        "empty": (OutcomeStatus.EMPTY, None),
        "broken": (OutcomeStatus.ERROR, "RuntimeError"),
        "slow": (OutcomeStatus.TIMEOUT, None),
    }
    # The other providers' failures do not lose the successful options.
    assert result.options == await rail.fetch_options(QUERY)
    logged = log_stream.getvalue()
    assert "provider broken failed: RuntimeError" in logged
    assert "provider slow timed out" in logged
    assert "provider empty returned no options" in logged
    assert "SHOULD-NOT-LEAK" not in logged
    assert "SHOULD-NOT-LEAK" not in repr(result)


@pytest.mark.asyncio
async def test_provider_raising_its_own_timeout_is_an_error_not_a_timeout() -> None:
    result = await collect_options(QUERY, [FakeProvider("own", error=TimeoutError())])
    assert result.outcomes[0].status is OutcomeStatus.ERROR
    assert result.outcomes[0].error_type == "TimeoutError"


@pytest.mark.asyncio
async def test_timeout_bounds_total_wait() -> None:
    loop = asyncio.get_running_loop()
    start = loop.time()
    result = await collect_options(
        QUERY, [FakeProvider(f"slow-{i}", hang=True) for i in range(3)], provider_timeout=0.05
    )
    assert loop.time() - start < 2
    assert {o.status for o in result.outcomes} == {OutcomeStatus.TIMEOUT}
    assert result.options == ()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "output",
    [
        None,
        "not options",
        b"bytes",
        42,
        {"option": 1},
        ["not an option"],
    ],
    ids=["none", "str", "bytes", "int", "dict", "list-of-str"],
)
async def test_malformed_output_is_an_error(output: object) -> None:
    result = await collect_options(QUERY, [FakeProvider("bad", result=output)])
    assert result.outcomes[0].status is OutcomeStatus.ERROR
    assert result.outcomes[0].error_type == INVALID_OUTPUT_ERROR


@pytest.mark.asyncio
async def test_option_of_the_wrong_mode_is_an_error() -> None:
    rail_options = await SampleOptionProvider(TravelMode.RAIL).fetch_options(QUERY)
    result = await collect_options(
        QUERY, [FakeProvider("liar", TravelMode.BUS, result=list(rail_options))]
    )
    assert result.outcomes[0].status is OutcomeStatus.ERROR
    assert result.outcomes[0].error_type == INVALID_OUTPUT_ERROR


@pytest.mark.asyncio
async def test_list_output_is_accepted_and_frozen() -> None:
    bus_options = await SampleOptionProvider(TravelMode.BUS).fetch_options(QUERY)
    result = await collect_options(
        QUERY, [FakeProvider("listy", TravelMode.BUS, result=list(bus_options))]
    )
    assert result.outcomes[0].status is OutcomeStatus.SUCCESS
    assert result.outcomes[0].options == bus_options
    assert isinstance(result.outcomes[0].options, tuple)


@pytest.mark.asyncio
async def test_concurrency_is_bounded() -> None:
    running = 0
    peak = 0

    class Counting(FakeProvider):
        async def fetch_options(self, query: TravelQuery) -> Sequence[TravelOption]:
            nonlocal running, peak
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.01)
            running -= 1
            return ()

    providers = [Counting(f"p{i}") for i in range(6)]
    result = await collect_options(QUERY, providers, max_concurrency=2)
    assert peak == 2
    assert len(result.outcomes) == 6


@pytest.mark.asyncio
async def test_providers_run_concurrently() -> None:
    gate = asyncio.Event()

    class Waiter(FakeProvider):
        async def fetch_options(self, query: TravelQuery) -> Sequence[TravelOption]:
            await gate.wait()
            return ()

    class Opener(FakeProvider):
        async def fetch_options(self, query: TravelQuery) -> Sequence[TravelOption]:
            gate.set()
            return ()

    result = await collect_options(QUERY, [Waiter("waiter"), Opener("opener")], provider_timeout=1)
    assert [o.status for o in result.outcomes] == [OutcomeStatus.EMPTY, OutcomeStatus.EMPTY]


@pytest.mark.asyncio
async def test_no_providers_gives_an_empty_result() -> None:
    assert await collect_options(QUERY, []) == CollectionResult(outcomes=())


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan"), True])
async def test_invalid_timeout_is_rejected(value: float) -> None:
    provider = FakeProvider("p")
    with pytest.raises(ValueError, match="provider_timeout"):
        await collect_options(QUERY, [provider], provider_timeout=value)
    assert provider.calls == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, -1, True])
async def test_invalid_concurrency_is_rejected(limit: int) -> None:
    with pytest.raises(ValueError, match="max_concurrency"):
        await collect_options(QUERY, [FakeProvider("p")], max_concurrency=limit)


@pytest.mark.asyncio
async def test_duplicate_provider_names_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        await collect_options(QUERY, [FakeProvider("dup"), FakeProvider("dup")])


@pytest.mark.asyncio
async def test_cancellation_is_not_swallowed() -> None:
    task = asyncio.create_task(collect_options(QUERY, [FakeProvider("slow", hang=True)]))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
