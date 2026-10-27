# Architecture & Decision Log

Each entry records its status:
- **APPROVED**: decided by the project owner. This includes decisions written into `CLAUDE.md` or `ROADMAP.md` by the owner.
- **PROPOSED**: recommended by Claude and awaiting owner approval. Do not implement against it until it is approved, except where an approved task explicitly requires an implementation choice. Such choices are logged as PROPOSED for owner review.
- **SUPERSEDED**: kept for history.

Never delete entries. Append new ones and change status lines in place, with a dated note.

---

## Approved (as stated in the original CLAUDE.md / ROADMAP.md, recorded 2026-10-27)

These rows were recorded during Task 001 from the **original** `CLAUDE.md`, which the owner preserved as untracked `CLAUDE-1.md` (archived on 2026-10-27 to `docs/history/CLAUDE.original-2026-10-27.md`). The owner replaced `CLAUDE.md` and `ROADMAP.md` on 2026-10-27, after Task 001 and before Task 002. Section references in the "Source" column point to the original file. The status notes dated 2026-10-27 (Task 002 preflight) reflect the replacement files.

| ID | Decision | Source (original CLAUDE.md) | Status note, 2026-10-27 (Task 002 preflight) |
|---|---|---|---|
| D-001 | Async-only Python (`asyncio`), `httpx.AsyncClient`, no `requests`. | §2 | **SUPERSEDED** by new CLAUDE.md §3 (owner-confirmed 2026-10-27, R2). Async for concurrent I/O and `httpx.AsyncClient` for HTTP still apply. Pure computation may stay synchronous. |
| D-002 | Playwright async API for browser automation. | §2 Rule 3 | **SUPERSEDED** by new CLAUDE.md §3 (owner-confirmed 2026-10-27, R2); related to D-PROP-02 and D-PROP-08. Use it only where terms permit, with no bypass of access controls. |
| D-003 | Pilot route BLR → MAA. | §3 | APPROVED. Unchanged, now in new CLAUDE.md §2. |
| D-004 | Supabase (Postgres) via `asyncpg` with parameterised queries. The frontend uses `supabase-js` and never the service role key. | §10 | **SUPERSEDED** by new CLAUDE.md §5 and §7 (owner-confirmed 2026-10-27, R2). Supabase is the *proposed* primary DB, and `asyncpg` *may* be used. The authorization model and RLS interaction must be designed and verified first. The service-role key must never reach the PWA (§5). |
| D-005 | Layered requirements under `requirements/`, not a single requirements.txt. | §6 | APPROVED. Extended by D-PROP-06 (`weather.txt`, `testing.txt`). |
| D-006 | PWA frontend with a service worker, a manifest, and offline fallback. | §7 | APPROVED in principle (new ROADMAP Phase 7). The frontend framework is still open: vanilla JS is a candidate. |
| D-007 | Free tiers and sandboxes only during development. Third-party calls are mocked in tests. | §11 | **SUPERSEDED** by new CLAUDE.md §4 and §11 (owner-confirmed 2026-10-27, R2); related to D-PROP-04 and D-PROP-05. Mocks by default. No material cost, trial, or paid plan without explicit approval. |
| D-008 | pytest + pytest-asyncio + pytest-mock, plus bandit SAST. | §8, §12 | APPROVED as refined by new CLAUDE.md §9 and D-PROP-06 (adds ruff, mypy, pip-audit, CI). pytest-mock is not yet required; it will be added to `requirements/testing.txt` when first needed. |

**Correction, 2026-10-27 (owner decision R2):** The owner confirmed the SUPERSEDED labels for D-001, D-002, D-004 and D-007 after the entry-by-entry check in Gate 1. Two of my earlier notes said D-002 was superseded "by … D-PROP-02 … D-PROP-08" and D-007 "by … D-PROP-04/05". Those were inferred mappings that the D-PROP entries do not state, so they are now "related to". D-004 now also cites CLAUDE.md §5. The decision texts in the table are unchanged.

**Caveat, logged 2026-10-27 (Task 001):** D-002 and the provider list in CLAUDE.md §4 are approved *as written*, but the audit found that parts of them cannot be executed (see D-PROP-01, -02, -03). The user must confirm how to reconcile them.
**Resolved 2026-10-27:** The owner approved D-PROP-01..08 (see below) and replaced CLAUDE.md and ROADMAP.md.

---

## Proposed (Task 001, 2026-10-27): owner decision recorded 2026-10-27

The original Task 001 proposal text is kept verbatim under each heading. The **Approval record** that follows each one is authoritative. Where the approved wording differs from the proposal, the approved wording wins.

### D-PROP-01: Replace Amadeus Self-Service as the flight-offers source
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Context:** Amadeus decommissioned Self-Service on 17 Jul 2026 (register F-1).
- **Proposal (Task 001, historical):** Use SerpApi Google Flights as the primary *indicative-fare* source, on the free plan of 250 searches/month with caching. Keep a provider-agnostic `FlightOffersAdapter` interface so a licensed source can be swapped in later. Use fixtures for all development.
- **Alternatives:** Duffel test mode (India coverage unverified); Amadeus Enterprise (commercial).
- **Rationale:** SerpApi is the only no-cost source already named in the original CLAUDE.md §4 that is still available.
- **Approval record (2026-10-27):**
  - **Decision:** Use **sample flight data** for the initial implementation.
  - **Conditions:**
    - SerpApi may be *evaluated* as a candidate only.
    - Do not assume it provides suitable, current, permitted fares until its capabilities, coverage, terms, quotas, costs, and required fields are verified.
    - Do **not** use the discontinued Amadeus Self-Service API.
    - No live flight integration in Task 002.
  - **Narrower than the proposal:** SerpApi was *not* approved as the primary source; it remains a candidate.
  - **Implications:**
    - Flight options use `DataOrigin.SAMPLE` provenance.
    - Amadeus is marked excluded in CLAUDE.md §4, ROADMAP Phase 3, and the provider register.
  - **Open questions:** Which flight source to use once evaluation completes. Whether any licensed or commercial source is acceptable.

### D-PROP-02: No IRCTC scraping behind CAPTCHA or login
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Context:** Register R-1. The IRCTC booking flow is protected by CAPTCHA and login. IRCTC agent rules prohibit automation software. Monitoring a booked WL would require users' IRCTC credentials.
- **Proposal (Task 001, historical):** For development and the vertical slice, rail data comes from fixtures. For the product, the user enters a PNR or WL position manually, or the project licenses a source from an authorised partner. Playwright stays approved for PWA E2E testing and for public, terms-permitted pages only. The project will never solve or bypass CAPTCHA and never store IRCTC passwords.
- **Rationale:** This complies with the Task 001 "do not bypass access controls" constraint and with zero-trust principles.
- **Approval record (2026-10-27):**
  - **Decision:** Use **sample rail data** initially. Possible future sources are manual user input or a licensed data partner.
  - **Conditions:**
    - No IRCTC scraping that bypasses CAPTCHA, login restrictions, access controls, or other restrictions.
    - Do not store or automate users' railway credentials.
    - No live rail integration in Task 002.
  - **Implications:** Rail options use sample provenance. A waitlisted state is representable in the shared contract with no IRCTC dependency.
  - **Open questions:** Whether a licensed partner is pursued and at what cost. The privacy design for user-entered PNRs.

