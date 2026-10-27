# RouteSmart India --- Project Instructions

## 1. Project Overview

RouteSmart India is a risk-aware, multimodal travel-planning
application. It aims to help users compare travel options across:

-   **Time efficiency:** total journey time, departure/arrival windows,
    transfer and waiting time.
-   **Cost optimization:** fares, tolls, fuel, EV charging and other
    applicable trip costs.
-   **Risk mitigation:** disruption exposure, uncertainty in schedules,
    weather, traffic and rail waitlist outcomes.

The product should explain its recommendations. Do not describe a score
as a probability unless it has been statistically calibrated and
validated as one.

## 2. Pilot Scope and Product Principles

-   Initial pilot route: **Bengaluru (BLR) to Chennai (MAA)**.
-   Prefer a small, demonstrable end-to-end vertical slice over building
    many isolated integrations first.
-   Use deterministic mocked provider data for development and automated
    tests unless a live integration is explicitly approved.
-   Clearly label mocked, stale, estimated, unavailable and live data.
    Never present cached or mocked data as current live information.
-   Keep recommendations explainable: show the relevant time, cost, risk
    factors, assumptions, data freshness and important trade-offs.
-   Treat all provider availability, free-tier access, permitted usage
    and route coverage as unverified until evidence is recorded.

## 3. Architecture and Coding Rules

-   Use Python for the backend and maintain a modular, asynchronous I/O
    architecture.
-   Use `asyncio` and async-compatible clients for concurrent I/O. Use
    `httpx.AsyncClient()` for asynchronous HTTP calls. Do not use
    synchronous `requests` in async execution paths.
-   Not every function needs to be `async`: pure computation and
    ordinary local transformations should remain simple synchronous
    functions unless asynchronous behavior is actually needed.
-   Use `playwright.async_api` only for browser automation when required
    and when the target site's terms, access rules and applicable
    requirements permit the activity. Do not bypass authentication,
    CAPTCHAs, rate limits or other access controls.
-   Keep provider integrations behind small, typed adapter interfaces.
    Avoid coupling scoring logic to any one provider.
-   All modes (flight, rail, car, cab, bus) map provider data into the
    shared, provider-neutral travel-option contract
    (`src/routesmart/contracts/`, documented in
    `docs/TRAVEL_OPTION_CONTRACT.md`). Scoring and the API consume only
    the contract and never read provider-specific metadata.
-   Define the backend API contract before the PWA depends on a backend.
-   Prefer a modular monolith for the initial MVP unless measured
    requirements justify separately deployed microservices. Keep logical
    components isolated without introducing unnecessary deployment
    complexity.
-   Review the existing repository before creating or replacing files.
    Reuse existing utilities and conventions where appropriate. Never
    overwrite unrelated user work.
-   Use type hints, useful docstrings, structured production logging and
    explicit error handling. Do not use bare `except:` blocks or
    silently suppress failures.
-   Handle timeouts, rate limits, malformed responses, missing fields
    and provider outages explicitly.
-   Avoid avoidable O(n²) processing, N+1 database queries and unbounded
    concurrency. Apply sensible timeouts, bounded concurrency and
    caching where appropriate.
-   Check the installed library/API documentation or version constraints
    before adopting a dependency or deprecated interface.

## 4. Provider Feasibility and External Data

The following are candidates, not approved or verified integrations.
Approved decisions D-PROP-01..04 (see `DECISIONS.md`) apply. **Sample
data is the approved initial source for flights, rail, road costs and
cab/bus alternatives.**

-   Flights and schedules: SerpApi is a candidate for evaluation only
    (D-PROP-01). **Amadeus Self-Service is excluded**: it was
    decommissioned on 17 Jul 2026 and must not be used.
-   Aircraft tracking and delay context: AeroDataBox through RapidAPI.
-   Weather: OpenWeatherMap and/or Tomorrow.io.
-   Rail availability and waitlist information: sample data initially.
    Later options are manual user input or a licensed data partner
    (D-PROP-02). Never scrape IRCTC in a way that bypasses CAPTCHA,
    login or other access controls, and never store or automate users'
    railway credentials.
-   Road routing, tolls, fuel and EV charging: sample values initially.
    TollGuru and/or Mappls are candidates. Do not start a trial or
    subscription without separate approval (D-PROP-04).
-   Ground transport alternatives: simulated cab/bus data only, as
    recommendations (D-PROP-03). Uber, Ola, sleeper buses or other
    providers are allowed only where suitable, permitted data/API access
    is established.

