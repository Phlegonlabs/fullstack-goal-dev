# Project Rules

## Runtime Boundary

- This file contains shared repository governance. Preserve the current host's effective instruction discovery and precedence.
- Apply `skills/delivery-harness/references/delegation-contract.md` before direct or managed routing. Split independent substantive research/exploration questions into distinct authorized sibling instances, resolve mandatory frontend/reviewer roles against effective host policy, and verify actual launch/result identity. One writer owns each checkout, including the parent. Required delegation never silently falls back to parent work.
- Use `skills/delivery-harness/references/runtime-adapters.md` for observed native capabilities, authorization, isolation and result contracts. Map the actual tools available to the session; capability does not grant an action.
- Managed rules apply only after work is routed into PLAN/RUN. Direct source maintenance follows the shared principles, Git safety and required verification below without creating managed state.
- This source repository intentionally omits the template's Skill Bindings (it has no consumer stage slots), Deployment and Post-Delivery Activation (it deploys and activates no product), and the delivery-acceptance bullet (it has no product accounts or data). Its Git Flow replaces the template's Git Safety, and its Required Reading replaces the template's. Treat these as local choices, not drift, in the handoff audit.

## Project Entry And Current Work

Start with the effective repository instructions, `docs/DOCUMENTS.md` when present, current product/design sources and relevant unfinished work. At the first work in a new session and every skill invocation, apply `delivery-harness/references/document-sync-contract.md` (under `skills/` in this source repository). Observe loaded versus installed skill identity; unknown means unknown, not the current disk version.

Keep one current PRD. Complete enhancements use `docs/epics/EPIC-<id>.md`, indexed in `docs/DOCUMENTS.md`, to record the problem, baseline, accepted outcome, requirement references, dependencies, document impact and result. Small fixes append to the relevant Epic; detailed direct-task evidence may be linked from it. Follow `delivery-harness/references/bounded-enhancement.md`; an Epic never duplicates PRD or RUN and never grants actions.

Select the record before implementation: a new accepted outcome gets a new Epic; same-outcome fixes append to its Change Log; an isolated small fix gets a bounded Epic entry that may link detailed direct-task evidence. Log the reason, affected scope, commit, tests and remaining work. Do not rewrite closed history. UI enhancements add or patch only named Wireframe/HiFi pages and necessary connecting controls; retain every unaffected product page, style and ID. Full package coverage is not an instruction to redraw the product.

Derive the goal, write scope, design source, dependencies and acceptance checks in the existing task record or PLAN/RUN. Use direct work when one writer and one coherent verification sequence suffice; use managed coordination only when durable handoff, isolated integration or a bounded graph requires it. Preserve valid decisions and authorizations; ask only about a concrete missing dependency.

## Repository Change Checkpoints

These checks apply to every agent task, including work outside Product Delivery Harness and repositories without PLAN/RUN. Run them at task start, after a significant edit/commit/merge/branch switch or newly observed external change, and before completion or handoff. They are task checkpoints, not a background timer, and require only local Git plus the repository documents.

- Observe repository root, branch, HEAD, staged/unstaged changes and non-ignored untracked paths. Compare with the last recorded repository/branch/HEAD and scoped change evidence in the relevant Epic. Use bounded local history and scoped diffs; do not fetch, scan all history or open credential files. Include commits made outside Harness as well as current working-tree changes.
- If the baseline is missing, unreachable or belongs to another branch/repository, record a first observation or baseline gap and the current facts. Do not claim an exact delta or that nothing changed. Preserve unrelated dirty work; discovering a change is not permission to edit it.
- Record each meaningful code, product, configuration or documentation change in `docs/epics/EPIC-<id>.md`, even for small direct work. Append to the matching Epic's Change Log; create a narrowly scoped Epic only when no suitable one exists. An unknown-purpose external change is `observed / unverified` with an explicit scope/intent gap, not an accepted feature or completed task. Keep `docs/DOCUMENTS.md` indexed.
- Keep the record factual: observation time, repository/branch, baseline and observed HEAD, affected paths and requirement IDs when known, observed behavior/change, decision source if known, actual verification and unresolved work. Label uncommitted evidence `working-tree` and record its actual verification separately; HEAD alone does not identify those bytes. Retain scoped diff evidence or its fingerprint so an unchanged HEAD cannot hide new edits. Exclude secrets, generated caches and the Epic/index update itself from recursive change logging.
- Group related changes into one logical entry; append again only when the observed change, verification or unresolved state differs. Reuse an existing entry from another agent instead of duplicating it. A no-change check needs no new Epic or log row. Preserve old results and archived records; a follow-up links them rather than rewriting history.
- During a read-only or no-write task, report the proposed Epic update without writing it. Otherwise update the Epic/index under the task's local documentation authority. The record never grants product approval, marks tests passed without evidence, creates PLAN/RUN, or authorizes commits, branches, installs, pushes, deployment or cleanup.

