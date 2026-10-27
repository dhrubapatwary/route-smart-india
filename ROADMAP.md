# RouteSmart India --- Product Roadmap

**Status:** Task 001 (baseline audit) is done. The owner approved
decisions D-PROP-01..08 on 2026-10-27 (see `DECISIONS.md`). **Phase 1
exit was approved by the owner on 2026-10-27** (Gate 6; DECISIONS.md
G6-2).
**Current status (2026-10-27, Task 003 in progress on a feature branch):**
-   **Approved (owner, 2026-10-27):** P2-PROP-01..04 (`DECISIONS.md`,
    "Owner decisions: Phase 2 planning"). The Phase 2 plan is approved as
    a planning structure only; later increments need their own
    authorization.
-   **Task 003:** implemented on `feature/task-003-sample-providers`
    (branched from `main` @ `3510ade`). Stopping point: a **draft PR**
    for owner review. **No merge**, and no further increment.
-   **Proposed, not approved:** the scoring model (P2-PROP-05).

**Earlier status (2026-10-27, Phase 2 planning; verified against GitHub; historical):**
-   **`main`:** `3510aded7a90a727b29c1c120cf6de3072b343f8`, the merge commit of
    **PR #2** (post-merge documentation reconciliation; merged
    2026-10-27T17:55:15Z). **Latest CI:** run 40555092439 (`push`, `main`
    @ `3510ade`), **success**: `331 passed, 1 deselected`; all checks
    passed; CI-only sudo namespace path; uid/euid/gid 1001; namespace
    verified (lo only; IPv4/IPv6 unreachable). There are no open PRs.
-   **Phase 2:** planning only. The plan below is **PROPOSED, awaiting
    owner approval**. **Task 003** (Phase 2, increment 1) is proposed in
    the Task log and has **not started**. Implementation is blocked
    until the owner approves its scope and decisions P2-PROP-01..04
    (`DECISIONS.md`).

