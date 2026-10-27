# Checkpoint

Newest entry first. Read this at the start of every session.

---

## 2026-10-27: Phase 2 planning revision PROPOSED (docs-only draft PR). STOPPED for owner review.

**Verified (GitHub, read-only):**
- `main` = `origin/main` = `7bc6416ded1d4f9bac5dabf011703aeef45a6b35`, the merge commit of PR #4.
- PRs #1 to #4 are merged; no other PRs exist. Post-merge CI run 40566118857 (`push`, `7bc6416`) succeeded.
- The local working tree had only the owner's unstaged `CLAUDE.md` edit. It is identical in `019ba26` and `7bc6416`, so it was carried over unchanged to the new branch, and not staged.

**State:**
- **Task 003 (increment 1):** complete and merged (PR #3, `725e266`).
- **Increment 2 (scoring):** **not started, not authorized.**

**Proposed in this update** (all PROPOSED --- OWNER APPROVAL REQUIRED; `DECISIONS.md`, "Proposed: Phase 2 planning revision"):
- **Contract evidence table:**
  - schema v1 has departure/arrival/duration/availability/provenance;
  - it has **no** legs or connections, scheduled-vs-estimated distinction, passenger count, cost basis or risk inputs;
  - the query has **no** time constraints.

  A multi-leg flight cannot be represented structurally.
- **P2-PROP-05 rev. 2:** scoring package A--D (risk not assessed; availability groups; weights and fixed-range normalisation with placeholder bounds; cost-basis and duration disclosures).
- **P2-PROP-06:** increment 2 scope.
- **P2-PROP-07:** extended increment sequence 2--13, with cross-cutting principles, dependencies, gates, stopping points and proposed home phases, plus 10 open questions.
- **P2-PROP-08:** contract and itinerary questions for increment 3a.
- **Owner instruction (2026-10-27):** keep the approved numbering. So 3 splits into 3a/3b, 4 stays the client, and the new briefs' increments 4--12 become 5--13.

**Unchanged:**
- approval records;
- `docs/TRAVEL_OPTION_CONTRACT.md`;
- code, schema, tests, dependencies, CI and network isolation.

No test results were added.

**Next authorized decision (owner):**
1. Review this documentation PR (merging needs separate authorization).
2. Decide P2-PROP-05 rev. 2 (A--D), including the bound values.
3. Approve or amend P2-PROP-06 before any increment 2 work.
4. Decide P2-PROP-07 (sequence and phase placement) and whether to authorize the 3a review.

Still pending as separate tasks:
- the `CLAUDE.md` commit decision;
- the ChatGPT/Claude Code GitHub-verification responsibility note.

---

## 2026-10-27: Task 003 merged (PR #3); post-merge documentation on a draft PR. STOPPED for owner review.

**Verified on GitHub** (read-only `gh api` / `gh run view`):
- **PR #3:** closed and **merged** at 2026-10-27T19:00:23Z by the owner's account.
  - Head: `5aea0c095272e7ff88845bcd8ba7f5ee131c302e`.
  - Base before the merge: `3510aded7a90a727b29c1c120cf6de3072b343f8`.
  - Merge commit: `725e2660be8fca45021b8a75c5d623337706cfe4`, with parents `3510ade` and `5aea0c0`. Its tree equals `5aea0c0^{tree}`, and it was authored with a GitHub no-reply address.
- **`origin/main`:** `725e266`.
- **CI:** each run is evidence for its own commit only; details are in `TEST_RESULTS.md`.
  - Run **40563608783** (`pull_request`) on the PR head `5aea0c0`: success, 427 passed.
  - Run **40565168769** (`push`) on the merge commit `725e266`: success, 427 passed, 0 failed steps.

**Phase 2 position:**
- **Increment 1 (Task 003):** complete as a merged implementation increment.
- **Increment 2 (scoring): not started and not authorized.** The scoring model is **P2-PROP-05, PROPOSED**. Its four open questions are unresolved:
  1. risk weighting before schema support;
  2. whether waitlisted rail is ranked;
  3. default weights;
  4. min–max vs fixed normalisation ranges.
- Approval to merge PR #3 is **not** approval of any later increment.

**This documentation update:**
- **Branch:** `docs/post-merge-task-003-status`, created from `origin/main` @ `725e266`.
- **Files:** ROADMAP, CHECKPOINT, TEST_RESULTS, DECISIONS (changes log R-036 only) and the README status line. Documentation only.
- **Draft PR:** for owner review; **no merge** without separate authorization.
- **`CLAUDE.md`:** the owner's unstaged edit was carried over unchanged when the branch was switched (the file is identical in `5aea0c0` and `725e266`). It was not staged or committed.

**Pending, separately authorized tasks:**
- the `CLAUDE.md` commit decision;
- the GitHub-verification responsibility note for `CLAUDE.md` (ChatGPT/Claude Code).

**Next authorized decision (owner):**
1. Review and merge this documentation PR. *(Done: PR #4 was merged as `7bc6416`; see the newer entry above.)*
2. Resolve P2-PROP-05.
3. Approve increment 2's scope and stopping point before any implementation.

---

## 2026-10-27: Task 003 review remediation on PR #3 (draft). STOPPED for owner review.

**Recovery check (CLAUDE.md §10):**
- Branch `feature/task-003-sample-providers` @ `0bc18c7` equalled `origin/feature/task-003-sample-providers`; merge base with `main` `3510ade`.
- PR #3 was open and a draft; its CI run 40558751674 succeeded.
- The only uncommitted change was the owner's unstaged `CLAUDE.md` edit. It was preserved and not staged.

**Done:** the three review findings were fixed with regression tests. Evidence and exact commands are in `TEST_RESULTS.md`, "Task 003 review remediation".
1. The collector revalidates returned `TravelOption`s.
2. Sample fixtures are deeply immutable.
3. `max_concurrency` must be a non-bool `int` ≥ 1.

**Local results:** 426 passed (normal and importlib); 427 passed offline; all checks clean.

**Unchanged:**
- the `TravelOption` schema, dependencies and lock;
- the network guard, CI and settings;
- the scoring proposal P2-PROP-05 (still PROPOSED);
- approval records.

No scoring and no increment 2.

**Next action:** owner review of updated draft PR #3. No merge, and no increment 2, without separate explicit authorization. `CLAUDE.md` (unstaged) still awaits a separate commit decision. *(Done: PR #3 was reviewed, corrected in `5aea0c0`, and merged as `725e266`; see the newer entry above. The `CLAUDE.md` decision is still pending.)*

---

## 2026-10-27: Task 003 implemented on a feature branch; draft PR for owner review. STOPPED at the stopping point.

**Approvals** (owner, 2026-10-27; recorded in `DECISIONS.md`, "Owner decisions: Phase 2 planning"):
- **P2-PROP-01:** Task 003 approved as documented.
- **P2-PROP-02:** option A.
- **P2-PROP-03:** `BLR`/`MAA` for all modes.
- **P2-PROP-04:** the plan, as planning structure only.
- The owner also authorized the branch, implementation, checks and a draft PR. **No merge** and no further increment.

**Verified repository state:**
- `origin/main` = `3510aded7a90a727b29c1c120cf6de3072b343f8` (re-verified after `git fetch`); no open PRs at the start.
- Branch **`feature/task-003-sample-providers`** was created from `3510ade` with `git switch -c` (no upstream until push), carrying the four planning edits. Local `main` is unchanged.

**Completed (Task 003 scope):**
- `src/routesmart/providers/`:
  - `TravelQuery`: rejects naive or ambiguous dates, identical endpoints, routes other than BLR → MAA, and past travel days (option A; no clock read);
  - the `OptionProvider` async protocol;
  - five deterministic `SampleOptionProvider`s: fictional operators; fixture version `2026-10-27.1`; fixed `retrieved_at`; `DataOrigin.SAMPLE`; a waitlisted rail option; car and cab with `not_applicable` times; a flight whose fare is missing and declared `not_provided`;
  - `collect_options`: per-provider timeout, bounded concurrency, and distinct `success`/`empty`/`error`/`timeout` outcomes. Malformed or wrong-mode output is an `error`. Only the exception type is logged.
- `tests/providers/`: 76 tests.
- Scoring proposal **P2-PROP-05** (PROPOSED only; no scoring code).
- Docs: DECISIONS, ROADMAP, TEST_RESULTS and this entry.
- **Not changed:**
  - `TravelOption` schema; dependencies and lock;
  - network guard; offline script; CI workflow;
  - repository settings.

**Checks:** all passed locally (`TEST_RESULTS.md`, "Task 003 local validation"):
- normal: 406 passed;
- importlib: 406 passed;
- offline script: 407 passed;
- ruff; mypy (22 files); bandit `src`;
- pip-audit ×2; `pip check`; `check_lock`; `check-gitignore`; `git diff --check`.

CI on the draft PR is reported in the session's final report, not here.

**Not part of the Task 003 commit:**
- An **unstaged edit to `CLAUDE.md`**: §10 "Context Compaction and Recovery", a separate owner task.
- Not staged or committed; it awaits separate authorization.

**Open decisions:** P2-PROP-05 (scoring model; four open questions).

**Blockers:** none for Task 003. Increment 2 (scoring) needs P2-PROP-05 approval and separate authorization.

**Next action:** owner review of the Task 003 draft PR against `main`. Do not merge, or start increment 2, without separate explicit authorization.

---

## 2026-10-27: Phase 2 planning; Task 003 PROPOSED (awaiting owner approval). Not started. STOPPED.

*(Annotation 2026-10-27: the owner later approved P2-PROP-01..04 and Task 003; see the newer entry above. This entry is kept as history.)*

**Verified repository state** (checked on GitHub and with `git`):
- **`main` = `origin/main` = `3510aded7a90a727b29c1c120cf6de3072b343f8`**, the merge commit of **PR #2** (merged 2026-10-27T17:55:15Z). PR #1 merged earlier as `baa9423`. There are **no open PRs**.
- **Latest CI:** run **40555092439** (`push`, `main` @ `3510ade`), **success**, 0 failed steps.
  - `331 passed, 1 deselected`; `test_offline_script.py` 34 and `test_offline_isolation.py` 1 passed.
  - CI-only sudo namespace path; uid/euid/gid 1001; namespace verified (lo only; IPv4/IPv6 unreachable).
  - lock, `.gitignore`, format, mypy, bandit and pip-audit all passed.
- **Local:** `main` was fast-forwarded only, from `2b302e0` to `3510ade`; no history was rewritten.
- **Planning edits:** the planning documents below were prepared in the working tree. They are not yet committed; branch creation awaits authorization (R4).

**Phase:** Phase 1 complete (exit approved, G6-2; merged). **Phase 2: planning only.**

**Phase 2 plan and Task 003:** see `ROADMAP.md`, "Phase 2 plan (PROPOSED …)" and the Task log entry "Task 003 --- Deterministic Sample-Data Option Providers for BLR → MAA". The full specification is there, not repeated here.
- **Task 003 status:** **PROPOSED, awaiting owner approval. Not started.**
- **Decisions awaiting the owner** (`DECISIONS.md`, "Proposed: Phase 2 planning"):
  - **P2-PROP-01:** Task 003 scope;
  - **P2-PROP-02:** travel-date interpretation. There is no existing convention, and instant comparison and calendar-day comparison give different results for "today";
  - **P2-PROP-03:** sample place identifiers;
  - **P2-PROP-04:** the Phase 2 increment plan.
- **Phase A check (2026-10-27):** the existing `TravelOption` contract can represent every proposed fixture (waitlisted rail; road with `not_applicable` times; declared missing fields; all five modes; sample provenance). **No schema change is needed.** No previously approved Task 003 scope exists, so nothing conflicts.

**Blockers:** owner approval of P2-PROP-01..04. Nothing else.

**Next authorized action (after approval only):**
1. Create a feature branch from `origin/main` (`3510ade`) and commit these planning documents.
2. Implement only the approved Task 003 scope.
3. Run all required checks, open a **draft PR** and stop for review. **No merge.**

**Unchanged:**
- `main` is unprotected (R6); the repository is public (R5).
- Accepted limitations: no runner-level refusal demonstrated; the unprivileged path unverified on GitHub.
- The e-mail note on PR #1's merge commit stands. PR #2's merge commit was authored with a GitHub no-reply address.

---

## 2026-10-27: PR #1 merged into `main`; post-merge CI passed. Post-merge documentation reconciliation. STOPPED.

**Phase:** **Phase 1 exit approved by the owner on 2026-10-27** (DECISIONS.md G6-2), and the Phase 1 work is **merged into `main`**.

**Merge (separate owner authorization, 2026-10-27):**
- **PR #1:** https://github.com/dhrubapatwary/route-smart-india/pull/1, **MERGED** at 2026-10-27T17:45:05Z. It was marked ready from draft for the merge. Merge method: merge commit, which preserves the four reviewed commits.
- **Merge commit / `main`:** `baa94234b90007bf5188326a409dcc3cc4f86d8c`. Parents: `2b302e0` (previous `main`) and `34deb8c` (reviewed PR head). **Its tree is identical to `34deb8c`**, and `43e6966`, `b64cb17`, `8bcc143` and `34deb8c` are all in `main`'s history.
- **Feature branch:** `feature/task-002-foundation` was kept (repository setting `delete_branch_on_merge=false`).

**CI:**

| Run | Commit | Event | Result |
|---|---|---|---|
| 40551958918 | PR head `34deb8c` | `pull_request` | success |
| **40553520066** | **`main` @ `baa9423`** | `push` | **success** (17:45:07Z → 17:47:23Z); 0 failed steps |

Run 40553520066 details (from its job log):
- two-stage locked install (pip 26.2.1 → 26.2.2); `check_lock` (52 pins), `.gitignore`, format, mypy, bandit and pip-audit all passed;
- `isolation path: network namespace via sudo (GitHub Actions opt-in); privileges dropped to uid 1001 by setpriv`;
- `namespace verified (lo only; IPv4/IPv6 unreachable) … uid=1001 euid=1001 gid=1001`;
- **`331 passed, 1 deselected`**: `test_offline_script.py` 34 passed, `test_offline_isolation.py` 1 passed;
- 0 failures or skips; no credential patterns in the log.

**Accepted limitations (unchanged):**
- A real refusal on the GitHub runner was **not** demonstrated; the D-IMPL-08 evidence was accepted under G6-1.
- The unprivileged namespace path remains **unverified** on GitHub.
- The CI evidence comes from observed runs on one runner image; it is not production sandbox certification.
- Pattern-based redaction; `sanitize_url` gaps; direct `model_construct`/`model_copy(update=…)` bypass; test coverage not measured.

**Repository observations (owner items; no settings changed):**
- `main` branch protection is unchanged: **not protected** (R6). It is not part of this work.
- The repository is public (R5).
- The GitHub-generated merge commit records the account's primary e-mail address as its author, not the no-reply address used by the reviewed commits. It is now in public history. Any change, such as GitHub's "Keep my email addresses private" option for future merges, is an owner decision.

**This documentation update:**
- Made on branch `docs/post-merge-phase1-status` from `origin/main` (`baa9423`), per R4.
- Opened as a PR against `main`. **Not merged**; merging needs separate owner authorization. *(As of this entry. Merged later as PR #2, `3510ade`; see the newer entry above.)*
- Its own CI result is reported in that PR.

**Next actions:**
1. Owner review of the documentation PR, and a separate merge decision. *(Done: the owner authorized it, and PR #2 was merged on 2026-10-27; see the newer entry above.)*
2. **Before any Task 003 work:** record Task 003's scope and stopping point in `ROADMAP.md` (Task log) and `CHECKPOINT.md`, and obtain its required owner authorization. **Task 003 has not started and remains blocked until then** (G6-4).

---

## 2026-10-27: Phase 1 exit APPROVED by the owner (Gate 6 decisions recorded). STOPPED for owner review.

**Phase:** **Phase 1 exit approved by the owner on 2026-10-27** (DECISIONS.md, "Owner decisions: Gate 6", G6-2). The Phase 1 work lives on `feature/task-002-foundation` in draft PR #1 and is **not merged into `main`**. *(As of this entry. Merged 2026-10-27 as `baa94234b90007bf5188326a409dcc3cc4f86d8c`; see the newer entry above.)*

**Owner decisions recorded (2026-10-27):**
- **G6-1, D-IMPL-08 CI evidence: accepted.**
  - Fail-closed behaviour was verified on CI with controlled inputs: the real script and probe, with stubbed `unshare`/`sudo` and fake sockets. 34 tests per run passed on the runner.
  - The real runner's successful namespace path was verified separately: sudo path; uid/euid/gid 1001; lo only; IPv4/IPv6 unreachable.
  - A real refusal on the GitHub runner was **not** demonstrated and is not claimed.
  - The unprivileged namespace path remains **unverified** on GitHub.
- **G6-2, Phase 1 exit: approved**, based on the Gate 6 review, CI run 40521272209 (success) on `8bcc143` and G6-1.
- **G6-3, PR #1 merge: not authorized**; this needs a separate explicit authorization after the final documentation commit's CI succeeds.
- **G6-4, Task 003: not started.**

**Commits** (`main` = `origin/main` = `2b302e0`, unchanged):

| Commit | Content | CI |
|---|---|---|
| `43e6966` | Task 002 | run 40515177175: success |
| `b64cb17` | Gate 5 documentation | run 40519555271: success |
| `8bcc143f57e4d81bae1466ee6844e8ba70822120` | Gate 6 documentation | **run 40521272209: success** (verified from run metadata and the job log) |
| **This entry** | documentation-only commit on top of `8bcc143` | reported in PR #1 (a commit cannot record its own CI run) |

Run 40521272209 details:
- two-stage locked install (pip 26.2.1 → 26.2.2); `pip check`, `check_lock` (52 pins), `.gitignore`, format, mypy, bandit and pip-audit all passed;
- `isolation path: network namespace via sudo (GitHub Actions opt-in); privileges dropped to uid 1001 by setpriv`;
- `namespace verified (lo only; IPv4/IPv6 unreachable) … uid=1001 euid=1001 gid=1001`;
- `331 passed, 1 deselected`; `test_offline_script.py` 34 passed, `test_offline_isolation.py` 1 passed; 0 failed or skipped; no credential patterns.

**PR #1:** https://github.com/dhrubapatwary/route-smart-india/pull/1, **open, draft**, base `main`. **Merge: pending separate owner authorization.** *(As of this entry. The owner authorized the merge and PR #1 was merged at 2026-10-27T17:45:05Z; see the newer entry above.)*

**Next actions:**
1. Confirm the CI run triggered by this documentation commit completes successfully (PR #1 checks). *(Done: run 40551958918 on `34deb8c`, success.)*
2. **Owner:** decide on merge authorization for PR #1. It is separate, and only after step 1 succeeds. *(Done: authorized and merged on 2026-10-27; see the newer entry above.)*
3. **Before any Task 003 work:** record Task 003's scope and stopping point in `ROADMAP.md` (Task log) and `CHECKPOINT.md`, and obtain its required owner authorization. **Task 003 has not started and remains blocked until then.**

**Accepted limitations:**
- pattern-based redaction;
- `sanitize_url` gaps;
- direct `model_construct`/`model_copy(update=…)` bypass;
- the unprivileged namespace path unverified on GitHub;
- CI evidence from three runs on one runner image (not sandbox certification);
- `main` unprotected (R6);
- public repository (R5);
- test coverage not measured.

---

## 2026-10-27: Gate 6. Formal Phase 1 exit review completed (exit NOT yet recommended); documentation-currency remediation. STOPPED.

**Phase:** Phase 1 **in progress (NOT complete)**. The owner has **not** approved the Phase 1 exit.

**Commits** (branch `feature/task-002-foundation`; `main` = `origin/main` = `2b302e0`, unchanged):
- `43e69663dbf5ce128d694782b0b6c3f16750749d`: Task 002 implementation.
- `b64cb175b852940660d39f46a641e4f3f1ab4302`: Gate 5 documentation reconciliation, owner-reviewed and authorized.
- **This entry** is part of the Gate 6 documentation-only remediation commit made on top of `b64cb17`. Its CI result is reported in PR #1 and is not recorded here; a commit cannot record its own CI run.

**PR #1:** https://github.com/dhrubapatwary/route-smart-india/pull/1, **open, draft**, base `main`. **Merge is not authorized.**

**CI evidence (independently verified at Gate 6 from run metadata and full logs):**

| Run | Commit | Result |
|---|---|---|
| 40515177175 | `43e6966` | **success** |
| 40519555271 | `b64cb17` | **success**: workflow 14:16:31Z → 14:17:05Z; `checks` job 30 s |

Both runs show:
- the two-stage locked install, `pip check`, `check_lock.py`, the `.gitignore` check, ruff, format, mypy, bandit and pip-audit all passing;
- the CI-only sudo namespace path; privileges dropped to uid 1001; `namespace verified (lo only; IPv4/IPv6 unreachable) … uid=1001 euid=1001 gid=1001`;
- `331 passed, 1 deselected`, 0 skipped;
- per-file progress lines `tests/test_offline_script.py` = 34 tests and `tests/test_offline_isolation.py` = 1;
- no credential patterns in the logs.

**Gate 6 review (2026-10-27):** completed; recommendation **"do not recommend Phase 1 exit yet"**.
- **Technical evidence** supports exit. The 14:22Z local re-run at `b64cb17` passed (TEST_RESULTS.md, "Gate 6").
- **Gap found:** the documentation-currency gap (stale "uncommitted" status and next action; run 40519555271 not recorded) is corrected in this remediation.

**D-IMPL-08 fail-closed condition: OPEN, owner decision required.** *(Status at the time of this entry. Resolved 2026-10-27: owner accepted the CI evidence; see the newer entry above.)* The approved wording asks CI to verify "fail-closed behaviour".
- **Verified on CI:**
  - (a) unit-level fail-closed tests using stub and fake inputs: all 34 tests in `tests/test_offline_script.py` ran and passed on the runner in both runs;
  - (b) real namespace establishment and verification.
- **Not verified on CI:** (c) a **runner-level failure path**, where the script refuses to run pytest. It has never been triggered on GitHub. The unprivileged path failed on the runner, but the script then took the approved sudo path; that is a fallback, not a fail-closed exit.
- A safe verification method has been proposed for owner approval (see the Gate 6 remediation report). It would be a workflow change, outside this documentation-only task.

**Remaining before Phase 1 exit** *(as of this entry; resolved 2026-10-27, Phase 1 exit owner-approved; see the newer entry above)*:
1. The owner resolves the D-IMPL-08 fail-closed condition: accept (a) + (b) as sufficient, or approve the proposed runner-level check and its evidence.
2. Complete any evidence or documentation that decision requires.
3. A successful CI run on the final HEAD of PR #1.
4. Explicit owner approval of the Phase 1 exit.

**Separate owner decisions:**
- whether Phase 1 exit also requires merging PR #1 (merge needs its own authorization);
- branch protection on `main` (R6; no settings changes authorized).

**Task 003:** **not started**; blocked pending explicit owner approval of the Phase 1 exit.

---

## 2026-10-27: Gate 5. Remote CI validation PASSED for the observed run; documentation reconciliation in progress. STOPPED.

**Phase:** Phase 1 **in progress (NOT complete)**. The formal Phase 1 exit review (Gate 6) is pending.

- **Task 002 commit:** `43e69663dbf5ce128d694782b0b6c3f16750749d` on `feature/task-002-foundation`. It was not amended. Local `main` = `origin/main` = `2b302e0`.
- **PR #1:** https://github.com/dhrubapatwary/route-smart-india/pull/1 is **open, draft**, base `main`. **Merge is not authorized.**
- **GitHub Actions run 40515177175:** **success** (workflow 37 s, `checks` job 34 s). https://github.com/dhrubapatwary/route-smart-india/actions/runs/40515177175
  - Every step passed: the two-stage locked install (bootstrap pip 26.2.1 → pinned 26.2.2), `pip check`, `check_lock.py`, `.gitignore`, ruff lint and format, strict mypy, bandit and pip-audit.
  - **Isolation:** the network namespace was created via sudo with the GitHub Actions opt-in, and privileges were dropped to uid 1001 by `setpriv`. Namespace verified: lo only; IPv4/IPv6 unreachable; uid=1001 euid=1001 gid=1001.
  - **pytest:** 331 passed, 1 deselected. The namespace proof test passed (0 skipped).
  - **Annotation:** only an informational `ubuntu-latest` → Ubuntu 26 migration notice.
- **Gate 5 remote CI validation: PASSED for the observed run.** This is not production sandbox certification. The unprivileged namespace path has not run on GitHub.
- **Documentation reconciliation:** when this entry was written, the changes were **uncommitted working-tree edits** pending owner review. *Update (Gate 6 remediation, 2026-10-27): the owner reviewed them, and they were committed as `b64cb175b852940660d39f46a641e4f3f1ab4302` and pushed. CI run 40519555271 on that commit succeeded. See the newer entry above.* The files were:
  - `TEST_RESULTS.md`: the Gate 5 section, plus clarifications on the historical Gate 3 statements;
  - `DECISIONS.md`: the D-IMPL-08 current status, the historical qualifiers, the addendum and R-030;
  - `ROADMAP.md`: the current status and the Gates 3–5 table;
  - `docs/TESTING.md`: the verification status table;
  - this entry.
- **External evidence files** (outside the repository, in `~/Text/`, not copied in):
  - `RemediationReport-27Oct-1801.md`
  - `RemediationReport-Round2-27Oct-1814.md`
  - `RemediationReport-Round3-27Oct-1832.md` (the final technical remediation report)
  - `Task002-OwnerDecision-27Oct-1832.md`
  - `Task002-OwnerDecisionFinal-27Oct-1837.md`
  - `Phase1-Gate5-Evidence-27Oct2026.md`

  `Task002-OwnerDecisionFinal-27Oct-1837.md` is byte-identical to the Round 3 report (md5 `5e0ccfb5…`), so it holds no separate decision text. The owner decisions on record are the ones recorded in `DECISIONS.md`, "Owner decisions: Gate 1".
- **Task 003:** **not started**; blocked pending explicit owner approval of the Phase 1 exit.

**Next action (owner), as of this entry:**
1. Review the documentation diff.
2. If approved, authorize a documentation-only commit and push to `feature/task-002-foundation`.
3. Then conduct the formal Phase 1 exit review (Gate 6).

*Status (Gate 6 remediation, 2026-10-27): steps 1–3 are done. The diff was reviewed, committed as `b64cb17` and pushed, and the Gate 6 review was completed. The current next actions are in the newer entry above.*

---

## 2026-10-27: Gate 4 decision 1. IPv4/IPv6 probe-outcome tests added; Gate 3 re-run PASS. STOPPED before any Git mutation.

- Added 17 committed regression tests for the offline probe's outcomes (fakes only; probe unchanged). The mutation check confirms they guard each branch.
- Full Gate 3 re-run passed: 330 passed + 1 skipped in-process and under importlib; 331 passed in the namespace; all 21 checks exit 0.
- Publication choices (owner): branch `feature/task-002-foundation`; **draft** PR against `main`; keep the two historical local paths; no settings changes.
- **Not yet authorized:** branch, staging, commit, push or PR.
- **Still unverified:** everything on GitHub Actions.
- Phase 1 is in progress.

---

## 2026-10-27: Task 002 closure, Gates 1–2. Owner decisions recorded; R3 guard implemented. STOPPED before any Git operation.

**Phase:** Phase 1 **in progress (NOT complete)**.

**Owner decisions recorded on 2026-10-27** (DECISIONS.md, "Owner decisions: Gate 1"):
- **D1:** D-IMPL-01..08 approved with conditions.
  - D-IMPL-03 is approved as direction only; the final schema stays a Phase 2 gate.
  - D-IMPL-04 is approved with limitations.
  - D-IMPL-07 is approved as a development-tooling lock, not a production lock.
  - D-IMPL-08 is approved as a requirement; its runtime is unverified until CI runs.
- **R2:** M4 labels confirmed. D-PROP mappings are reworded as "related to", and D-004 cites §5 and §7.
- **R3:** CI-only sudo fallback, enforced in the script.
- **R4:** branch/PR policy in CLAUDE.md §13. This is policy only; there is no Git authorization.
- **R5:** the two local-path lines in TEST_RESULTS.md stay unchanged. The repo is public, so they would be published.
- **R6:** `main` is unprotected. This is a recorded risk; no settings changes.

**Gate 2 changes (local):**
- `scripts/test-offline.sh`:
  - the sudo path requires `GITHUB_ACTIONS=true`;
  - the probe refuses euid 0;
  - it prints netns/pid/uid evidence and exports `ROUTESMART_OFFLINE_NETNS`.
- New tests: `tests/test_offline_script.py` (17) and `tests/test_offline_isolation.py` (1).
- A scoped `allow_subprocesses` fixture.
- An explicit package-import logging test.
- Documentation updates: CLAUDE.md §9/§13, `docs/TESTING.md` (with the action-update process), LOGGING, CONTRACT, requirements README, CI comment, ROADMAP.

**Validation (local, 13:21:30Z):** all 22 checks exit 0.
- pytest: 313 passed + 1 skipped, both in-process and under importlib; 314 passed inside the network namespace.
- The rest of the suite is clean. Details are in TEST_RESULTS.md.

**Not yet verified:** everything on GitHub Actions (Gate 5); in particular, the sudo path has never run.

**Not yet authorized:** branch creation, staging, commit, push, PR or merge.

**Next action:** Gate 3 (final local validation report), then Gate 4 (a Git operation plan for owner authorization).

---

## 2026-10-27: Task 002 remediation round 3 (N1–N12) complete locally. STOPPED.

**Scope and boundary:** fix Round 2 review findings N1–N12 within Task 002. No commit, push, staging, Task 003 or live calls. Stop after the report.

**Phase:** Phase 1, **NOT complete.** Outstanding:
- an observed GitHub Actions run;
- owner decisions on D-IMPL-01..08 (all still PROPOSED) and on M4;
- the CI sudo opt-in decision;
- owner approval of the Phase 1 exit.

**Fixed locally (evidence in TEST_RESULTS.md Round 3 and DECISIONS.md R-014..R-025):**
- **N1:** linear-time redaction. The quadratic JWT pattern and the slow key pattern were both rewritten.
- **N2:** importing the package installs the redacting handler, covering direct `routesmart.*` loggers. pytest now runs with `-p no:logging`, because its capture handler would bypass redaction.
- **N3:** nested models are revalidated.
- **N6:** `FrozenMapping` internals are read-only.
- **N7:** equality is type-aware and matches serialisation.
- **N4:** the isolation proof and pytest run in the same namespace.
- **N10:** the isolation path is reported, there is a missing-Python diagnostic, there is no root inside the namespace, and `sudo` is opt-in.
- **N5:** two-stage hash-verified install.
- **N8:** `check_lock.py` detects missing, obsolete and mismatched pins.
- **N9:** path-aware `sanitize_url`, with a precise contract.
- **N11:** `try/finally` in the nested-guard test.
- **N12:** the ROADMAP row is now Candidate.

**Validation (local, single final run at 12:56:08Z):** all 21 checks exit 0.
- pytest: 295 passed, in-process, under importlib, and in the network namespace.
- ruff, strict mypy, bandit: clean.
- pip-audit (lock and venv), pip check, check_lock: clean.
- `.gitignore` check, actionlint, shellcheck, config parse and whitespace: clean.

**Unverified on GitHub Actions:**
- Ubuntu 24.04 may block unprivileged user namespaces (AppArmor; desk evidence only). CI therefore sets `ROUTESMART_OFFLINE_ALLOW_SUDO=1`, keeping the previous fallback behaviour, now explicit. Whether to keep it is an owner decision.
- The sudo path has never been exercised.

**Residual risk:**
- Pattern redaction cannot catch arbitrary secrets.
- `sanitize_url` misses short or letters-only path secrets, secrets in host names, and percent-encoded secrets.
- Importing the package configures the `routesmart` logger (documented).
- `model_construct`/`model_copy(update=)` called directly still bypass validation (documented).

**Exact next action:** an independent read-only review of round 3. Then the owner decides on D-IMPL-01..08, M4, the CI sudo opt-in, and committing (explicit paths; branch plus PR so CI runs).

**Round 3 has stopped. Task 003 has not started.**

---

## 2026-10-27: Task 002 remediation complete locally. STOPPED; awaiting a fresh independent review.

**Scope and boundary:** fix the pre-commit review findings within Task 002 scope. No commit, push, staging, Task 003 or live calls.

**Phase:** Phase 1, **NOT complete.** Outstanding:
- An observed GitHub Actions run (none yet).
- Owner review of the working tree.
- Owner decisions on D-IMPL-01..08 (all PROPOSED).
- Owner approval of the Phase 1 exit.

**Fixed:** findings B1, H1–H5, M1–M3, M5, L1–L7. Each was reproduced before fixing; details are in DECISIONS.md R-005..R-013 and TEST_RESULTS.md "Task 002 remediation".
- **Logging:** whole-output redaction (tracebacks included), malformed calls never raise, early records redacted, `sanitize_url()`.
- **Contract:** immutable and hashable, with strict ISO 8601 time/duration inputs, canonical 2-decimal money, bounds and finite metadata.
- **Test isolation:** session-wide guard (DNS, UDP, subprocess, all fixture scopes); `live` deselected by default and gated by `ROUTESMART_ALLOW_LIVE=1`; OS-level network namespace via `scripts/test-offline.sh`, which fails closed.
- **Dependencies:** hash-verified `requirements/dev.lock.txt` (pip-tools, includes pip), enforced in CI.
- **Repository:** `.gitignore` anchored, with regression script; CI triggers on push to `main` and on PRs.
- **Documentation:**
  - CLAUDE.md §9 wording now matches the enforced isolation; §14 is now a durable per-task rule; §6 has the lock rule.
  - Open questions added to D-PROP-05/06/08.
  - Unique product intent carried into ROADMAP with an approval status for each item.

**Historical files:**
- `CLAUDE-2.md` was removed after verifying it is a byte-exact prefix of `CLAUDE.md`.
- `CLAUDE-1.md` and `ROADMAP-1.md` were archived byte-for-byte (md5 verified), with superseded notices, to `docs/history/`.
- `.gitattributes` exempts only those archives from whitespace checks.

**Validation (local only, single final run):**

| Check | Result |
|---|---|
| pytest | 236 passed, 1 live deselected. Same result under `--import-mode=importlib` and inside the network namespace. |
| ruff, mypy (strict), bandit (490 LOC) | clean |
| pip-audit (lock and venv) | clean |
| pip check, lock-range check, `.gitignore` check | pass |
| actionlint, shellcheck | clean |
| whitespace | clean |

**Not fixed / residual risk:** see the remediation report and docs/LOGGING.md and docs/TESTING.md.
- Pattern redaction cannot catch arbitrary secrets.
- The in-process guard is not a sandbox.
- The OS-level isolation and lock install are unverified on GitHub runners.
- The currency check is format-only (documented).
- A future `retrieved_at` is accepted by design.
- `model_construct` bypasses validation (documented).

**Exact next action:** a fresh, independent read-only review of the working tree. Then the owner decides on D-IMPL-01..08 and on committing (explicit paths, ideally on a branch with a PR so CI runs).

**Task 002 remediation has stopped. Task 003 has not started.**

---

## 2026-10-27: CLAUDE.md §14 (Subagents) merged. No task work performed

- The owner updated `CLAUDE.md` at 11:39 UTC, adding **§14 Subagents and Parallel Work**. That update was based on the pre-reconciliation text, so it dropped the Task 002 reconciliation edits (Amadeus exclusion, D-PROP-01..04 provider conditions, the 7 requirements files, Python Playwright, the network-blocking/no-credentials CI rule, the "zero human review" override, and the no-commit-on-approval note).
- The owner's untracked `CLAUDE-2.md` is the reconciled version.
- **Merged:** `CLAUDE.md` = `CLAUDE-2.md` + the owner's §14, with §14 verbatim (verified with `diff`). Undo by restoring the backup kept outside the repo in the session scratchpad (`CLAUDE.owner-1139.md`).
- **§14 compliance for Task 002:** no subagents were used. All Task 002 work, checks and reviews were done sequentially by the main agent.
- **Untracked owner copies awaiting a keep/delete decision:** `CLAUDE-1.md` (original), `CLAUDE-2.md` (reconciled, pre-§14), `ROADMAP-1.md` (original plus the Task 001 note).
- The Task 002 status is unchanged: Partially Passed locally (no remote CI run). Phase 1 is not complete. The next action is unchanged (see the entry below). No Task 003 work has started.

---

## 2026-10-27: Task 002 (Minimum Tested Development Foundation) complete locally. STOPPED at the task boundary.

**Phase:** Phase 1 (Foundation), **NOT complete.** Outstanding Phase 1 criteria (ROADMAP.md):
- No GitHub Actions run has been observed, because nothing is committed or pushed.
- The owner has not reviewed the working tree, including the untracked governance files.
- The owner has not approved the Phase 1 exit.

**Decisions:** D-PROP-01..08 are recorded as APPROVED with conditions (`DECISIONS.md`; grep count 8). Task 002 implementation choices D-IMPL-01..06 are logged as PROPOSED for owner review.

**Documentation reconciliation (preflight):**
- `CLAUDE.md` and `ROADMAP.md` (the owner-replaced versions) were read from disk and reconciled: Amadeus excluded, approved provider conditions, the 7 requirements files, Python Playwright, approval-gate precedence, and Task 002 scope and boundary.
- The audit's history is preserved, with a dated follow-up (§7).
- The provider register has an evidence-level note and a post-approval status table.
- The gate **passed** before any Task 002 code was written.

**Task 002 files created:**
- `pyproject.toml`
- `.env.example`
- `requirements/{base,flight,rail,road,weather,testing,dev}.txt` and `requirements/README.md`
- `src/routesmart/__init__.py`, `src/routesmart/log.py`
- `src/routesmart/contracts/__init__.py`, `src/routesmart/contracts/travel_option.py`
- `tests/conftest.py`, `tests/test_network_guard.py`, `tests/test_log.py`, `tests/contracts/test_travel_option.py`
- `.github/workflows/ci.yml`
- `docs/TRAVEL_OPTION_CONTRACT.md`

**Files modified:** `CLAUDE.md`, `ROADMAP.md`, `README.md`, `.gitignore`, `CHECKPOINT.md`, `DECISIONS.md`, `TEST_RESULTS.md`, `docs/PROVIDER_FEASIBILITY.md`, `docs/audits/TASK_001_BASELINE_AUDIT.md`.

**Not touched:** the owner files `CLAUDE-1.md` and `ROADMAP-1.md` (checksums verified).

**Environment changes:**
- `route_smart_env` now has the `requirements/dev.txt` toolset installed.
- Its pip was upgraded from 25.1.1 to 26.2.2 to remediate advisories.

**Results (local only; see `TEST_RESULTS.md`):** all final runs exited 0.
- pytest: 129 passed, 0 failed.
- ruff check and ruff format: clean.
- mypy (strict): clean.
- bandit: 0 issues.
- pip-audit: no known vulnerabilities, for both the requirements files and the installed venv.
- actionlint 1.7.7: 0 errors.

The initial failures (3 test-bug failures, 8 lint errors, 1 mypy finding, pip advisories) were fixed. They are recorded in `TEST_RESULTS.md` and the `DECISIONS.md` remediation log.

**Known limitations / open items:**
- The contract is a minimal v1. Phase 2 must extend and approve it (cost breakdown, risk inputs, multi-leg journeys, API envelope).
- Log redaction is best-effort, pattern-based, and does not cover exception tracebacks.
- No coverage measurement is configured.
- `requests` is present in the venv only as a transitive dependency of `pip-audit`.
- Untracked `CLAUDE-1.md` and `ROADMAP-1.md`: the owner should decide whether to keep them (e.g. move them under `docs/history/`) or delete them. They contain superseded instructions, including "zero human review".
- No unresolved security findings.

**Exact next action (owner):**
1. Review the working tree (`git status`, `git diff`, and the untracked files).
2. Decide on `CLAUDE-1.md` and `ROADMAP-1.md`.
3. If satisfied, commit and push to `main` or a branch, so CI runs.
4. Record the observed CI result in `TEST_RESULTS.md`.
5. Approve or reject D-IMPL-01..06.
6. Decide on the Phase 1 exit.

The next Claude task (not started) would be **Task 003: Phase 2, contract approval and API contract for the mocked BLR→MAA slice**, once Phase 1 is approved.

**Task 002 has stopped. No later task has been started.**

---

## 2026-10-27: Task 002 preflight. Decisions recorded, documentation reconciled, gate check

- The owner approved D-PROP-01..08. They are recorded as APPROVED, with conditions, in `DECISIONS.md`.
- The owner-replaced `CLAUDE.md` and `ROADMAP.md` were read from disk and reconciled with the approved decisions (Amadeus excluded, requirements files, Python Playwright, approval precedence, Task 002 scope).
- The Task 001 audit keeps its historical findings, with a dated follow-up appended (§7).
- The provider register has an evidence-level note and a post-approval status table.
- The untracked `CLAUDE-1.md` and `ROADMAP-1.md` are owner copies of the previous versions. They were left untouched; the owner decides whether to keep or remove them.
- Gate result: **passed**. See the Task 002 entry above.

---

## 2026-10-27: Task 001 (Baseline Audit) complete. Awaiting user decisions.

**Project status:** Pre-Phase 1. The repo contains documentation only. There is no code, no tests, no dependencies (the venv has only pip), no CI, and no DB migrations. **Phase 1 is NOT complete.** None of its acceptance criteria are met.

**Completed in Task 001**
- Audited the repository, git state, venv, tooling, tests, CI, and migrations (results in `TEST_RESULTS.md`).
- Reconciled ROADMAP with CLAUDE.md and found 18 gaps (`docs/audits/TASK_001_BASELINE_AUDIT.md` §2).
- Created the provider feasibility register (`docs/PROVIDER_FEASIBILITY.md`).
- Proposed a fixture-only BLR→MAA vertical slice and phase acceptance criteria with approval gates.
- Logged approved vs proposed decisions (`DECISIONS.md`).

**Broken / blocked**
- Amadeus Self-Service is decommissioned (17 Jul 2026), so ROADMAP 2.1 cannot proceed as written.
- IRCTC scraping conflicts with access controls and IRCTC rules, so ROADMAP 2.2 and 5 need a decision.
- The Uber price-estimate API is gated and its ToS bans comparison, so the Phase 5 fallback needs a decision.
- TollGuru has no permanent free API tier, which conflicts with CLAUDE.md §11.
- `CLAUDE.md`, `ROADMAP.md`, and `.gitignore` are still untracked in git.

**Pending user decisions:** D-PROP-01 … D-PROP-08 in `DECISIONS.md`.

**Exact next step:** The user reviews and approves or rejects D-PROP-01..08. Then start **Task 002: Phase 1 scaffolding**, which covers:
- the `requirements/` files;
- `pyproject.toml`;
- `.env.example`;
- the logging helper;
- the `TravelOption` contract with edge-case tests;
- installing dev tooling into `route_smart_env`;
- a CI workflow;
- the first real pytest and bandit run, recorded in `TEST_RESULTS.md`.
