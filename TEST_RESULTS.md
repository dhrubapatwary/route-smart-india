# Test Results

Append-only log of real commands and their verbatim terminal output. Never record results that were not actually produced.

---

## 2026-10-27: Task 001 baseline audit

**Context:** The repository has no source code and no tests. These commands record the baseline tooling state. No dependencies were installed (Task 001 constraint).

### Test runner availability
```
$ route_smart_env/bin/python -m pytest --version
/home/dhrubapatwary/projects/route-smart-india/route_smart_env/bin/python: No module named pytest
```

### SAST tool availability
```
$ route_smart_env/bin/python -m bandit --version
/home/dhrubapatwary/projects/route-smart-india/route_smart_env/bin/python: No module named bandit
```

### HTTP client availability
```
$ route_smart_env/bin/python -c "import httpx"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import httpx
ModuleNotFoundError: No module named 'httpx'
```

### Virtual environment contents
```
$ route_smart_env/bin/python --version
Python 3.13.5
$ route_smart_env/bin/python -m pip list
Package Version
------- -------
pip     25.1.1
```

### Source / test / CI / migration discovery
```
$ find . -path ./route_smart_env -prune -o -path ./.git -prune -o \( -name '*.py' -o -name '*.sql' -o -name '*.yml' -o -name '*.yaml' -o -name '*.toml' -o -name 'requirements*' -o -name '.env*' \) -print
(no output)
$ ls -d .github supabase migrations requirements tests
ls: cannot access '.github': No such file or directory
ls: cannot access 'supabase': No such file or directory
ls: cannot access 'migrations': No such file or directory
ls: cannot access 'requirements': No such file or directory
ls: cannot access 'tests': No such file or directory
```

### Provider evidence probe (read-only, unauthenticated)
```
$ curl -s -m 15 https://www.irctc.co.in/robots.txt | head -40
... <meta http-equiv="refresh" content="0; url=/nget/error" /> ... <h2>Page Not Found</h2> ...
```
IRCTC does not serve a robots.txt file.

**Summary:** 0 tests exist, and 0 were run, passed, or failed. The test and SAST tooling is not installed; it is installed in Phase 1.

---

## 2026-10-27: Task 002, minimum tested development foundation

**Context**
- Environment: `route_smart_env`, Python 3.13.5, Debian Linux.
- All runs below are **local**. **No remote GitHub Actions run has occurred**: nothing was committed or pushed.
- No live provider calls were made, and the test suite blocks outbound sockets.
- All commands were run from the repository root.

### Documentation gate check (before any Task 002 code)
```
$ grep -c "→ \*\*APPROVED\*\*" DECISIONS.md
8
```
Greps also confirmed:
- Amadeus is marked excluded in CLAUDE.md:81 and ROADMAP.md:155.
- `weather.txt` and `testing.txt` are listed in CLAUDE.md and ROADMAP.md.
- Python Playwright is named in CLAUDE.md and ROADMAP.md.
- The "zero human review" override is in CLAUDE.md §11.
- Audit rows G-01..G-03 are intact.

**Result:** gate passed.

### Dependency installation
```
$ route_smart_env/bin/python -m pip install -r requirements/dev.txt
Successfully installed ... bandit-1.9.4 ... mypy-2.4.0 ... pip-audit-2.10.1 ... pydantic-2.14.1 pydantic-core-2.50.1 ... pytest-9.1.1 pytest-asyncio-1.4.1 ... ruff-0.17.3 ...
[exit 0]
```
`requests` 2.34.2 was installed as a transitive dependency of `pip-audit` (dev tooling only). No project code imports it.

### Initial runs (failures found and fixed)

| Command | Exit | Finding | Fix |
|---|---|---|---|
| `python -m pytest` | 1 | 3 failed, 126 passed: `test_origin_equal_to_destination_is_rejected[MAA, maa, " Maa "]` | **Test bug**: the test set `destination` (already `MAA`) instead of `origin`. The test was corrected; the contract was unchanged. |
| `ruff check` | 1 | 8 errors: 7× E501 line too long in tests, 1× I001 import order | `ruff check --fix`, then `ruff format` |
| `ruff format --check` | 1 | 2 files would be reformatted (`tests/test_network_guard.py`, `tests/contracts/test_travel_option.py`) | `ruff format` |
| `mypy` | 1 | `tests/contracts/test_travel_option.py:92: error: Unused "type: ignore" comment` | **Real finding**: the pydantic mypy plugin could not see `frozen`/`extra="forbid"` because `model_config` came from a shared module variable. `ConfigDict` is now inlined in each model; see DECISIONS.md remediation log. |
| `bandit -c pyproject.toml -r src` | 0 | No issues | none |
| `pip-audit --progress-spinner off` (installed venv) | 1 | 12 advisory rows, all for `pip 25.1.1` itself (PYSEC-2026-1795, -1796, -196, -2875, -2876, -3721; some listed twice under aliases) | `python -m pip install --upgrade pip` → pip 26.2.2 [exit 0] |

**Self-review fix:** `test_asyncio_open_connection_is_blocked` originally accepted `OSError`. A real network timeout (`TimeoutError`) is a subclass of `OSError`, so the test could pass with the guard broken. It now requires `NetworkBlockedError`. Re-run: 3 passed [exit 0].