### D-PROP-03: The Safety Net is recommend-only, with fixture fallbacks
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Context:** Register X-1..X-3. Uber price estimates are gated, and Uber's ToS bans price comparison. The Ola ride API is invite-only. No bus provider is named.
- **Proposal (Task 001, historical):** Phase 5 recommends alternatives and never books them. Cab cost is estimated as distance × configurable ₹/km. Bus options come from fixtures until a provider is approved.
- **Approval record (2026-10-27):**
  - **Decision:** Initially recommend alternative **cabs and buses using simulated data only**.
  - **Conditions:**
    - Do not book, cancel, purchase, or execute consequential travel actions.
    - Any future live monitoring or action first needs authorized data access, explicit user opt-in, bounded execution, and duplicate-action prevention.
    - No live integrations in Task 002.
  - **Implications:**
    - The shared contract includes `cab` and `bus` modes.
    - The Safety Net appears in new ROADMAP Phase 6, not Phase 5.
  - **Open questions:** The cab cost formula, which was proposed and not approved. Bus data sources.

### D-PROP-04: Road cost inputs
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Proposal (Task 001, historical):** The slice uses dated static config for tolls, fuel ₹/litre, and vehicle km/l. A TollGuru 14-day trial is used only in a scheduled window to record fixtures, and only if the user approves the trial. The Mappls free tier is to be verified before any adoption.
- **Approval record (2026-10-27):**
  - **Decision:** Use **sample values** for tolls, fuel, and EV charging initially.
  - **Conditions:**
    - Do not start a TollGuru trial, incur a subscription, or incur any other paid-provider cost without separate approval.
    - No live road-cost integration in Task 002.
  - **Narrower than the proposal:** The trial window in the proposal is *not* approved.
  - **Open questions:** The road provider choice after Mappls and others are verified.

### D-PROP-05: Human approval gates at phase exits
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Context:** The original CLAUDE.md §12 said "Zero Human Review", but Task 001 requested approval gates.
- **Proposal (Task 001, historical):** Claude keeps autonomous remediation of code findings. Phase exits, provider/legal choices, DB schema, and any spend need explicit user approval.
- **Approval record (2026-10-27):**
  - **Decision:** Explicit human approval gates **override** any earlier "zero human review" instruction.
  - **Autonomous work:** Routine, reversible code changes and ordinary remediation within the approved task scope may be done autonomously.
  - **Human approval required before:**
    - material spending;
    - production deployment;
    - destructive database operations;
    - consequential live travel actions.
  - **Not authorized:** This approval does **not** authorize Git commits or pushes.
  - **Implications:** Reflected in new CLAUDE.md §11–§13 and ROADMAP gates.
  - **Open questions (checked 2026-10-27):** None identified. The four approval triggers are consistent with the longer list in CLAUDE.md §11, and commit/push authorization is explicitly per-request.

### D-PROP-06: Phase 1 additions
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Proposal (Task 001, historical):**
  - Add a typed `TravelOption` data contract.
  - Add `requirements/weather.txt` and `requirements/db.txt`.
  - Add `pyproject.toml` with the pytest, ruff, and mypy configs.
  - Add `.env.example`.
  - Add a shared logging helper.
  - Add a GitHub Actions CI workflow running pytest, bandit, pip-audit, ruff, and mypy.
- **Rationale:** Audit gaps G-07, G-09, G-10, G-14.
- **Approval record (2026-10-27):**
  - **Decision:** Introduce a shared travel-option data contract, CI, and separate `requirements/weather.txt` and `requirements/testing.txt`.
  - **Files retained:** `base.txt`, `flight.txt`, `rail.txt`, `road.txt`, `dev.txt`.
  - **Conditions:** Document dependency ownership and inclusion rules to avoid duplication and circular references.
  - **Differs from the proposal:** `testing.txt` was approved instead of `db.txt`. A DB requirements file is not approved.
  - **Implications:** Task 002 scope. See D-IMPL-* below and `requirements/README.md`.
  - **Open questions (checked 2026-10-27):**
    - Which file owns future DB dependencies (`asyncpg`). `db.txt` was not approved.
    - Whether to adopt the generated lock `requirements/dev.lock.txt` (D-IMPL-07, PROPOSED).
    - Whether to set a test-coverage threshold. None is configured.

### D-PROP-07: Fixture-only BLR→MAA vertical slice before live integrations
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27), with the conditions below.
- **Proposal (Task 001, historical):** See `docs/audits/TASK_001_BASELINE_AUDIT.md` §4.
- **Approval record (2026-10-27):**
  - **Decision:** Build a mocked, deterministic vertical slice before live integrations. Its core question is: "For Bengaluru to Chennai on a given date, which travel option is recommended, and why?" The recommendation must be explainable.
  - **Conditions:** This approval does **not** authorize implementing the full vertical slice in Task 002.
  - **Implications:** The slice belongs to new ROADMAP Phase 2.
  - **Open questions:** The scoring weights and normalisation are still proposals (CLAUDE.md §8). The detailed slice design in audit §4 is a proposal, not approved scope.

### D-PROP-08: Python Playwright for E2E
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27).
- **Proposal (Task 001, historical):** Use `pytest-playwright` (Python) for the PWA E2E tests, to keep a single test runner and report format.
- **Approval record (2026-10-27):**
  - **Decision:** Use Python Playwright for browser-based E2E testing, alongside pytest and pytest-asyncio.
  - **Conditions:** Do not introduce a separate Node-based testing stack without a specific, documented need and approval.
  - **Implications:** Not installed in Task 002 because there are no E2E tests yet. It will be owned by `requirements/testing.txt` when added.
  - **Open questions (checked 2026-10-27):**
    - How browser binaries are installed and cached in CI (download size, version pinning).
    - Whether to use the `pytest-playwright` plugin or `playwright.async_api` directly with pytest-asyncio.

**Verification (2026-10-27):** All eight D-PROP entries above show status APPROVED with their conditions. Confirmed by `grep -c "→ \*\*APPROVED\*\*" DECISIONS.md` = 8 (recorded in TEST_RESULTS.md).

---

## Task 002 implementation choices (2026-10-27): originally PROPOSED; owner decision recorded 2026-10-27 (see "Owner decisions: Gate 1")

These are implementation choices made within the approved D-PROP-06 scope. They are not product decisions and can be changed.

### D-IMPL-01: Pydantic v2 for the shared contract
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002)
- **Choice:** `pydantic>=2.14,<3` in `requirements/base.txt`.
- **Rationale:** Declarative validation and JSON-schema export, which helps the later backend API contract. It also has a mypy plugin.
- **Alternatives:** stdlib `dataclasses` with hand-written validation (more code, more risk); `attrs` + `cattrs`.
- **Consequences:** Pydantic is the one runtime dependency in the baseline.

### D-IMPL-02: `src/` layout, package `routesmart`, no install step
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002)
- **Choice:** Code lives in `src/routesmart/`. Tests import it via `pythonpath = ["src"]` in pytest config and `mypy_path = "src"`. There is no `[build-system]`; packaging is deferred until a deployable artefact is needed.
- **Rationale:** A modular monolith (CLAUDE.md §3). Modules can be split later if measurements justify it.

### D-IMPL-03: Contract shape
- **Status:** ~~PROPOSED~~ → **APPROVED (direction only)** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1"). The final schema remains a Phase 2 approval gate. Phase 2 must approve the schema before live data (ROADMAP Phase 2 gate).
- **Choice:** See `docs/TRAVEL_OPTION_CONTRACT.md`. In summary:
  - Timestamps must be timezone-aware.
  - Durations are `timedelta`, serialised as ISO 8601.
  - Money is `Decimal` plus an ISO 4217 code.
  - Provenance is required (`sample` | `live`), and freshness is derived.
  - A missing measurable field must be declared in `unavailable` with a reason.
  - Provider metadata is a flat, size-capped mapping that scoring must not read.
