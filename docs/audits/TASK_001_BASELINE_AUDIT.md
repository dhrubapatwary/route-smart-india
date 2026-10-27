# Task 001: Baseline Audit

- **Date:** 2026-10-27
- **Scope:** Read-only audit of the repository, reconciliation of the roadmap with CLAUDE.md, provider feasibility, a vertical-slice proposal, and phase acceptance criteria.
- **No application code was written. No dependencies were installed. No live provider APIs were called.**

## 1. Repository baseline (observed)

| Item | Finding |
|---|---|
| Git | Branch `main`, 1 commit (`2b302e0 Initial commit`, README only). It matches `origin/main`. |
| Untracked | `.gitignore`, `CLAUDE.md`, `ROADMAP.md`. These are **not committed**, so they could be lost. |
| Source code | None. There are no `*.py` files outside the venv. |
| Dependencies | No `requirements/` directory. The `route_smart_env` venv (Python 3.13.5) contains only `pip 25.1.1`. |
| Tests | None. `pytest`, `bandit`, and `httpx` are not installed (see `TEST_RESULTS.md`). |
| DB migrations | None. There is no `supabase/` or `migrations/` directory, and no Supabase CLI or `psql` on PATH. |
| CI | None. There is no `.github/` directory. `gh` is authenticated as `dhrubapatwary`. |
| Env template | No `.env.example`. `.gitignore` already allows `!.env.example`. |
| Tooling on host | node v22.23.3, npm, docker, gh available. |
| `.gitignore` | Covers venvs, caches, `.env*`, `.vscode/`. At baseline it did not cover `node_modules/`, `test-results/`, or `playwright-report/`. Those were appended during Task 001; nothing else was changed. |

## 2. Gaps, contradictions, and unverified assumptions

Severity: **H** = blocks a phase, **M** = needs a decision before the phase starts, **L** = housekeeping.

| # | Sev | Where | Issue |
|---|---|---|---|
| G-01 | H | CLAUDE.md §4, §11; ROADMAP 2.1 | **Amadeus Self-Service is gone** (decommissioned 17 Jul 2026). The mandated "Amadeus test endpoint" does not exist for new developers. See register F-1. |
| G-02 | H | CLAUDE.md Rule 3; ROADMAP 2.2, 5 | **IRCTC scraping conflicts with access controls** (CAPTCHA, login) and with IRCTC rules against automation software. Monitoring a booked WL would require handling users' IRCTC credentials, which is incompatible with §10 zero-trust. See register R-1. |
| G-03 | H | ROADMAP 5 | **Uber/Ola fallback is not feasible.** Uber estimates are gated and its ToS bans price comparison. Ola is invite-only. Sleeper bus has no provider at all. See register X-1..X-3. |
| G-04 | M | CLAUDE.md §11 vs §4 | **The "strictly free tier" rule conflicts with TollGuru** (trial only, then $80/month). Mappls free terms are unconfirmed. AeroDataBox's free tier (400 units/month) is too small for a product. |
| G-05 | M | ROADMAP 5 wording | "Automatically trigger the Road Agent" is ambiguous. Does it mean recommend, or book? Automated booking is not in scope anywhere and has legal/payment implications. **Proposal:** recommend-only. |
| G-06 | M | CLAUDE.md §12 vs Task 001 | §12 says "Zero Human Review", but Task 001 asks for approval gates. **Proposal:** autonomous remediation of code-level findings stays, while phase exits, provider/legal choices, and schema changes need explicit human approval. |
| G-07 | M | ROADMAP order | The data contract (normalised `TravelOption` schema) is not defined before Phase 2 agents are built. The engine (Phase 4) and DB (Phase 3) both depend on it. **Proposal:** add a contract step to Phase 1. |
| G-08 | M | ROADMAP 6 | "Arbitrage Engine API endpoints" is referenced, but no phase builds an HTTP API service. No framework or inter-service transport is chosen, although §7 requires microservices. |
| G-09 | M | CLAUDE.md §6 | Requirements layering lacks files for weather, DB, and API. `requirements/weather.txt` and `requirements/db.txt` are proposed. |
| G-10 | M | ROADMAP 1, 7 | CI is absent from the roadmap, but §12 mandates automated SAST. **Proposal:** a GitHub Actions workflow in Phase 1 (pytest + bandit + pip-audit + ruff + mypy). |
| G-11 | M | CLAUDE.md §10; ROADMAP 3 | No migration tool is chosen. Row-Level Security (RLS) policies are not mentioned, though supabase-js on the frontend requires RLS to be safe. The pooler mode/port is unstated. **Assumption, unverified:** asyncpg on Supabase's transaction pooler needs `statement_cache_size=0`. |
| G-12 | M | ROADMAP 6 | "Vanilla JS" plus supabase-js needs either an ESM CDN import or a bundler. The XSS sanitisation approach is unspecified (e.g. `textContent` only vs DOMPurify). |
| G-13 | M | CLAUDE.md §8; ROADMAP 7 | Playwright is used for two things: the rail scraper (Python) and PWA E2E tests. It is not decided whether E2E uses Python `pytest-playwright` or Node `@playwright/test`. **Proposal:** Python, to keep one test runner. |
| G-14 | L | ROADMAP 1 | Phase 1 omits logging configuration (§9), `.env.example`, a pytest config (`asyncio_mode`), type-checker, and linter. |
| G-15 | L | CLAUDE.md §8, §10 | The "60%" and "45%" statistics are uncited. They do not affect the rules but should not be quoted as fact. |
| G-16 | L | Repo | Untracked governance files should be committed (needs user approval; not done in this task). |
| G-17 | L | Unverified | Python 3.13 compatibility of the chosen libraries (asyncpg, playwright, httpx) is assumed, not checked. Check it during Phase 1 install. |
| G-18 | L | Scoring | Weights, normalisation, and risk inputs for the "Arbitrage Score" are unspecified. There is no definition of "WL failure probability". |