**Earlier status (2026-10-27, after the PR #1 merge; historical):**
-   **Merged:** the Phase 1 work (`43e6966` Task 002; `b64cb17`,
    `8bcc143` and `34deb8c` documentation) is **merged into `main`**.
    PR #1 was merged at 2026-10-27T17:45:05Z with merge commit
    `baa94234b90007bf5188326a409dcc3cc4f86d8c`, after separate owner authorization.
-   **Content preserved:** the merge commit's parents are `2b302e0` and
    the reviewed PR head `34deb8c`. Its tree is identical to `34deb8c`,
    and all four reviewed commits are in `main`'s history.
-   **CI:**
    -   PR head `34deb8c`: run 40551958918, success.
    -   **Post-merge on `main` (`baa9423`): run 40553520066, success.**
        `331 passed, 1 deselected`; CI-only sudo namespace path;
        uid/euid/gid 1001; namespace verified (lo only; IPv4/IPv6
        unreachable).
-   **Earlier validation:** Gate 3 local validation passed. Gate 5 runs
    40515177175 and 40519555271 succeeded. The Gate 6 exit decision
    rests on run 40521272209 on `8bcc143`.
-   **D-IMPL-08:** the owner accepted the existing CI evidence (G6-1).
    The fail-closed tests ran on CI with controlled inputs, and the real
    runner's namespace path was verified separately. A real refusal on
    the runner was **not** demonstrated, and the unprivileged path
    remains **unverified** on GitHub.
-   **Unchanged:** `main` branch protection (not part of this work;
    R6).
-   **Task 003:** not started; blocked until its scope and stopping
    point are recorded (Task log and `CHECKPOINT.md`) and its required
    authorization is obtained (G6-4).

Older Task log entries below are historical; the latest entry is
authoritative.\
**Pilot route:** Bengaluru (BLR) → Chennai (MAA).\
**Product objective:** Explainable multimodal recommendations balancing
time, cost and risk.

## Delivery principles

1.  Deliver a small end-to-end working slice early; do not wait for all
    live providers.
2.  Treat all provider integrations, API access, pricing, usage rights,
    coverage and data freshness as unverified until recorded in the
    provider feasibility register.
3.  Keep mocked data clearly labelled and separate from live data.
4.  Run relevant tests and security checks continuously, not only in the
    final phase.
5.  Gate each phase on observable acceptance criteria. A task being
    implemented is not the same as being accepted.
6.  Use the simplest architecture that preserves logical component
    boundaries. Independently deployed microservices are not an MVP
    requirement unless justified by evidence.
7.  Obtain approval before material costs, production deployment,
    destructive data changes or consequential live actions.

## Phase 1 --- Repository Baseline, Feasibility and Foundation

**Phase status:** **exit approved by the owner on 2026-10-27** (Gate 6;
DECISIONS.md G6-1 and G6-2). The evidence is the Gate 6 review and CI run
40521272209 (success) on `8bcc143`. The scope and acceptance criteria
below are unchanged. The work was merged into `main` on 2026-10-27 (PR #1,
merge commit `baa94234b90007bf5188326a409dcc3cc4f86d8c`; post-merge CI run 40553520066 succeeded).

**Goal:** Establish a trustworthy baseline before implementation.

### Tasks

-   Inspect the repository, Git history/status, existing code,
    dependencies, tests, CI, migrations and documentation. Preserve
    existing work.
-   Reconcile `CLAUDE.md`, `ROADMAP.md` and `README.md`; record
    conflicts and proposals in `DECISIONS.md`.
-   Establish or verify modular `requirements/` files: `base.txt`,
    `flight.txt`, `rail.txt`, `road.txt`, `dev.txt`. Do not add
    dependencies without a reason.
-   Establish `.env.example` and root `.gitignore` rules for virtual
    environments, secrets, caches and generated artifacts.
-   Establish `CHECKPOINT.md`, `DECISIONS.md` and `TEST_RESULTS.md`,
    preserving any existing history.
-   Create a provider feasibility register covering flight/schedule
    data, aircraft tracking, weather, road/tolls/EV, rail/waitlist data
    and ground-transport alternatives.
-   Record the existing test and security-check baseline. Add `pytest`,
    `pytest-asyncio`, `pytest-mock`, `bandit` or other tools only if
    needed and compatible with the repository.
-   **Foundation (D-PROP-06; Task 002):**
    -   Add `requirements/weather.txt` and `requirements/testing.txt`
        alongside the five files above, with documented ownership and
        inclusion rules.
    -   Add `pyproject.toml` tool configuration.
    -   Add a minimal shared, provider-neutral travel-option contract
        with tests. Phase 2 extends it and approves it.
    -   Add a shared logging helper.
    -   Configure pytest/pytest-asyncio, ruff, mypy, bandit and
        pip-audit.
    -   Add a GitHub Actions CI workflow that needs no provider
        credentials.

### Acceptance criteria

-   Repository structure and current Git state are documented
    accurately.
-   Existing changes are preserved; secrets are not added to version
    control.
-   Tracking documents identify verified facts, proposals, open
    questions and the next task.
-   Each candidate provider has a status, evidence or explicit evidence
    gap, usage/pricing/access questions and a next verification action.
-   No claim is made that a provider is suitable, free or permitted
    without evidence.
-   Relevant baseline checks are run where feasible; skipped checks have
    a reason.
-   Foundation tooling installs into `route_smart_env`. pytest, ruff
    (lint and format), mypy, bandit and pip-audit run locally, with
    actual results recorded in `TEST_RESULTS.md`. Findings are fixed or
    have a documented exception.
-   The CI workflow has actually run on GitHub and its observed result
    is recorded. Local workflow validation alone does not satisfy this.
    It needs the owner to commit and push.
-   The owner has reviewed the working-tree changes, including the
    untracked governance files.
-   **Gate:** no live integration commitment until feasibility and
    approval requirements are understood. The owner explicitly approves
    the Phase 1 exit. Completing Task 002 alone does not complete
    Phase 1.

## Phase 2 --- Contract and Early Vertical Slice (Mocked)

**Goal:** Demonstrate the core product end to end with deterministic
mock data.

### Phase 2 plan (PROPOSED 2026-10-27; awaiting owner approval, P2-PROP-04)

*(Annotation 2026-10-27: the owner **approved** this plan as the proposed
roadmap (P2-PROP-04). It approves the planning structure only, not the
implementation of increments 2–4.)*

The Phase 2 tasks and acceptance criteria further below are unchanged and
remain the authoritative definition of the phase. This plan only proposes
how to deliver them in owner-gated increments. Each increment needs its own
recorded scope, stopping point and owner authorization before work starts
(CLAUDE.md §13–§14).

| Increment | Proposed content | Owner decisions needed first | Status |
|---|---|---|---|
| **1: Task 003** | Deterministic sample-data option providers for BLR → MAA (all five modes) and a concurrent collector, using the existing `TravelOption` contract unchanged. Also a scoring-model *proposal* (documentation only). | P2-PROP-01 (scope), P2-PROP-02 (travel-date interpretation), P2-PROP-03 (sample place identifiers) | **Approved 2026-10-27**; implemented on `feature/task-003-sample-providers`; draft PR for owner review (not merged) |
| 2 (candidate) | Deterministic scoring module | Approval of the scoring model: weights, normalisation, directionality, missing data, ties (CLAUDE.md §8; D-PROP-07 open question) | Not proposed in detail |
| 3 (candidate) | Schema extensions and the backend API contract and service | Final schema approval (D-IMPL-03 Phase 2 gate: risk inputs, cost breakdown, place codes, API envelope); API framework choice (a new dependency) | Not proposed in detail |
| 4 (candidate) | Minimal client/PWA view | Client/PWA approach (ROADMAP Phase 7 requires it to be selected in `DECISIONS.md`) | Not proposed in detail |

**Dependencies:**
-   Increment 2 consumes increment 1's options.
-   Increment 3's API must exist before the client depends on it
    (CLAUDE.md §3).
-   The order of increments 2–4 is a proposal.

**Approval gates (existing, unchanged):**
-   Schema and scoring semantics must be approved before any live
    provider data is used (Phase 2 gate below).
-   Scores are not probabilities (CLAUDE.md §8).
-   No live providers, new dependencies, costs or deployment without
    approval (CLAUDE.md §4, §6, §11).

**Stopping conditions for every increment:** stop and ask if work would
need any of the following:
-   a schema change;
-   a new dependency or framework;
-   a scoring, API or client decision;
-   live or network access;
-   a change to the network guard or CI isolation;
-   any work beyond the recorded stopping point.

### Tasks

-   Extend and approve the provider-neutral travel-option schema
    started in Task 002. Define the backend API contract **before** the
    PWA/client depends on it.
-   The slice answers: "For Bengaluru to Chennai on a given date, which
    travel option is recommended, and why?" The answer must be
    explainable (D-PROP-07). Flight, rail, road, cab and bus inputs are
    sample data (D-PROP-01..04).
-   Define normalized representations for time, cost, risk, data
    freshness, assumptions and unavailable fields.
-   Implement mock flight, rail and road options for BLR--MAA.
    Weather/disruption context can be mocked where it helps illustrate
    the model.
-   Implement a deterministic scoring module and API that consumes the
    common option schema.
-   Create a minimal PWA/client view that requests the API and presents
    ranked options, component scores, trade-offs and data provenance.
-   Keep the API contract independent of the UI framework and
    provider-specific response formats.

### Proposed scoring model

A candidate model is a configurable weighted aggregation such as:

`Score = w_time × TimeComponent + w_cost × CostComponent + w_risk × RiskComponent`

Normalize components to a common documented scale and define
directionality so a better option scores consistently. Weights should
sum to 1. Treat weights and normalization choices as **proposals** until
approved and recorded in `DECISIONS.md`. Do not label the score as a
probability. Document missing-data behavior, ties, constraints and score
explanations.

### Acceptance criteria

-   A user can request BLR--MAA options and see at least one mocked
    option from each represented mode.
-   API schema validation and deterministic scoring are tested.
-   Tests cover missing/invalid fields, ties, empty option sets and
    unavailable component data.
-   UI labels mocked data as simulated; it does not imply live
    availability or bookability.
-   Ranking and component explanations are reproducible from documented
    inputs.
-   Unit and API tests pass, or failures are recorded and the phase
    remains open.
-   **Gate:** approve the schema and scoring semantics before using live
    provider data.

## Phase 3 --- Provider Feasibility and Data Adapters

**Goal:** Add only justified data adapters behind the common contract.

### Candidate workstreams

-   **Flights/schedules:** evaluate SerpApi as a candidate (D-PROP-01).
    Amadeus Self-Service is excluded because it was decommissioned on
    17 Jul 2026.
-   **Aircraft tracking/delay context:** assess AeroDataBox via RapidAPI
    and verify the exact fields and coverage needed.
-   **Weather:** assess OpenWeatherMap and/or Tomorrow.io.
-   **Road:** assess TollGuru and/or Mappls for route, toll, fuel and EV
    information. No trial, subscription or paid cost without separate
    approval (D-PROP-04).
-   **Rail:** investigate permitted, reliable access to relevant rail
    availability/waitlist data, such as manual user input or a licensed
    data partner (D-PROP-02). Never bypass CAPTCHA, login or other
    access controls, and never store or automate users' railway
    credentials.
-   **Ground transport alternatives:** assess Uber, Ola, bus or other
    sources only if a suitable permitted API/data source is identified.

### Tasks

-   For each selected source, record official documentation, access
    state, pricing/quota, permitted use, coverage, fields, freshness,
    authentication, rate limits and failure behavior.
-   Implement typed async adapters using `httpx.AsyncClient()` where
    appropriate, with timeouts and bounded concurrency.
-   Keep adapters replaceable and provide mocks/fakes for tests.
-   Map provider responses into the shared schema; preserve source and
    observation timestamps where available.
-   Add caching only with an explicit freshness/expiry policy.

### Acceptance criteria

-   Each implemented adapter has a feasibility status and evidence
    record.
-   Tests cover valid responses, empty/malformed responses, timeouts,
    rate limits, provider errors and missing fields.
-   Credentials come from environment configuration and never appear in
    logs.
-   Mocked tests run without live credentials.
-   Live tests are separately marked, bounded, permitted and approved
    where required.
-   Unavailable providers do not block the mock vertical slice.
-   **Gate:** no provider is represented as production-ready solely
    because a basic request succeeded.

## Phase 4 --- Database and State Management

**Goal:** Persist user preferences and travel state safely when
justified by the product slice.

### Tasks

-   Confirm which state must be persisted before designing tables.
-   Define Supabase PostgreSQL schemas, migrations, constraints, indexes
    and retention needs.
-   Evaluate `asyncpg` for backend access and use parameterized queries.
-   Define user identity, ownership, authorization and least-privilege
    database roles.
-   Use Supabase Auth and `supabase-js` for appropriate client
    authentication/Realtime features.
-   Enable and test RLS for tables exposed through Supabase APIs.
-   Explicitly design authorization for backend `asyncpg` access; direct
    privileged connections do not automatically inherit the end user's
    RLS context.

### Acceptance criteria

-   Migrations can be applied and validated in the intended development
    environment.
-   Schema and constraints have tests for valid and invalid data.
-   Authorization tests cover access to owned versus other users'
    records.
-   Secrets are not committed; the service-role key is never exposed to
    the client.
-   Database failure, timeout and connection cleanup behavior are
    tested.
-   **Gate:** no production data or destructive migration without
    explicit approval and a rollback/backup plan.

## Phase 5 --- Recommendation Quality and Risk Model

**Goal:** Improve the recommendation engine with transparent, tested
time/cost/risk comparisons.

### Tasks

-   Refine time estimates, cost components and risk indicators based on
    available data.
-   Document units, normalization ranges, directionality, weight
    choices, missing-data policy and tie-breaking.
-   Separate observed facts, provider estimates and model-derived
    inferences.
-   Add data freshness and confidence/uncertainty indicators where
    defensible.
-   Test sensitivity to weights and incomplete inputs.
-   Do not call a risk score a probability unless statistically
    calibrated and validated.

### Acceptance criteria

-   Same inputs produce deterministic outputs under the documented
    model.
-   Each recommendation exposes its component scores and key trade-offs.
-   Unknown or stale inputs are surfaced rather than silently treated as
    reliable.
-   Tests cover boundaries, missing data, conflicting signals and
    ranking stability.
-   Product wording does not promise a guaranteed fastest, cheapest or
    safest journey.
-   **Gate:** scoring model and user-facing explanations are documented
    and reviewed before production use.

## Phase 6 --- Intelligent Safety Net (Opt-in Recommendations)

**Goal:** Demonstrate how changing travel conditions could lead to
timely alternative recommendations without taking consequential action
automatically.

### Tasks

-   First validate data access, permitted monitoring frequency and
    relevant provider limitations.
-   Begin with simulated waitlist/disruption events and deterministic
    tests. Cab and bus alternatives use simulated data only and are
    recommendations only (D-PROP-03).
-   Define thresholds, monitoring cadence, stale-data handling, retries,
    deduplication, idempotency and notification preferences.
-   Present alternatives with source, timestamp, estimated cost/time,
    uncertainty and a clear user decision step.
-   Only add live monitoring when access, privacy, reliability and
    operating cost are approved.

### Acceptance criteria

-   Simulated events produce the expected recommendation at the
    configured threshold.
-   Duplicate events do not create duplicate alerts; retry and failure
    behavior is tested.
-   Monitoring is bounded and respects provider constraints.
-   User opt-in and notification preferences are enforced.
-   No automatic booking, purchase or cancellation occurs.
-   Uber/Ola/bus alternatives are shown only when supported by available
    data; otherwise the limitation is explicit.
-   **Gate:** any consequential external action requires separate
    explicit approval and a safe design.

## Phase 7 --- PWA Usability, End-to-End QA and Release Readiness

**Goal:** Deliver a usable client and establish evidence-based release
readiness.

### Tasks

-   Implement or refine the PWA using the frontend approach selected in
    `DECISIONS.md`. The initial roadmap's vanilla JS/HTML/CSS is a
    candidate, not a binding choice if repository evidence supports
    another approach.
-   Include manifest/service worker support and responsive layouts.
-   Clearly distinguish offline/cached results from live results and
    display timestamps/freshness.
-   Connect the UI to the backend API; keep provider secrets
    server-side.
-   Add Python Playwright end-to-end tests (D-PROP-08) from the user
    journey through API/scoring and the PWA.
-   Run the relevant test suite, lint/type checks and configured
    SAST/security checks.
-   Document operational configuration, known limitations and rollback
    steps before any production deployment.

### Acceptance criteria

-   The principal BLR--MAA user journey passes the defined E2E checks in
    the target test environment.
-   Offline and stale-data behavior is tested and labelled clearly.
-   Accessibility, responsive behavior, validation and error states
    receive appropriate checks.
-   Security findings are triaged; no unresolved critical issue is
    accepted without explicit risk approval.
-   `TEST_RESULTS.md` contains actual commands/results, and skipped
    tests are explained.
-   Production deployment remains blocked until explicitly approved.
-   **Gate:** release readiness is an evidence-backed decision, not an
    automatic consequence of reaching Phase 7.

## Product intent carried forward from the original brief

The owner's original instructions and roadmap are archived in
`docs/history/`. They contained product intent that the current documents
did not otherwise preserve. It is recorded here with its **status**:

-   **Approved:** covered by an approved decision or the current
    `CLAUDE.md`.
-   **Candidate:** an idea requiring validation; not a commitment.

Superseded rules from those files are **not** carried forward. These
include "zero human review", mandatory microservices, the Amadeus test
endpoint, IRCTC scraping, automatic booking and the uncited statistics.

| Original intent | Status | Where it lives / what must be validated first |
|---|---|---|
| "Algorithmic Arbitrage": balancing time, cost and risk into one recommendation | **Approved** as product goal. The scoring formula is still a **proposal**. | CLAUDE.md §1, §8; Phase 2 and 5. "Arbitrage Score" is a working name only. |
| Reactionary flight-delay risk from inbound aircraft rotation/tail history | **Candidate** | Needs AeroDataBox (or other) field, coverage and quota verification (register F-4). Any output is a risk *indicator*, not a probability, unless calibrated (CLAUDE.md §8). |
| Rail waitlist (WL/RAC) outcome risk | **Approved** as a risk dimension; data source per D-PROP-02. | Sample data first. The old "WL probability" wording is not allowed without calibration. |
| Safety Net trigger: WL has not cleared X hours before departure → offer alternatives | **Approved** direction (D-PROP-03), recommend-only. | Threshold X, monitoring cadence and opt-in are undecided (Phase 6). No automatic booking. |
| Cab and sleeper-bus alternatives | **Approved** with simulated data only (D-PROP-03). | Uber is BLOCKED (register X-1). Ola and bus sources are unverified. |
| Dynamic ticket fares | **Approved** with sample data (D-PROP-01). | SerpApi is an evaluation candidate only. |
| Road costs: NHAI FASTag toll plazas, fuel cost, EV charging points | **Approved** with sample values (D-PROP-04). | FASTag/NHAI-specific toll data and an EV-charging source need provider verification. No paid trial without approval. |
| Route weather conditions as a risk input | **Candidate** | OpenWeatherMap / Tomorrow.io are PARTIALLY VERIFIED (desk research only). |
| User profile with vehicle parameters and fuel efficiency | **Candidate** | Phase 4. Data ownership and RLS design first (CLAUDE.md §7). |
| Cached live travel state (e.g. current WL status) | **Candidate** | Phase 4. Requires an explicit freshness/expiry policy (Phase 3). |
| PWA with `manifest.json`, service worker (`sw.js`) and offline-first fallback | **Approved** in principle (D-006, Phase 7). | The frontend framework is open. |
| `supabase-js` auth and Realtime dashboard updates | **Approved** in principle (CLAUDE.md §7). | Auth/RLS plan before implementation (Phase 4). |
| Logs include timestamp, level and service name | **Approved** with limitations (D-IMPL-04, owner-approved 2026-10-27) | `src/routesmart/log.py`. Redaction is best-effort, and sensitive values must not be logged. |
| No aggressive polling; minimise API calls | **Approved** | CLAUDE.md §3 (bounded concurrency, caching); Phase 6 (bounded monitoring). |

## Continuous quality requirements (all phases)

-   Run targeted tests and available security/static checks for each
    relevant change.
-   Keep mocked, live integration and E2E test results distinct.
-   Record exact commands and actual output in `TEST_RESULTS.md`; never
    fabricate success.
-   Update `CHECKPOINT.md` before ending work, including current phase,
    verified state, blockers, open decisions and the next exact task.
-   Log architectural decisions in `DECISIONS.md` with status
    `APPROVED`, `PROPOSED` or `SUPERSEDED`.
-   Preserve existing user changes. Do not commit, push, deploy, incur
    material costs or perform destructive operations without explicit
    authorization.
-   Do not mark a phase complete until every applicable acceptance
    criterion has been evaluated and evidence recorded.

## Task log

**Task 001 --- Baseline Audit and Roadmap Reconciliation** (done
2026-10-27)

Inspect the actual repository and Git state; read `CLAUDE.md`,
`ROADMAP.md`, `README.md` and any existing checkpoint/decision/test
files; assess existing code, dependencies, tests, migrations and CI;
reconcile documentation without losing history; create/update the
provider feasibility register; run only checks justified by the
repository state; report actual results, unresolved decisions and the
next task. Do not implement application features or start Task 002
during this audit. The output is in `docs/audits/TASK_001_BASELINE_AUDIT.md`.

**Task 002 --- Minimum Tested Development Foundation** (Phase 1)

**Scope:**
-   Modular requirements, including `weather.txt` and `testing.txt`.
-   `pyproject.toml` and `.env.example` (placeholders only).
-   `.gitignore` hardening.
-   The shared travel-option contract with tests.
-   The shared logging helper with tests.
-   pytest/pytest-asyncio, ruff, mypy, bandit and pip-audit
    configuration.
-   A GitHub Actions CI workflow.
-   Actual check results in `TEST_RESULTS.md`.

**Out of scope:**
-   Live provider calls of any kind.
-   IRCTC scraping.
-   Bookings.
-   Supabase schema and auth.
-   The scoring engine.
-   The full vertical slice.
-   The PWA.
-   Commits and pushes.

**Stopping boundary:** stop after Task 002 and its review preparation.
Do not start Task 003. Task 002 completion does not complete Phase 1
(see the Phase 1 acceptance criteria).

**Task 002 remediation** (2026-10-27, within Task 002 scope): fixes for
the pre-commit review findings B1, H1–H5, M1–M3, M5 and L1–L7. This adds
the dependency lock, OS-level test isolation, contract immutability and
input strictness, and logging confidentiality fixes, and archives the
historical files. Phase 1 is still **not complete**: GitHub Actions has
not run and the owner has not reviewed or approved the Phase 1 exit.
**Stopping boundary:** stop after the remediation report. No commit and
no Task 003.

**Task 002 remediation round 3** (2026-10-27, within Task 002 scope):
fixes for Round 2 review findings N1–N12. These cover linear-time
redaction, redaction of direct `routesmart.*` loggers at package import,
revalidation of nested models, `FrozenMapping` internals and type-aware
equality, same-namespace isolation proof with least-privilege defaults, a
two-stage locked install, the lock drift checker, path-aware
`sanitize_url`, and documentation fixes. Phase 1 is still **not
complete**: GitHub Actions has not run, and D-IMPL-01..08 are not
approved. **Stopping boundary:** stop after the round-3 report.

**Task 002 closure: Gate 1 decisions and Gate 2 changes** (2026-10-27):
-   The owner approved D-IMPL-01..08 with conditions. D-IMPL-03 is
    approved as direction only; the final schema stays a Phase 2 gate.
    D-IMPL-08's runtime behaviour is unverified until CI runs.
-   The owner approved the M4 labels, the CI-only sudo fallback (R3,
    enforced in the script and tested) and the branch/PR policy (R4).
-   Phase 1 remains **in progress**. Still required: GitHub Actions
    evidence (Gate 5) and the formal owner Phase 1 exit approval
    (Gate 6).
-   **Stopping boundary:** no Git operation without explicit operational
    authorization.

**Task 002 closure: Gates 3–6 status** (2026-10-27; latest entry; updated after the Gate 6 review):

| Workstream | Status | Evidence |
|---|---|---|
| Task 002 implementation and remediation (rounds 1–3, Gate 2, Gate 4 decision 1) | **Done** | Probe-outcome regression tests added. Commit `43e69663dbf5ce128d694782b0b6c3f16750749d` on `feature/task-002-foundation`. |
| Gate 3 local validation | **PASS** | All 21 documented checks. Re-run after the probe tests: 330 passed + 1 skipped; 331 passed in the network namespace. |
| Publication | **Done** (owner-authorized) | Branch pushed; draft PR #1 against `main`. `main` is unchanged at `2b302e0`. *(At publication. `main` was later advanced by the PR #1 merge; see the "Merge" row.)* |
| Gate 5 remote CI validation | **PASSED for the observed runs** | GitHub Actions run 40515177175 (`43e6966`) and run 40519555271 (`b64cb17`) succeeded. Both: CI-only sudo namespace path; privileges dropped to uid 1001; namespace verified (lo only; IPv4/IPv6 unreachable); 331 passed, 1 deselected; namespace proof test passed. |
| Documentation reconciliation | **Done** (owner-reviewed and authorized) | Committed as `b64cb175b852940660d39f46a641e4f3f1ab4302` and pushed; CI run 40519555271 succeeded. A further documentation-currency correction (Gate 6 remediation) was committed on top. |
| Formal Phase 1 exit review (Gate 6) | **Review completed: exit NOT yet recommended** *(at the time of the review; superseded by the next row)* | The Phase 1 acceptance criteria above are unchanged. Remaining: (1) the owner resolves the D-IMPL-08 fail-closed condition (CI verified stub-level fail-closed tests and real namespace verification, but no runner-level failure path); (2) a successful CI run on the final HEAD; (3) explicit owner approval of the Phase 1 exit. |
| Gate 6 owner decisions | **Phase 1 exit APPROVED by the owner (2026-10-27)** | G6-1: D-IMPL-08 CI evidence accepted (controlled-input fail-closed tests ran on CI, and the real namespace path was verified; no real refusal on the runner was demonstrated, and the unprivileged path is unverified on GitHub). G6-2: exit approved on the basis of run 40521272209 (success) on `8bcc143`. G6-3: merge not authorized. G6-4: Task 003 not started. |
| Merge of PR #1 into `main` | **Done** (separate owner authorization, 2026-10-27) | Merge commit `baa94234b90007bf5188326a409dcc3cc4f86d8c` (merged 17:45:05Z; the PR was marked ready from draft for the merge). Parents `2b302e0` and `34deb8c`; the tree is identical to the reviewed PR head. Post-merge CI run 40553520066 on `main` succeeded: 331 passed, 1 deselected; same namespace evidence and limitations. The feature branch was kept. |

Notes:
-   PR #1 must not be merged before the Phase 1 exit review. *(The
    review is done and the exit is approved; merging still needs
    separate owner authorization after the final documentation commit's
    CI succeeds, per G6-3.)*