## Handoff Documentation Audit

Before every handoff, repeat the repository change checkpoint and check whether the documents affected by the observed work agree with the current product and task state. Use `docs/DOCUMENTS.md` to find applicable live PRD, architecture, design, deployment and activation sources; check their status, links, requirement IDs and acceptance criteria. Confirm that each meaningful change appears in the matching Epic Change Log and that the current task record names the actual result, verification and remaining work. For a managed run, compare `docs/goal/PLAN.md` and `RUN.md` with any `docs/tasks.md` view using the renderer's `--check`; RUN is authoritative and a direct task does not need a tasks view. Do not hand-edit the generated part of `docs/tasks.md` or rewrite archived records.

At the same handoff, compare this `AGENTS.md` with the **observed installed** `delivery-harness/assets/templates/PROJECT_AGENTS.template.md` and `delivery-harness/VERSION`. Check shared rules by meaning, not whole-file equality: repositories may add stricter local instructions. Mark the shared rules `current`, `stale` or `unknown` with the observed template identity and concrete differences. Under the current task's authorized document-write scope, update only stale shared instructions in place, preserving owner rules, local paths, bindings and historical decisions; never replace the file from the template. If the installed template is unobserved or a safe merge is unclear, leave the file intact and name the gap in the handoff.

The handoff names the repository, branch, HEAD and working-tree status, the template identity and drift decision, document/Epic/task findings, changes actually made, verification and the next owner/action. A read-only handoff reports proposed updates without writing. A no-change audit needs no new Epic row. This is a task-boundary check, not a timer or permission to publish, approve, commit, push or delete.

## Required Reading

- Before editing `skills/` or any documented flow, read the canonical SKILL.md and the references the change touches; the four READMEs are the documentation of record.
- Before running a Product Delivery Harness flow in a target repository, that repository's seeded `AGENTS.md` Required Reading rules govern the session — they are mandatory, not advisory.
- Work that skipped this reading is a blocking review finding.

## Protect Local Data

- Never delete, overwrite, or move important local data without explicit user approval.
- Preserve unrelated dirty files, branches, and worktrees.
- Avoid destructive Git and filesystem commands unless the user asked for that exact action.

## Gitignore Hygiene

- Treat `.gitignore` as part of every direct and managed change. During the scope scan, decide whether the task introduces or retires a local secret file, generated output, dependency directory, cache, log, temporary file, editor state, or platform artifact.
- Add only patterns justified by the repository's observed toolchain. Ignore value-bearing local environment and credential files plus reproducible local artifacts; keep source, lockfiles, migrations, tests, fixtures, configuration examples and schemas, product documents, and required canonical artifacts tracked.
- Keep `.env.example` or the platform-native example tracked with placeholders only, and ignore the corresponding value-bearing local file. Never open a secret file to decide its ignore rule.
- Preserve existing entries and use the narrowest practical patterns. Never add an ignore rule just to hide a dirty worktree, and never untrack a tracked file, delete it, or rewrite Git history without explicit approval. If a likely secret file is already tracked, stop and report its path without reading its value.
- Update `.gitignore` in the same scoped change that introduces the artifact class. Verify representative ignored and tracked paths with `git check-ignore -v`, `git status --short --ignored`, and `git ls-files` before completion.

## Keep Changes Simple

- Make the smallest change that satisfies the request.
- Do not add speculative abstractions or unrelated cleanup.
- Write short, direct documentation, comments, commit messages, and reports.

## Core Development Principles

For work consuming a Product Definition package, apply `skills/delivery-harness/references/pre-delivery-self-review.md` before execution. A backend-only binding check is not permission to defer required UI/self-review for a UI-bearing initial delivery. Keep scoped enhancement/maintenance routes and the reference's historical-approval catch-up rules.