**Scope fix:** ruff 0.17 formats Markdown by default. It counted 11 `.md` files, including the owner's `CLAUDE-1.md` and `ROADMAP-1.md`. Their md5 checksums were confirmed **unchanged** against preflight:
- `c30273c0f7e4c3a088eebf440890fda2` (`CLAUDE-1.md`)
- `2cdb0e5e030540ab6348d616b84263de` (`ROADMAP-1.md`)

`[tool.ruff] include` is now Python-only.

### Final local runs (after all fixes)

> **Correction note (added 2026-10-27, pre-commit review finding B1):** This block is a **composite**, not one run:
> - pytest, mypy, bandit and both pip-audit outputs come from a single run made *before* the last Task 002 config change (the ruff `include` scope in `pyproject.toml`).
> - The ruff check/format outputs come from a re-run *after* that change.
>
> The bandit "Total lines of code" was originally recorded as **281**. That figure was copied from the *first* bandit run, before `_STRICT_MODEL` was removed. The correct value for this code state is **280**, as observed by the independent review's re-run. No pass/fail outcome changes.
>
> This block is superseded by the single fresh run in the "Task 002 remediation" section below.

```
$ route_smart_env/bin/python -m pytest -m "not live"
...
============================= 129 passed in 0.37s ==============================
[exit 0]

$ route_smart_env/bin/ruff check
All checks passed!
[exit 0]

$ route_smart_env/bin/ruff format --check
8 files already formatted
[exit 0]

$ route_smart_env/bin/mypy            # strict, pydantic plugin, src + tests
Success: no issues found in 8 source files
[exit 0]

$ route_smart_env/bin/bandit -c pyproject.toml -r src
Test results:
	No issues identified.
Code scanned:
	Total lines of code: 280        # corrected 2026-10-27 (was misrecorded as 281; see note above)
	Total lines skipped (#nosec): 0
Total issues (by severity): Undefined: 0 Low: 0 Medium: 0 High: 0
[exit 0]

$ route_smart_env/bin/pip-audit --strict --progress-spinner off -r requirements/dev.txt
No known vulnerabilities found
[exit 0]

$ route_smart_env/bin/pip-audit --progress-spinner off      # installed venv
No known vulnerabilities found
[exit 0]
```

**Test count by file:**

| File | Tests |
|---|---|
| `tests/contracts/test_travel_option.py` | 97 |
| `tests/test_log.py` | 29 |
| `tests/test_network_guard.py` | 3 |
| **Total** | **129** (all unit tests; 0 integration, 0 live, 0 E2E) |

**Not measured:**
- Coverage: no coverage tool is installed, because it is not required for Task 002.
- Bandit was not run on `tests/`: they are excluded by config. Ruff's `S` rules do lint `tests/`, with `S101` (assert) allowed.

### Configuration validation (local)
```
$ docker run --rm -v "$PWD:/repo:ro" --workdir /repo rhysd/actionlint:1.7.7 -color=false -verbose
verbose: Found 0 parse errors in 0 ms for .github/workflows/ci.yml
verbose: Found total 0 errors in 16 ms for .github/workflows/ci.yml
[exit 0]

$ route_smart_env/bin/python -c "import yaml; d=yaml.safe_load(open('.github/workflows/ci.yml')); print(list(d), list(d['jobs']), len(d['jobs']['checks']['steps']),'steps', d['permissions'])"
['name', True, 'permissions', 'concurrency', 'jobs'] ['checks'] 9 steps {'contents': 'read'}
[exit 0]

$ route_smart_env/bin/python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); print(d['project']['name'], d['project']['requires-python'], sorted(d['tool']))"
routesmart >=3.13 ['bandit', 'mypy', 'pydantic-mypy', 'pytest', 'ruff']
[exit 0]
```

Notes on these runs:
- A first YAML parse attempt raised `TypeError: '<' not supported between instances of 'bool' and 'str'`. The cause was my one-liner calling `sorted()` on keys: PyYAML (YAML 1.1) reads `on:` as boolean `True`. This is not a workflow defect; GitHub reads `on:` correctly.
- pytest runs with `--strict-config --strict-markers` and `filterwarnings=error`, so a misconfigured pytest section or any warning fails the run.
- The actionlint Docker image was pulled from Docker Hub for this local check. It is not a project dependency.

### Hygiene greps (exit 1 = no matches)

| Check | Exit |
|---|---|
| `grep -rnE "^\s*(import requests\|from requests)" src tests` | 1 |
| `grep -rnE "except\s*:" src tests` | 1 |
| Secret-pattern grep (`sk_live`, `AKIA…`, JWT-like `eyJ…`, `service_role`) over the repo, excluding the venv and `.git` | 1 |
| `.env` present at repo root | no |

### Remote CI
**Not run.** The workflow exists only in the uncommitted working tree. A GitHub Actions result can be observed only after the owner commits and pushes.

---

## 2026-10-27: Task 002 remediation (pre-commit review findings)