-   Task 003 has **not** started and remains blocked until the owner
    explicitly approves the Phase 1 exit. *(The exit was approved on
    2026-10-27; Task 003 now also needs its scope and stopping point
    recorded and its required authorization, per G6-4.)*
-   *Post-merge (2026-10-27):* PR #1 was merged into `main` under a
    separate owner authorization, and post-merge CI succeeded. Task 003
    remains not started and blocked as stated above.
-   Gate 5 verifies the observed runs only. It is not a production
    sandbox certification. The unprivileged namespace path has not run
    on GitHub.


**Task 003 --- Deterministic Sample-Data Option Providers for BLR → MAA** (Phase 2, increment 1)

**Status: PROPOSED (2026-10-27), awaiting owner approval** (P2-PROP-01;
date semantics P2-PROP-02; place identifiers P2-PROP-03). **Not started.**
No implementation may begin before the owner approves.

**Status update (2026-10-27): APPROVED by the owner** (P2-PROP-01..04;
`DECISIONS.md`, "Owner decisions: Phase 2 planning"). The text above is
kept as history. **In progress** on `feature/task-003-sample-providers`.
The approved conditions are:
-   P2-PROP-02 option A: aware dates; the current instant is converted
    into the travel date's timezone and calendar dates are compared;
    today or later is accepted; the system clock is never read.