- Follow `delivery-harness/references/bounded-enhancement.md`: reuse the accepted scope and valid action grants for repairs, document synchronization, module replacement and retesting. Do not repeat approvals for unchanged decisions. Never infer external, destructive, publication or installation authority.
- A module that fails accepted requirements may be replaced inside its write scope; preserve required interfaces, unaffected requirements, data and recoverable history. Bound repair attempts and keep unresolved gaps for the next round; ending a round is not a PASS.
- Reason from the problem's actual constraints, not from habit, inherited patterns, or how another project solved it.
- At 500 lines, review whether a module has more than one responsibility. Split when it improves ownership and verification; otherwise record why it stays together. This is a checkpoint, not a hard limit. The consumer template's hard cap does not apply to this skill-source repository.
- Don't add hacks, shims, or dual-path logic unless a frozen contract requires compatibility. Don't break an existing interface as unrelated cleanup; when an authorized change removes one, update its consumers and tests in the same change. Remove code only when verification proves it is dead.
- For multi-step, high-risk, or ambiguous work, state a brief approach, acceptance criteria, and test plan before editing. Small bounded work may proceed directly.
- Every change must be verifiable. For bug fixes, add or update a regression test when practical; otherwise explain the verification used.

## Keep Product Contracts Current

- English `PRD.md` and `architecture.md` remain implementation authority. When drafting or updating them, maintain complete Chinese `PRD.zh-TW.md` and `architecture.zh-TW.md` review copies under the Product Definition bilingual-review contract; reconcile owner feedback into English first. Chinese copies never replace canonical inputs or grant separate approval. At task entry and change checkpoints, when an existing English PRD or architecture has no Chinese copy, create a complete same-directory `<source-stem>.zh-TW.md` translation under existing write authority, even without a full Harness flow. Preserve English bytes and approvals; validate each available pair and record the backfill in the matching Epic. Read-only tasks report the missing copy; do not overwrite existing translations or automatically rewrite archives.

- When `docs/product/PRD.md` exists, every product change updates the affected PRD requirements, acceptance criteria, and trace IDs in the same change, including small post-delivery fixes that do not use Product Delivery Harness PLAN/RUN.
- Before implementation, classify the change's UI impact as `none`, `structure`, `style`, or `both`. Adding a page, route, visible region, state, or responsive behavior is at least `structure`.
- First classify the work as initial design, enhancement, routine maintenance or explicit full redesign under `skills/ui-design-builder/references/review-workflow.md`. Routine maintenance with UI impact `none` or `style` updates the actual product, effective PRD and accepted change record while retaining historical Wireframe/HiFi/token artifacts. A structural impact follows affected design gates. New product or stack decisions return to `product-definition-builder`; initial design and enhancements use `ui-design-builder`, required `frontend-design`, PRD-to-HiFi completeness checks, independent HiFi review and consolidated Visual Approval. Compile a design-system pair only when the Need Gate requires it. Preserve unrelated pages and old approval semantics.
- Preserve unaffected requirements, IDs, pages, wireframes, and design decisions. A direct task may stay small, but it is not complete while implementation and the canonical product documents disagree.

## Monetization And Partner Channels

When a product has pricing, paid access, purchase-gated features or outside sellers, read `skills/delivery-harness/references/project-operating-rules.md#monetization-and-partner-channels` before product, stack or UI changes. Keep those gates in the PRD and separate billing, entitlements and partner responsibilities.

## Mission Task Split

- When decomposing a PRD into full-delivery missions, split each mission into more, finer tasks: one task per small, independently verifiable step, so each step is done and checked carefully.
- Each task keeps its own atomic commit. Finer tasks stay sequential checkpoints inside their mission. A section may contain several independent frontend, backend or integration missions after shared interfaces are frozen; each writer uses an isolated checkout and a nonconflicting scope.

## Git Flow