The register lives at `docs/PROVIDER_FEASIBILITY.md`.

Before implementing a live adapter, update a provider feasibility
register with: 1. Official evidence URL and date checked. 2. Account/API
access and environment availability. 3. Free/developer-tier limits,
pricing and quota where documented. 4. Terms, permitted use and relevant
restrictions. 5. Geographic and route coverage, fields available and
freshness. 6. Authentication and secret requirements. 7. Rate limits,
timeout/error behavior and operational dependencies. 8. Status:
`VERIFIED`, `PARTIALLY VERIFIED`, `UNVERIFIED`, `BLOCKED` or
`NOT REQUIRED FOR MVP`. 9. The next verification step and any approval
needed.

Do not infer that a service is free, production-usable, permitted for
scraping, or capable of providing a particular field merely because an
API or website exists. If public evidence is inconclusive, mark the item
unverified. Do not make costly live calls or create accounts with
financial commitments without explicit approval.

Keep a mock adapter available so the MVP and tests do not depend on
provider access.

## 5. Environment and Secrets

-   Develop in the project virtual environment `route_smart_env` when it
    exists; do not create a second environment without a reason.
-   Read secrets from environment variables, commonly loaded locally
    from `.env` using a suitable configuration approach. Never commit
    `.env` or real credentials.
-   Keep a safe `.env.example` containing variable names and non-secret
    placeholders only.
-   Never print secrets in logs, terminal summaries, test fixtures or
    documentation.
-   Never expose a Supabase service-role key or other privileged backend
    credential to the PWA.

## 6. Dependency Management

Use modular dependency files under `requirements/` rather than a single
monolithic requirements file:

-   `requirements/base.txt`
-   `requirements/flight.txt`
-   `requirements/rail.txt`
-   `requirements/road.txt`
-   `requirements/weather.txt`
-   `requirements/testing.txt`
-   `requirements/dev.txt`

Ownership and inclusion rules (no duplication, no circular `-r`
references) are documented in `requirements/README.md` (D-PROP-06). CI
installs from the hash-verified `requirements/dev.lock.txt`, generated
from `requirements/dev.txt` with pip-tools. Never edit the lock by hand;
regenerate it whenever a requirements file changes.

Create or modify these files only when justified by the current phase.
Avoid unnecessary dependencies and install only what is needed for the
task. Record why a significant dependency was added and which file owns
it.

## 7. Database and Authorization

-   Supabase PostgreSQL is the proposed primary database.
-   `asyncpg` may be used for backend asynchronous database access when
    appropriate.
-   Use parameterized SQL and validate all untrusted inputs. Never
    interpolate user-supplied values into SQL.
-   Use Supabase Auth and `supabase-js` for client authentication and
    permitted client-side Realtime features when needed.
-   Define schema migrations, constraints, indexes, data retention and
    ownership/tenant boundaries before relying on persistent data.
-   **Important:** a direct `asyncpg` connection does not automatically
    enforce the same user-context protections as Supabase client
    requests protected by RLS. Explicitly design and test backend
    authentication/authorization and database roles; do not assume RLS
    alone secures privileged connections.
-   Apply least privilege. Enable and test RLS for tables exposed
    through Supabase APIs. Keep privileged credentials server-side.
-   Render user/provider data safely; use framework-safe rendering and
    contextual output encoding rather than relying on an unspecified
    generic sanitization step.

## 8. Scoring and Recommendation Integrity

-   Define the scoring model before treating scores as product
    decisions.
-   Candidate model: configurable weighted aggregation of normalized
    time, cost and risk components, with weights summing to 1. This is a
    proposal until recorded as an approved decision.
-   Specify directionality, units, normalization ranges, missing-data
    handling, ties, constraints and default weights.
-   Make score components and the reasons for a recommendation
    inspectable.
-   Do not compare incomparable values or silently substitute missing
    data. If an input is unavailable, disclose the limitation and apply
    a documented fallback or mark the option unscored.
-   Do not call risk scores "probabilities" without calibration and
    validation. Do not claim that the recommended option is guaranteed
    to be fastest, cheapest or safest.

## 9. Testing and Quality Gates

-   Use `pytest` for unit and integration tests, `pytest-asyncio` for
    asynchronous tests, and **Python** Playwright for relevant
    end-to-end browser flows (D-PROP-08). Do not add a Node-based test
    stack without a documented need and approval.