**Context**
- Same environment as above: `route_smart_env`, Python 3.13.5, pip 26.2.2.
- All runs are **local**. **GitHub Actions has still not run**: nothing was committed or pushed.
- No live provider calls were made. The `live` opt-in check below runs a canary test that makes no network call.
- Caches and bytecode were suppressed (`-p no:cacheprovider`, `--no-cache`, `--cache-dir=/dev/null`, `PYTHONDONTWRITEBYTECODE=1`).

### 1. Findings reproduced before fixing (probe scripts in the session scratchpad, outside the repo)

| Finding | Reproduced behaviour (before fix) |
|---|---|
| H1 | `log.info("count %d", "x")` raised `TypeError %d format: a real number is required, not str` into the caller |
| H2 | `log.exception()` printed a secret contained in the exception message. With no handler configured, `api_key=…` reached the last-resort handler unredacted. |
| H3 | `redact()` left these in clear: `{"api_key": "…"}`, `access_token=`, `refresh_token=`, `client_secret=`, `password='…'`, bare `Bearer …`, `https://user:pass@host`, `key=`, standalone JWT |
| H4 | After validation, 40 entries could be added to `provider_metadata` (cap is 32), and `unavailable["total_cost"]` could be set while `total_cost` had a value. `hash(option)` raised `TypeError: unhashable type: 'dict'`. |
| H5 | With the guard active (create_connection was blocked): `getaddrinfo`, UDP `sendto` and `subprocess.run` were ALLOWED, a module-scoped fixture made a real connect attempt, and `_socket.socket.connect` made a real connect attempt. `addopts` lacked `-m "not live"`. |
| M1 | Accepted: `duration=3900` → 3900 s; `3900.5`; epoch int `1793580000` and numeric string `"1793580000"` as timestamps; `waitlist_position=True` → 1; `schema_version=True` |
| M2 | Accepted: float `4250.5`; `"1E+2"` kept as `1E+2`; `1e30` (no bound); `XYZ` currency |
| L1 | `git check-ignore --no-index` matched `src/routesmart/reports/x.py` and `src/routesmart/build/x.py` |
| L4 | Metadata NaN silently became `null` on a JSON round trip; a 1 MB metadata string was accepted |

### 2. Verification experiments

**C-level socket type cannot be patched in-process**
```
$ python -c "import _socket; _socket.socket.connect = lambda *a: None"
C type not patchable: cannot set 'connect' attribute of immutable type '_socket.socket'
```

**OS-level isolation is feasible here**
```
$ unshare -rn python -c "import socket;socket.create_connection(('192.0.2.1',443),timeout=1)"
OSError: [Errno 101] Network is unreachable
```

**The isolation probe fails closed outside a namespace**
- Outside a namespace it exits 1 with `test-offline: unexpected interfaces in namespace: [..., 'eth0', 'lo', ...]`.
- Inside `unshare --user --map-root-user --net` it exits 0.
- My first probe used only a connect to a non-routable address. That would also "pass" on a normal host, so I replaced it before recording any results.

**Lock tooling: `pip lock --help`**
```
EXPERIMENTAL ... The generated lock file is only guaranteed to be valid for the current python version and platform.
```
This is why pip-tools was chosen (D-IMPL-07).

**Lock verification (fresh scratch venv, outside the repo)**
```
$ python3 -m venv <scratch>/locktest
$ <scratch>/locktest/bin/python -m pip install --require-hashes -r requirements/dev.lock.txt    [exit 0]  -> pip 26.2.2
$ <scratch>/locktest/bin/python -m pip check                                                    No broken requirements found. [exit 0]
$ <scratch>/locktest/bin/python -m pip install --dry-run -r requirements/dev.txt                (no "Would install" lines)
```

**Tamper test** (two hashes of `annotated-types` replaced in a scratch copy of the lock):
```
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE. ...
```

**Project venv vs lock:** 52 locked, 52 installed. No package is installed but not locked or locked but not installed, and there are no version mismatches.

**`.gitignore` regression check against the OLD rules** (scratch git repo with the unanchored patterns) exits 1:
```
check-gitignore: source path is ignored: src/routesmart/reports/summary.py
check-gitignore: source path is ignored: src/routesmart/build/plan.py
check-gitignore: source path is ignored: src/routesmart/dist/x.py
check-gitignore: source path is ignored: tests/reports/test_x.py
check-gitignore: source path is ignored: docs/build/notes.md
```

**Intermediate failures during remediation (fixed, not suppressed)**

| Failure | Cause and fix |
|---|---|
| 2 contract tests failed | (a) `" P1DT2H "`: the validators checked the stripped string but passed the unstripped one on. Fixed to return the stripped value. (b) A test wrongly expected `maxProperties` in the *serialization* schema. It is a validation constraint, so the test now checks each schema mode for what that mode should contain. |
| ruff: 16 findings | Line length/format; import order; SIM105; one stale `noqa`; S105 ×2. The S105 hits were false positives on the *names* `_SECRET_KEY` (a regex of key names) and `SECRET` (a test sentinel). They were fixed by renaming to `_SENSITIVE_KEY_NAMES` and `SENTINEL`, not by suppressing. |
| mypy: 5 errors | `Formatter.converter` type: now set per instance with a typed `_utc_time`. Property narrowing made an assert unreachable: the test was restructured. `model_construct` call in a test was missing required args. |

