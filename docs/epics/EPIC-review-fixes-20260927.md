# EPIC-review-fixes-20260927: Fix the verified findings from the seven-skill review

Status: in_progress

## Problem And Baseline

A multi-agent review of the seven bundled skills reported 62 findings. Verification refuted three
(dh-docs-06, dh-docs-07, small-skills-activation-profile-matrix-nominal), so 59 survived. They cover
authorization targets, push isolation, RUN closeout state, gate checks, approval digests, UI and
design-system gates, SEO and security review contracts, installers, CI and documentation drift.

- Repository: `product-delivery-harness`, source-maintenance work. No consumer PRD applies.
- Baseline: `70ab12bd8770ec4d9ae394b66e640c8c597c7cbb` on `codex/runtime-contract-adoption`.
- Branch: `codex/review-fixes`, observed at `fae73077` when this record was written.
- Review inputs: first review (62 findings) and a second review of `70ab12bd..f14f4d5b`
  (harness-correctness, security, skills-correctness and docs-consistency findings).

## Accepted Scope

Fix each surviving finding with the smallest correct change and a focused test, or document it
when code cannot or should not change. Writers worked in separate worktrees with explicit file
ownership; the parent integrated them serially. Out of scope: rewriting the legacy push parser,
force or lease pushes, new release infrastructure. This record grants no actions.

## Acceptance And Dependencies

| Requirement / TEST ID | Expected outcome | Verification / environment | Dependency |
| --- | --- | --- | --- |
| Each fixed finding | Failure scenario from the review no longer reproduces | Focused test per finding, run by its writer | Writer worktree at the listed commit |
| Changed safety checks | A negative test proves the unsafe input is still rejected | Focused tests in the owning skill | none |
| Release surfaces | `VERSION`, `package.json`, RUNBOOK default, README badges and history agree on 0.55.0 | `test_skill_contract.py` | none |
| Full regression | Required Verification in `AGENTS.md` passes on the integrated head | Full suite, run by the parent | Round-3 fixes integrated |

## Document Impact

| Changed source / requirement | Affected live artifact | Required recheck |
| --- | --- | --- |
| Approval digests (pdb-1), Styling approach row (dsc-01) | Consumer Product Definition packages | Re-run finalize; re-record Product Definition Approval and Stack Decision Checkpoint |
| Environment Status RFC3339 Checked (dh-gates-2) | Consumer `docs/DEPLOYMENT.md` | `check_deployment.py` |
| Cleanup lifecycle exact targets (dh-authz-1) | PLANs of runs that require 0.55.0 | PLAN validation |
| Impeccable required, enhancement UI gate names (udb-04, pdb-2) | Consumer `ui-design.md` and Enhancement Impact Records | UI and product checkers |
| All of the above | Four READMEs, `docs/DOCUMENTS.md`, version 0.55.0 | `test_readme_structure.py`, `test_skill_contract.py` |

## Change Log

Observed 2026-09-27 on `codex/review-fixes` from baseline `70ab12bd`. All entries below are
committed; no working-tree changes are recorded.

