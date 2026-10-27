"""Travel-option providers and the concurrent collector.

Task 003 ships deterministic sample providers only; no live provider exists.
"""

from routesmart.providers.base import OptionProvider
from routesmart.providers.collector import (
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_PROVIDER_TIMEOUT_SECONDS,
    INVALID_OUTPUT_ERROR,
    CollectionResult,
    OutcomeStatus,
    ProviderOutcome,
    collect_options,
)
from routesmart.providers.query import SUPPORTED_ROUTES, TravelQuery
from routesmart.providers.sample import (
    SAMPLE_FIXTURE_VERSION,
    SAMPLE_FIXTURES,
    SAMPLE_RETRIEVED_AT,
    SAMPLE_SOURCE,
    SampleFixture,
    SampleOptionProvider,
    build_sample_option,
    sample_providers,
)

__all__ = [
    "DEFAULT_MAX_CONCURRENCY",
    "DEFAULT_PROVIDER_TIMEOUT_SECONDS",
    "INVALID_OUTPUT_ERROR",
    "SAMPLE_FIXTURES",
    "SAMPLE_FIXTURE_VERSION",
    "SAMPLE_RETRIEVED_AT",
    "SAMPLE_SOURCE",
    "SUPPORTED_ROUTES",
    "CollectionResult",
    "OptionProvider",
    "OutcomeStatus",
    "ProviderOutcome",
    "SampleFixture",
    "SampleOptionProvider",
    "TravelQuery",
    "build_sample_option",
    "collect_options",
    "sample_providers",
]