### 3. Final validation suite: one run, against the final code, 2026-10-27T12:28:19Z

Commands are run from the repo root with `P=route_smart_env/bin/python`.

| Check | Command | Exit | Result |
|---|---|---|---|
| Environment | `$P --version`; `$P -m pip --version` | 0 | Python 3.13.5; pip 26.2.2 |
| Installed deps consistent | `$P -m pip check` | 0 | No broken requirements found. |
| Lock satisfies declared ranges | `$P -m pip install --dry-run -r requirements/dev.txt` | 0 | No `Would install` lines |
| `.gitignore` rules | `scripts/check-gitignore.sh` | 0 | `check-gitignore: ok (6 visible, 8 ignored)` |
| Lint | `ruff check --no-cache` | 0 | All checks passed! |
| Format | `ruff format --check --no-cache` | 0 | 10 files already formatted |
| Types | `mypy --cache-dir=/dev/null` (strict, pydantic plugin) | 0 | Success: no issues found in 10 source files |
| Unit tests (in-process guard) | `$P -m pytest -p no:cacheprovider -q` | 0 | **236 passed, 1 deselected** |
| L7 regression | `$P -m pytest -p no:cacheprovider -q --import-mode=importlib` | 0 | 236 passed, 1 deselected |
| Unit tests (OS network namespace) | `PYTHON=$P scripts/test-offline.sh -p no:cacheprovider -q` | 0 | 236 passed, 1 deselected (isolation probe passed first) |
| Live gate, no opt-in | `$P -m pytest -p no:cacheprovider -q -m live` | 0 | 1 skipped (`live tests need ROUTESMART_ALLOW_LIVE=1 and owner approval`) |
| Live gate, with opt-in | `ROUTESMART_ALLOW_LIVE=1 $P -m pytest -p no:cacheprovider -q -m live` | 0 | 1 passed. The canary asserts the guard was lifted and makes no network call. |
| SAST | `bandit -c pyproject.toml -r src` | 0 | No issues; Total lines of code: **490**; #nosec: 0; Low/Medium/High: 0/0/0 |
| Dependency audit (lock) | `pip-audit --strict --progress-spinner off --disable-pip --require-hashes -r requirements/dev.lock.txt` | 0 | No known vulnerabilities found |
| Dependency audit (venv) | `pip-audit --strict --progress-spinner off` | 0 | No known vulnerabilities found |
| Workflow | `docker run … rhysd/actionlint:1.7.7 -color=false -verbose` | 0 | 0 parse errors, 0 errors |
| Shell scripts | `docker run … koalaman/shellcheck:v0.10.0 scripts/test-offline.sh scripts/check-gitignore.sh` | 0 | no findings |
| Config parse | `python -I -c "import tomllib,yaml; …"` | 0 | pyproject tool sections ok; CI: 12 steps, triggers `push: [main]` + `pull_request`, `permissions: contents: read` |
| Whitespace (tracked) | `git diff --check` | 0 | clean |
| Whitespace (untracked) | `git diff --no-index --check /dev/null <file>` for each untracked file | 1 → 0 | See below |

**Whitespace (untracked):** the first run exited 1, flagging trailing whitespace only in the two `docs/history/*.md` archives. That whitespace is the owner's original text, preserved byte-for-byte (verified by md5). I added `.gitattributes` (`docs/history/*.md -whitespace`), confirmed with `git check-attr`, and re-ran the check: exit 0, no whitespace errors.

**Test counts by file**

| File | Tests |
|---|---|
| `tests/contracts/test_travel_option.py` | 157 |
| `tests/test_log.py` | 54 |
| `tests/test_network_guard.py` | 25 + 1 `live` canary |
| **Total** | **236 non-live** (unit) + **1 live canary** |

There are no integration or E2E tests, and no real live tests.

**Not run / limitations**
- **Remote CI: not run.** The OS-level isolation step (including its `sudo` fallback) and the lock install are unverified on GitHub runners.
- Coverage is not measured (no tool configured).
- Bandit excludes `tests/` by config. Ruff's `S` rules lint `tests/`, with the intentional inline suppressions listed in DECISIONS.md R-013.

---

## 2026-10-27: Task 002 remediation round 3 (Round 2 review findings N1–N12)

**Context**
- All runs are **local** (Debian, Python 3.13.5, pip 26.2.2, util-linux 2.41.5).
- **GitHub Actions has not run**: nothing was committed or pushed.
- No live provider calls were made. Index access was used only for the pip installs, `check_lock.py` metadata resolution and pip-audit.
- Caches and bytecode were suppressed for every check.

### 1. Reproduction and investigation (before or while fixing)

