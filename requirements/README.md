# Requirements layout

Dependencies are split by owner (D-005, D-PROP-06). Each package is listed in **exactly one** input file.

| File | Owns | Includes |
|---|---|---|
| `base.txt` | Shared runtime dependencies (contract, logging) | nothing |
| `flight.txt` | Flight-module runtime deps | `base.txt` |
| `rail.txt` | Rail-module runtime deps | `base.txt` |
| `road.txt` | Road/toll/fuel/EV-module runtime deps | `base.txt` |
| `weather.txt` | Weather-module runtime deps | `base.txt` |
| `testing.txt` | Test runners and test plugins | `base.txt` |
| `dev.txt` | Lint, type, SAST, dependency-audit and lock-generation (pip-tools) tools | `testing.txt` |
| `dev.lock.txt` | **Generated.** Exact pins and hashes for the full `dev.txt` closure, including `pip` itself | (not an input; never included by another file) |

## Inclusion rules

1. `base.txt` includes no other file.
2. Domain files (`flight`, `rail`, `road`, `weather`) include only `base.txt`. They never include each other.
3. `testing.txt` includes only `base.txt`. `dev.txt` includes only `testing.txt`.
4. No file includes `dev.txt`. Runtime files never include `testing.txt` or `dev.txt`.
5. The include graph is a tree rooted at `base.txt`, so there are no cycles.
6. Never list a package in two files. If two domains need the same package, move it to `base.txt`.
7. Use a lower bound at the tested version and an upper bound at the next breaking release. Ruff is limited to one minor series because its rules change between minors.
8. Record why any significant dependency was added in `DECISIONS.md`.

## Lock file (reproducible, hash-verified installs)

`dev.lock.txt` is a **development-tooling lock** (owner-approved D-IMPL-07, 2026-10-27). It is generated from `dev.txt` by pip-tools and is what CI installs. It is **not** a production dependency lock: it pins the developer/CI toolchain, and the declared ranges in the `*.txt` input files remain the dependency contract.

```bash
route_smart_env/bin/pip-compile --generate-hashes --allow-unsafe --strip-extras --no-emit-index-url \
    --output-file requirements/dev.lock.txt requirements/dev.txt
PYTHON=route_smart_env/bin/python scripts/install-locked.sh   # two-stage, hash-verified
route_smart_env/bin/python scripts/check_lock.py               # lock == what dev.txt needs
```

- **Inputs vs output.** The `*.txt` files above remain the human-edited source of truth: owners and ranges. The lock is output only. Never edit it by hand, and regenerate it whenever an input file changes.
- **What it pins.** Every package in the dev/CI environment, transitive dependencies, `pip` (`--allow-unsafe`) and `setuptools`. Each pin carries sha256 hashes for all of its published files, so the same lock works on Linux CI and other platforms for the same Python minor version. It was generated on Python 3.13.
- **CI enforcement:**
  1. `scripts/install-locked.sh` installs in two stages, both with `--require-hashes`:
     - **Stage 1:** the environment's *existing* pip installs **only** the pinned pip, with `--no-deps`. On GitHub Actions that is the runner's preinstalled pip. Its version is printed, **not pinned**.
     - **Stage 2:** the now-pinned pip installs the full lock. So every package except pip itself is installed by the pinned pip, and a changed or tampered artefact fails the install.
  2. Run `pip check`.
  3. `scripts/check_lock.py` resolves `dev.txt` with pip, constrained to the locked versions, and fails on:
     - **missing** pins: needed but not locked;
     - **obsolete** pins: locked but no longer needed;
     - **mismatched** versions.

     It needs index access for package metadata and installs nothing. This replaces the earlier `pip install --dry-run` check, which could not detect obsolete pins.
  4. Run `pip-audit --disable-pip --require-hashes` on the lock. pip is not used for auditing.
- **Scope.** Only the dev/CI environment is locked today. Runtime-only installs (`base.txt` and the domain files) are not separately locked, because no deployable artefact exists yet. A runtime lock is a future decision (D-IMPL-07).
- **Updating.** To pick up new releases or security fixes, re-run `pip-compile` with `--upgrade`, run the full check suite, and review the lock diff.

## Typical installs

```bash
PYTHON=route_smart_env/bin/python scripts/install-locked.sh   # exact CI toolset (two-stage)
route_smart_env/bin/python -m pip install -r requirements/flight.txt  # flight runtime only
```