-   P2-PROP-03: `BLR`/`MAA` for all modes; location mapping deferred.
-   The contract is unchanged, and there are no new dependencies.

**Delivered** (see `TEST_RESULTS.md` for evidence):
-   `src/routesmart/providers/`: `query.py` (`TravelQuery`), `base.py`
    (the `OptionProvider` protocol), `sample.py` (five sample providers;
    fixture version `2026-10-27.1`; fixed `retrieved_at`
    2026-10-27T00:00Z) and `collector.py` (`collect_options`).
-   Tests: `tests/providers/` (76 tests).
-   Scoring proposal: P2-PROP-05 in `DECISIONS.md`, PROPOSED only.

**Review remediation (2026-10-27):** three review findings were fixed on
PR #3 (still a draft). The findings were collector revalidation of options,
deep immutability of the fixtures, and strict validation of
`max_concurrency`. There are now 96 provider tests. Evidence is in
`TEST_RESULTS.md`. Scope, acceptance criteria and the stopping point are
unchanged.

**Purpose:** a deterministic, tested, mocked source of travel options for
the five modes, used as input for later Phase 2 scoring and API work.

**In scope (if approved):**
1.  **Query:** a typed query with origin, destination, travel date and a
    caller-supplied current date, following existing conventions
    (pydantic v2 contract style; timezone-aware datetimes).