| Item | Observation |
|---|---|
| N1 | Old JWT pattern: `redact("eyJ-"*20000)` 3.09 s, `*40000` 11.04 s (quadratic). |
| N1, per-pattern profiling | After the JWT fix, `_SECRET_ASSIGNMENT` still took 1.38 s at `"eyJ-"*80000` (linear but heavy) and was rewritten too. |
| N2 | `logging.getLogger("routesmart.adapters.flight").warning("api_key=…")`, both before and after `import routesmart.log`, reached the last-resort handler unredacted. |
| N3 | `Money.model_construct(amount=-5, currency="rupees")` and a naive `live`/`sample` `Provenance.model_construct` were accepted into `TravelOption.model_validate`. |
| N6 | Writing `FrozenMapping._data` added keys (cap bypassed: 42 entries) and changed the hash. |
| N7 | Metadata `{f: 1}` vs `{f: True}`: options equal and hash-equal, but their JSON differed. |
| GitHub runner evidence (desk research) | Ubuntu 24.04 restricts unprivileged user namespaces through AppArmor by default; there is a runner user report of `unshare` failing. Not verified for GitHub's current image. Sources: openwall oss-security 2025-03-27, Ubuntu discourse "Understanding AppArmor User Namespace Restriction", actions/runner-images#10443. |

### 2. Verification experiments

**N1 – old vs new redaction timing.** Old pattern on the 400 KB regression payload:
```
$ timeout 20 python -I -c '<old JWT pattern>.sub("*", "eyJ-" * 100_000)'
exit=124 (killed at 20 s)
```

New patterns, `redact(unit * n)`:

| Unit | n = 20 000 | n = 80 000 | Ratio |
|---|---|---|---|
| `eyJ-` | 0.015 s | 0.061 s | 3.9 |
| `eyJaaaaa.` | 0.023 s | 0.095 s | 4.1 |
| `a.` | 0.010 s | 0.045 s | 4.4 |
| `key ` | 0.018 s | 0.073 s | 4.0 |
| `key="` | 0.020 s | 0.074 s | 3.7 |
| `a://` | 0.020 s | 0.085 s | 4.3 |
| `Bearer ` | 0.027 s | 0.112 s | 4.1 |

`key=`, `x` and `token:` all had a ratio of 4.0–4.1.

**N2 – pytest interaction discovered.** After the package-import fix, 7 logging tests failed. pytest 9's `catching_logs` attaches its `LogCaptureHandler` to every non-propagating logger (`_pytest/logging.py:356-366`). That handler re-raises emit errors (lines 409-415) and does not redact. With `-p no:logging`, all 54 tests passed, so `-p no:logging` was added to `addopts`.

**N4/N10 – `scripts/test-offline.sh`**

| Case | Command | Result |
|---|---|---|
| A | `PYTHON=$P scripts/test-offline.sh -q` | `isolation path: unprivileged user+network namespace (uid 1000 mapped to itself; no root)`, then `namespace verified`, then pytest passed. exit 0 |
| B | `PYTHON=/nonexistent/python scripts/test-offline.sh` | `Python interpreter not found: '/nonexistent/python' …` exit 2 |
| C | `env -i PATH=<dir without unshare> … scripts/test-offline.sh` | `cannot create a network namespace … sudo fallback is disabled … Refusing to run tests` exit 2 |
| C2 | same as C, with `ROUTESMART_OFFLINE_ALLOW_SUDO=1` and no sudo | `… sudo fallback is enabled but 'sudo -n unshare --net' failed … Refusing` exit 2 |
| D | `unshare --user --map-current-user --net id -u` | `1000` (outside: 1000) |
| E | probe run directly on the host | `unexpected interfaces in namespace: [... 'eth0', 'lo', ...]` exit 1 (pytest not executed) |

**My own intermediate failure:** the first version expected `ENETUNREACH` for IPv6 and failed closed with `OSError(99, 'Cannot assign requested address')`. An empty namespace has no IPv6 source address. IPv6 now accepts `ENETUNREACH` or `EADDRNOTAVAIL`; IPv4 stays strict.

**N5 – `scripts/install-locked.sh` in a fresh scratch venv**
```
install-locked: stage 1 bootstrap pip: pip 25.1.1 from <scratch venv>
Successfully installed pip-26.2.2
install-locked: stage 2 installing requirements/dev.lock.txt with pinned pip 26.2.2
exit=0; pip --version -> pip 26.2.2; pip check -> No broken requirements found.
```

**N8 – `scripts/check_lock.py`**

| Case | Result |
|---|---|
| Real tree | `check-lock: ok (52 pins; lock matches dev.txt exactly)` exit 0 |
| Scratch copy, `pip-tools` removed from `dev.txt` | obsolete: build, click, pip-tools, pyproject-hooks, setuptools, wheel. exit 1 |
| Scratch copy, `httpx>=0.28,<1` added to `base.txt` | missing: anyio, h11, httpcore, httpx. exit 1 |

**Intermediate failures (fixed, not suppressed)**
- ruff: an import-order nit, 2× E501, and SIM300 on a deliberate reflected-equality assertion (rewritten with a named variable).
- mypy: wrong or unused `type: ignore` codes on the new private-attribute tests.
- `tests/test_check_lock.py` collection error: a file-loaded module must be registered in `sys.modules` before `exec_module` because of dataclasses.

### 3. Final validation suite: one run against the final code, 2026-10-27T12:56:08Z

`P=route_smart_env/bin/python`. Every command exited 0.

