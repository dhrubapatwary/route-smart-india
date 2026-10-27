#!/usr/bin/env bash
# Run the test suite inside an OS-level network namespace that has no network.
#
# Complements the in-process guard in tests/testsupport/network_guard.py, which
# cannot intercept the C-level _socket type, os.fork/exec or native extensions.
#
# Fails closed: if no namespace can be created, or the namespace is not proven
# to be empty, the script exits non-zero before any test runs. The proof and
# pytest run in the SAME process and namespace: the probe exec()s pytest.
#
# Isolation paths, in order:
#   1. Unprivileged: unshare --user --map-current-user --net (no root anywhere;
#      needs util-linux >= 2.38 and unprivileged user namespaces).
#   2. GitHub Actions only: requires BOTH ROUTESMART_OFFLINE_ALLOW_SUDO=1 and
#      GITHUB_ACTIONS=true (owner decision R3, 2026-10-27). sudo -n unshare --net,
#      then setpriv drops back to the invoking uid/gid before Python starts.
#      For runners that restrict unprivileged user namespaces (e.g. Ubuntu
#      24.04's AppArmor default). See docs/TESTING.md for the trade-off.
#
# In every path the tests must run as a non-root user: the probe refuses
# euid 0. It exports ROUTESMART_OFFLINE_NETNS so the suite can assert that it
# runs in the verified namespace (tests/test_offline_isolation.py).
#
# Usage: [PYTHON=/path/to/python] scripts/test-offline.sh [pytest args...]
set -euo pipefail

cd "$(dirname "$0")/.."

requested_python="${PYTHON:-python}"
if ! python_bin="$(command -v -- "$requested_python")"; then
  echo "test-offline: Python interpreter not found: '${requested_python}' (set PYTHON=/path/to/python)" >&2
  exit 2
fi
case "$python_bin" in
  /*) ;;
  *) python_bin="$PWD/$python_bin" ;;
esac

if unshare --user --map-current-user --net true 2>/dev/null; then
  mode="unprivileged user+network namespace (uid $(id -u) mapped to itself; no root)"
  runner=(unshare --user --map-current-user --net --)
elif [ "${ROUTESMART_OFFLINE_ALLOW_SUDO:-0}" = "1" ] && [ "${GITHUB_ACTIONS:-}" = "true" ] \
  && sudo -n unshare --net true 2>/dev/null; then
  mode="network namespace via sudo (GitHub Actions opt-in); privileges dropped to uid $(id -u) by setpriv"
  runner=(sudo -n unshare --net -- setpriv --reuid="$(id -u)" --regid="$(id -g)" --init-groups --)
else
  {
    echo "test-offline: cannot create a network namespace."
    echo "  - unprivileged 'unshare --user --map-current-user --net' failed (user namespaces"
    echo "    restricted, e.g. by AppArmor, or util-linux < 2.38);"
    if [ "${ROUTESMART_OFFLINE_ALLOW_SUDO:-0}" != "1" ]; then
      echo "  - the sudo fallback is disabled (it needs ROUTESMART_OFFLINE_ALLOW_SUDO=1 on GitHub Actions)."
    elif [ "${GITHUB_ACTIONS:-}" != "true" ]; then
      echo "  - the sudo fallback is allowed only on GitHub Actions (GITHUB_ACTIONS=true); it is ignored here."
    else
      echo "  - the sudo fallback is enabled but 'sudo -n unshare --net' failed."
    fi
    echo "Refusing to run tests without OS-level isolation."
  } >&2
  exit 2
fi
echo "test-offline: isolation path: ${mode}" >&2

# Runs inside the namespace. A non-routable address alone is not proof (it also
# fails on a normal host), so require: loopback is the only interface; an IPv4
# connect through the C-level socket type (which the in-process guard cannot
# patch) fails immediately with ENETUNREACH; and an IPv6 connect fails immediately
# with ENETUNREACH or EADDRNOTAVAIL (an empty namespace has no IPv6 source
# address). Then exec pytest in this same process.
probe_then_pytest='
import _socket, errno, os, sys
if os.geteuid() == 0:
    sys.exit("test-offline: refusing to run tests as root (euid 0); run as an unprivileged user")
names = {name for _, name in _socket.if_nameindex()}
if names != {"lo"}:
    sys.exit(f"test-offline: unexpected interfaces in namespace: {sorted(names)}")
checks = (
    (_socket.AF_INET, ("192.0.2.1", 443), {errno.ENETUNREACH}),
    (_socket.AF_INET6, ("2001:db8::1", 443), {errno.ENETUNREACH, errno.EADDRNOTAVAIL}),
)
for family, address, expected in checks:
    sock = _socket.socket(family, _socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(address)
    except OSError as exc:
        if exc.errno not in expected:
            sys.exit(f"test-offline: unexpected error for {address[0]}: {exc!r}")
    else:
        sys.exit(f"test-offline: {address[0]} is reachable inside the namespace")
    finally:
        sock.close()
netns = os.readlink("/proc/self/ns/net")
print(
    f"test-offline: namespace verified (lo only; IPv4/IPv6 unreachable); netns={netns} "
    f"pid={os.getpid()} uid={os.getuid()} euid={os.geteuid()} gid={os.getgid()}; exec pytest",
    file=sys.stderr,
)
os.environ["ROUTESMART_OFFLINE_NETNS"] = netns
os.execv(sys.executable, [sys.executable, "-m", "pytest", *sys.argv[1:]])
'

exec "${runner[@]}" "$python_bin" -I -c "$probe_then_pytest" "$@"