2.  **Provider interface:** a typed asynchronous provider interface
    (CLAUDE.md §3) returning the existing `TravelOption` contract
    **unchanged**.
3.  **Five sample providers:** flight, rail, car, cab and bus, all
    deterministic, with `DataOrigin.SAMPLE` provenance.
4.  **Fixtures:** fixed and versioned. They include a **waitlisted rail**
    option (`availability=waitlisted`, `waitlist_position`); a **road
    option without fixed departure/arrival times**, declared
    `not_applicable`; and options with **explicitly missing fields**
    declared in `unavailable`, all within the existing contract.
5.  **Collector:** runs the providers concurrently with a timeout per
    provider. It reports **success, empty, exception and timeout**
    distinctly, and keeps other providers' successful results.
6.  **Tests:** focused tests in the normal and offline suites.
7.  **Scoring proposal:** a scoring-model proposal in `DECISIONS.md`,
    marked **PROPOSED**. No scoring code.

**Query validation (deterministic):** reject
-   identical origin and destination;
-   any route other than BLR → MAA in this increment;
-   a travel date before the supplied current date, with the semantics
    per P2-PROP-02;
-   a travel date or current date without timezone information.

**Acceptance criteria:**
-   Each of the five modes returns at least one valid, explicitly
    sample-labelled option for BLR → MAA with a valid date.