| Check | Command | Result |
|---|---|---|
| Environment | `$P --version`; `$P -m pip --version` | Python 3.13.5; pip 26.2.2 |
| Installed deps | `$P -m pip check` | No broken requirements found. |
| Lock consistency | `$P scripts/check_lock.py` | `ok (52 pins; lock matches dev.txt exactly)` |
| `.gitignore` | `scripts/check-gitignore.sh` | ok (6 visible, 8 ignored) |
| Lint | `ruff check --no-cache` | All checks passed! |
| Format | `ruff format --check --no-cache` | 12 files already formatted |
| Types | `mypy --cache-dir=/dev/null` (strict; src, tests, scripts) | no issues in 12 source files |
| Tests (in-process guard) | `$P -m pytest -p no:cacheprovider -q` | **295 passed, 1 deselected** |
| Tests (importlib mode) | `… -q --import-mode=importlib` | 295 passed, 1 deselected |
| Tests (network namespace) | `PYTHON=$P scripts/test-offline.sh -p no:cacheprovider -q` | 295 passed, 1 deselected (unprivileged path; probe verified) |
| Live gate, no opt-in | `$P -m pytest … -m live` | 1 skipped |
| Live gate, opt-in | `ROUTESMART_ALLOW_LIVE=1 $P -m pytest … -m live` | 1 passed (canary; no network call) |
| SAST | `bandit -c pyproject.toml -r src` | no issues; 581 LOC; #nosec 0 |
| Dependency audit (lock) | `pip-audit --strict --disable-pip --require-hashes -r requirements/dev.lock.txt` | No known vulnerabilities |
| Dependency audit (venv) | `pip-audit --strict` | No known vulnerabilities |
| Workflow | actionlint 1.7.7 (Docker, read-only mount) | no findings |
| Shell scripts | shellcheck v0.10.0 on `test-offline.sh`, `check-gitignore.sh`, `install-locked.sh` | no findings |
| Config parse | tomllib + yaml | pyproject ok; CI 12 steps, triggers push:[main] + pull_request, permissions contents:read |
| Whitespace | `git diff --check` and per-file check of untracked files | clean |

**Test counts by file**

| File | Tests |
|---|---|
| `tests/contracts/test_travel_option.py` | 172 |
| `tests/test_log.py` | 88 |
| `tests/test_network_guard.py` | 25 + 1 live canary |
| `tests/test_check_lock.py` | 10 |
| **Total** | **295 non-live + 1 live canary** |

**Not run / unverified**
- **GitHub Actions (not run):**
  - whether the unprivileged namespace path works on the runner (evidence suggests AppArmor may block it);
  - the `sudo` opt-in path, never exercised anywhere;
  - `install-locked.sh` with the runner's bootstrap pip;
  - `check_lock.py` against the runner's network;
  - the overall workflow result.
- Coverage is not measured.

---

## 2026-10-27: Task 002 closure, Gate 2 (owner decisions recorded; R3 CI-only sudo guard)

**Context**
- All runs are **local**. **GitHub Actions has not run**: nothing staged, committed or pushed.
- No live provider calls were made. Index access was used only by `check_lock.py` and pip-audit.

**R3 verification**
- **Stub-based script tests:** `tests/test_offline_script.py` has 17 tests, all passing.
- **Mutation check** (scratch copy outside the repo):
  - removing the `GITHUB_ACTIONS` condition: `6 failed, 11 passed`;
  - removing the root refusal: `1 failed, 16 passed`.
- **Namespace identity, from inside pytest:** `tests/test_offline_isolation.py` is skipped under plain pytest and **passes** under the offline script. A direct run printed:
  ```
  test-offline: isolation path: unprivileged user+network namespace (uid 1000 mapped to itself; no root)
  test-offline: namespace verified (lo only; IPv4/IPv6 unreachable); netns=net:[4026533209] pid=68394 uid=1000 euid=1000 gid=1000; exec pytest
  PASSED tests/test_offline_isolation.py::test_suite_runs_in_the_verified_namespace_as_non_root
  ```
- **Test-harness fixes during development** (the script was not at fault):
  - The stub logger first split multi-line arguments.
  - It then depended on `tr`, which is absent from the minimal stub `PATH`.
  - It now uses bash builtins.

**Full local suite (single run, 2026-10-27T13:21:30Z).** Every command below exited 0. `P=route_smart_env/bin/python`.

| Check | Result |
|---|---|
| `$P -m pip check` | No broken requirements found |
| `$P scripts/check_lock.py` | ok (52 pins; lock matches dev.txt exactly) |
| `scripts/check-gitignore.sh` | ok (6 visible, 8 ignored) |
| `ruff check --no-cache`; `ruff format --check --no-cache` | All checks passed; 14 files already formatted |
| `mypy --cache-dir=/dev/null` | no issues in 14 source files |
| `$P -m pytest -p no:cacheprovider -q` | **313 passed, 1 skipped** (namespace test; only under the script), 1 deselected (live) |
| same with `--import-mode=importlib` | 313 passed, 1 skipped, 1 deselected |
| `PYTHON=$P scripts/test-offline.sh -p no:cacheprovider -q -rA -k 'verified_namespace or offline_script'` | 18 passed |
| `PYTHON=$P scripts/test-offline.sh -p no:cacheprovider -q` | **314 passed**, 1 deselected |
| `$P -m pytest -q -m live` / with `ROUTESMART_ALLOW_LIVE=1` | 1 skipped / 1 passed (canary, no network) |
| `bandit -c pyproject.toml -r src` | no issues; 581 LOC |
| pip-audit (lock with `--disable-pip --require-hashes`; installed venv) | No known vulnerabilities (both) |
| actionlint 1.7.7; shellcheck v0.10.0 (3 scripts) | no findings |
| TOML/YAML parse | ok (CI: 12 steps; push `[main]` + pull_request; `contents: read`) |
| `git diff --check`; per-file whitespace check of untracked files | clean |

