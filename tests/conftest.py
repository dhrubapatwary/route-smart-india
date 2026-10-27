"""Shared test configuration.

Installs the network/subprocess guard for the whole session, so collection and
fixtures of every scope run guarded (DECISIONS.md D-IMPL-05). Tests marked
``live`` are deselected by default (``-m "not live"`` in pyproject addopts) and,
even when selected, are skipped unless ``ROUTESMART_ALLOW_LIVE=1`` is set. Only
then is the guard lifted, and only for that test.
"""

from __future__ import annotations

import os
from collections.abc import Generator, Iterator

import pytest

from testsupport.network_guard import NetworkGuard, live_tests_allowed

_GUARD_KEY = pytest.StashKey[NetworkGuard]()


def pytest_configure(config: pytest.Config) -> None:
    guard = NetworkGuard()
    guard.install()
    config.stash[_GUARD_KEY] = guard


def pytest_unconfigure(config: pytest.Config) -> None:
    guard = config.stash.get(_GUARD_KEY, None)
    if guard is not None:
        guard.uninstall()


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if live_tests_allowed(os.environ):
        return
    skip_live = pytest.mark.skip(
        reason="live tests need ROUTESMART_ALLOW_LIVE=1 and owner approval"
    )
    for item in items:
        if item.get_closest_marker("live") is not None:
            item.add_marker(skip_live)


@pytest.fixture
def allow_subprocesses(request: pytest.FixtureRequest) -> Iterator[None]:
    """Lift only the child-process block for one test (network/DNS stay blocked)."""
    with request.config.stash[_GUARD_KEY].subprocesses_allowed():
        yield


@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(
    item: pytest.Item, nextitem: pytest.Item | None
) -> Generator[None, object, object]:
    guard = item.config.stash[_GUARD_KEY]
    lift = item.get_closest_marker("live") is not None and live_tests_allowed(os.environ)
    if lift:
        guard.uninstall()
    try:
        return (yield)
    finally:
        if lift:
            guard.install()
