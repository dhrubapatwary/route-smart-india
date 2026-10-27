# route-smart-india

RouteSmart India is a risk-aware travel planning agent. It compares flight, rail, and road options on time, cost, and risk, and explains its recommendations. The pilot route is Bengaluru (BLR) → Chennai (MAA).

**Status:** Phase 1 (foundation) is in progress and **not complete**.
- Task 002 added the tooling, the shared travel-option contract and a logging helper.
- There are no live provider integrations. Development uses sample data only.

## Development setup

```bash
python3 -m venv route_smart_env                          # only if it does not exist yet
PYTHON=route_smart_env/bin/python scripts/install-locked.sh      # two-stage, hash-verified
cp .env.example .env                                     # optional; no credentials needed today
```

## Checks (the same ones CI runs)

```bash
route_smart_env/bin/python -m pip check
route_smart_env/bin/python scripts/check_lock.py                # lock == what dev.txt needs (uses the index)
scripts/check-gitignore.sh
route_smart_env/bin/ruff check && route_smart_env/bin/ruff format --check
route_smart_env/bin/mypy
PYTHON=route_smart_env/bin/python scripts/test-offline.sh       # pytest in a network namespace (unprivileged; CI opts in to a sudo fallback)
route_smart_env/bin/bandit -c pyproject.toml -r src
route_smart_env/bin/pip-audit --strict --disable-pip --require-hashes -r requirements/dev.lock.txt
```

Plain `route_smart_env/bin/python -m pytest` also works. It relies only on the in-process guard, which blocks Python-level network, DNS and child-process access but is not a sandbox. `live` tests are deselected by default and skipped unless `ROUTESMART_ALLOW_LIVE=1`. See [docs/TESTING.md](docs/TESTING.md).

## Documents

| Document | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Project rules and architecture constraints |
| [ROADMAP.md](ROADMAP.md) | Phases, acceptance criteria and gates |
| [CHECKPOINT.md](CHECKPOINT.md) | Current status and next steps |
| [DECISIONS.md](DECISIONS.md) | Approved and proposed decisions |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Real test and SAST command output |
| [docs/TRAVEL_OPTION_CONTRACT.md](docs/TRAVEL_OPTION_CONTRACT.md) | Shared travel-option schema |
| [docs/TESTING.md](docs/TESTING.md) | Test isolation layers and live-test opt-in |
| [docs/LOGGING.md](docs/LOGGING.md) | Logging usage, redaction guarantees and limits |
| [docs/history/](docs/history/) | Superseded original instructions and roadmap (historical only) |
| [docs/PROVIDER_FEASIBILITY.md](docs/PROVIDER_FEASIBILITY.md) | Provider feasibility register |
| [docs/audits/TASK_001_BASELINE_AUDIT.md](docs/audits/TASK_001_BASELINE_AUDIT.md) | Baseline audit (historical) plus follow-up status |
| [requirements/README.md](requirements/README.md) | Dependency ownership and inclusion rules |
