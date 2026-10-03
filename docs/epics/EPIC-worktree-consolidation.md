# Consolidate the current worktrees

Status: all 16 worktree heads published; current source integrated locally.
Fixed-candidate contract/correctness review, complete CI and exact main promotion remain pending.

## Request And Scope

On 2026-10-03 the owner requested committing, pushing and merging every current
worktree. The owner then questioned the development target. Fresh remote
observation confirms no development ref and main at
`bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61` (0.58.0).
The new dual-branch consumer contract remains intact. Creating or protecting
development is not part of this request. Direct main landing needs the owner's
exact-candidate decision and an explicit source-release exception to that route.

This is one parent-owned direct consolidation sequence. It creates no consumer
Product Definition, PLAN/RUN, worktree, local branch or UI design decision.
UI impact of conflict repair is none: the newer UI3/DS4 fixtures are retained,
and their synthetic PRD declares eval exemption before approval hashing.
Existing Epics retain accepted scope and historical verification.

Write scope is the 15 Eval conflict paths, the Vite proposal/index, this Epic,
the workflow guide and four-language candidate descriptions. The 13 older
detached checkouts have no uncommitted changes; their exact commits are retained
as remote snapshot branches rather than reapplying old versions over current
sources. Snapshot publication is preservation, not fresh verification or release.

## Repository Observations

- Entry: clean `codex/harness-flow-modernization` at
  `2f4ed10ec7a3571f1252f017544b77d9617bee82`.
- Eval: clean `codex/eval-contract-research` at
  `72560a1b7cb5d1d8e7b0163babd0a9ed9ecc9483`, initially unpublished.
- Vite: detached `2fa9b343175f585aca1da551edc0a8654380de9b`, with only two
  research documents uncommitted. Their checkpoint is `23d56690`.
- All heads below were pushed without force in one atomic operation, with
  exact remote read-back. Main was unchanged and development remained absent.
- Live ruleset 18970503 requires a PR and validate, and allows only squash.
  The proposed sole change is allowed_merge_methods: squash -> merge,squash.
  PR/check/deletion/non-fast-forward controls stay intact. No ruleset write,
  protected-branch update, tag, installation, deletion or cleanup has occurred.

| Worktree | Published full SHA | Remote branch | Disposition |
| --- | --- | --- | --- |
| primary | `2f4ed10ec7a3571f1252f017544b77d9617bee82` | `codex/harness-flow-modernization` | current source |
| eval | `72560a1b7cb5d1d8e7b0163babd0a9ed9ecc9483` | `codex/eval-contract-research` | current source |
| viteplus | `23d5669089fb19b13b932361adf392346ea5d9ae` | `codex/viteplus-evaluation` | current source |
| harness-installer-repair | `70ab12bd8770ec4d9ae394b66e640c8c597c7cbb` | `codex/worktree-snapshot-harness-installer-repair` | historical snapshot; no uncommitted edits |
| pdh-review-followups | `fd54a797559c7994eca6af838a581d7fad0e30ac` | `codex/worktree-snapshot-pdh-review-followups` | historical snapshot; no uncommitted edits |
| wf_81434796-014-1 | `d9b037b96f7797629394f9dc5592d572d0c2f772` | `codex/worktree-snapshot-wf_81434796-014-1` | historical snapshot; no uncommitted edits |
| wf_81434796-014-2 | `206a92ed4057367f0eb255387e5f831723de2a67` | `codex/worktree-snapshot-wf_81434796-014-2` | historical snapshot; no uncommitted edits |
| wf_81434796-014-3 | `4b76728d3c6b7956aa2ecf44977c0cb2925f9902` | `codex/worktree-snapshot-wf_81434796-014-3` | historical snapshot; no uncommitted edits |
| wf_81434796-014-4 | `6ccd5a22d516e6619b9c96e2639f7bb088a054ce` | `codex/worktree-snapshot-wf_81434796-014-4` | historical snapshot; no uncommitted edits |
| wf_81434796-014-5 | `72538ec21eab61ef1ed7ea9f5dc9d382c7d7d74f` | `codex/worktree-snapshot-wf_81434796-014-5` | historical snapshot; no uncommitted edits |
| wf_cf68e735-fca-1 | `66bfd01203aa11170efe375ddb4d5dfcdfdd1b00` | `codex/worktree-snapshot-wf_cf68e735-fca-1` | historical snapshot; no uncommitted edits |
| wf_cf68e735-fca-2 | `a1065919dec551fcc930961ee3eb6f1630c65098` | `codex/worktree-snapshot-wf_cf68e735-fca-2` | historical snapshot; no uncommitted edits |
| wf_cf68e735-fca-3 | `bb8d9a11a70bd3153afb4cf837ab1bded96360af` | `codex/worktree-snapshot-wf_cf68e735-fca-3` | historical snapshot; no uncommitted edits |
| wf_f2da7312-78e-1 | `14e1bb633ea26aac96a79b6b93e112e7092c461c` | `codex/worktree-snapshot-wf_f2da7312-78e-1` | historical snapshot; no uncommitted edits |
| wf_f2da7312-78e-2 | `3ab107af56baefd8791e2104c4bff7adeaaf9cda` | `codex/worktree-snapshot-wf_f2da7312-78e-2` | historical snapshot; no uncommitted edits |
| wf_f2da7312-78e-3 | `84ec6261b466a1dce97fb4b038ec8ea502f22c07` | `codex/worktree-snapshot-wf_f2da7312-78e-3` | historical snapshot; no uncommitted edits |