## 3. Provider feasibility

See [`docs/PROVIDER_FEASIBILITY.md`](../PROVIDER_FEASIBILITY.md). Headline:

- **Usable now with mocks/free tier:** SerpApi (flights, 250/month), OpenWeatherMap 2.5 (free), Tomorrow.io (free).
- **At risk:** AeroDataBox (tiny free quota), TollGuru (trial only).
- **Blocked as specified:** Amadeus Self-Service (shut down), IRCTC scraping (access controls/terms), Uber estimates (gated, ToS).
- **Unverified:** Mappls toll/fuel/EV, fuel prices, Ola, buses.

## 4. Proposed minimum vertical slice (PROPOSAL, not approved)

**Goal:** One command answers "BLR → MAA on date D: which mode, and why?" from **fixture data only**, end to end through the real code path.

**In scope**
1. **Data contract:** a typed `TravelOption` model (mode, provider, depart/arrive, duration, cost breakdown in INR, risk inputs, data source = `fixture|live`, fetched-at timestamp).
2. **Four provider adapters behind one async interface** (`async def fetch_options(query) -> list[TravelOption]`). Each has a fixture-backed implementation:
   - Flight: synthetic BLR→MAA offers. The shape is modelled on SerpApi Google Flights; prices are fictional.
   - Rail: synthetic SBC→MAS trains with availability states `AVAILABLE`, `RAC`, `WL n`. No IRCTC access.
   - Road: distance, duration, toll and fuel cost from dated static config values (labelled fixtures).
   - Weather: a synthetic origin/destination forecast that feeds a risk modifier.
3. **Orchestrator:** `asyncio.gather` with per-adapter timeout. A failed or empty adapter degrades the result and is reported; it never silently drops data.
4. **Arbitrage engine v0:** min-max normalisation of time, cost, and risk across options, with configurable weights. Output is the ranked options plus per-dimension scores and an explanation.
5. **Safety-net rule v0:** a pure function. Given WL position, hours to departure, and a threshold, it returns `fallback_recommended: bool` and the next-best non-rail option. Recommend-only.
6. **Entry point:** a CLI (`python -m routesmart.plan --from BLR --to MAA --date …`) that prints JSON.
7. **Logging:** standard `logging` with timestamp, level, and service name.

**Out of scope for the slice:** live API calls, Supabase/DB, PWA, auth, booking, background monitoring.