- Before every authorized commit, read `skills/delivery-harness/references/commit-convention.md`. Direct tasks use `<type>(<scope>): <imperative summary>`; managed task and mission trailers apply only inside managed runs.
- This repository permanently protects both `development` and `main`. Never delete either local or remote branch, including through wildcard cleanup. Author only on a separate work branch. Development holds reviewed integration candidates; main holds formal releases. Protected-branch landing follows exact-SHA promotion under `skills/delivery-harness/references/branch-promotion-contract.md`, with separate authorization for each target. Historical pinned RUNs retain their execution semantics, never permission to delete either protected branch.
- Before any action represented in the RUN authorization ledger, verify its exact authorization. When a RUN ledger exists, the matching action must be true for the exact target; direct work without RUN still requires an explicit user instruction for the covered mutation.
- With matching `create_local_branches` authorization, create the exact non-default work branch named by governance or the user. Ordinary initial/enhancement work starts from observed remote `development`; a hotfix starts from observed remote `main`. Freeze the original base and retain correction-continuation ancestry. If development does not yet exist, record the bootstrap gap and separately authorize its creation/protection; never fabricate its observation. The owner-approved modernization branch starts from the observed 0.58.0 main baseline as the one-time migration source. If the delivery kind or branch name is unresolved, ask; never add a fixed prefix.
- With matching `create_local_commits` authorization, commit only the verified task scope. Commit atomically: one commit per minimal logical change (matching the minimal task split), never bundling unrelated changes.
- Worker branches and worktrees stay local. With matching `integrate_locally` authorization, the parent integrates verified worker commits into that one run branch.
- Harness 0.38+ RUNs close `local_only` at candidate C. Their `push` authorization remains false, `pushed_head_sha` remains null, and PLAN contains no push lifecycle node. Explicitly pinned pre-0.38 RUNs retain their historical run-branch push path only for recovery.
- After RUN close, archive on the same work branch with exact main evidence and an immutable checkout-external anchor, create archive-only direct child A, and verify archived PLAN/RUN, receipt, anchor, relocation and required candidate checks. The frozen PLAN also preserves the original development/hotfix base. Publishing A to its work branch retains the separate trusted-host request/attempt/receipt; it grants no protected-branch landing. Never force-push.
- Land a reviewed candidate into development under exact target/SHA authorization, read back its SHA S, and freeze S for the release. Later development commits do not widen S. Complete release gates before separately authorized main promotion. A provider-created merge SHA needs tree/ancestry reconciliation and fresh exact-SHA verification. Preserve atomic task history; do not squash unrelated task commits. A hotfix released from main must integrate forward into development. Candidate preview, development deployment and production deployment each retain their own exact build/configuration evidence.
- Branch deletion and worktree removal are separate actions. Do not infer approval for them from implementation or from a successful push.

## Update Local Skills

- After a verified formal release, compare its seven-skill bundle digest with the observed installed digest. When different, complete one local update at a quiescent boundary in the release handoff; a feature or development push does not replace the installed release. An explicitly requested development installation is a separate channel and never becomes the official release by implication. Quiesce only relevant active skill-using sessions, then run `install.sh` or `install.ps1` against `~/.agents/skills/`. It installs `delivery-harness`, `product-definition-builder`, `ui-design-builder`, `design-system-compiler`, `code-security-review`, `product-activation`, and `seo-growth-review`; retires `full-harness`, `prd-builder`, and `product-design-builder`; and writes prior copies under `~/.agents/skill-backups/product-delivery-harness/`. Never replace the installer with manual move/copy commands, or overwrite/delete backups. A failed install rolls itself back. If post-install verification fails, rerun the installer from the previous release tag so it backs up the bad copy first. Restart the relevant host only after successful verification and when needed to load changed skills. If installation cannot finish, report it pending; do not claim the release handoff fully complete.
- Per-runtime copies (Codex plugin, Claude plugin, Pi extension) stay retired. Do not install, update, or reinstall them.

## Required Verification

Edit the canonical skill sources in `skills/`. For each atomic task, run focused checks for its changed behavior and negative cases; unknown impact requires the full applicable suite. Source maintenance does not create a consumer Product Definition, UI approval, Activation pass or managed archive merely to edit a skill. Before a formal release, run the complete required matrix below on the fixed candidate from the repository root. Preserve all suites; this separates the development loop from release verification.

For required UI browser checks, prepare dependencies with `npm ci` and `npx playwright install chromium` when missing or changed, then set `PDH_REQUIRE_BROWSER_TESTS=1` and `PLAYWRIGHT_MODULE` to this checkout's `node_modules/playwright`. Reuse only an observed installation matching the current lockfile and Playwright browser revision; do not reinstall it for every task. Linux CI installs Chromium with `--with-deps`. Missing prerequisites must fail required browser verification. Python test dependencies follow the current requirements file.