## Change Log And Verification

- `23d56690`: preserve the dated Vite/AI tooling research and index. Whitespace,
  index uniqueness, five referenced source locations and staged diff passed.
- `14eb8674`: merge the 42-commit Eval line into the modernization branch.
  Resolve 15 paths by preserving both contracts, choosing version 0.60.0,
  combining README histories and keeping the newer UI3/DS4 plus dual-branch
  fixtures. Current golden-path PRDs receive the reasoned Eval declaration
  before their approvals; production validators are unchanged by that repair.
- `bd45e8f2`: integrate the Vite documentation. Resolve only DOCUMENTS by
  preserving current rows and adding the proposal. Scoped whitespace/index
  and staged diff checks passed.
- Working-tree candidate preparation: index this consolidation, reconcile the
  workflow's Eval steps and distinguish the unreleased 0.59 source milestone
  from the unified 0.60 candidate in all four README histories.
- 2026-10-03 owner clarification: "這套是 skills，skills 不用去 review security".
  Skip security review for this source consolidation. Continue the independent
  contract/correctness review and complete source CI. This is this task's owner
  exception; it does not edit consumer product security gates. PR #135 was
  opened at `27b634c3`; this documentation checkpoint creates its next exact
  candidate, without repinning earlier checks or review results.

Focused integration checks passed on the resolved working source before the
Eval merge commit: skill specification, full six-skill Pyflakes, docs weight,
new RUN, tasks view, both golden paths, all three Eval suites, current source
binding and version contract. These are working-tree results, not repinned
final-SHA evidence. Logs and immutable publication inventory are outside Git:
`C:/Users/mps19/AppData/Local/Temp/pdh-worktree-merge-20261003-eb6k85jg`.

The complete fixed-candidate Linux/macOS/Windows CI, required browser suites,
golden path and independent contract/correctness review must cover the unified SHA.
The bound reviewer is native GPT-6.1-Sol/xhigh with read-only assignments;
review coverage and actual returned identity will be retained externally.

## Document And Local-Data Audit

Observed installed Harness is 0.59.0 from a development installation. Its
PROJECT_AGENTS template and the source template both hash to
`0d5064d94c0072ad2d1f06f3b516dab328d425be79454df10b50ce6f44b2470e`.
Shared governance is current by meaning, with the source-repository omissions
and stricter local Git rules retained. Loaded-at-start skill identity is unknown.
Document sync reports only loaded_identity_unobserved and baseline_review_required;
neither is a PASS. No live consumer PRD/architecture or generated tasks view applies.

No new local artifact class is added: logs, process records and proposal JSON
stay outside the checkout. Existing ignores cover dependencies, bytecode and
local values. All source fixtures, templates, locks, research and Epics stay
tracked. No local worktree, data, branch, backup or old installed skill is removed.

Next action: finish the fixed-candidate checks and independent review, retain
the PR and results, then request the exact main landing and merge-method change.
Do not infer either from a branch push. Formal tag and local installation
remain separate from this source consolidation.
