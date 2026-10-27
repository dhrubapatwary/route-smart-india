# Testing and Network Isolation

## Running tests

| Command | What it does |
|---|---|
| `route_smart_env/bin/python -m pytest` | Full non-live suite with the in-process guard. `-m "not live"` is in the default `addopts`. |
| `PYTHON=route_smart_env/bin/python scripts/test-offline.sh` | The same suite inside an OS-level network namespace. CI runs this. |
| `scripts/check-gitignore.sh` | Checks that source paths are never ignored and that generated/secret paths are. |

pytest runs with `-p no:logging`. pytest's log capture would attach an unredacted handler to the `routesmart` logger (see docs/LOGGING.md). Tests use streams and `capsys` instead of `caplog`.

## Layer 1: in-process guard

The guard lives in `tests/testsupport/network_guard.py` and is installed by `tests/conftest.py`. It is active from `pytest_configure` to `pytest_unconfigure`. That covers collection, imports, and fixtures of **every scope**, including module- and session-scoped fixtures, which an autouse function fixture would not cover.

**Blocked:**

| Area | Entry points |
|---|---|
| TCP/UDP | `socket.socket.connect`, `connect_ex`, `sendto`; `sendmsg` when given an address; `socket.create_connection`. This covers asyncio and httpx-style clients. |
| DNS | `socket.getaddrinfo`, `getnameinfo`, `gethostbyname`, `gethostbyname_ex`, `gethostbyaddr`, including `loop.getaddrinfo`. |
| Child processes | `subprocess.Popen` (so `subprocess.run` and asyncio subprocesses too), `os.system`, `os.posix_spawn`, `os.posix_spawnp`. |

**Not blocked (verified limitations):**

- The C-level `_socket.socket` type. It is immutable and cannot be patched in-process.
- `os.fork`, `os.exec*`, and native extensions that open sockets themselves.
- Local `socket.socketpair()`. This is intentional: asyncio needs it, and it never leaves the process.

The guard is therefore **not a sandbox**. Use layer 2 for that.

## Layer 2: OS-level network namespace

`scripts/test-offline.sh` runs pytest in a new network namespace. It reports which path it used on stderr.

| Path | When | Privilege |
|---|---|---|
| 1. `unshare --user --map-current-user --net` | default | **None.** The current uid is mapped to itself, so tests do not run as root, even inside the namespace. Needs util-linux ≥ 2.38 and unprivileged user namespaces. |
| 2. `sudo -n unshare --net -- setpriv --reuid=$(id -u) --regid=$(id -g) --init-groups --` | **only on GitHub Actions**: requires `ROUTESMART_OFFLINE_ALLOW_SUDO=1` **and** `GITHUB_ACTIONS=true` (exact values), and path 1 failed. The opt-in alone is ignored elsewhere (owner decision R3). | Root is used only to create the network namespace. `setpriv` drops back to the invoking uid/gid before Python starts. `sudo -n` never prompts, and sudo resets the environment. |

If neither path is available, or a required tool or the Python interpreter is missing, the script prints a diagnostic and exits 2 without running tests.

**Never as root.** The probe exits with an error if the effective uid is 0, on every path.

**Evidence for CI logs.** The probe prints `netns=…`, `pid=…`, `uid=…`, `euid=…` and `gid=…`, then exports `ROUTESMART_OFFLINE_NETNS`. `tests/test_offline_isolation.py` then asserts, from inside pytest, that:
- the suite is in that same namespace;
- `lo` is the only interface;
- uid and euid are non-zero.

Under plain pytest that test is skipped. Under the script it must pass.

