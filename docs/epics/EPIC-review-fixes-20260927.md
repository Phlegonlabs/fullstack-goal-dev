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
| Release surfaces | `VERSION`, `package.json`, RUNBOOK default, README badges and history agree on 0.55.0 (0.55.1 after round 4) | `test_skill_contract.py` | none |
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

Round 4 was observed 2026-09-28 on `codex/review-followups` from base `2fa9b343` (v0.55.0).
Five writers worked in separate worktrees; the parent merged them serially, then added the
leftover fixes and this documentation sync. All entries are committed.

| Change / request | Reason and affected scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| Exchange races | RUN, DOCUMENTS and design-system exchange commits, POSIX and Windows: the restore check compares with the displaced bytes, not the expected ones; displaced bytes move to a named `.recovery` file before any other read (Windows keeps `.backup`/`.rollback`) and the error names that path; a second write moved out by the restore is kept unless it matches our payload | `603a7c16`, `732efe56`, `d7f6e255`, `1be57bcc`, `d9b037b9`; merge `2c84dbb0` | Exchange and concurrent-write tests passed on Windows. The three older native displaced-edit tests passed only because their regex also matched the buggy `restore` message; they now require `displaced bytes changed`. Real POSIX primitives still need Linux/macOS CI |
| Authorization gating | Mission launches and `app_threads` reviewers under a `*` mission scope are deferred by the selector and refused by `lease-worker` at every RUN-v11 version (validation already rejected them); the 0.55.0 `coordination_paths` and protected `delete_branches` checks skip only pins that parse below 0.55.0 | `9ec65427`, `8bcbddd7`, `2883140c`, `c924894c`, `3fd33787`, `206a92ed`; merge `3daeeb9c` | Focused tests passed: `test_select_ready_nodes` 64, `test_harness_v11` 29, `test_lifecycle_cleanup_targets` 9, `test_harness_manifest` 117 and neighbors |
| Acceptance slot and template rows | dh-docs-01 PLAN/RUNBOOK rows (`SRC-004`, `delivery-acceptance` gate, `N-ACCEPTANCE-GATE`, two edges); the register is committed at H2 and recorded with `record-integration`; `check_delivery_acceptance.py` needs `--candidate-sha` or `--candidate-from-head` and requires the candidate to be HEAD or an ancestor with only register, evidence and coordination changes after it | `5ea531b3`, `3dc114f6`, `62a89456`, `4fbac821`, `1f769049`, `3026b62a`, `887ca93a`, `df04a0e4`, `b921e87b`, `4b76728d`; merge `e02743a2` | Focused tests passed: `test_delivery_acceptance` 31, `test_close_wave` 40, `test_new_run` 10 and neighbors. The checker cannot see the RUN version, so the Git check also applies to in-flight 0.55.0 runs |
| Contract adoption check | dh-docs-04: workers and reviewers return `contract_adoption_check`; recording transitions require it under an adopted contract for runs that require 0.55.1; the wrapped reviewer file is accepted, a blocked reviewer's mismatch digest is kept, and the check stays out of security results | `9b3339cf`, `69a88cb5`, `5fcea6d0`, `641df034`, `526ec426`, `ea469dbd`, `b91a7d2a`, `6ccd5a22`; merge `b0596941` | Focused tests passed: `test_validate_worker_result` 38, `test_harness_v11` 30, `test_write_path_transitions` 26 |
| Current-HiFi cutover | skills-correctness-3: a legacy approval decided on or after 2026-09-27, or with a HiFi or motion receipt run from that date, needs current HiFi evidence; publication, the compiler preflight and UI joins enforce it (joins from 0.55.1 after the final review fixes) | `d518d6a1`, `7dcd0307`, `89d0791c`, `a0400101`, `ab9caf5b`, `72538ec2`; merge `a0fd1245` | Focused UI, compiler and Harness tests passed. The compiler preflight has no RUN version gate |
| Leftovers | DA-5: with an acceptance gate in PLAN, worker-result validation refuses a worker change outside every task `write_scope` in all workspace modes; `--contract-adoption-check` documented in the state model, RUNBOOK and security review skill | `8434dccc`, `6c3bb959` | `test_validate_worker_result` 41 OK, rerun during the doc sync |
| Base UI / Radix Primitives | Product Definition names both as headless React component-foundation options, one per product; UI Design Builder draws the chosen layer's states and focus behavior | `6238c318` | Product Definition `test_skill_contract` 96 OK, rerun during the doc sync |
| Final review fixes | Fresh correctness and security review of `2fa9b343..d87df8ed`: security-01/correctness-acceptance-evidence-whitelist acceptance evidence must sit under `evidence/` next to the register; security-02 the worker guard finds the acceptance gate in any argv form and fails closed; security-03 workers can never write the register or its evidence; correctness-review-retryable-needs-adoption-check plus a pre-existing conflict: `retryable_failure` and `contract_gap` reviews may omit the adoption check and validators now accept their findings, so a crashed review can be recorded; correctness-compiler-preflight-cutover-ungated and correctness-hifi-join-gate-0550-inflight: UI and pair joins apply the dated rule from 0.55.1 by RUN pin; security-04 receipts compared with the 2026-09-27T00:00:00Z instant | `d077de32`, `8d9d3ee5`, `115c36a0`, `66bfd012`, `cbc5a73e`, `a1065919`, `36f16b38`, `80ebdfd5`, `bb8d9a11`, `d1f82287`, `832b1155`; merges `152b44a5`, `85383c34`, `909013c9` | Focused tests passed per writer and after integration; full suite below |
| README sync, version 0.55.1, index, this record | 0.55.1 release surfaces and history; README descriptive sections for round 4 and Base UI; these rows and the DOCUMENTS status | `bfc0e782`, `c28c7d6a`, and the commit that adds these rows | README structure, skill contract and docs-weight checks passed |