-   Identical inputs produce identical outputs.
-   Invalid queries are rejected deterministically.
-   Provider failure, empty output and timeout are distinguishable, and
    the other providers still return results.
-   No network activity occurs.
-   The normal and offline suites pass.
-   Existing checks pass:
    -   pytest (normal, `--import-mode=importlib`, offline script);
    -   ruff lint and format; strict mypy; bandit;
    -   pip-audit; `pip check`; `check_lock.py`; `check-gitignore.sh`.
-   CI passes on the draft PR.

**Exclusions:** Task 003 does not authorize any of the following:
-   scoring code, or approval of scoring semantics;
-   a backend API or API framework;
-   a client/PWA or client approach;
-   any `TravelOption` schema change or new schema version;
-   new dependencies;
-   live providers, network calls, credentials, paid APIs or external
    integrations;
-   Supabase or database work;
-   deployment;
-   changes to the network guard or CI isolation;
-   merging;
-   any unlisted work.

**Stop-and-ask conditions:**
-   a fixture cannot fit the existing contract;
-   an approved decision conflicts with the scope;
-   a new dependency, framework, scoring, API or client decision, live
    integration or network change appears necessary;
-   any acceptance criterion cannot be met within scope.

**Stopping point:** a **draft PR** with the approved implementation and
documentation updates, all required checks passing, ready for owner
review. Then stop: **no merge**, and no scoring, API, UI or further
increment without separate explicit authorization.

**Assumptions (to be confirmed with the scope):**
-   **Code location:** a new `src/routesmart/providers/` package, with
    tests under `tests/`.
-   **Fixture content:** fictional operator names and illustrative
    prices and times, clearly labelled as sample data. They do not imply
    live availability or bookability (CLAUDE.md §2).
-   **Provenance timestamps:** a fixed `retrieved_at` per fixture
    version, not the system clock, so the output is deterministic.