-   Development and CI must not require live provider credentials or
    paid API calls. Tests marked `live` are deselected by default, are
    skipped unless `ROUTESMART_ALLOW_LIVE=1` is set, and never run in CI.
-   Network isolation has two layers. Do not overstate either:
    -   An **in-process guard** (`tests/testsupport/network_guard.py`)
        blocks Python-level TCP/UDP connects, DNS lookups and child
        processes for the whole test session. It is **not a sandbox**: the
        C-level `_socket` type, `os.fork`/`exec*` and native extensions
        bypass it.
    -   **OS-level isolation**: `scripts/test-offline.sh` runs pytest in a
        network namespace and fails closed if isolation cannot be proven.
        By default it uses unprivileged user namespaces, and tests never run
        as root (the probe refuses euid 0). A `sudo` fallback exists **only on
        GitHub Actions**: it needs both `ROUTESMART_OFFLINE_ALLOW_SUDO=1` and
        `GITHUB_ACTIONS=true` (owner decision R3). CI uses it.

    See `docs/TESTING.md`.
-   Use mocks/fakes for third-party APIs by default. Live integration
    tests must be explicitly identified, bounded, permitted and approved
    when they can incur costs or affect real accounts.
-   Test success and failure paths, including empty/missing fields,
    invalid input, timeouts, rate limits, malformed provider responses,
    stale data, provider outages, duplicate events and retry/idempotency
    behavior where applicable.
-   Run the relevant tests and static checks for each change, not only
    at the end of the project.
-   Use `bandit` or another suitable configured SAST tool for Python,
    plus available lint/type checks where configured. Report tool
    limitations and findings honestly.
-   Never fabricate commands, output, coverage, test results, provider
    verification or deployment status. If a check cannot run, record why
    and what remains unverified.
-   Record exact commands and actual results in `TEST_RESULTS.md`.
    Distinguish unit, mocked integration, live integration, E2E and
    security checks.
-   Fix routine defects within scope, rerun affected checks and record
    material decisions. Do not suppress a security finding simply to
    obtain a passing scan.

## 10. Project State and Required Documentation

At the start of each session/task, read `CLAUDE.md`, `ROADMAP.md`,
`README.md` and `CHECKPOINT.md` if present, then inspect `git status`
before editing.

Maintain these root-level documents as work progresses:

-   `CHECKPOINT.md`: current phase, verified state, completed work,
    outstanding issues, open decisions, exact next task and acceptance
    criteria.
-   `DECISIONS.md`: dated decisions, rationale, alternatives,
    consequences and status (`APPROVED`, `PROPOSED` or `SUPERSEDED`).
    Never record a proposal as an approved decision.
-   `TEST_RESULTS.md`: exact commands, actual results, date/context and
    any failures or checks not run.
-   Provider feasibility register: evidence-backed status and next steps
    for each relevant provider.
-   `ROADMAP.md`: phases, tasks, acceptance criteria, dependencies and
    gates.

Preserve useful history. Update documents only with findings supported
by repository inspection, executed commands or cited evidence. Do not
claim these files exist or are current until you have checked.

Before ending a task, update the checkpoint with the exact next action.
At the beginning of a new session, use that checkpoint to resume---but
verify it against the actual repository.

## 11. Approval Boundaries

These human approval gates (D-PROP-05) override any earlier
instruction calling for "zero human review", including the one in
earlier versions of this file.

Proceed autonomously with routine, reversible in-scope edits, tests and
low-risk remediation. Ask for explicit approval before: - incurring
material costs, upgrading to paid plans or making financial
commitments; - production deployment or changes to production systems; -
destructive database/schema/data operations or irreversible
migrations; - live integrations that access personal, booking or account
data, or that may change real-world bookings; - enabling automated
booking, cancellation or other consequential external actions; -
bypassing or materially changing agreed scope, security posture or
architecture.

For IRCTC or other travel-provider monitoring, verify permitted access
and data feasibility first. Start with simulated tests and user-visible,
opt-in recommendations. Do not automatically book, cancel or purchase
travel.

## 12. Self-Review and Security

Before reporting a task complete, review the diff and ask: 1. Are
missing, null, empty, malformed and stale inputs handled? 2. Are there
SQL, command-injection, XSS, secret-leakage or authorization risks? 3.
Is I/O asynchronous where required, with bounded timeouts and
concurrency? 4. Are there avoidable N+1 queries, unbounded loops or
performance bottlenecks? 5. Are errors visible and actionable rather
than silently swallowed? 6. Do tests cover important failure paths? 7.
Are documentation claims supported by evidence and the actual Git diff?