```text
python -m pip install -r skills/delivery-harness/requirements-test.txt
python skills/delivery-harness/scripts/check_skill_spec.py
python -m pyflakes skills/delivery-harness/scripts skills/product-definition-builder/scripts skills/ui-design-builder/scripts skills/design-system-compiler/scripts skills/product-activation/scripts skills/seo-growth-review/scripts
python skills/delivery-harness/scripts/docs_weight.py
python -m unittest discover -s skills/delivery-harness/scripts/tests -v
# POSIX shells
HARNESS_GOLDEN_PATH=1 python -m unittest discover -s skills/delivery-harness/scripts/tests -p "test_golden_path.py" -v
# PowerShell
$env:HARNESS_GOLDEN_PATH='1'; python -m unittest discover -s skills/delivery-harness/scripts/tests -p "test_golden_path.py" -v; Remove-Item Env:HARNESS_GOLDEN_PATH
python -m unittest discover -s skills/product-definition-builder/scripts/tests -v
python -m unittest discover -s skills/ui-design-builder/scripts/tests -v
python -m unittest discover -s skills/design-system-compiler/scripts/tests -v
python -m unittest discover -s skills/product-activation/scripts/tests -v
python -m unittest discover -s skills/seo-growth-review/scripts/tests -v
git diff --check
```

CI retains the same required coverage with exact-candidate jobs and a required aggregate. A successful deterministic suite may be cited from that same exact SHA and unchanged configuration, dependencies and toolchain; retain its origin, do not relabel it as a fresh execution. New SHA or relevant input changes require new evidence. Security freshness, browser/live state and migration checks retain their own contracts. Never cache PASS or waive a missing platform result.

Every flow that promotes to `main` bumps the release version in the same change: `package.json`, `skills/delivery-harness/VERSION`, the README badges and version-history entries in all four languages, and the RUNBOOK `required_harness_version` default. `test_skill_contract.py` reads `VERSION` and fails when any of these surfaces differ from it. A breaking skill-bundle change bumps the minor version. After the release promotion reaches `main`, tag that commit with the matching `v<version>` tag — the READMEs' Releasing section is the full checklist.

Any change that adds or alters a skill, rule, or documented flow also updates the READMEs' descriptive sections in the same change, in all four languages — the README is documentation-of-record, not a release-time artifact.

## Managed Product Delivery Harness Runs

Before creating or resuming a managed PLAN/RUN in this source repository, read `skills/delivery-harness/references/project-operating-rules.md#managed-product-delivery-harness-runs` and the canonical Harness SKILL.md. These rules grant no actions. Consumer stage-slot bindings must be resolved and checked for the applicable stage before such work begins; this source-maintenance task has no consumer Product Definition or managed PLAN/RUN and does not invent a binding table or pins.

## Review Guidelines

Treat these as blocking findings:

- Any path that bypasses explicit action authorization for one of the 12 ledger keys: `invoke_external_runtime`, `spawn_subagents`, `create_user_owned_tasks`, `create_local_worktrees`, `create_app_managed_worktrees`, `create_local_branches`, `create_local_commits`, `integrate_locally`, `push`, `archive_worker_tasks`, `remove_worktrees`, or `delete_branches`.
- Any Harness 0.38+ RUN with `integration_push`, non-null `pushed_head_sha`, enabled push grant, or a push lifecycle node; any legacy RUN push that reaches `main` or `development`; or any run whose integration branch resolves to either name.
- Any archive-candidate publication that lacks the receipt-bound immutable external anchor and separately authorized external request/attempt/receipt, does not prove exact C-to-A relocation, uses force, accepts remote drift, or fails to read back exact A. Neither it nor a legacy RUN grant authorizes development or main landing.
- Any protected-branch promotion that bypasses `skills/delivery-harness/references/branch-promotion-contract.md`, lacks separate exact branch/SHA authorization, uses force, moves a stale/diverged ref, loses task ancestry, or lacks required exact-candidate verification. A required PR may create a new main SHA only with verified tree equality and immediate full exact-main-SHA verification before tag or release completion. Any local or remote deletion of development or main is blocking.
- Any gate PASS that is not bound to the exact integration head SHA.
- Any worker that edits parent-owned PLAN/RUN state, escapes its write scope, or independently pushes.
- Any behavior change without focused tests, or any test/workflow command that does not run from the repository root.

Do not report formatting preferences as blockers. Focus on correctness, authorization boundaries, stale-state safety, data preservation, and missing verification.

## Completion

Update the affected skills, references, READMEs and Epic records under existing authority. Preserve untouched rules, IDs, decisions and historical evidence. Report the actual SHA, checks, independent review, release/installation state and unresolved obligations. Required failures, stale evidence or skipped checks prevent a complete delivery claim.