**Script tests.** `tests/test_offline_script.py` drives the script with stub `unshare`/`sudo` binaries on a controlled `PATH`. No real namespace, sudo or network is used. It checks:
- the sudo opt-in is off by default;
- it is ignored outside GitHub Actions;
- only the exact values count;
- the CI path fails closed when the namespace cannot be created;
- `setpriv` drops to the invoking non-root uid/gid;
- the unprivileged path never maps root;
- the probe refuses euid 0;
- a missing interpreter fails clearly;
- **probe outcomes**, using fake sockets (no network):
  - only IPv4 `ENETUNREACH` with IPv6 `ENETUNREACH`/`EADDRNOTAVAIL` proceeds;
  - every other outcome fails closed **before pytest starts**: a timeout, `ETIMEDOUT`, `EHOSTUNREACH`, `ECONNREFUSED`, `EACCES`/`EPERM`, IPv4 `EADDRNOTAVAIL`, or a successful connect, on either address family;
  - extra interfaces are rejected before any connect.

These tests use the `allow_subprocesses` fixture, which lifts **only** the in-process child-process block for that test. Network and DNS stay blocked.

**Proof of isolation, in the same namespace as the tests.** The script starts one Python process inside the namespace. That process:

- checks that `lo` is the only interface;
- checks that an IPv4 connect through the C-level `_socket` type fails immediately with `ENETUNREACH`;
- checks that an IPv6 connect fails immediately with `ENETUNREACH` or `EADDRNOTAVAIL`;
- then `exec`s pytest in that same process.

`exec` keeps the namespace, so the proof applies to exactly the namespace the tests use. A non-routable address alone is not accepted as proof, because it also fails on a normal host.

**Trade-off of the sudo opt-in (CI):**
- **Evidence:** Ubuntu 24.04, the current `ubuntu-latest`, restricts unprivileged user namespaces through AppArmor by default. A runner user report describes `unshare` failing there. This is not verified for GitHub's current image.
  - https://discourse.ubuntu.com/t/understanding-apparmor-user-namespace-restriction/58007
  - https://openwall.com/lists/oss-security/2025/03/27/6
  - https://github.com/actions/runner-images/issues/10443
- **What the workflow does:** it sets `ROUTESMART_OFFLINE_ALLOW_SUDO=1`. GitHub sets `GITHUB_ACTIONS=true` itself. The owner approved this CI-only fallback on 2026-10-27 (R3), with enforcement in the script.
- **What the fallback adds:** the runner's passwordless sudo is used for one command, `unshare --net`, and the tests themselves run unprivileged.
- **The alternative:** remove the variable to require unprivileged isolation only. CI will then fail closed if the runner forbids it.
- **Decision:** approved by the owner (R3, 2026-10-27). The sudo path is **not verified** until a GitHub Actions run demonstrates it.

**Verification status:**

| Environment | Status |
|---|---|
| Local (Debian, util-linux 2.41.5) | Path 1 verified on 2026-10-27. uid inside the namespace = 1000 (not root). Missing-interpreter and no-namespace failure paths both exit 2. The probe refuses on the real host. |
| GitHub Actions | **Unverified** until CI runs. Path 1 may be blocked by AppArmor. Path 2 (sudo) has never been exercised. |

## Live tests

Live tests call real external providers. They have three gates:

1. Mark the test `@pytest.mark.live`.
2. Run it explicitly with `-m live`. Live tests are deselected by default.
3. Set `ROUTESMART_ALLOW_LIVE=1`. Without it, selected live tests are **skipped**.

Only when all three hold is the guard lifted, and only for that test.

CI never sets `ROUTESMART_ALLOW_LIVE`, and CI runs inside the network namespace, so live tests cannot run there. Live tests also require owner approval under CLAUDE.md §9 and §11.

## Updating pinned GitHub Actions (D-IMPL-06)

Actions in `.github/workflows/ci.yml` are pinned to full commit SHAs, with the upstream version in a trailing comment. To update one, through a reviewed pull request, never directly on `main`:

1. Read the upstream release notes for the new version.
2. Resolve the tag to a commit SHA: `gh api repos/<owner>/<action>/commits/<tag> --jq .sha`.
3. Replace the SHA and update the `# vX.Y.Z` comment. Never use a floating tag such as `@v7`.
4. Run actionlint locally, open a PR, and review the CI run before merging.
5. Record the change in DECISIONS.md (D-IMPL-06).
