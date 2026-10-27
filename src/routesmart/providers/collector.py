"""Run option providers concurrently and report each provider's outcome.

Each provider runs under its own timeout, with bounded concurrency. A provider
that raises, times out, returns nothing or returns malformed output gets its own
outcome; the other providers' options are kept. Returned options are
revalidated against the ``TravelOption`` contract. Only the exception *type* is
recorded and logged, never its message, so provider responses or secrets
embedded in error text cannot leak into outcomes or logs.
"""

from __future__ import annotations

import asyncio
import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from pydantic import ValidationError

from routesmart.contracts import TravelOption
from routesmart.log import get_logger
from routesmart.providers.base import OptionProvider
from routesmart.providers.query import TravelQuery

DEFAULT_PROVIDER_TIMEOUT_SECONDS: Final = 5.0
DEFAULT_MAX_CONCURRENCY: Final = 8
INVALID_OUTPUT_ERROR: Final = "InvalidProviderOutput"

_log = get_logger("providers.collector")


class OutcomeStatus(StrEnum):
    """How one provider's fetch ended."""

    SUCCESS = "success"
    EMPTY = "empty"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ProviderOutcome:
    """Result of one provider's fetch.

    ``options`` is non-empty only for ``SUCCESS``. ``error_type`` names the
    exception class (or ``INVALID_OUTPUT_ERROR``) for ``ERROR`` and is ``None``
    otherwise.
    """

    provider: str
    status: OutcomeStatus
    options: tuple[TravelOption, ...] = ()
    error_type: str | None = None


@dataclass(frozen=True)
class CollectionResult:
    """Per-provider outcomes, in the order the providers were given."""

    outcomes: tuple[ProviderOutcome, ...]

    @property
    def options(self) -> tuple[TravelOption, ...]:
        """All successful options, in provider order, then each provider's own order."""
        return tuple(option for outcome in self.outcomes for option in outcome.options)


def _check_output(provider: OptionProvider, output: object) -> tuple[TravelOption, ...] | None:
    """Return revalidated options if ``output`` is valid for ``provider``, else ``None``.

    Every item must be a ``TravelOption`` of the provider's mode. Each one is
    revalidated against the contract, because instances built with
    ``model_construct()`` skip validation; the revalidated copies are returned.
    """
    if not isinstance(output, Sequence) or isinstance(output, str | bytes):
        return None
    options: list[TravelOption] = []
    for item in output:
        if not isinstance(item, TravelOption):
            return None
        try:
            option = TravelOption.model_validate(item)
        except ValidationError:
            return None
        if option.mode is not provider.mode:
            return None
        options.append(option)
    return tuple(options)


async def _run_one(
    provider: OptionProvider,
    query: TravelQuery,
    provider_timeout: float,
    semaphore: asyncio.Semaphore,
) -> ProviderOutcome:
    name = provider.name
    async with semaphore:
        try:
            async with asyncio.timeout(provider_timeout) as scope:
                output: object = await provider.fetch_options(query)
        except TimeoutError as exc:
            if not scope.expired():
                return _error(name, type(exc).__name__)
            _log.warning("provider %s timed out after %.3fs", name, provider_timeout)
            return ProviderOutcome(provider=name, status=OutcomeStatus.TIMEOUT)
        except Exception as exc:  # noqa: BLE001 (isolated per provider; recorded as an outcome)
            return _error(name, type(exc).__name__)
    try:
        options = _check_output(provider, output)
    except Exception:  # noqa: BLE001 (malformed output must not escape provider isolation)
        options = None
    if options is None:
        return _error(name, INVALID_OUTPUT_ERROR)
    if not options:
        _log.info("provider %s returned no options", name)
        return ProviderOutcome(provider=name, status=OutcomeStatus.EMPTY)
    _log.debug("provider %s returned %d options", name, len(options))
    return ProviderOutcome(provider=name, status=OutcomeStatus.SUCCESS, options=options)


def _error(name: str, error_type: str) -> ProviderOutcome:
    _log.warning("provider %s failed: %s", name, error_type)
    return ProviderOutcome(provider=name, status=OutcomeStatus.ERROR, error_type=error_type)


async def collect_options(
    query: TravelQuery,
    providers: Sequence[OptionProvider],
    *,
    provider_timeout: float = DEFAULT_PROVIDER_TIMEOUT_SECONDS,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
) -> CollectionResult:
    """Fetch options from ``providers`` concurrently.

    Args:
        query: The validated query passed to every provider.
        providers: Providers to run; names must be unique.
        provider_timeout: Per-provider timeout in seconds (finite, > 0). Waiting for a
            concurrency slot does not count against it.
        max_concurrency: Maximum number of providers running at once (>= 1).

    Returns:
        One outcome per provider, in the given order.

    Raises:
        ValueError: If ``provider_timeout`` or ``max_concurrency`` is invalid, or provider
            names repeat.
    """
    if isinstance(provider_timeout, bool) or not (
        math.isfinite(provider_timeout) and provider_timeout > 0
    ):
        raise ValueError("provider_timeout must be a finite number of seconds greater than 0")
    if (
        isinstance(max_concurrency, bool)
        or not isinstance(max_concurrency, int)
        or max_concurrency < 1
    ):
        raise ValueError("max_concurrency must be an integer >= 1")
    names = [provider.name for provider in providers]
    if len(set(names)) != len(names):
        raise ValueError("provider names must be unique")
    semaphore = asyncio.Semaphore(max_concurrency)
    outcomes = await asyncio.gather(
        *(_run_one(provider, query, provider_timeout, semaphore) for provider in providers)
    )
    return CollectionResult(outcomes=tuple(outcomes))