**Exit tests (edge cases required by §8):**
- Empty results from every adapter.
- One adapter times out.
- All adapters fail, giving an explicit error and a non-zero exit.
- A single option, where normalisation divides by zero.
- Tied scores.
- Null fields in a fixture.
- Negative or zero prices and durations, rejected by validation.
- Invalid IATA/station codes and a past travel date, rejected.
- WL threshold boundaries: exactly at the threshold, and one above and one below it.
- Weights that do not sum to 1, or a negative weight, rejected.

## 5. Phase acceptance criteria and gates (PROPOSAL, not approved)

Common gate for **every** phase. A phase is not complete until all of these hold, and each must be recorded in `TEST_RESULTS.md` with the real command and output:
- `pytest` passes, with edge-case tests present for each new public function. Coverage is ≥ 85% on changed packages (proposed threshold).
- `bandit -r <pkg> -ll` reports 0 medium or high findings, or each one is justified in DECISIONS.md.
- `pip-audit -r requirements/*.txt` reports 0 known vulnerabilities, or each one is justified.
- `ruff check` is clean and `mypy --strict` is clean on the new packages (proposed).
- `grep` finds no `import requests`, no bare `except:`, and no hard-coded keys. Any `.env` key used is listed in `.env.example`.
- CHECKPOINT.md, DECISIONS.md, TEST_RESULTS.md, and the provider register are updated.
- **Human approval gate:** the user explicitly approves the phase exit before the next phase starts.

| Phase | Additional acceptance criteria |
|---|---|
| **1: Scaffolding** | `requirements/{base,flight,rail,road,weather,db,dev}.txt` exist with pinned versions and install cleanly into `route_smart_env` on Python 3.13. `.env.example` lists every key, with no values. `pyproject.toml` contains the pytest (`asyncio_mode`), ruff, and mypy configs. A shared logging helper exists and is tested. The `TravelOption` contract exists and is tested. The CI workflow runs the common gate on push/PR and is green on GitHub. The tracking files exist. `.gitignore` covers Node/Playwright artefacts. |
| **Slice (1.5)** | All items in §4 work with fixtures only. The CLI returns a ranked JSON for BLR→MAA. Every exit test listed in §4 exists and passes. Zero network calls occur in the test suite, enforced (e.g. by a socket-blocking fixture). |
| **2: Ingestion** | Each agent has a fixture adapter and a live adapter behind the same interface. Live adapters handle 401/403/429/5xx/timeouts with bounded retry plus backoff, and do no polling loops. Live calls run only under an explicitly marked E2E test (`-m live`), with call counts logged against the free quota. Each provider's register entry moves to `VERIFIED` or stays blocked with evidence. **Gate:** the user approves any replacement provider for G-01, G-02, and G-03 before the work starts. |
| **3: Database** | Migrations are versioned in the repo and re-applied cleanly on an empty DB. All queries are parameterised (tested, including an injection-string test). RLS is enabled on every table exposed to supabase-js, with a test proving cross-user access is denied. The connection pool is tested against a local or disposable Postgres. The service role key appears only in backend env. **Gate:** the user approves the schema. |
| **4: Engine** | Deterministic scoring with the weights in config. Golden-file tests cover the BLR→MAA fixtures. Property tests check that scores are within [0,1] and that ranking is stable under ties. The explanation output is included. The complexity is ≤ O(n log n) in the number of options. |
| **5: Safety net** | Recommend-only (no auto-booking unless separately approved). It is scheduled or event-based with documented API call budgets, and never runs as a tight loop. Every fallback decision is logged with its inputs. Threshold-boundary tests pass. **Gate:** the user approves the data source for WL status (R-1) and the fallback providers (X-1..X-3). |
| **6: PWA** | The manifest and service worker pass a Lighthouse PWA check (installable, offline fallback page). The UI uses only the anon key, never the service role key. All rendering goes through `textContent` or a sanitiser, with an XSS test. Auth is via supabase-js. |
| **7: E2E and security** | Playwright E2E covers the flow from button click to ranked result, on fixtures plus one opt-in live run. A full bandit run and pip-audit come back clean. A `/security-review` (or equivalent) pass is run. All silent-failure checks are documented. |

## 6. Unresolved decisions (need user)

