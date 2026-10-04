# Generate, verify and correct with platform ordering

Status: accepted
UI impact: none

## Problem And Baseline

Released source `aab39d0545a95b3ae2b972cf7843dcf8eadb7cf4` already supports
bounded task, mission and integration correction. Feature completion and approved
Web/iOS order are not explicitly joined to executable acceptance gates.

## Accepted Scope

On 2026-10-04 the owner approved the proposed Generate -> Verify -> Correct
method and requested multi-agent implementation. Retain one writer per checkout.
Use direct source maintenance with serial writers and one integration verification
sequence. Do not create consumer product documents or PLAN/RUN for this task.

Define measurable loops across stages and execution levels. Link feature outcomes
to existing final gates. Put owner-selected platform order in canonical architecture
and check its frozen join to PLAN dependencies. Keep both platforms' interfaces
and design obligations upstream. Separate historical platform handoff evidence from
fresh unified-candidate regression. Preserve retry budgets and human decisions.

## Acceptance And Dependencies

| Contract | Expected result | Verification |
| --- | --- | --- |
| Bounded loops | Clear target, scope, verifier, feedback and stopping condition; success stops the loop | Skill/spec checks and semantic review |
| Feature acceptance | Contributing missions precede declared acceptance gates; current-head results required | Positive and negative PLAN/closeout tests |
| Platform sequence | Approved surface order and required TEST IDs join to completion-mission verification and strict dependencies | Product parser, frozen-source join and graph regressions |
| Compatibility | Unmarked historical packages keep their contracts; marked malformed inputs fail closed | Legacy, duplicate, spoofed-marker and stale-source tests |
| Integration | No scheduler, new state store, zero-bug claim or unrelated policy change | Full applicable local suite and independent source/security review |

## Document Impact

Update the applicable canonical skills, references, templates and all four README
descriptions in the same logical changes. Keep consumer release branch policy.
No product UI or visual evidence applies. Existing ignore patterns cover Python
cache and dependencies; task logs and receipts stay outside Git.

## Implementation Design

Use the approved `platform-delivery/1` section in canonical architecture. It records
whole-platform order, stable release surfaces, required TEST IDs, completion signals,
shared surfaces and interface ARCH IDs. Keep existing Product approval authority.
Absent markers retain legacy behavior; present malformed markers fail closed.
New authoring requires an explicit protocol or justified single-platform exemption.

PLAN v6 may declare `platform_delivery` stage mappings with mission IDs, a completion
mission ID and that mission's integration verifier IDs. Use the last substantive
mission as the stage handoff. Every contributing mission precedes it through
pass-only dependencies. It precedes every next-platform mission the same way.
Mission integration retains PASS at its actual integrated SHA. This is historical
stage-start evidence, not proof of current platform health.

Verifier `acceptance_test_ids` joins commands to required upstream tests. Feature
Must traces may declare `acceptance_gate_ids` referencing existing final gates.
Every contributing mission precedes those gates through pass-only dependencies.
The final gates cover both platforms at the current unified SHA. Existing candidate
invalidation and retry budgets remain unchanged. Route-only reachability is not
a completion dependency. No new scheduler or RUN state is needed.

Serialize Product-contract, Harness-contract and cross-stage guidance writers.
Each writer owns its files, tests and same-outcome README descriptions. The parent
owns the index, integration checkpoint and final independent source/security review.

## Change Log