### Skipped or partial, with reasons

- dh-git-push-6: documented only. A lease or force push flag is forbidden here, so the residual
  window between the remote recheck and the no-force push is described instead.
- dh-authz-4: not changed. The regex parser only serves pinned pre-0.38 RUN recovery.
- udb-05: skipped. `review-workflow.md` makes the preserved-page flag intentional.
- cross-installer-dirty-bytes-no-source-identity: installers still install uncommitted bytes;
  refusing them was replaced by printing and recording the source commit and dirty state.
- dh-docs-01: partial. The PLAN template names the delivery-acceptance entries in prose. The
  template rows were left for a follow-up because `MISSION_RUNBOOK.template.md`,
  `test_new_run.py` and `test_render_tasks_view.py` fixtures must change together. Done in round 4.
- skills-correctness-3: documented limitation. Only `check_ui_publication.py` enforces the udb-01
  HEAD comparison; Harness joins and the compiler preflight still accept legacy approvals.
  Fixed in round 4.

## Results And Remaining Work

### Breaking changes (0.55.0)

- Product Definition Package and Stack Checkpoint digests cover raw bytes, including fences,
  indented lines and HTML comments. Re-run finalize and re-record both approvals.
- Mobile/Desktop stacks need a `Styling approach` row.
- Environment Status Checked values must be RFC3339 with a timezone.
- Cleanup lifecycle nodes need an exact target in runs that require 0.55.0.
- Impeccable critique and audit are required before Visual Approval.
- Enhancement UI rows name Wireframe Validation and Visual Approval.

### Changes consumers may notice (0.55.1)

- `check_delivery_acceptance.py` needs `--candidate-sha` or `--candidate-from-head`. An
  in-flight 0.55.0 run fails the gate if its register commit holds unlisted or product files,
  or if it passes a stale `--candidate-sha` after a repair.
- Under an adopted contract, runs that require 0.55.1 need `contract_adoption_check` from
  every worker and non-blocked reviewer.
- A legacy approval dated on or after 2026-09-27 on `ui-evidence/2` fails the compiler
  preflight at any run version.

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
- Round 4 (2026-09-28): focused tests per writer passed; full suite: pending (parent fills in).

### Open follow-ups

- macOS support: Harness fails 353 tests on macos-latest. Causes seen: `_trusted_executable`
  rejects Homebrew Git (symlinked, user-owned under `/opt/homebrew`), `/var` symlink temp roots
  hit the transition-path link check, `linked skill paths are not supported`, and `/dev/fd/3`
  permission errors. Remove `continue-on-error` from the macos job once these pass.
- The POSIX commit paths (Linux and macOS), including the round-4 race recovery arms, are
  verified only by reading, mocked-libc and os-proxy tests until CI runs them.
- Rerunning acceptance after H2 needs a formal PLAN revision; a transition that accepts a
  register-only commit on top of a repair would remove that cost. Manifest validation does not
  require the acceptance gate entries or reject unreplaced `<...>` argv placeholders. A product
  commit that lands between the scenario run and the register commit, and that the register
  names, passes the Git check; only review catches it.
- Optional (CAC-4): the recording transitions could recompute the contract digest at record time.