| Change / request | Reason and affected scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| Git publication | dh-git-push-1 hooks/askpass isolation; -2 linked-worktree config is local; -3 askPass and URL-scoped TLS/header keys; -4 UTF-8 output; -5 execute-to-recover test; -6 residual window documented; dh-docs-05 promotion vs publication | `39d11c7e`, `2d6cd3a0`, `ff9d5b7b`, `787bc401`, `15bb8940`, `92eecaad`, `99b8964b`, `8a2677fb`; merge `74c825a3` | Focused tests passed per writer. The execute-to-recover test fails on the writer host because of a temp-key ACL; CI must confirm |
| Authorization | dh-authz-1 exact targets for cleanup lifecycle nodes; -2 subagent reviewer spawn receipts; -3 `invoke_external_runtime` scope documented; dh-gates-1 coordination path check | `fbd1c5e7`, `e3b4d990`, `c2f78646`, `71daef93`, `fda4f0a3`; merge `f96126b9` | Focused tests passed per writer |
| RUN state | dh-state-01 closeout accepts untaken routes; -02 budget check in record-integration; -03 route OR / dependency AND documented; -04 non-integer attempts; -05 one sandbox check | `b8fc7746`, `ba822636`, `fd2fcaf8`, `d1971f72`, `9ca1ebb1`; merge `37d7e1b2` | Focused tests passed per writer |
| Gates | dh-gates-2 every Environment Status row checked; -3 UI contract exemptions; -4 PASS is exit 0; -5 acceptance evidence source; -6 dead verifier cache removed; -7 token-source flags not clean | `8ad67038`, `42e2bcbc`, `6d78577e`, `caa96ba1`, `5d6c619c`, `a31252a0`; merge `3fd8c62e` | Focused tests passed per writer |
| Design System Compiler | dsc-01 Styling approach row; -02 stylingMechanism mapping; -03 preflight location; -04 alpha hex and rem/em; -05 house line-height floors; -06 `--write` without renameat2; -07 exact repo-relative sources; -08 legacy join repo root | `074a5751`, `fadcc79f`, `2754f9e1`, `be4b3c7d`, `7fd00d0f`, `b92daedd`, `6f85b356`, `fb7effb9`; merge `7fdf43e2` | Focused tests passed per writer. dsc-06 is replaced by the round-3 exchange fix below |
| UI Design Builder | udb-01 current HiFi evidence for new legacy approvals; -02 one wireframe evidence contract; -03 approval date vs receipts; -04 Impeccable required; -06 case-insensitive manifest | `fc84dfe5`, `633f98a5`, `a5b671e6`, `1f5a6963`, `6ec48ea1`; merge `7044beb0` | Focused tests passed per writer |
| Product Definition | pdb-1 raw-text approval digests (breaking); -2 current enhancement gate names; -3 honest PASS wording; -4 closed release source policies; -5 dead legacy validator removed; -6 raw-byte prior outcome digest | `468f8752`, `06820634`, `d50af40f`, `bfc4377d`, `e42f43e5`, `0d60c6d9`, test fix `f14f4d5b`; merge `c8040804` | Focused tests passed per writer; `test_harness_strict_authority` re-approves its package after `f14f4d5b` |
| SEO and security review | seo checker TypeError; single package validation; only the reviewed target must be ready; security `required_checks` in the packet; no reviewer reason codes | `22715311`, `75ef7f30`, `b6ef4c4d`, `f2b16689`, `0bc4c8a0`, `692f7bd5`; merge `434c5b9d` | Focused tests passed per writer |
| Installers, CI and repo rules | cross-ps1-symlink-mode-parity; cross-installer-dirty-bytes-no-source-identity (reporting, see skipped); cross-restore-instruction-unfollowable; cross-version-pins-literal-readme-unchecked; dh-docs-02 routine maintenance; dh-docs-03 main default branch; dh-docs-08 AGENTS/CLAUDE drift; macOS CI job; installer test deadlines; worker goal word budget | `ca29d605`, `d3a4a4c9`, `6eab8045`, `6d48590f`, `16d94714`, `2c310ac2`, `4c7aad71`, `033c68e1`, `0a526d02`, `44d4dc32` | Focused tests passed |
| Round-2 follow-ups | security-04 legacy push isolation; cleanup nodes without a target rejected in PLAN and deferred by the selector; docs-consistency promotion order, stale verifier docs, restore rule, new required inputs; skills-correctness-4 mobile stack record; routine maintenance and main default branch wording | `53b525fe`, `bfe15af0`, `0ef94a48`, `5e494867`, `6f2ac607`, `a9eb17c9`, `f2635c76`, `0a18d480`, `705ba403`, `ffdf374d`, `4a60347a`; merges `ec272b25`, `fae73077` | Focused tests passed per writer |
| Round-3 fixes | docs-consistency-macos-renameat2 and skills-correctness-1: RUN, DOCUMENTS and design-system commits keep the atomic exchange and add macOS `renameatx_np` `RENAME_SWAP`; security-03, harness-correctness-03: new receipt and cleanup rules apply only to runs that require 0.55.0; harness-correctness-01 subagent review deferred under a wildcard mission scope; skills-correctness-2 non-checkout repo root; security-01 CI extraheader allowed for local reads; security-02 live-head diff without rename detection; security-05 readback repo discovery; security-06 repo signing programs; harness-correctness-05/security-07 case-insensitive default branch; harness-correctness-02 nested token-block styles; skills-correctness-5 approval date only for current HiFi; acceptance register commit order; skills-correctness-3 documented; trusted-host key ACL in the Windows test; README preflight wording and lockfile 0.55.0 | `30560d51`, `43b8db06`, `96051fc4`, `2f8d037d`, `514f174e`, `4f0461e6`, `644c64df`, `89cb21de`, `84203955`, `e7c95443`, `08c96e35`, `b707e99e`, `31fb85d7`, `da617d3d`, `045e9bae`, `78fca572`, `27ea4979`; merges `7792eb40`, `2eaa412f`, `91437497`, `85c421a4`, `8e05d3e0` | Focused tests passed per writer; full suite below. POSIX exchange paths verified by reading and mocked-libc tests only |
| README sync, version 0.55.0, index, this record | cross-readme-mermaid-provider-section, docs-consistency-readme-sync, docs-consistency-epic-and-version-sync, skills-correctness-6, cross-documents-index-stale-release-status | `99372247`, `9cc2617d`, `5a3cf8be`, and the commit that adds this file | README structure, skill contract and docs-weight tests passed |