| Observation | Scope and evidence | Verification and remaining work |
| --- | --- | --- |
| 2026-10-04 entry | Clean baseline above; branch codex/loop-engineering. Independent loop and platform explorers plus read-only architecture assignment dispatched. | Design underway; no implementation verified. Installed skill 0.61.0 observed previously; loaded identity remains unknown. |
| 2026-10-04 P1 | Product parser `platform_delivery.py`, package checker opt-in integration, focused regressions, Product guidance, and four README behavior notes on branch `codex/loop-engineering`, based on `74d401a6a13d8ecb2f99f4417ffdb87fec8372b6` and the approved architecture contract. | Working-tree verification: 13 `test_platform_delivery.py` tests PASS; 80 `test_product_package_checker.py` tests PASS; `pyflakes`, `docs_weight.py`, and `git diff --check` PASS. Logs stay under the task-owned external check directory. Commit pending in this change; PLAN sequence mapping remains for the Harness writer. |
| 2026-10-04 10:13 -07:00 H1 | Branch codex/loop-engineering; baseline 92dd8756. Working-tree H1 adds `platform_delivery_contract.py`, PLAN/runtime/packet joins, standalone planned `PRD-*` feature gates, focused tests and shared fixture support, canonical PRD TEST authority in `delivery_acceptance_io.py`, Harness contracts/templates and four README descriptions. Product files remain at 92dd8756. The 659-line module is kept together: it owns one fail-closed PLAN-to-architecture and acceptance join; shape, dependency paths, verifier annotations and gates share the same canonical decision. | Passed at this working-tree scope: platform contract 28; manifest 117; verifier runtime 20 (2 Windows skips); source join 32; review packet 9; selector 64; graph 45; closeout 8; transition 15 (1 skip); delivery acceptance 43; eval contract 21 (1 skip); skill contract 60; scoped pyflakes. `check_skill_spec.py`, `docs_weight.py` and final diff checks run before commit. Remaining: parent post-H1 Product parser repairs, G1 guidance/Windows inventory, full fixed-candidate validation and independent review. |
| 2026-10-04 P1 repair | Baseline `da8a916d75b567b2b5a5048b6979b8cb7559210f` was clean. Product repair changes only `platform_delivery.py`, `test_platform_delivery.py`, and this Epic row. Active protocol markers are now counted globally and must resolve to exactly one marker inside the canonical section. Stage IDs reuse Release Targets' `KEBAB_RE`. Exported parser and checker APIs are unchanged. The 518-line module stays together because it owns one responsibility: fail-closed parsing and normalization of the `platform-delivery/1` contract; splitting helpers would create an unused boundary without a second consumer. | Working-tree verification: 14 `test_platform_delivery.py` tests PASS; 80 `test_product_package_checker.py` tests PASS; scoped `pyflakes`, `check_skill_spec.py`, `docs_weight.py`, and `git diff --check` PASS. Final log: `p1-repair-final-9cea5246d9c04349ba0d7b4356625fb6.log` under the task-owned external check directory. Full fixed-candidate suite and independent review remain pending. |
| 2026-10-04 P1 review repair | Baseline `594266c3c3c658c42eab9509e26ab1fdcf99f76f`. Review hardening changes only the Product parser, its focused tests, and this row. The duplicate-marker fixture now places its second active marker in an explicit `## Notes` section, so it independently proves global placement instead of relying on the fixture's trailing Observability section. Stage validation restores the prior meaningful/placeholder check before the lowercase kebab check and asserts rejection of the covered `todo` stage. | Working-tree verification: 14 `test_platform_delivery.py` tests PASS; 80 `test_product_package_checker.py` tests PASS; scoped `pyflakes`, `check_skill_spec.py`, `docs_weight.py`, and `git diff --check` PASS. Log: `p1-review-repair-35a2d155861740b3af566fd26707849e.log`; the same suite is rerun after this row. Full fixed-candidate suite and independent review remain pending. |
| 2026-10-04 G1 guidance and CI inventory | Baseline `507544862ea4a943da9910acfaa28a8ebe662a9b` was clean. G1 adds the shared `gen-verify-correct.md`, one pointer in each of the seven SKILL entrypoints, a Traditional Chinese workflow section, one reconciled flow overview in each README, and the Epic/index update. It preserves the committed P1/H1 platform and feature paragraphs. CI adds `test_platform_delivery_contract.py` to `WINDOWS_NATIVE_FILES` and raises the planner fixture expectation to 13 files; it uses existing `--allow-unmeasured` timing policy and no workflow mutation. The first skill-contract run found the Harness word cap at 3,621; a concise same-scope pointer repair and clarified broaden rule produced the passing final bytes. | Final working-candidate verification: `check_skill_spec.py` exit 0; `docs_weight.py` exit 0; `test_skill_contract.py` 60 tests PASS; `test_ci_test_shards.py` 13 tests PASS; `test_ci_candidate_gate.py` 12 tests PASS; `git diff --check` exit 0. Captured PID and 120-second deadline logs: `summary.json` under `g1-final-bookkeeping` in the task visualization directory. The parent-owned final unified-check and review authority is [loop-engineering-result.md](C:/Users/mps19/.codex/visualizations/2026/10/04/01a106f3-1755-7b42-873e-dbd7ebc45feb/loop-engineering-result.md), written after fixed-SHA checks and review. Source remains unreleased; push, PR merge, tag, and install remain outside this task. |

## Results And Remaining Work

H1 is committed at `da8a916d75b567b2b5a5048b6979b8cb7559210f`. Its focused
platform, manifest, verifier-runtime, source-join, review, selector, graph,
closeout, transition, acceptance, eval, and skill-contract results remain the
recorded evidence for that exact change. P1 is committed at
`92dd875607fd00cde3ccf7581f671694e0097f9a`; its later review repairs are
committed at `594266c3c3c658c42eab9509e26ab1fdcf99f76f` and
`507544862ea4a943da9910acfaa28a8ebe662a9b`. Their Product parser and checker
results also remain exact-change evidence.

P1 adds the exported `parse_platform_delivery(architecture_text, prd_text, *, require=False)`
API. It returns a contract with `protocol`, `mode`, owner/status, ordered stages,
stage IDs/surfaces/test IDs, shared surfaces, and shared ARCH IDs, or `None` for
an absent active legacy section. The opt-in checker flag requires the contract and
approved status.

G1 adds cross-stage loop ownership, human/read-only boundaries, focused-first
verification with full required escalation, exact-candidate reuse rules, feature
and platform gate joins, and the Windows-native inventory entry for the new
Harness contract test. This row records focused checks run on the working
candidate before its atomic G1 commit. The external fixed-SHA report named in the
G1 row is the authority for final unified checks and review; until that report
exists, those final outcomes remain pending and do not invalidate the committed
focused results above.

The source is unreleased. Push, PR merge, release tag, and local skill
installation remain outside this task.
