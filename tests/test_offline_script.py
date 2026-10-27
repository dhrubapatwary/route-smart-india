"""Behaviour of scripts/test-offline.sh, driven with stub ``unshare``/``sudo`` binaries.

No real namespace, sudo or network is used: the script runs with a PATH that holds
only stubs plus ``dirname`` and ``id``. The stubs record their arguments.
"""

from __future__ import annotations

import errno
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "test-offline.sh"
BASH = shutil.which("bash") or "/bin/bash"

_STUB = """#!{bash}
args="$*"; printf '%s\\n' "${{args//$'\\n'/ }}" >> "$STUB_LOG"  # bash builtins only
if [ "$*" = "{probe_args}" ]; then exit "${{{probe_exit_var}:-1}}"; fi
exit 0
"""

pytestmark = pytest.mark.usefixtures("allow_subprocesses")


def _stub_dir(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("dirname", "id"):
        real = shutil.which(tool)
        assert real is not None
        (bin_dir / tool).symlink_to(real)
    stubs = {
        "unshare": ("--user --map-current-user --net true", "STUB_UNSHARE_PROBE_EXIT"),
        "sudo": ("-n unshare --net true", "STUB_SUDO_PROBE_EXIT"),
    }
    for name, (probe_args, exit_var) in stubs.items():
        stub = bin_dir / name
        stub.write_text(
            _STUB.format(bash=BASH, probe_args=probe_args, probe_exit_var=exit_var),
            encoding="utf-8",
        )
        stub.chmod(0o755)
    return bin_dir


def _run(tmp_path: Path, **env: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    log = tmp_path / "calls.log"
    environ = {
        "PATH": str(_stub_dir(tmp_path)),
        "HOME": str(tmp_path),
        "PYTHON": sys.executable,
        "STUB_LOG": str(log),
        **env,
    }
    result = subprocess.run(  # noqa: S603 (fixed argv; stubs only)
        [BASH, str(SCRIPT), "-q"],
        env=environ,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    calls = [line.rstrip() for line in lines]  # one call per line (newlines in args flattened)
    return result, calls


def _sudo_calls(calls: list[str]) -> list[str]:
    return [c for c in calls if c.startswith("-n unshare")]


def test_unprivileged_path_maps_current_user_not_root(tmp_path: Path) -> None:
    result, calls = _run(tmp_path, STUB_UNSHARE_PROBE_EXIT="0")
    assert result.returncode == 0
    assert "uid " + str(os.getuid()) + " mapped to itself; no root" in result.stderr
    final = calls[-1]
    assert final.startswith(f"--user --map-current-user --net -- {sys.executable} -I -c")
    assert "--map-root-user" not in "\n".join(calls)
    assert _sudo_calls(calls) == []


@pytest.mark.parametrize("github_actions", [None, "true"])
def test_sudo_fallback_is_off_by_default(tmp_path: Path, github_actions: str | None) -> None:
    env = {"GITHUB_ACTIONS": github_actions} if github_actions else {}
    result, calls = _run(tmp_path, **env)
    assert result.returncode == 2
    assert "sudo fallback is disabled" in result.stderr
    assert "Refusing to run tests without OS-level isolation" in result.stderr
    assert _sudo_calls(calls) == []


@pytest.mark.parametrize("github_actions", [None, "", "false", "1", "TRUE", "yes"])
def test_opt_in_cannot_enable_sudo_outside_github_actions(
    tmp_path: Path, github_actions: str | None
) -> None:
    env = {"ROUTESMART_OFFLINE_ALLOW_SUDO": "1", "STUB_SUDO_PROBE_EXIT": "0"}
    if github_actions is not None:
        env["GITHUB_ACTIONS"] = github_actions
    result, calls = _run(tmp_path, **env)
    assert result.returncode == 2
    assert "allowed only on GitHub Actions" in result.stderr
    assert _sudo_calls(calls) == []


@pytest.mark.parametrize("opt_in", ["0", "", "true", "yes"])
def test_only_exact_opt_in_value_counts(tmp_path: Path, opt_in: str) -> None:
    result, calls = _run(
        tmp_path,
        ROUTESMART_OFFLINE_ALLOW_SUDO=opt_in,
        GITHUB_ACTIONS="true",
        STUB_SUDO_PROBE_EXIT="0",
    )
    assert result.returncode == 2
    assert _sudo_calls(calls) == []


def test_ci_path_fails_closed_when_namespace_cannot_be_created(tmp_path: Path) -> None:
    result, calls = _run(
        tmp_path,
        ROUTESMART_OFFLINE_ALLOW_SUDO="1",
        GITHUB_ACTIONS="true",
        STUB_SUDO_PROBE_EXIT="1",
    )
    assert result.returncode == 2
    assert "sudo fallback is enabled but 'sudo -n unshare --net' failed" in result.stderr
    assert _sudo_calls(calls) == ["-n unshare --net true"]  # probe only; tests never started


def test_ci_path_drops_to_the_invoking_user_before_python(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("must run as a non-root user to check the privilege drop")
    result, calls = _run(
        tmp_path,
        ROUTESMART_OFFLINE_ALLOW_SUDO="1",
        GITHUB_ACTIONS="true",
        STUB_SUDO_PROBE_EXIT="0",
    )
    assert result.returncode == 0
    assert "GitHub Actions opt-in" in result.stderr
    final = _sudo_calls(calls)[-1]
    expected = (
        f"-n unshare --net -- setpriv --reuid={os.getuid()} --regid={os.getgid()} "
        f"--init-groups -- {sys.executable} -I -c"
    )
    assert final.startswith(expected)
    match = re.search(r"--reuid=(\d+)", final)
    assert match is not None
    assert int(match.group(1)) != 0


def test_missing_python_fails_with_a_clear_diagnostic(tmp_path: Path) -> None:
    result, calls = _run(tmp_path, PYTHON=str(tmp_path / "no-such-python"))
    assert result.returncode == 2
    assert "Python interpreter not found" in result.stderr
    assert calls == []


def _probe_source() -> str:
    text = SCRIPT.read_text(encoding="utf-8")
    match = re.search(r"^probe_then_pytest='\n(.*?)^'$", text, re.MULTILINE | re.DOTALL)
    assert match is not None
    return match.group(1)


def test_probe_refuses_to_run_as_root(tmp_path: Path) -> None:
    code = "import os\nos.geteuid = lambda: 0\n" + _probe_source()
    result = subprocess.run(  # noqa: S603 (fixed argv)
        [sys.executable, "-I", "-c", code, "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "refusing to run tests as root" in result.stderr
    assert "exec pytest" not in result.stderr


# --- Probe outcomes (deterministic fakes; no real sockets, no network) -----------------
#
# The real probe source runs in a child interpreter with ``_socket.socket``,
# ``_socket.if_nameindex``, ``os.geteuid`` and ``os.execv`` replaced. Each fake connect
# returns or raises exactly what a case specifies. The fake ``execv`` only prints a
# marker, so "pytest would have started" is observable without starting anything.

_EXEC_MARKER = "EXEC-PYTEST-REACHED"

_PROBE_HARNESS = """
import _socket, os
OUTCOMES = {outcomes!r}  # address family -> ("ok",) | ("errno", n) | ("timeout",)
CONNECTS = []
_socket.if_nameindex = lambda: [(1, "lo")]
os.geteuid = lambda: 1000
class FakeSocket:
    def __init__(self, family, kind):
        self.family = family
    def settimeout(self, seconds):
        pass
    def close(self):
        pass
    def connect(self, address):
        CONNECTS.append(address[0])
        outcome = OUTCOMES[self.family]
        if outcome[0] == "errno":
            raise OSError(outcome[1], os.strerror(outcome[1]))
        if outcome[0] == "timeout":
            raise TimeoutError("timed out")
_socket.socket = FakeSocket
def fake_execv(path, argv):
    print("{marker}", CONNECTS, flush=True)
os.execv = fake_execv
"""

_OK = ("ok",)
_TIMEOUT = ("timeout",)


def _errno(code: int) -> tuple[str, int]:
    return ("errno", code)


def _run_probe(
    tmp_path: Path, ipv4: tuple[object, ...], ipv6: tuple[object, ...]
) -> subprocess.CompletedProcess[str]:
    outcomes = {int(socket.AF_INET): ipv4, int(socket.AF_INET6): ipv6}
    harness = _PROBE_HARNESS.format(outcomes=outcomes, marker=_EXEC_MARKER)
    return subprocess.run(  # noqa: S603 (fixed argv; fakes only)
        [sys.executable, "-I", "-c", harness + _probe_source(), "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=tmp_path,
    )


@pytest.mark.parametrize(
    ("ipv4", "ipv6"),
    [
        (_errno(errno.ENETUNREACH), _errno(errno.ENETUNREACH)),
        (_errno(errno.ENETUNREACH), _errno(errno.EADDRNOTAVAIL)),
    ],
    ids=["v6-enetunreach", "v6-eaddrnotavail"],
)
def test_probe_accepts_only_the_expected_unreachable_outcomes(
    tmp_path: Path, ipv4: tuple[object, ...], ipv6: tuple[object, ...]
) -> None:
    # Positive control: proves the harness reaches exec, so the fail-closed cases below
    # are not passing vacuously.
    result = _run_probe(tmp_path, ipv4, ipv6)
    assert result.returncode == 0, result.stderr
    assert _EXEC_MARKER in result.stdout
    assert "['192.0.2.1', '2001:db8::1']" in result.stdout  # both families were probed
    assert "namespace verified" in result.stderr


@pytest.mark.parametrize(
    ("ipv4", "expected_message"),
    [
        (_TIMEOUT, "unexpected error for 192.0.2.1"),
        (_errno(errno.ETIMEDOUT), "unexpected error for 192.0.2.1"),
        (_errno(errno.EHOSTUNREACH), "unexpected error for 192.0.2.1"),
        (_errno(errno.ECONNREFUSED), "unexpected error for 192.0.2.1"),
        (_errno(errno.EADDRNOTAVAIL), "unexpected error for 192.0.2.1"),  # accepted for IPv6 only
        (_errno(errno.EACCES), "unexpected error for 192.0.2.1"),
        (_errno(errno.EPERM), "unexpected error for 192.0.2.1"),
        (_OK, "192.0.2.1 is reachable inside the namespace"),
    ],
    ids=[
        "timeout-no-errno",
        "etimedout",
        "ehostunreach",
        "econnrefused",
        "eaddrnotavail-v4",
        "eacces",
        "eperm",
        "connected",
    ],
)
def test_unexpected_ipv4_outcomes_fail_closed_before_pytest(
    tmp_path: Path, ipv4: tuple[object, ...], expected_message: str
) -> None:
    result = _run_probe(tmp_path, ipv4, _errno(errno.ENETUNREACH))
    assert result.returncode == 1
    assert expected_message in result.stderr
    assert _EXEC_MARKER not in result.stdout
    assert "namespace verified" not in result.stderr


@pytest.mark.parametrize(
    ("ipv6", "expected_message"),
    [
        (_TIMEOUT, "unexpected error for 2001:db8::1"),
        (_errno(errno.ETIMEDOUT), "unexpected error for 2001:db8::1"),
        (_errno(errno.EHOSTUNREACH), "unexpected error for 2001:db8::1"),
        (_errno(errno.ECONNREFUSED), "unexpected error for 2001:db8::1"),
        (_errno(errno.EACCES), "unexpected error for 2001:db8::1"),
        (_OK, "2001:db8::1 is reachable inside the namespace"),
    ],
    ids=["timeout-no-errno", "etimedout", "ehostunreach", "econnrefused", "eacces", "connected"],
)
def test_unexpected_ipv6_outcomes_fail_closed_before_pytest(
    tmp_path: Path, ipv6: tuple[object, ...], expected_message: str
) -> None:
    result = _run_probe(tmp_path, _errno(errno.ENETUNREACH), ipv6)
    assert result.returncode == 1
    assert expected_message in result.stderr
    assert _EXEC_MARKER not in result.stdout
    assert "namespace verified" not in result.stderr


def test_probe_rejects_extra_interfaces_before_any_connect(tmp_path: Path) -> None:
    harness_override = "import _socket\n_socket.if_nameindex = lambda: [(1, 'lo'), (2, 'eth0')]\n"
    result = subprocess.run(  # noqa: S603 (fixed argv; fakes only)
        [
            sys.executable,
            "-I",
            "-c",
            _PROBE_HARNESS.format(outcomes={0: _OK}, marker=_EXEC_MARKER)
            + harness_override
            + _probe_source(),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 1
    assert "unexpected interfaces in namespace: ['eth0', 'lo']" in result.stderr
    assert _EXEC_MARKER not in result.stdout