**Test counts by file**

| File | Tests |
|---|---|
| `tests/contracts/test_travel_option.py` | 172 |
| `tests/test_log.py` | 89 |
| `tests/test_network_guard.py` | 25 + 1 live canary |
| `tests/test_offline_script.py` | 17 |
| `tests/test_check_lock.py` | 10 |
| `tests/test_offline_isolation.py` | 1 (skipped outside the script) |

**Unverified until GitHub Actions runs**
- which isolation path the runner takes;
- the sudo path itself, never executed anywhere;
- runner-user identity and IPv4/IPv6 behaviour on the runner;
- the two-stage install with the runner's bootstrap pip;
- the overall workflow result.

---

## 2026-10-27: Task 002 closure, Gate 3: final local validation (independent re-run)

**Context and state**
- `main` at `2b302e0`, equal to `origin/main`. 0 staged; `README.md` modified; 43 untracked. `git diff --check` exit 0.
- No file changed since the Gate 2 report (none modified after 13:24 UTC).
- `source route_smart_env/bin/activate`: Python 3.13.5.
- Commands are the documented ones (README "Checks", `ci.yml`, `docs/TESTING.md`). They write only to already-ignored cache directories.
- Run window: 13:33:30Z–13:33:51Z.
- All results are **local**. **GitHub Actions has not run.** No live provider calls were made and no costs were incurred. Index access was used only by `check_lock.py` and pip-audit.

| # | Command | Exit | Result |
|---|---|---|---|
| 01 | `python -m pytest -q -rs` | 0 | 313 passed, 1 skipped (`test_offline_isolation`: "only under scripts/test-offline.sh"), 1 deselected (live) |
| 02 | `python -m pytest -q -rs --import-mode=importlib` | 0 | 313 passed, 1 skipped, 1 deselected |
| 03 | `scripts/test-offline.sh -q -rs` | 0 | 314 passed, 1 deselected. `isolation path: unprivileged user+network namespace (uid 1000 mapped to itself; no root)`; `namespace verified … netns=net:[4026533209] pid=76125 uid=1000 euid=1000 gid=1000` |
| 04a | `python -m pytest -q -rA tests/test_offline_isolation.py` | 0 | 1 skipped (expected under plain pytest) |
| 04b | `scripts/test-offline.sh -q -rA tests/test_offline_isolation.py` | 0 | `PASSED …::test_suite_runs_in_the_verified_namespace_as_non_root` |
| 05a | `python -m pytest -q -rs -m live` | 0 | 1 skipped ("live tests need ROUTESMART_ALLOW_LIVE=1 and owner approval") |
| 05b | `ROUTESMART_ALLOW_LIVE=1 python -m pytest -q -rA -m live` | 0 | 1 passed (canary asserts the guard was lifted; makes no network call; no provider contacted) |
| 06 | `ruff check`; `ruff format --check` | 0; 0 | All checks passed; 14 files already formatted |
| 07 | `mypy` (strict; src, tests, scripts) | 0 | no issues in 14 source files |
| 08 | `bandit -c pyproject.toml -r src` | 0 | No issues identified; 581 LOC; #nosec 0 |
| 09 | `pip-audit --strict --progress-spinner off --disable-pip --require-hashes -r requirements/dev.lock.txt`; `pip-audit --strict --progress-spinner off` | 0; 0 | No known vulnerabilities found (both) |
| 10 | `python -m pip check` | 0 | No broken requirements found |
| 11 | `python scripts/check_lock.py` | 0 | ok (52 pins; lock matches dev.txt exactly) |
| 12 | `scripts/check-gitignore.sh` | 0 | ok (6 visible, 8 ignored) |
| 13 | `docker run … rhysd/actionlint:1.7.7 -color=false -verbose` | 0 | 0 parse errors, 0 errors |
| 14 | `docker run … koalaman/shellcheck:v0.10.0` on `test-offline.sh`, `install-locked.sh`, `check-gitignore.sh` | 0 | no findings |
| 15 | `python -I -c "import tomllib,yaml; …"` | 0 | pyproject ok, including `-p no:logging`; CI 12 steps, push `[main]` + pull_request, `contents: read` |
| 16 | `git diff --check`; `git diff --no-index --check` per untracked file | 0; 0 | clean (43 untracked files checked) |

**Offline-script guard (Section 3)**
- `python -m pytest -q -rA tests/test_offline_script.py`: 17 passed (all cases listed in the run log).
- **Inspection (`scripts/test-offline.sh`):**
  - The sudo path requires `ROUTESMART_OFFLINE_ALLOW_SUDO` = `1` **and** `GITHUB_ACTIONS` = `true`, exact string comparisons (line 42).
  - The probe refuses euid 0 (line 72) and requires interfaces == {`lo`} (line 75).
  - IPv4 expects only ENETUNREACH; IPv6 expects ENETUNREACH or EADDRNOTAVAIL (lines 78-79).
  - The probe `exec`s pytest in its own process (line 100), inside the namespace started at line 103.
  - Namespace failure exits 2 before Python runs (line 60).
