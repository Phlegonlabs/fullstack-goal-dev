# EPIC-lightweight-entry: Bound dispatch input and shorten routine entry

Status: in_progress

## Problem And Baseline

Large parent messages can exceed a child request's context allowance or delay its first response.
The review renderer limits inline diff bytes, but it does not limit the complete message.
Skill entries also include procedures for stages that a routine task does not use.

Repository: `product-delivery-harness`.
Baseline: released `v0.62.2`, commit `4338305518bac8155af9b89da6e10a02fe62e71f`.
Work branch: `codex/lightweight-context`.
The local `main` ref is older; this task preserves it and uses the released tag.
UI impact: `none`. This is direct skill-source maintenance, without a consumer Product Definition or PLAN/RUN.

## Accepted Scope

The owner accepted the lightweight architecture and requested implementation with multi-agent work on 2026-10-07.
The owner then confirmed the proposed work branch.
Existing machine instructions require local atomic commits. Push, release, installation and cleanup remain unauthorized.

- Check the final parent message's UTF-8 bytes against an explicit positive budget.
- Apply the same check to the complete scripted review packet before durable dispatch or artifact writes.
- Keep direct and managed routes. Move stage procedures behind mandatory, conditional reading links.
- Give the parent global document inventory ownership. Children verify their applicable sources independently.
- Reuse a semantic template audit only while its observed inputs and applicable scope remain unchanged.
- Preserve host roles, authorization, source identity, independent review, complete applicable evidence and historical contracts.

The checker cannot observe every host-injected instruction, tool schema or model token.
It does not guarantee that a request cannot time out.
No model, provider, retry or timeout setting changes are included.

## Acceptance And Dependencies

| ID | Expected outcome | Verification |
| --- | --- | --- |
| LIGHT-01 | Full-message UTF-8 budget rejects overflow without durable RUN or artifact changes | Checker, renderer and reservation regression tests |
| LIGHT-02 | Seven entries expose applicable mandatory stage reads; moved rules remain reachable | Skill contracts, link checks and before/after source inventory |
| LIGHT-03 | Scoped child checks preserve unknown identity and do not replace the parent snapshot | Document-sync and entry contract tests |
| LIGHT-04 | Root governance, templates, workflow and four READMEs agree with the accepted routing | Governance, README and cross-skill tests |
| LIGHT-05 | Fixed local candidate passes applicable checks and independent source/security review | Exact-SHA test logs and reviewer result |

One writer owns this checkout at a time. Read-only siblings may inspect it.
Complete and commit each logical task before starting the next task.
New required reviews use fresh sibling context.

## Document Impact

| Source | Affected artifacts | Required recheck |
| --- | --- | --- |
| Dispatch checker and renderer | Runtime references, worker template and four READMEs | Byte boundaries, invalid limits and atomic rejection |
| Seven skill entries | Named stage references and each skill's contract tests | Mandatory triggers, links and retained authority |
| Document-sync policy | Root AGENTS, templates and existing task evidence | Parent/child ownership and compaction recovery |
| Governance entry | Workflow and source-maintenance rules | Local exceptions, effective discovery and authorization |

## Change Log

| Observation / change | Reason and scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| 2026-10-07: first observation and scope acceptance | Clean checkout at baseline; branch created from released tag after owner confirmation | Baseline `4338305518bac8155af9b89da6e10a02fe62e71f`; branch `codex/lightweight-context` | Read-only exploration and architecture review completed. Implementation and tests remain pending. Loaded skill identity and actual child model identity are unobserved. |
| 2026-10-07: LIGHT-01 working-tree implementation | Added the full-message UTF-8 checker, optional renderer/reservation guard and distinct inline-diff/full-message budgets; synchronized runtime guidance, worker template and four READMEs | working-tree on `codex/lightweight-context` from `f4ae46f18f46d79e938fe6dee1291f416b879a84`; logs under `.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light01-attempt2` | Focused suites passed: 15 launch/budget tests, 39 renderer/reservation tests, 60 contract tests, pyflakes, skill spec and docs weight. Atomic commit, exact-SHA evidence and independent review remain pending. |

## Results And Remaining Work

Implement LIGHT-01 through LIGHT-04 in separate verified commits.
Then complete LIGHT-05 on the final local candidate.
Keep complete test logs outside the checkout and report bounded summaries.
Observe the installed `0.62.2` template separately from this development source.
No release or installation is part of this task.
