# Skills source maintenance uses main

Status: complete
UI impact: none

## Problem And Baseline

Source instructions still required a permanent development branch at released
main `aab39d0545a95b3ae2b972cf7843dcf8eadb7cf4`. The owner changed that policy
on 2026-10-04. The remote development branch was deleted under separate
explicit authorization. The source instructions must reflect the decision.

## Accepted Scope

These skills are maintained for the owner's own repositories. Source maintenance
uses temporary work branches and reviewed PRs directly to main. Consumer branch
policies remain unchanged. Update source governance and all four README release
instructions. Do not change consumer templates or archived records.

## Acceptance And Dependencies

Require source instructions to distinguish source maintenance from consumer flows.
Preserve exact-candidate verification, version bumps, tags and official installation
gates. Check the staged diff and current skill contracts.

## Change Log

| Observation | Scope and evidence | Verification and remaining work |
| --- | --- | --- |
| 2026-10-04 entry | Clean main baseline above; work branch codex/loop-engineering. Earlier owner decision and branch deletion are separate from this document edit. | No consumer policy change. Source documentation update pending. |
| 2026-10-04 source policy | AGENTS, four README introductions/release instructions and source-contract expectations updated in place | 60 skill contracts and whitespace passed. First test run exposed two stale source assertions; corrected while retaining consumer checks. |

## Results And Remaining Work

Source governance synchronization passed local verification and is committed with
this record. Its atomic commit is available through path history.
No publication or installation is authorized by this record.