These are listed in DECISIONS.md as `D-PROP-*`:
1. The flight offers provider that replaces Amadeus Self-Service.
2. The rail data strategy: no IRCTC scraping behind CAPTCHA/login.
3. The disruption-fallback scope and providers (Uber is not possible).
4. Whether a paid or trial tier is acceptable for tolls (TollGuru), or the project uses static toll fixtures.
5. Whether human approval gates override the "Zero Human Review" stance in §12 for phase exits.
6. Whether to adopt the vertical slice and Phase 1 additions (contract, CI, extra requirements files).
7. Whether to commit the currently untracked `CLAUDE.md`, `ROADMAP.md`, and `.gitignore`.

---

## 7. Follow-up status (added 2026-10-27, Task 002 preflight)

Sections 1–6 above are the historical record as written during Task 001. They have not been edited. This section records what changed afterwards.

**Context changes after Task 001**
- The owner replaced `CLAUDE.md` and `ROADMAP.md` with new versions. The previous versions are kept by the owner as untracked `CLAUDE-1.md` and `ROADMAP-1.md`. *(Update 2026-10-27, Task 002 remediation: both were archived byte-for-byte, with superseded notices, to `docs/history/CLAUDE.original-2026-10-27.md` and `docs/history/ROADMAP.original-2026-10-27.md`. The phase numbers in §1–6 refer to the latter.)*
- Phase numbers, section numbers ("§"), and the "Zero Human Review" wording referenced above refer to the **previous** files. In particular:
  - The new ROADMAP orders phases as: 1 Foundation, 2 Contract + mocked slice, 3 Adapters, 4 DB, 5 Risk model, 6 Safety Net, 7 PWA/E2E.
  - The Phase 1–7 acceptance table in §5 above is a historical proposal. The authoritative criteria are in the new `ROADMAP.md`.
- The owner approved D-PROP-01..08 with conditions (see `DECISIONS.md`). Several approvals are **narrower** than the proposals:
  - SerpApi is a candidate only.
  - No TollGuru trial.
  - `testing.txt` was approved instead of `db.txt`.
  - The vertical slice is not authorized in Task 002.

**Gap status**

| # | Status 2026-10-27 | Resolution / owner |
|---|---|---|
| G-01 | Resolved in docs | D-PROP-01: sample flight data. Amadeus is excluded in CLAUDE.md §4 and ROADMAP Phase 3. |
| G-02 | Resolved in docs | D-PROP-02: sample rail data, no access-control bypass, no credential storage. |
| G-03 | Resolved in docs | D-PROP-03: simulated cab/bus data, recommend-only. |
| G-04 | Resolved in docs | D-PROP-04: sample road values. Paid or trial use needs separate approval. |
| G-05 | Resolved in docs | New CLAUDE.md §11 and ROADMAP Phase 6: no automatic booking/cancellation. |
| G-06 | Resolved in docs | D-PROP-05: approval gates override "zero human review" (CLAUDE.md §11). |
| G-07 | In progress (Task 002) | Minimal contract created in Task 002. Phase 2 must approve the schema. |
| G-08 | Resolved in docs | New ROADMAP Phase 2 defines the backend API contract before the PWA. The framework is still open. |
| G-09 | In progress (Task 002) | `weather.txt` and `testing.txt` approved. No DB file is approved yet. |
| G-10 | In progress (Task 002) | CI workflow added. A remote run is pending an owner commit and push. |
| G-11 | Open | New CLAUDE.md §7 and ROADMAP Phase 4 now require an explicit auth/RLS design. The migration tool and pooler mode are still undecided. |
| G-12 | Open | The PWA framework and rendering approach are undecided (ROADMAP Phase 7). |
| G-13 | Resolved | D-PROP-08: Python Playwright. |
| G-14 | In progress (Task 002) | Logging helper, `.env.example`, pytest/ruff/mypy config. |
| G-15 | Resolved | The uncited statistics no longer appear in the new CLAUDE.md. |
| G-16 | Open | Governance files are still untracked. Committing needs separate owner authorization. |
| G-17 | In progress (Task 002) | Python 3.13 compatibility checked for the Task 002 tooling only. |
| G-18 | Open | Scoring model is a proposal (CLAUDE.md §8, ROADMAP Phase 2). |

The final status of the "in progress" rows is recorded in `CHECKPOINT.md` and `TEST_RESULTS.md` for Task 002.