- **Amended 2026-10-27 (Task 002 remediation; still PROPOSED):**
  - `unavailable` and `provider_metadata` are immutable `FrozenMapping`s, so validated options are deeply immutable and hashable.
  - Timestamps and durations accept only `datetime`/`timedelta` objects or ISO 8601 strings. Numeric epoch values, numeric durations and booleans are rejected.
  - `waitlist_position` is a strict int.
  - Money amounts are canonicalised to 2 decimal places, floats are rejected, and amounts must be below 10¹² (a technical bound).
  - Currency is checked for format only; this narrower guarantee is documented.
  - Metadata floats must be finite and strings are at most 256 characters.
  - A future `retrieved_at` is accepted by design.
  - Rationale and details are in `docs/TRAVEL_OPTION_CONTRACT.md`.
- **Amended 2026-10-27 (round 3; still PROPOSED):**
  - All three models set `revalidate_instances="always"`, so nested instances built with `model_construct` are revalidated (N3).
  - `FrozenMapping` stores its items in a read-only `MappingProxyType` and rejects attribute assignment and deletion (N6).
  - `FrozenMapping` equality and hashing are type-aware, so `1`, `True` and `1.0` differ, which matches serialisation (N7).

### D-IMPL-04: Logging helper
- **Status:** ~~PROPOSED~~ → **APPROVED with limitations** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002)
- **Choice:**
  - Uses stdlib `logging` only.
  - Logs go to the `routesmart.<service>` logger hierarchy, with UTC ISO-8601 timestamps.
  - Configuration is idempotent.
  - A best-effort redaction filter masks common secret patterns. Redaction is defence in depth, **not** a guarantee: callers must still not log secrets.
- **Rejected:** a `QueueHandler`/listener for async. It is unnecessary at this stage; revisit if logging I/O shows up in profiling.
- **Amended 2026-10-27 (Task 002 remediation; still PROPOSED):**
  - Redaction moved from a filter to a `RedactingFormatter` that redacts the **fully formatted** output, including tracebacks and stack info. The patterns were broadened.
  - Malformed `%` calls degrade to a placeholder without their arguments. Other emit errors print an argument-free notice.
  - `get_logger()` installs the redacting stderr handler if none exists, so early records are never routed to Python's unredacted last-resort handler.
  - Added `sanitize_url()`.
  - Limits are in `docs/LOGGING.md`.
- **Amended 2026-10-27 (round 3; still PROPOSED):**
  - All redaction patterns were rewritten to be linear-time: matches start only at token starts, quantifiers are possessive, key suffixes are checked with fixed-width lookbehinds, and keys are at most 64 characters (N1).
  - Importing the `routesmart` package installs the redacting handler, so direct `logging.getLogger("routesmart.*")` use is covered (N2). This adds a documented import side effect: it configures the `routesmart` logger.
  - `sanitize_url()` now also masks token-like path segments, and its contract is stated precisely (N9).
  - The pytest suite runs with `-p no:logging`, because pytest's capture handler would bypass redaction on non-propagating loggers.

### D-IMPL-05: Test network guard
- **Status:** ~~PROPOSED~~ → **APPROVED as a layered guard** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002)
- **Choice:** `tests/conftest.py` blocks outbound socket connections in every test unless the test carries a `live` marker. No `live` tests exist, and CI never runs them.
- **Rationale:** Enforces the rules that development and CI need no live provider credentials and make no paid calls (CLAUDE.md §9; ROADMAP Phase 3).
- **Amended 2026-10-27 (Task 002 remediation; still PROPOSED):**
  - The guard moved to `tests/testsupport/network_guard.py` and is installed for the whole session via `pytest_configure`, so it now covers collection and module/session-scoped fixtures.
  - It now also blocks DNS lookups, UDP `sendto`/`sendmsg` with an address, and child processes (`subprocess.Popen`, `os.system`, `os.posix_spawn*`).
  - `live` tests are deselected by default (`-m "not live"`) and skipped unless `ROUTESMART_ALLOW_LIVE=1`.
  - `tests/` is on pytest's `pythonpath`, so test imports no longer depend on the import mode.
  - The C-level `_socket`, `fork`/`exec` and native-extension paths cannot be blocked in-process. D-IMPL-08 covers them.
- **Amended 2026-10-27 (Gate 2, for the R3 tests):** Added the `allow_subprocesses` fixture (`NetworkGuard.subprocesses_allowed()`).
  - It lifts **only** the child-process block, for one test; network and DNS stay blocked.
  - It is used solely by `tests/test_offline_script.py`, which runs local stub binaries.
  - If the guard is not installed, it does nothing.

