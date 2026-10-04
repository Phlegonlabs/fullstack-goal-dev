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

## Results And Remaining Work

Implementation, focused regressions, unified checks and independent review pending.
No push, PR merge, release tag or local skill installation is part of this task.

P1 adds the exported `parse_platform_delivery(architecture_text, prd_text, *, require=False)`
API. It returns a contract with `protocol`, `mode`, owner/status, ordered stages,
stage IDs/surfaces/test IDs, shared surfaces, and shared ARCH IDs, or `None` for
an absent active legacy section. The opt-in checker flag requires the contract and
approved status. PLAN mapping, full source suite, unified review, and release remain pending.