Run available checks, remediate in-scope issues and rerun affected
tests. Human review remains appropriate for consequential decisions and
approval boundaries above.

## 13. Task Execution Protocol

-   Start with a short plan and inspect relevant files/status.
-   Work only on the requested task; do not silently proceed to the next
    roadmap phase.
-   Keep changes focused and avoid unrelated refactoring.
-   Do not commit, push, deploy, or discard changes unless explicitly
    requested. Approval of a decision or task does not by itself
    authorize commits or pushes.
-   **Branch and pull-request policy (owner decision R4, 2026-10-27):**
    -   Prepare changes on a feature branch and review them through a pull
        request against `main`. Never commit directly to `main`.
    -   Do not merge before CI verification and any required phase-exit
        review.
    -   The policy itself authorizes no Git operation. Before creating a
        branch, staging, committing, pushing or opening a PR, present the
        exact operation and an explicit file list, and get explicit
        authorization.
    -   Never use `git add .` or `git add -A`.
-   At completion, report: files changed, key decisions, exact commands
    and real results, known gaps, approval needs, and the next task with
    its acceptance criteria.
-   Never declare a phase complete unless each stated acceptance
    criterion has been evaluated and evidence is recorded.

## 14. Subagents and Parallel Work

Use Claude Code subagents when they are available in the current environment and when delegation is likely to improve elapsed time, coverage, or review quality. Do not assume a subagent capability or tool exists: check the capabilities available in the current session. If subagents are unavailable, continue with a clear sequential workflow and report the limitation only when it materially affects the task.

### Good candidates for parallel work

- Independent read-only reviews of different documentation areas.
- Independent provider feasibility research, when external research is authorized.
- Separate test-design or code-review tasks that do not edit the same files.
- Independent analysis of security, test coverage, type-checking findings, or acceptance criteria.
- Work on isolated modules with clear interfaces and non-overlapping file ownership.

### Work that should remain sequential or centrally coordinated

- Decisions and approval gates that depend on prior findings.
- Documentation reconciliation where one authoritative version must be maintained.
- Shared data-contract or architecture changes that affect multiple modules. Agree the interface first, then delegate independent implementation or review.
- Dependency installation and configuration changes that affect the shared environment. Coordinate these through the main agent.
- Final integration, test execution, diff review, checkpoint updates, and the final report. The main agent remains accountable for these.

### Delegation rules

1. Break work into bounded tasks with explicit goals, inputs, outputs, acceptance criteria, and file ownership.
2. Prefer read-only investigation and review in parallel. For editing tasks, assign non-overlapping files or isolated modules. Do not have multiple agents independently edit the same file.
3. Tell subagents not to commit, push, deploy, install paid services, access secrets, or expand scope. They must follow all project approval boundaries.
4. Give each subagent only the context and access needed for its task. Do not expose secrets or sensitive user data.
5. Ask subagents to report files inspected or changed, commands run, actual results, assumptions, and unresolved issues. A subagent's claim is not verification by itself.
6. The main agent must inspect delegated changes, resolve conflicts, check consistency, run the relevant tests and quality checks, and verify acceptance criteria before reporting completion. Do not rely solely on subagent summaries.
7. Do not parallelize tasks whose outputs depend on each other. Establish shared interfaces and decisions first, then delegate independent work.
8. Use a reasonable number of subagents. Avoid creating agents for trivial tasks where coordination overhead exceeds the benefit.
9. If subagents modify the working tree, inspect the complete Git status and diff, including untracked files, before finishing. Preserve existing user changes.
10. If parallel work cannot be coordinated safely, stop delegation and complete the task sequentially rather than risking conflicting edits.

### Task gates still apply

Subagents do not bypass the roadmap, documentation gates, human approvals, testing requirements, or task stopping boundaries. For each task, the main agent must record the task's scope, any required gate and its stopping boundary (in `ROADMAP.md` → Task log and in `CHECKPOINT.md`) before work starts, verify that every gate the task requires has passed, and stop at that boundary. No subagent may begin a later task or phase early.

In the final report, briefly state where parallel work was used, what was delegated, and how the main agent verified the results. Do not claim time savings unless they were actually measured.