- **Ad-hoc branch check** (scratchpad harness; fake `_socket` and `if_nameindex`; `os.execv` stubbed; no network; not part of the committed suite):

  | Case | Outcome |
  |---|---|
  | v4 ENETUNREACH + v6 EADDRNOTAVAIL | proceeds |
  | v4 ENETUNREACH + v6 ENETUNREACH | proceeds |
  | v4 ETIMEDOUT | exit 1, no exec |
  | v4 EHOSTUNREACH | exit 1, no exec |
  | v4 EADDRNOTAVAIL | exit 1, no exec |
  | v4 connects | exit 1, no exec |
  | v6 ECONNREFUSED | exit 1, no exec |
  | v6 connects | exit 1, no exec |

  The first harness attempt failed with SyntaxError because of my own extraction regex (`^.$` matched a `)` line); it was corrected to the anchor the committed test uses.

**Differences from Gate 2:** none in outcomes or counts. The namespace inode was the same value as in Gate 2; inode numbers are reused after a namespace is freed, so it isn't the same namespace. The PIDs differ.

**Unverified until GitHub Actions runs**
- the namespace path the runner selects;
- whether the sudo fallback works on the runner (never executed anywhere);
- runner identity and non-root execution on the runner;
- IPv4/IPv6 isolation on the runner;
- the two-stage locked install under the runner's initial pip;
- the overall workflow result.

---

## 2026-10-27: Gate 4 decision 1: IPv4/IPv6 probe-outcome regression tests, then full Gate 3 re-run

**Change:** `tests/test_offline_script.py` gained 17 tests. They run the real probe source (extracted from `scripts/test-offline.sh`) in a child interpreter with fake `_socket.socket`, `_socket.if_nameindex`, `os.geteuid` and `os.execv`. No real sockets or network are used. The probe itself is unchanged.

- **Accepted (positive controls; exec reached; both families probed):**
  - IPv4 ENETUNREACH + IPv6 ENETUNREACH;
  - IPv4 ENETUNREACH + IPv6 EADDRNOTAVAIL.
- **IPv4 fails closed** (exit 1, no "namespace verified", exec not reached): timeout without errno, ETIMEDOUT, EHOSTUNREACH, ECONNREFUSED, EADDRNOTAVAIL, EACCES, EPERM, successful connect.
- **IPv6 fails closed** (same assertions): timeout without errno, ETIMEDOUT, EHOSTUNREACH, ECONNREFUSED, EACCES, successful connect.
- **Extra interface (`eth0`)** is rejected before any connect.

```
$ python -m pytest -p no:cacheprovider -q -rA tests/test_offline_script.py
34 passed in 0.45s
```

**Mutation check** (scratch copies outside the repo; `tests/test_offline_script.py`):

| Mutation | Result |
|---|---|
| accept any errno | 12 failed, 22 passed |
| IPv4 also accepts ECONNREFUSED | 1 failed, 33 passed |
| successful connect not rejected | 2 failed, 32 passed |
| IPv6 check removed | 8 failed, 26 passed |
| interface check removed | 1 failed, 33 passed |

**Lint after the change:** `ruff check` initially flagged one E501 in the new test. `ruff format` fixed it, and ruff, format and mypy are clean.

**Full Gate 3 suite re-run.** Same documented commands as the Gate 3 section, run at 13:41:19Z–13:41:38Z, local only. Every command exited 0.

| # | Check | Result |
|---|---|---|
| 01 | pytest | **330 passed**, 1 skipped (namespace test), 1 deselected (live) |
| 02 | pytest `--import-mode=importlib` | 330 passed, 1 skipped, 1 deselected |
| 03 | `scripts/test-offline.sh -q -rs` | **331 passed**, 1 deselected. Unprivileged path, uid/euid 1000, namespace verified |
| 04a/04b | namespace test | skipped under plain pytest; **PASSED** under the offline script |
| 05a/05b | live gate | skipped by default; canary passed with opt-in (no network) |
| 06–07 | ruff, format (14 files), strict mypy (14 files) | clean |
| 08 | bandit | no issues; 581 LOC |
| 09 | pip-audit (lock; environment) | no known vulnerabilities |
| 10–12 | `pip check`; `check_lock.py` (52 pins); `check-gitignore.sh` | ok |
| 13–15 | actionlint; shellcheck (3 scripts); TOML/YAML parse | clean |
| 16 | `git diff --check`; whitespace of 43 untracked files | clean |

**Test counts by file**

| File | Tests |
|---|---|
| `tests/contracts/test_travel_option.py` | 172 |
| `tests/test_log.py` | 89 |
| `tests/test_network_guard.py` | 25 + 1 live canary |
| `tests/test_offline_script.py` | 34 |
| `tests/test_check_lock.py` | 10 |
| `tests/test_offline_isolation.py` | 1 |

**Result:** Gate 3 PASS on the updated tree. GitHub Actions has still not run.