### D-IMPL-06: CI actions pinned by commit SHA
- **Status:** ~~PROPOSED~~ → **APPROVED** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002)
- **Choice:**
  - Pinned actions:
    - `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1)
    - `actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` (v7.1.0)
    - Resolved with `gh api` on 2026-10-27.
  - The workflow has `permissions: contents: read` and uses no secrets.
- **Rationale:** Supply-chain hardening. Tags can be moved; SHAs cannot.
- **Update process (owner approval condition, 2026-10-27):** Upstream versions are recorded beside each SHA in `ci.yml`. Updates follow the reviewed procedure in `docs/TESTING.md`, "Updating pinned GitHub Actions": resolve the tag to a full SHA with `gh api`, update the SHA and the version comment, open a PR, and review the upstream release notes and the CI run. Never use a floating tag.
- **Amended 2026-10-27 (Task 002 remediation):**
  - CI runs on pushes to `main` and on pull requests, to avoid duplicate runs for PR branches.
  - It installs from the hash-verified lock (D-IMPL-07) instead of an unpinned `pip install --upgrade pip`.
  - It checks the `.gitignore` rules and runs pytest through `scripts/test-offline.sh` (D-IMPL-08).

### D-IMPL-07: Hash-verified dependency lock generated by pip-tools
- **Status:** ~~PROPOSED~~ → **APPROVED as a development-tooling lock** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1") (implemented in Task 002 remediation). It is not a production dependency lock.
- **Choice:**
  - `requirements/dev.lock.txt` is generated from `requirements/dev.txt` with `pip-compile --generate-hashes --allow-unsafe` (pip-tools 7.6.2, owned by `dev.txt`).
  - It pins all 52 packages of the dev/CI environment, including `pip==26.2.2`, with sha256 hashes for all published files.
  - CI installs it with `--require-hashes`, runs `pip check`, verifies with `pip install --dry-run -r dev.txt` that the lock still satisfies the declared ranges, and audits the lock with `pip-audit --disable-pip --require-hashes`.
- **Rationale:** Reproducible, tamper-evident CI installs (review M3). This keeps the existing requirements-file structure: the inputs stay human-edited, and the lock is output only.
- **Alternatives considered:**
  - `pip lock` / `pylock.toml`: pip marks it EXPERIMENTAL and "only valid for the current python version and platform".
  - `uv pip compile`: a new tool.
  - Constraints files without hashes: no tamper detection.
- **Consequences / open:**
  - Dependency updates require regenerating the lock.
  - Runtime-only installs are not separately locked yet.
  - The lock was generated on Python 3.13; CI uses 3.13.
- **Amended 2026-10-27 (round 3; still PROPOSED):**
  - CI installs in two stages with `scripts/install-locked.sh` (N5). The runner's existing pip installs only the hash-verified pinned pip, and that pinned pip then installs the full lock. The bootstrap pip version is printed, not assumed.
  - `scripts/check_lock.py` replaces the dry-run range check. It resolves `dev.txt` under the locked versions and fails on missing, obsolete or mismatched pins (N8).

### D-IMPL-08: OS-level network isolation for the test suite
- **Status:** ~~PROPOSED~~ → **APPROVED: isolation requirement** (owner, recorded 2026-10-27; see "Owner decisions: Gate 1"). At approval, runtime behaviour was unverified until GitHub Actions ran. **Current status (Gate 5, 2026-10-27): runtime verified for the observed run.**
  - GitHub Actions run 40515177175 exercised the CI-only sudo namespace fallback successfully.
  - The namespace was verified as loopback-only, with IPv4 and IPv6 unreachable.
  - Privileges were dropped, and pytest ran with `uid=1001 euid=1001 gid=1001`.
  - The namespace proof test passed.
  - The unprivileged namespace path remains **unverified** on GitHub.
  - This verifies the observed workflow run; it is **not** production sandbox certification.
  - **Owner acceptance (Gate 6, 2026-10-27):** the owner accepted the existing CI evidence as satisfying the D-IMPL-08 verification conditions (runner path, runner-user identity, IPv4/IPv6 isolation, fail-closed behaviour). A real refusal on the GitHub runner was **not** demonstrated and is not claimed. See "Owner decisions: Gate 6".
  - The approval and its conditions are unchanged; see the runtime verification addendum below. (Implemented in Task 002 remediation.)
- **Choice:**
  - `scripts/test-offline.sh` runs pytest in a Linux network namespace, using `unshare --user --map-root-user --net`, with a `sudo -n unshare --net` + `setpriv` fallback.
  - Before running tests it proves isolation: `lo` must be the only interface, and a C-level `_socket` connect must fail with `ENETUNREACH`. Otherwise it fails closed.
  - CI runs the suite only through this script.
- **Rationale:** Review H5. The in-process guard cannot patch the immutable C-level socket type or `fork`/`exec`, so OS-level isolation is the reliable control for those paths.
- **Verification:**
  - Locally on 2026-10-27, through the `unshare --user` path: the probe fails outside a namespace and passes inside one.
  - **Unverified on GitHub Actions** (historical, before Gate 5), including the `sudo` fallback, until CI runs. *The sudo fallback was later verified in run 40515177175; see the Gate 5 addendum.*
- **Consequences:** If the runner forbids both paths, CI fails closed rather than silently running without isolation.
- **Amended 2026-10-27 (round 3; still PROPOSED):**
  - The probe and pytest now run in one process in the same namespace: the probe `exec`s pytest (N4).
  - The default path is `--map-current-user`, so there is no root inside the namespace.
  - The `sudo` path runs only with `ROUTESMART_OFFLINE_ALLOW_SUDO=1`.
  - The script prints which path it used and gives a clear diagnostic when Python is missing (N10).
  - The CI workflow sets `ROUTESMART_OFFLINE_ALLOW_SUDO=1` explicitly, preserving its previous behaviour, where the fallback was automatic.
  - Desk evidence suggests Ubuntu 24.04 runners restrict unprivileged user namespaces, so the unprivileged path may fail there (unverified).
  - **Owner decision pending:** keep the CI opt-in, or remove it to require unprivileged isolation only. CI would then fail closed if the runner forbids it.
  - *Resolved 2026-10-27 by owner decision R3; see the next amendment.*
- **Amended 2026-10-27 (owner decision R3: CI-only sudo fallback, enforced):**
  - The sudo path now needs **both** `ROUTESMART_OFFLINE_ALLOW_SUDO=1` and `GITHUB_ACTIONS=true`. The opt-in alone is ignored outside GitHub Actions, and only the exact values `1` and `true` count.
  - The probe refuses to run as root (euid 0) on every path, and prints `netns`, `pid`, `uid`, `euid` and `gid` as CI evidence.
  - It exports `ROUTESMART_OFFLINE_NETNS`, and `tests/test_offline_isolation.py` asserts from inside pytest that the suite runs in that same namespace, as non-root, with only `lo`.
  - Stub-based tests in `tests/test_offline_script.py` cover: the opt-in is off by default; it is ignored outside GitHub Actions; the CI path fails closed when the namespace cannot be created; and `setpriv` drops to the invoking non-root uid/gid. A mutation check confirmed these tests fail if the `GITHUB_ACTIONS` condition or the root refusal is removed.
  - **Not verified (historical, before Gate 5):** at the time of this amendment, the sudo path had never run, and GitHub Actions evidence was required (Gate 5). *Superseded by the runtime verification addendum below.*
- **Runtime verification addendum (2026-10-27, Gate 5; evidence only, the approval and its conditions are unchanged):**
  - **Where:** GitHub Actions run **40515177175** (https://github.com/dhrubapatwary/route-smart-india/actions/runs/40515177175) on commit `43e69663dbf5ce128d694782b0b6c3f16750749d` (PR #1, draft).
  - **Path exercised:** the CI-only sudo fallback ran successfully: `isolation path: network namespace via sudo (GitHub Actions opt-in); privileges dropped to uid 1001 by setpriv`.
  - **Namespace verified:** loopback only, IPv4/IPv6 unreachable (`namespace verified (lo only; IPv4/IPv6 unreachable) … uid=1001 euid=1001 gid=1001`).
  - **Tests:** pytest ran in that process as uid/euid 1001, with 331 passed and 1 deselected. The namespace proof test passed (0 skipped).
  - **Overall:** the workflow concluded `success`.
  - **Unchanged:** the fallback still requires **both** `ROUTESMART_OFFLINE_ALLOW_SUDO=1` and `GITHUB_ACTIONS=true`, and the script still fails closed.
  - **Not verified:** the unprivileged namespace path has not run on GitHub.
  - **Scope:** one successful run is evidence for that run, not production sandbox certification. Details are in TEST_RESULTS.md, "Gate 5".

---

## Remediation log (CLAUDE.md §9 / §12)

- 2026-10-27 (Task 001): No code existed yet, so no SAST findings were remediated.
- 2026-10-27 (Task 002), **R-001, mypy / pydantic plugin:**
  - *Finding:* `model_config` was assigned from a shared module-level `ConfigDict` variable. As a result, the pydantic mypy plugin could not see `frozen=True` or `extra="forbid"`, so it did not flag assignment to a frozen model or unknown constructor kwargs. This surfaced as mypy's `unused "type: ignore"` error.
  - *Fix:* `ConfigDict(...)` is inlined in each model.
  - *Residual risk:* none known. Runtime behaviour was already correct.
- 2026-10-27 (Task 002), **R-002, pip-audit on the installed venv:**
  - *Finding:* `pip 25.1.1` in `route_smart_env` had 6 distinct advisories (PYSEC-2026-1795, -1796, -196, -2875, -2876, -3721).
  - *Fix:* upgraded venv pip to 26.2.2. CI now upgrades pip before installing.
  - *Residual risk:* none known. pip is not a project dependency.
- 2026-10-27 (Task 002), **R-003, test weakness:**
  - *Finding:* the async network-guard test accepted any `OSError`, which would also match a real network timeout.
  - *Fix:* it now requires `NetworkBlockedError`.
- 2026-10-27 (Task 002), **R-004, tool scope:**
  - *Finding:* ruff 0.17 formats Markdown by default, so it could rewrite owner documentation.
  - *Fix:* `[tool.ruff] include` is now Python only.
  - *Verification:* the owner files `CLAUDE-1.md` and `ROADMAP-1.md` were confirmed unchanged by checksum. They have since been archived byte-for-byte under `docs/history/` (2026-10-27 remediation).
- Bandit reported no findings. No `# nosec` suppressions and no rule exceptions were added. The only per-file ignore is ruff `S101`/`D` in `tests/` (asserts and docstrings in tests).
- 2026-10-27 (Task 002 remediation of the pre-commit review). Each finding was reproduced before it was fixed; evidence is in TEST_RESULTS.md.
  - **R-005 (B1):** `TEST_RESULTS.md` recorded bandit "281" lines of code in its "final" block. The true value at that time was 280, because the 281 was copied from the first run. That block also combined runs from before and after a config change. Corrected in place with a dated note, and superseded by a single fresh run.
  - **R-006 (H1):** A malformed `%` format raised `TypeError` into application code (from the filter's `getMessage()`). It now degrades to a placeholder without arguments, and other emit errors print an argument-free notice.
  - **R-007 (H2/H3):** Secrets in tracebacks, in records emitted before configuration, and in 9 common forms (JSON keys, `*_token`, `client_secret`, quoted values, bare Bearer, URL userinfo, JWTs, `key=`) were logged in clear. Fixed by whole-output redaction, broader patterns, a default redacting handler and `sanitize_url()`. **Residual risk:** arbitrary secrets that match no pattern still leak; the caller rules in docs/LOGGING.md are the primary control.
  - **R-008 (H4):** Post-validation mutation of `unavailable` and `provider_metadata` could bypass the invariants, and options were unhashable. Fixed with `FrozenMapping`, which is now hashable, picklable and serialises to plain dicts.
  - **R-009 (H5):** DNS, UDP, child processes and module/session-scoped fixtures bypassed the guard, and plain `pytest` would have run `live` tests. Fixed per the D-IMPL-05 amendment and D-IMPL-08. **Residual risk:** the in-process guard alone is not a sandbox (C-level `_socket`, `fork`/`exec`), and the OS-level layer is unverified on GitHub Actions.
  - **R-010 (M1/M2/L4):** Ambiguous coercions were accepted: numeric durations and epoch timestamps, boolean positions and schema versions, float amounts, unbounded amounts and exponent forms, non-finite and oversized metadata. Fixed per the D-IMPL-03 amendment.
  - **R-011 (M3):** No lock or hashes, and an unpinned CI pip. Fixed by D-IMPL-07.
  - **R-012 (L1):** The unanchored `build/`, `dist/` and `reports/` rules hid source directories. They are now anchored to the root, with regression check `scripts/check-gitignore.sh` (also run in CI). Verified to fail against the old rules.
  - **R-013 (L7):** `from conftest import …` depended on the import mode. Support code now lives in the `tests/testsupport` package, with `tests` on `pythonpath`. Verified under `--import-mode=importlib`.
  - **Inline suppressions in tests (intentional):** `type: ignore` on four lines that assert mutation fails; `noqa: S605,S607` (`os.system` blocked-call test); `noqa: S301` (pickle of the test's own data); and two `noqa: DTZ001` (naive-datetime rejection tests). `src/` has no suppressions.
- 2026-10-27 (Task 002 remediation round 3: Round 2 review findings N1–N12). Each finding was reproduced or confirmed by inspection first; evidence is in TEST_RESULTS.md, Round 3.
  - **R-014 (N1):** The JWT pattern was quadratic (`"eyJ-"*40000`: 11 s). Profiling also showed the key-assignment pattern had a high constant: 1.38 s at 80 K repetitions. Both were rewritten to be linear: 4× the input now takes ≈ 4× the time, and `eyJ-`×80 K takes 0.06 s. A regression test uses ten 400 KB adversarial payloads with a 5 s budget each; the old pattern exceeded 20 s on one of them. The docs' linear-time claim is now backed by that evidence.
  - **R-015 (N2):** A direct `logging.getLogger("routesmart.x")` before `get_logger()` reached the unredacted last-resort handler. Fixed: `routesmart/__init__.py` now calls `ensure_redacting_handler()`, with tests for use before and after package import and after configuration.
    - **Discovered while fixing:** pytest 9 attaches its unredacted capture handler to every non-propagating logger (`_pytest/logging.py:356-366`), which would also print RouteSmart records unredacted in failure reports. Fixed with `-p no:logging` in `addopts`.
  - **R-016 (N3):** `model_construct`-built `Money`/`Provenance` were accepted inside a validated `TravelOption`. Fixed with `revalidate_instances="always"`, plus tests.
  - **R-017 (N6):** `FrozenMapping._data` was a mutable dict, which allowed a 42-entry cap bypass and hash drift. It is now a read-only `MappingProxyType`, `__setattr__`/`__delattr__` raise, and `__reduce__` keeps pickle and deepcopy working; covered by tests.
  - **R-018 (N7):** `1`/`True`/`1.0` metadata compared and hashed equal although their JSON differed. Equality and hashing are now type-aware, and a test checks equal ⇔ equal JSON across a value matrix.
  - **R-019 (N4):** The probe and pytest ran in different namespaces. They now run in one process (probe `exec`s pytest).
  - **R-020 (N10):**
    - The script now reports its isolation path and gives an explicit diagnostic (exit 2) when Python is missing.
    - It uses `--map-current-user` (uid 1000 inside, not root).
    - The `sudo` fallback is opt-in.
    - **My own first attempt failed closed:** the new IPv6 check expected `ENETUNREACH` but got `EADDRNOTAVAIL`. Both errnos are now accepted for IPv6; IPv4 stays strict.
  - **R-021 (N5):** The CI bootstrap install was done by the runner's unpinned pip. It is now two-stage, and only the pinned pip is installed by the bootstrap pip.
  - **R-022 (N8):** The range check could not detect obsolete pins. `scripts/check_lock.py` now detects missing, obsolete and mismatched pins. Verified on scratch copies: dropping `pip-tools` reports 6 obsolete pins, and adding `httpx` reports 4 missing.
  - **R-023 (N9):** `sanitize_url` kept path tokens. It now masks token-like segments and applies `redact()` to the other segments, with the contract and limits stated precisely.
  - **R-024 (N11):** The nested-guard test now uses `try/finally`.
  - **R-025 (N12):** A ROADMAP row marked logging "Approved" while citing PROPOSED D-IMPL-04. It is now Candidate, and D-IMPL-04 was not approved.
  - **New inline suppressions (tests only, intentional):**
    - `type: ignore[attr-defined]` ×2 and `type: ignore[assignment]` ×1: assertions that private-attribute writes fail;
    - `noqa: DTZ001` ×1: a deliberately naive timestamp;
    - `noqa: S301` ×1: pickle of the test's own data.
    - `scripts/check_lock.py` carries `noqa: S603` for a fixed-argv `subprocess.run` with no shell.
    - `src/` still has no suppressions.

---

## Owner decisions: Gate 1 (recorded 2026-10-27)

These were recorded on 2026-10-27 from the owner's Gate 1 decision message. No earlier approval date is claimed. The historical PROPOSED text above is preserved, and the status lines carry dated in-place notes.

### D1: D-IMPL-01 to D-IMPL-08: APPROVED, subject to these conditions
- **D-IMPL-01 (Pydantic v2):** Approved. Validate at trust boundaries and revalidate nested model instances. Document that `model_construct()` and `model_copy(update=...)` can bypass validation.
- **D-IMPL-02 (`src/` layout):** Approved. Keep the current `src/` layout without introducing a build system now. Revisit packaging when API or deployment needs justify it.
- **D-IMPL-03 (travel-option contract):** Direction approved; the **final schema remains a Phase 2 approval gate**.
  - Preserve: metadata immutability, normalised money and duration, timezone-aware timestamps, provenance, freshness, explicit missing values and documented assumptions.
  - This does **not** approve the final scoring formula or every schema field.
- **D-IMPL-04 (logging helper):** Approved with limitations.
  - Redaction is best-effort, not a guarantee that every secret is removed. Sensitive values must not be logged.
  - It must be documented and tested that importing `routesmart` configures the `routesmart` logger (`docs/LOGGING.md`; `tests/test_log.py::test_importing_routesmart_configures_the_routesmart_logger`).
- **D-IMPL-05 (network guard):** Approved as a layered guard.
  - The offline suite must fail closed if isolation cannot be established.
  - Namespace proof and pytest must run in the same namespace.
  - It is not a production sandbox.
- **D-IMPL-06 (Actions pinning):** Approved. Pin actions to full commit SHAs, record upstream versions, and use a controlled, reviewed update process.
- **D-IMPL-07 (development dependency lock):** Approved.
  - Keep `requirements/dev.lock.txt` as a **development-tooling lock**, separate from the declared dependency ranges.
  - Document updates, and verify the two-stage installation in CI.
  - Do not represent it as a production dependency lock.
- **D-IMPL-08 (CI isolation):** The isolation requirement is approved. **Runtime behaviour remains unverified until GitHub Actions runs.** Verify on CI: the actual runner path, the runner-user identity, IPv4 and IPv6 isolation, and fail-closed behaviour.
  - *Verification note (added 2026-10-27, Gate 5; the owner wording above is unchanged):* GitHub Actions run 40515177175 verified the runner path (CI-only sudo fallback), the runner-user identity (`uid=1001 euid=1001 gid=1001`), and IPv4/IPv6 isolation (loopback-only). See the D-IMPL-08 runtime verification addendum. Fail-closed behaviour is covered by the local regression tests. It was not triggered in that run, because isolation succeeded.
  - *Gate 6 evidence assessment (added 2026-10-27; the owner wording and conditions above are unchanged):* The same fail-closed regression tests also **ran on the GitHub runner**. In runs 40515177175 and 40519555271, pytest's per-file progress shows `tests/test_offline_script.py` with 34 passing tests, matching local collection.
    - **Verified on CI:**
      - (a) unit-level fail-closed behaviour with stub and fake inputs: namespace-creation failure exits 2 without pytest; the opt-in is ignored outside GitHub Actions; root is refused; unexpected IPv4/IPv6 outcomes and extra interfaces fail closed before pytest;
      - (b) real namespace establishment and verification.
    - **Not verified on CI:** (c) a **runner-level failure path** in which the script itself refuses to run pytest. In both runs the unprivileged path failed on the runner and the script took the approved sudo path, which is a fallback, not a fail-closed exit.
    - **Status of the "fail-closed behaviour" CI condition: open, owner decision required.** *(Status when this assessment was written. Resolved 2026-10-27: the owner accepted the existing CI evidence; see "Owner decisions: Gate 6".)* A safe runner-level verification method has been proposed for owner approval.

### R2: M4 historical labels: APPROVED
The SUPERSEDED labels for D-001, D-002, D-004 and D-007 are confirmed, conditional on the Gate 1 entry-by-entry check.
- D-PROP-02/08 are not described as replacements for D-002, and D-PROP-04/05 are not described as replacements for D-007; they are "related to".
- D-004 cites CLAUDE.md §5 and §7.
- The correction note is under the table above.

### R3: CI-only sudo fallback: APPROVED with an enforcement requirement
The fallback must work only on GitHub Actions: the opt-in is insufficient without `GITHUB_ACTIONS=true`. The required tests cover:
- the opt-in is off by default;
- it cannot activate outside GitHub Actions;
- the approved CI path stays fail-closed;
- tests execute as the runner user, not root.

Implemented in Gate 2; see the D-IMPL-08 amendment. The sudo path is **not** claimed verified until the actual CI workflow demonstrates it.

### R4: Feature branch and pull request policy: APPROVED as repository policy
- Changes are prepared on a feature branch and reviewed through a pull request, never committed directly to `main`.
- No merge before CI verification and the formal Phase 1 exit review.
- This approves the **policy only**, not Git operations. Each branch creation, staging, commit, push or PR needs explicit operational authorisation, with the exact operation and file list presented first. Recorded in CLAUDE.md §13.

### R5: Absolute local paths in TEST_RESULTS.md: leave unchanged
Two lines of verbatim historical Task 001 output contain the owner's local username and path (`/home/dhrubapatwary/...`). The repository is **public**, so they would be published. They stay unedited by owner decision unless a concrete security or privacy issue is identified.

### R6: Unprotected `main`: recorded risk, no change
`main` has no branch protection (GitHub API: "Branch not protected", checked 2026-10-27). This is recorded as a repository risk for owner consideration. No settings changes are authorised.

## Changes log (Gate 2, 2026-10-27)
- **R-026 (R3):** `scripts/test-offline.sh` now:
  - requires `GITHUB_ACTIONS=true` for the sudo path;
  - refuses euid 0;
  - prints its identity and namespace evidence;
  - exports `ROUTESMART_OFFLINE_NETNS`.

  New tests: `tests/test_offline_script.py` (17, stub-based) and `tests/test_offline_isolation.py` (1, runs only under the offline script). Mutation check: removing the `GITHUB_ACTIONS` condition fails 6 tests, and removing the root refusal fails 1.
- **R-027 (D-IMPL-04 condition):** added an explicit test that importing the package configures the `routesmart` logger.
- **R-028 (D-IMPL-05):** added the scoped `allow_subprocesses` fixture. It lifts only the child-process block, and only for the script tests.
- **R-029 (Gate 4 decision 1, 2026-10-27):** Added committed regression tests for the probe's IPv4/IPv6 outcomes in `tests/test_offline_script.py`. There are 17 new tests, using the real probe source with fake `_socket`/`if_nameindex`/`execv`, so no network is used.
  - Mutation check: accepting any errno fails 12 tests; IPv4 also accepting `ECONNREFUSED` fails 1; not rejecting a successful connect fails 2; skipping the IPv6 check fails 8; removing the interface check fails 1.
  - The probe itself is unchanged.
- **R-030 (Gate 5, recorded 2026-10-27):** Remote CI evidence recorded.
  - **Run:** run 40515177175 on `43e6966` (PR #1, draft, base `main`) concluded `success`: 37 s workflow, 34 s job.
  - **Steps:** all passed: the two-stage locked install (bootstrap pip 26.2.1 → pinned 26.2.2), `pip check`, `check_lock.py`, the `.gitignore` check, ruff lint and format, strict mypy, pytest in the network namespace, bandit and pip-audit.
  - **Isolation:** the sudo path ran as uid 1001, the namespace was verified, and pytest gave 331 passed / 1 deselected with the namespace proof test passing.
  - **Decision record:** the D-IMPL-08 verification addendum was added. No decision wording or conditions were changed.
  - **Documentation only:** no code, test, dependency or workflow change.
- **R-031 (Gate 6 remediation, 2026-10-27):** Documentation-currency corrections after the Gate 6 exit review.
  - **CHECKPOINT:** the stale "uncommitted" status and next action in the Gate 5 entry are annotated as superseded, and a new Gate 6 entry was added.
  - **ROADMAP:** the current status and the Gates 3–6 table now record `b64cb17` and CI run 40519555271.
  - **DECISIONS:** a Gate 6 evidence assessment was added under the D-IMPL-08 verification note. The CI logs show the fail-closed tests ran on the runner; a runner-level failure path was not exercised, so the condition stays **open** for an owner decision.
  - **TEST_RESULTS:** a Gate 6 evidence section was added.
  - No decision wording or conditions were changed, and there are no code, test, dependency or workflow changes.

---

## Owner decisions: Gate 6 (recorded 2026-10-27)

These were recorded on 2026-10-27 from the owner's Gate 6 decision message, based on the completed Gate 6 review. No earlier date is claimed. Earlier records, including the original D-IMPL-08 wording, are unchanged.

### G6-1: D-IMPL-08 CI evidence: ACCEPTED
- **Decision:** the owner accepts the existing CI evidence as satisfying the approved D-IMPL-08 requirement to verify on CI the actual runner path, the runner-user identity, IPv4 and IPv6 isolation, and fail-closed behaviour.
- **Fail-closed evidence (controlled inputs):** the fail-closed tests in `tests/test_offline_script.py` execute on GitHub Actions against the real script and the real probe source, with stubbed `unshare`/`sudo` and fake sockets. They passed on the runner in runs 40515177175, 40519555271 and 40521272209: 34 tests per run, according to the per-file progress lines.
- **Real-runner evidence:** the runner's successful namespace path is independently verified in the same runs:
  - the CI-only sudo path;
  - privileges dropped to uid 1001;
  - `namespace verified (lo only; IPv4/IPv6 unreachable) … uid=1001 euid=1001 gid=1001`;
  - `tests/test_offline_isolation.py` passed.
- **Not demonstrated and not claimed:** a real refusal by the script on the GitHub runner itself.
- **Limitation preserved:** the unprivileged namespace path remains **unverified on GitHub**. The evidence covers the observed runs only; it is not production sandbox certification.
- **Unchanged:** the fallback still requires both `ROUTESMART_OFFLINE_ALLOW_SUDO=1` and `GITHUB_ACTIONS=true`, and the script still fails closed.

### G6-2: Phase 1 exit: APPROVED
- **Decision:** the owner approves the Phase 1 exit.
- **Basis:**
  - the completed Gate 6 review;
  - the verified CI result on commit `8bcc143f57e4d81bae1466ee6844e8ba70822120` (GitHub Actions run 40521272209, success);
  - acceptance of the D-IMPL-08 evidence interpretation in G6-1.
- **Location of the work:** Phase 1 artefacts remain on `feature/task-002-foundation` in draft PR #1. **They are not merged into `main`.** *(As of this decision. Merged 2026-10-27 as `baa94234b90007bf5188326a409dcc3cc4f86d8c` under a separate owner authorization; see R-033.)*

### G6-3: PR #1 merge: NOT authorized by this decision
- Merge authorization is separate. It must be obtained explicitly after the CI run on the final documentation commit succeeds.
- *Subsequent event (2026-10-27):* after run 40551958918 on `34deb8c` succeeded, the owner separately authorized the merge, and PR #1 was merged; see R-033. This decision record itself is unchanged.

### G6-4: Task 003: not started
- Task 003 has not started.
- Before implementation begins, its scope and stopping point must be recorded in `ROADMAP.md` (Task log) and `CHECKPOINT.md` (CLAUDE.md §14), and its required authorization must be obtained.

## Changes log (Gate 6 decisions, 2026-10-27)
- **R-032:** Recorded owner decisions G6-1 to G6-4.
  - **Status notes:** the earlier "open, owner decision required" note (D-IMPL-08 Gate 6 assessment) is marked as resolved, and an owner-acceptance bullet was added to the D-IMPL-08 current status.
  - **Other files:** CHECKPOINT, ROADMAP, TEST_RESULTS and the README status line were updated.
  - **Unchanged:** decision wording, conditions and approval records. There are no code, test, script, workflow or dependency changes.

## Changes log (post-merge, 2026-10-27)
- **R-033:** Recorded the PR #1 merge and the post-merge CI result.
  - **Merge:** separate owner authorization (2026-10-27) to merge PR #1 only. Merged at 17:45:05Z with a merge commit, `baa94234b90007bf5188326a409dcc3cc4f86d8c` (parents `2b302e0` and `34deb8c`; tree identical to the reviewed head `34deb8c`).
  - **Post-merge CI:** run 40553520066 on `main` succeeded, with 331 passed and 1 deselected, and the same namespace evidence: sudo path, uid/euid/gid 1001, lo only, IPv4/IPv6 unreachable.
  - **Annotations:** G6-2's "not merged" statement and G6-3 are annotated, with their wording unchanged. CHECKPOINT, ROADMAP, README and TEST_RESULTS were updated.
  - **Unchanged:** approval records and the original D-IMPL-08 wording. No code, test, script, workflow, dependency or settings changes.
  - **Unchanged limitations:** a real refusal on the runner was not demonstrated, and the unprivileged path remains unverified on GitHub.

---

## Proposed: Phase 2 planning (2026-10-27), awaiting owner approval

These are proposals, not approved decisions. Nothing here may be implemented until the owner approves it explicitly.

*(Annotation 2026-10-27: the owner approved P2-PROP-01..04 on 2026-10-27, with the conditions recorded in "Owner decisions: Phase 2 planning" below.)*

### P2-PROP-01: Task 003 scope
- **Status:** PROPOSED (awaiting owner approval) *(Annotation 2026-10-27: **APPROVED by the owner**; see "Owner decisions: Phase 2 planning" below. The proposal text is kept unchanged as history.)*
- **Proposal:** Task 003 is "Deterministic Sample-Data Option Providers for BLR → MAA", Phase 2 increment 1. The full scope, acceptance criteria, exclusions and stopping point are in `ROADMAP.md` (Task log).
- **Basis:** builds only on approved decisions:
  - D-PROP-01..04: sample data;
  - D-PROP-07: mocked slice first;
  - D-IMPL-03: contract direction, schema unchanged.
- **Requires no:** new dependency, schema change, scoring decision, API decision or client decision.
- **Consequences:** produces sample options for later increments. Scoring, API and client remain unstarted.

### P2-PROP-02: Travel-date interpretation for queries
- **Status:** PROPOSED (awaiting owner approval). There is **no existing convention**. The contract compares aware timestamps as instants (`docs/TRAVEL_OPTION_CONTRACT.md`), but the project has no travel-date concept. *(Annotation 2026-10-27: **APPROVED by the owner**; see "Owner decisions: Phase 2 planning" below. The proposal text is kept unchanged as history.)*
- **The question:** "Reject dates before the supplied current date" needs a definition, because the options give different results for "today".
- **Recommended (A):** the travel date is a timezone-aware datetime whose **calendar day in its own UTC offset** is the travel day. Compare that day with the current date converted to the same offset; reject if earlier. For example, travel `2026-11-02T00:00+05:30` with current `2026-11-02T10:00+05:30` is accepted (same day). Sample departures are generated on that travel day, in that offset.
- **Alternative (B):** reject if the travel datetime is earlier, as an instant, than the current datetime. This would reject "today at 00:00" once the current time is later than midnight.

### P2-PROP-03: Place identifiers for sample options
- **Status:** PROPOSED (awaiting owner approval) *(Annotation 2026-10-27: **APPROVED by the owner**; see "Owner decisions: Phase 2 planning" below. The proposal text is kept unchanged as history.)*
- **Proposal:** all sample options for every mode use the query's city-level codes, `origin="BLR"` and `destination="MAA"`. Place-code typing (IATA vs station codes such as SBC/MAS) is deferred to the Phase 2 schema gate (D-IMPL-03, `docs/TRAVEL_OPTION_CONTRACT.md` "Deliberately deferred"). This needs no schema change.
- **Alternative:** mode-specific free-text places, e.g. "SBC"/"MAS" for rail. The contract permits this too, but it would pre-empt the deferred place-code decision.

### P2-PROP-04: Phase 2 increment plan
- **Status:** PROPOSED (awaiting owner approval) *(Annotation 2026-10-27: **APPROVED by the owner**; see "Owner decisions: Phase 2 planning" below. The proposal text is kept unchanged as history.)*
- **Proposal:** deliver Phase 2 in owner-gated increments, as set out in `ROADMAP.md`, "Phase 2 plan":
  1. Task 003, sample providers;
  2. scoring, once the scoring model is approved;
  3. schema extensions and the API, once the schema is approved and an API framework is chosen;
  4. the minimal client, once a client approach is chosen.
- **Unchanged:** Phase 2's tasks and acceptance criteria. Each increment needs its own scope approval.

**Note:** the scoring-model *proposal* is a Task 003 deliverable (item 7). It will be added here as PROPOSED only if Task 003 is approved. It is not added now.

## Changes log (Phase 2 planning, 2026-10-27)
- **R-034:** Added proposals P2-PROP-01..04, each PROPOSED and awaiting owner approval.
  - **ROADMAP:** the Phase 2 plan and the Task 003 task-log entry, both marked PROPOSED.
  - **CHECKPOINT:** a new top entry, with the previous entry's "not merged / next action" lines annotated.
  - **TEST_RESULTS:** run 40555092439.
  - **Post-merge status reconciled:** PR #2 merged as `3510ade`; latest CI run 40555092439 succeeded.
  - **Unchanged:** no approved decision changed or added. No code, test, script, workflow or dependency changes.

---

## Owner decisions: Phase 2 planning (recorded 2026-10-27)

Recorded on 2026-10-27 from the owner's approval message for the Phase 2 planning and the Task 003 proposal. The proposals above are unchanged and annotated.

### P2-PROP-01: Task 003: APPROVED
- **Decision:** Task 003 is approved as documented in `ROADMAP.md` (Task log), including the code location (`src/routesmart/providers/`), fictional operator names, fixed provenance timestamps, scope, acceptance criteria, exclusions and stopping point.
- **Condition:** the existing `TravelOption` contract remains authoritative. If implementation needs a schema change or a new dependency, stop and request approval.

### P2-PROP-02: Travel-date semantics: APPROVED (option A)
- **Decision:** both the travel date and the caller-supplied current date must be **timezone-aware**.
- **Rule:** convert the supplied current instant into the **travel date's timezone**, then compare **calendar dates** in that timezone. Accept a travel date that is today or later; reject one before today.
- **Constraint:** validation must **not read the system clock**.
- **Rejected:** option B (instant comparison).

### P2-PROP-03: Sample place names: APPROVED
- **Decision:** use `BLR` and `MAA` from the query for all five modes.
- **Deferred:** mode-specific airport, station and other location mapping, to the relevant future contract or design gate.

### P2-PROP-04: Phase 2 plan: APPROVED as the proposed roadmap
- **Decision:** the four-increment plan is approved as the **planning structure** only.
- **Not authorized by this decision:** implementation of any later increment. Scoring, schema extensions, API framework selection and the client/PWA approach each remain subject to their own approval gates.

### Execution authorization (same message)
- Create `feature/task-003-sample-providers` from verified `origin/main` at `3510aded7a90a727b29c1c120cf6de3072b343f8`, carrying the four planning-document edits. Never commit directly to `main`.
- Record the approvals in the existing documents; no standalone Task 003 document.
- Implement only Task 003's approved scope, run the required checks, and open a **draft PR**.
- Stop when the draft PR is ready for owner review: **no merge** and no further increment.
- Preserve historical entries and approval records. No branch-protection changes, history rewrites, unapproved dependencies, live providers or external side effects.

---

## Proposed: scoring model (Task 003 deliverable, 2026-10-27), awaiting owner approval

This is a **proposal only**. No scoring code exists or is authorized. Approving it is a separate owner decision, and implementing it is Phase 2 increment 2, which needs its own authorization (P2-PROP-04).

### P2-PROP-05: Scoring model for travel options
- **Status:** PROPOSED (awaiting owner approval)
- **Inputs:** only `TravelOption` fields (CLAUDE.md §3); never `provider_metadata`.
- **Model:** a configurable weighted sum of three normalised components, `score = w_time·time + w_cost·cost + w_risk·risk`, with `w_time + w_cost + w_risk = 1` and each weight in [0, 1]. **Lower is better.** The score is a relative ranking aid within one query's comparison set. It is **not a probability**, and it is not comparable across queries.
- **Components and units:**
  - **time:** `duration`, in minutes. Departure and arrival times are not scored, so road options whose times are `not_applicable` stay comparable.
  - **cost:** `total_cost.amount`, in INR. Options in any other currency are not scored (no cross-currency handling; deferred in `docs/TRAVEL_OPTION_CONTRACT.md`).
  - **risk:** schema version 1 has **no risk inputs** (deferred to the Phase 2 schema gate, D-IMPL-03), so no risk component can be computed yet. See open question 1.
- **Normalisation:** min–max within the comparison set, `(x − min) / (max − min)`, giving 0 for the best and 1 for the worst. If every option has the same value, the component is 0 for all of them. This is deliberately relative: adding or removing an option can change the others' scores, and the explanation must say so.
- **Missing data:** values are never substituted.
  - An option whose `duration` or `total_cost` is unavailable is **unscored**. It is still listed, with the `unavailable` reason shown.
  - The alternative of scoring on the remaining components with renormalised weights is not proposed, because it compares options on different bases.
- **Constraints:**
  - `sold_out` options are excluded from ranking and listed with the reason.
  - `waitlisted` options are ranked, but flagged with the waitlist position. That position is **not** a confirmation probability.
  - `unknown` availability is ranked and flagged.
- **Ties:** equal scores (compared exactly as `Decimal`) are broken deterministically by lower cost, then shorter duration, then `option_id`.
- **Explanation:** every result shows:
  - each component's raw value, normalised value and weight;
  - the weights used;
  - the data origin and freshness (sample data is labelled **sample**);
  - unscored and excluded options with their reasons.

  Nothing claims that the top option is guaranteed fastest, cheapest or safest (CLAUDE.md §8).
- **Proposed default weights:** `w_time = 0.5`, `w_cost = 0.5`, `w_risk = 0` until a risk component exists. This is a placeholder for the owner to set, not a product judgement.
- **Open questions for the owner:**
  1. **Risk before schema support:** either (a) keep `w_risk = 0` and disclose "risk not assessed", or (b) block scoring until the schema gate adds risk inputs.
  2. **Waitlisted rail:** keep it as ranked and flagged, or exclude it until confirmation-likelihood data exists?
  3. **Default weights,** and whether users may change them.
  4. **Min–max vs fixed reference ranges** (for example, 0–12 h and ₹0–₹10,000). Fixed ranges keep scores stable when options change, but they need maintained bounds.

## Changes log (Task 003, 2026-10-27)
- **R-035:** Recorded the owner's approval of P2-PROP-01..04 and the execution authorization.
  - The original proposal text is unchanged; each proposal's status line is annotated.
  - Added the **P2-PROP-05** scoring-model proposal (PROPOSED only).
  - Task 003 implementation is on `feature/task-003-sample-providers`: `src/routesmart/providers/` plus tests. No schema change and no new dependency.
  - **Unchanged:** all earlier approval records.

## Changes log (post-merge Task 003, 2026-10-27)
- **R-036:** Recorded the PR #3 merge (Task 003, Phase 2 increment 1).
  - **Merge:** merged 2026-10-27T19:00:23Z. Final head `5aea0c095272e7ff88845bcd8ba7f5ee131c302e`; merge commit `725e2660be8fca45021b8a75c5d623337706cfe4` (parents `3510ade` and `5aea0c0`; tree identical to the head).
  - **CI:**
    - Run 40563608783 on the PR head succeeded.
    - Push run 40565168769 on the merge commit succeeded.
    - Each run is evidence for its own commit only.
  - **Unchanged:**
    - P2-PROP-05 remains **PROPOSED**, with its four open questions unresolved;
    - the approval records and proposal wording of P2-PROP-01..04.
  - **Merge approval is not increment 2 approval.** Increment 2 needs the scoring decisions and separate scope approval.
  - **Updated:** ROADMAP, CHECKPOINT, TEST_RESULTS and the README status line. No code, test, script, workflow, dependency or settings changes.