### Skipped or partial, with reasons

- dh-git-push-6: documented only. A lease or force push flag is forbidden here, so the residual
  window between the remote recheck and the no-force push is described instead.
- dh-authz-4: not changed. The regex parser only serves pinned pre-0.38 RUN recovery.
- udb-05: skipped. `review-workflow.md` makes the preserved-page flag intentional.
- cross-installer-dirty-bytes-no-source-identity: installers still install uncommitted bytes;
  refusing them was replaced by printing and recording the source commit and dirty state.
- dh-docs-01: partial. The PLAN template names the delivery-acceptance entries in prose. The
  template rows were left for a follow-up because `MISSION_RUNBOOK.template.md`,
  `test_new_run.py` and `test_render_tasks_view.py` fixtures must change together.
- skills-correctness-3: documented limitation. Only `check_ui_publication.py` enforces the udb-01
  HEAD comparison; Harness joins and the compiler preflight still accept legacy approvals.

## Results And Remaining Work

### Breaking changes (0.55.0)

- Product Definition Package and Stack Checkpoint digests cover raw bytes, including fences,
  indented lines and HTML comments. Re-run finalize and re-record both approvals.
- Mobile/Desktop stacks need a `Styling approach` row.
- Environment Status Checked values must be RFC3339 with a timezone.
- Cleanup lifecycle nodes need an exact target in runs that require 0.55.0.
- Impeccable critique and audit are required before Visual Approval.
- Enhancement UI rows name Wireframe Validation and Visual Approval.

### Verification

- Focused tests per writer passed; see the Change Log rows.
- Full suite on `27ea4979` (Windows 11, Python 3.14, 2026-09-27), from the repository root:
  `check_skill_spec.py`, `pyflakes` on all six script dirs, `docs_weight.py` and
  `git diff --check 70ab12bd HEAD` passed. Unit suites: delivery-harness 1318 OK (16 skipped),
  product-definition-builder 240 OK, ui-design-builder 292 OK, design-system-compiler 116 OK
  (4 skipped), product-activation 56 OK, seo-growth-review 21 OK. Golden path 1 OK.
- Not run: the Playwright browser tests (`PDH_REQUIRE_BROWSER_TESTS=1`) and Linux/macOS CI.
- 2026-09-27 first CI run on `a3da039d` (PR #128): windows-hardening passed; validate (Linux)
  failed 1 test, macos failed 353 (209 failures, 144 errors). The Linux failure was the
  tracked-symlink installer test reading pwsh's colored, "|"-wrapped error record; fixed in
  `7db24835`. The macos job is set non-blocking in `221bac00` (owner decision, 2026-09-27).
- PR #128 review (Codex connector) left two P1 threads that blocked the squash merge:
  closeout reachability let a dependency activate an untaken repair route (fixed in `fd9600b1`,
  regression `test_a_dependency_does_not_activate_an_untaken_repair_route`), and both installers
  could overwrite an existing `<backup>.source` receipt (fixed in `b125ba8f`, regressions
  `test_*_keeps_an_existing_source_receipt`; installer tests 21 OK on Windows).

### Open follow-ups

- macOS support: Harness fails 353 tests on macos-latest. Causes seen: `_trusted_executable`
  rejects Homebrew Git (symlinked, user-owned under `/opt/homebrew`), `/var` symlink temp roots
  hit the transition-path link check, `linked skill paths are not supported`, and `/dev/fd/3`
  permission errors. Remove `continue-on-error` from the macos job once these pass.
- The POSIX commit paths (Linux and macOS) are verified only by reading and mocked-libc tests
  until CI runs them.
- The exchange verify/restore code (RUN, DOCUMENTS, design-system) has two older narrow races:
  after a restore swap it compares with the expected bytes instead of the displaced bytes, and on
  a double concurrent write the cleanup deletes displaced bytes it reports as preserved.
- Mission subagent workers have the same wildcard mission-scope mismatch that
  harness-correctness-01 fixed for reviewers (pre-existing, not gated).
- The coordination_paths allowlist and protected-branch grant checks are not version-gated;
  older in-flight RUNs that violate them will need a PLAN/RUN revision.
- The acceptance register commit (H1 to H2) has no slot in the RUN state model.
- dh-docs-01: add the delivery-acceptance rows to the PLAN and RUNBOOK templates together with
  their test fixtures.
- dh-docs-04: workers and reviewers still have no result field that carries contract-adoption
  reading evidence.
- skills-correctness-3: Harness joins and the compiler preflight do not enforce the current-HiFi
  rule for legacy approvals.
