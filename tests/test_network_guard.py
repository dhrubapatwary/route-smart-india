"""The session-wide guard must stop network, DNS and child-process access."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from testsupport.network_guard import (
    LIVE_ENV_VAR,
    NetworkBlockedError,
    NetworkGuard,
    SubprocessBlockedError,
    live_tests_allowed,
)

TEST_NET = ("192.0.2.1", 443)  # RFC 5737 documentation address; never routed


def test_create_connection_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        socket.create_connection(TEST_NET, timeout=0.1)


@pytest.mark.parametrize("method", ["connect", "connect_ex"])
def test_socket_connect_is_blocked(method: str) -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock,
        pytest.raises(NetworkBlockedError),
    ):
        getattr(sock, method)(TEST_NET)


@pytest.mark.asyncio
async def test_asyncio_open_connection_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        await asyncio.wait_for(asyncio.open_connection(*TEST_NET), timeout=1)


@pytest.mark.parametrize(
    ("function", "args"),
    [
        ("getaddrinfo", ("localhost", 80)),
        ("gethostbyname", ("localhost",)),
        ("gethostbyname_ex", ("localhost",)),
        ("gethostbyaddr", ("127.0.0.1",)),
        ("getnameinfo", (("127.0.0.1", 80), 0)),
    ],
)
def test_dns_lookups_are_blocked(function: str, args: tuple[object, ...]) -> None:
    with pytest.raises(NetworkBlockedError):
        getattr(socket, function)(*args)


@pytest.mark.asyncio
async def test_asyncio_dns_lookup_is_blocked() -> None:
    with pytest.raises(NetworkBlockedError):
        await asyncio.get_running_loop().getaddrinfo("example.com", 443)


def test_udp_sendto_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(NetworkBlockedError),
    ):
        sock.sendto(b"x", TEST_NET)


def test_udp_sendmsg_with_address_is_blocked() -> None:
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(NetworkBlockedError),
    ):
        sock.sendmsg([b"x"], [], 0, TEST_NET)


def test_local_socketpair_still_works() -> None:
    left, right = socket.socketpair()
    with left, right:
        left.sendall(b"ping")
        assert right.recv(4) == b"ping"


def test_subprocess_run_is_blocked() -> None:
    with pytest.raises(SubprocessBlockedError):
        subprocess.run([sys.executable, "--version"], check=True)


def test_os_system_is_blocked() -> None:
    with pytest.raises(SubprocessBlockedError):
        os.system("true")  # noqa: S605, S607


@pytest.mark.asyncio
async def test_asyncio_subprocess_is_blocked() -> None:
    with pytest.raises(SubprocessBlockedError):
        await asyncio.create_subprocess_exec(sys.executable, "--version")


@pytest.fixture(scope="module")
def module_scoped_connection_error() -> type[BaseException] | None:
    try:
        socket.create_connection(TEST_NET, timeout=0.1)
    except (NetworkBlockedError, OSError) as exc:
        return type(exc)
    return None


def test_module_scoped_fixtures_are_guarded(
    module_scoped_connection_error: type[BaseException] | None,
) -> None:
    assert module_scoped_connection_error is NetworkBlockedError


def test_nested_guard_restores_previous_state() -> None:
    session_patched = socket.getaddrinfo
    guard = NetworkGuard()
    try:
        guard.install()
        guard.install()  # idempotent
        installed_after_install = guard.installed
    finally:
        guard.uninstall()  # never leave extra patches behind, even if an assertion fails
    installed_after_uninstall = guard.installed
    assert (installed_after_install, installed_after_uninstall) == (True, False)
    assert socket.getaddrinfo is session_patched  # session guard still active


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({LIVE_ENV_VAR: "1"}, True),
        ({}, False),
        ({LIVE_ENV_VAR: ""}, False),
        ({LIVE_ENV_VAR: "0"}, False),
        ({LIVE_ENV_VAR: "true"}, False),
        ({LIVE_ENV_VAR: " 1"}, False),
    ],
)
def test_live_tests_require_explicit_opt_in(environ: dict[str, str], expected: bool) -> None:
    assert live_tests_allowed(environ) is expected


def test_live_tests_are_deselected_by_default() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    addopts = tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"]["pytest"]["ini_options"][
        "addopts"
    ]
    assert addopts[addopts.index("-m") + 1] == "not live"


@pytest.mark.live
def test_live_gate_lifts_guard_only_with_opt_in() -> None:
    # Runs only with `-m live` and ROUTESMART_ALLOW_LIVE=1; makes no network call.
    assert live_tests_allowed(os.environ)
    assert socket.create_connection.__name__ == "create_connection"  # original, not the blocker
