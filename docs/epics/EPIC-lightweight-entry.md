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
| 2026-10-07: LIGHT-01 committed-head follow-up | Observed the completed LIGHT-01 commit without changing its earlier working-tree outcome row | Commit `6ae6b3e0f938b13e71907e0844607072e19fb882`, `feat(harness): enforce complete launch message budgets`, on clean `codex/lightweight-context` | This is the clean base for LIGHT-02. Earlier row remains labeled as working-tree evidence. |
| 2026-10-07: LIGHT-02 working-tree implementation | Moved managed route, reference routing, adapter routing, runtime/wave policy, mission topology and workflow steps 2-6 to `references/stages/managed-delivery.md`; kept intake, size gate, direct route, boundaries, context and UI triggers in the entry; added conditional mandatory anchor routes; synchronized four READMEs and owner tests | working-tree on `codex/lightweight-context` from `6ae6b3e0f938b13e71907e0844607072e19fb882`; entry `29304` before and `14352` after bytes (`-14952`); stage `16098` bytes, SHA-256 `5f12ea8d7bafbdd391154e1490638a473c88aa7e663ab444d90b1a74505ccc94`; logs under `.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light02-attempt1` | Focused tests passed: entry 61, docs weight 13, schema 4, cross-skill 17, self-review 4; skill spec and pyflakes passed; moved blocks compare exact to base after newline normalization. Document sync reports review-required for unknown loaded identity, first-use baseline and README retirement catalogs; final diff check, commit and independent review remain pending. |
| 2026-10-07: LIGHT-02B Product entry working-tree implementation | Moved the complete Workflow, PRD self-review, interview, reference-routing, UI-preflight and output sections intact to `references/stages/product-definition.md`; added conditional trigger links, an entry boundary and a stage path interpretation; updated owner assertions and four README descriptions | working-tree on `codex/lightweight-context` from `dd72a3d9cfa3899c09ce2f241be16f9f22f906dd`; entry `55272` before and `5394` after bytes; stage `51772` bytes; total `57166` (`+1894`) including the stage title and routing preamble; moved blocks compare exact to base after the title/preamble boundary; logs under `C:/Users/mps19/.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light02b-attempt1` | Product skill 101, Harness skill 61, graph identity 7, review translations 15, cross-skill 17, self-review 4 and reference-library 9 tests passed. New routing test, skill spec, docs weight, pyflakes and `git diff --check` passed. Atomic commit, independent source/security review and final SHA observation remain pending. |
| 2026-10-07: LIGHT-02C UI entry working-tree implementation | Moved the complete Required Skills And Inputs, Workflow with its enhancement-first preamble, Author Self-Review Before Handoff and Reference Routing to `references/stages/ui-design.md`; kept Installed Commands, Purpose, Design Lifecycle and Review And Repair Boundaries in the entry; added conditional stage links, an entry boundary and stage path interpretation; synchronized four README descriptions and owner/cross-skill assertions | working-tree on `codex/lightweight-context` from `31beddd1379c9b293c1935f5db272a0ad21d8f02`; entry `22603` before and `7948` after bytes, SHA-256 `9b6a1f02488f28cf4c9ce50e6d1c42fdf54e8af8210f1e960fa6362c71548919`; stage `16293` bytes, SHA-256 `837fa88fad76100fe80f9b9f205994cf8fd40ce7b44da2b5580dd865552c0d88`; total `24241` (`+1638`); moved blocks compare exact to base; logs under `C:/Users/mps19/.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light02c-attempt1` | UI skill 13, Harness skill 61, graph identity 7, cross-skill 17, self-review 4 and reference-library 9 tests passed. Skill spec, docs weight, pyflakes and `git diff --check` passed. Atomic commit, independent source/security review and final SHA observation remain pending. |
| 2026-10-07: LIGHT-02D Compiler entry working-tree implementation | Moved the complete Compilation Skills Gate, Inputs And Ownership, Workflow, Validation, Reference Routing and Output Rules to `references/stages/design-compilation.md`; kept Installed Commands, Purpose, approval-digest semantics, conditional mandatory routes and the entry boundary; made Validation explicit for compile/update; corrected three stage-relative cross-skill links after advisory review; updated owner-section assertions and four README descriptions | working-tree on `codex/lightweight-context` from `cde5d1837430415c18b81969015f96a236126b1b`; entry `16557` before and `5943` after bytes, SHA-256 `4dc374670c5a1a20200ff071672089aa6f1c46ba84d842684ccf39d887a7f887`; stage `12926` bytes, SHA-256 `d154a49b1965dd69d69c95124fb5cd177368d8d839a03ec2c85b7ee4b4da616a`; total `18869` (`+2312`); moved blocks compare exact to base after actual-link path normalization; logs under `C:/Users/mps19/.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light02d-attempt1` | Compiler skill 14, Harness skill 61, cross-skill 17, self-review 4 and reference-library 9 tests passed; all entry/stage Markdown targets and anchors resolve from their own file; skill spec, docs weight, changed-test pyflakes and pre-Epic `git diff --check` passed. Atomic commit, independent source/security review and final SHA observation remain pending. |
| 2026-10-07: LIGHT-02E Activation entry working-tree implementation | Moved complete Required Inputs, Workflow, Status And Outcome Handoff, Reference Routing and Output to `references/stages/activation.md`; kept Installed Commands, Purpose, Boundary, Capability And Authorization, Secrets And Evidence, execution-by-default, exact target/action grants, unknown-result read-back, configured-versus-verified, fixed identity, honest blockers and unknown-applicability boundaries; added conditional preparation/execution, closeout, status/measurement and applicable-profile routes; synchronized four README descriptions and owning tests | working-tree on `codex/lightweight-context` from `d6534ec58a88896aa356a79f76330ebd759e2ff7`; raw entry `16887` before and `8259` after bytes, SHA-256 `9be320dbac9e87a38e051f288b450ab22209df281536abc69cd5700070c27951`; stage `10828` bytes, SHA-256 `82d0fc6298e5edde07e0960510deca26fe6753975900b3ab81fb0033d4aa73fc`; total `19087` (`+2200`) including title and narrow path preamble; all five moved sections compare exact to base; logs under `C:/Users/mps19/.codex/visualizations/2026/10/06/01a11277-8783-7192-8c29-2f37de1cf543/light02e-attempt1` | Activation skill 9, Harness skill 62, cross-skill 17, reference-library 9 and enhancement-entry 7 tests passed; all entry links and targets/anchors resolve from their own file. Skill spec, full-script pyflakes, docs weight and `git diff --check` passed. An earlier red run found the Workflow duplicate and was repaired before these final runs. Atomic commit, independent source/security review and final SHA observation remain pending. |

## Results And Remaining Work

Implement LIGHT-01 through LIGHT-04 in separate verified commits.
Then complete LIGHT-05 on the final local candidate.
Keep complete test logs outside the checkout and report bounded summaries.
Observe the installed `0.62.2` template separately from this development source.
No release or installation is part of this task.
