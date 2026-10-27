"""In-process network and subprocess guard for the test suite.

The guard is installed for the whole pytest session (collection and every
fixture scope) and lifted only for tests marked ``live`` when live tests are
explicitly enabled. It replaces Python-level entry points:

* TCP/UDP: ``socket.socket.connect``, ``connect_ex``, ``sendto`` and
  ``sendmsg`` (when given an address), plus ``socket.create_connection``.
* DNS: ``socket.getaddrinfo``, ``getnameinfo``, ``gethostbyname``,
  ``gethostbyname_ex`` and ``gethostbyaddr``.
* Child processes: ``subprocess.Popen`` (so ``subprocess.run`` and asyncio
  subprocesses too), ``os.system``, ``os.posix_spawn`` and ``os.posix_spawnp``.

It is **not a sandbox**. Code that uses the C-level ``_socket.socket`` type
directly, ``os.fork``/``os.exec*``, or native extensions with their own
networking is not intercepted. ``scripts/test-offline.sh`` runs the suite in an
OS-level network namespace to cover those paths (see docs/TESTING.md).
"""

from __future__ import annotations

import os
import socket
import subprocess
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any, Final, NoReturn

LIVE_ENV_VAR: Final = "ROUTESMART_ALLOW_LIVE"
_SUBPROCESS_TARGETS: Final = frozenset({"__init__", "system", "posix_spawn", "posix_spawnp"})


class NetworkBlockedError(RuntimeError):
    """Raised when guarded code attempts network or DNS access."""


class SubprocessBlockedError(RuntimeError):
    """Raised when guarded code attempts to start a child process."""


def _block_network(*_args: Any, **_kwargs: Any) -> NoReturn:
    raise NetworkBlockedError("network access is blocked in tests; see docs/TESTING.md")


def _block_subprocess(*_args: Any, **_kwargs: Any) -> NoReturn:
    raise SubprocessBlockedError("child processes are blocked in tests; see docs/TESTING.md")


def live_tests_allowed(environ: Mapping[str, str]) -> bool:
    """Return whether live tests are explicitly enabled (``ROUTESMART_ALLOW_LIVE=1``).

    Args:
        environ: Environment mapping to inspect.

    Returns:
        ``True`` only when the variable is exactly ``"1"``.
    """
    return environ.get(LIVE_ENV_VAR) == "1"


class NetworkGuard:
    """Installs and removes the patches. Nested guards restore in LIFO order."""

    def __init__(self) -> None:
        """Prepare a guard; nothing is patched until ``install()``."""
        original_sendmsg = socket.socket.sendmsg

        def guarded_sendmsg(sock: socket.socket, *args: Any, **kwargs: Any) -> int:
            if len(args) >= 4 or "address" in kwargs:
                _block_network()
            return original_sendmsg(sock, *args, **kwargs)

        self._replacements: tuple[tuple[object, str, object], ...] = (
            (socket.socket, "connect", _block_network),
            (socket.socket, "connect_ex", _block_network),
            (socket.socket, "sendto", _block_network),
            (socket.socket, "sendmsg", guarded_sendmsg),
            (socket, "create_connection", _block_network),
            (socket, "getaddrinfo", _block_network),
            (socket, "getnameinfo", _block_network),
            (socket, "gethostbyname", _block_network),
            (socket, "gethostbyname_ex", _block_network),
            (socket, "gethostbyaddr", _block_network),
            (subprocess.Popen, "__init__", _block_subprocess),
            (os, "system", _block_subprocess),
            (os, "posix_spawn", _block_subprocess),
            (os, "posix_spawnp", _block_subprocess),
        )
        self._saved: list[tuple[object, str, object]] = []

    @property
    def installed(self) -> bool:
        """Whether the patches are currently applied by this guard."""
        return bool(self._saved)

    def install(self) -> None:
        """Apply all patches. Calling it twice is a no-op."""
        if self._saved:
            return
        for target, name, replacement in self._replacements:
            self._saved.append((target, name, getattr(target, name)))
            setattr(target, name, replacement)

    def uninstall(self) -> None:
        """Restore the attributes saved by ``install()``."""
        while self._saved:
            target, name, original = self._saved.pop()
            setattr(target, name, original)

    @contextmanager
    def subprocesses_allowed(self) -> Iterator[None]:
        """Temporarily lift ONLY the child-process block; network and DNS stay blocked.

        For tests that must run local, non-networking helper processes (e.g. the
        shell-script tests with stub binaries). Child processes are outside any
        in-process guard by nature; OS-level isolation covers them in CI.
        """
        if not self._saved:  # guard not installed: nothing to lift
            yield
            return
        lifted = [
            (target, name, replacement, original)
            for (target, name, original), (_, _, replacement) in zip(
                self._saved, self._replacements, strict=True
            )
            if name in _SUBPROCESS_TARGETS
        ]
        for target, name, _replacement, original in lifted:
            setattr(target, name, original)
        try:
            yield
        finally:
            for target, name, replacement, _original in lifted:
                setattr(target, name, replacement)
