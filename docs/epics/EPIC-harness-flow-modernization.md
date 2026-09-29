# Harness Flow Modernization

Status: implementation in progress; not released.

## Accepted Outcome

On 2026-09-29 the owner approved the researched workflow changes: merge current shared guidance into existing AGENTS files; retain host-neutral role binding; render three UI directions and the approved design system as Markdown, JSON and HTML; use isolated parallel writers with one atomic commit per task; protect both development and main; close Activation through actual authorized execution and independent read-back; remove repeated CI work without weakening acceptance or security.

The owner selected `codex/harness-flow-modernization`. Initial source baseline is `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61` on main, with a clean worktree and Harness 0.58.0. This is a source-maintenance change, not a consumer product delivery: there is no consumer PRD, binding table or PLAN/RUN to invent. Each isolated checkout has one writer; the parent serially integrates verified commits.

## Scope And Dependencies

1. Context template merge and host-neutral template wording.
2. Exact-candidate CI, nonduplicated triggers and measured native test sharding.
3. Versioned development/main policy, preserving pinned historical run contracts.
4. Approved-source design specimens, complete derived HTML and the new full-UI Need Gate.
5. Activation execution closeout with explicit incomplete outcomes.
6. Runtime and acceptance guidance, bounded optimization only where the same immutable validation snapshot can be reused safely.
7. Four-language documentation, exhaustive workflow, version consistency and final validation/review.

Shared interfaces are frozen before dependent writers begin. Existing templates, IDs, approvals and historical evidence remain in place. Work branches remain isolated from both protected branches. No remote publication, ruleset change, skill installation or host restart has occurred.

## Acceptance And Verification

Each task runs focused positive and negative checks before its own commit. The final fixed candidate requires all source-repository suites, required Chromium checks, golden path, Pyflakes, skill spec, docs weight and diff checks, followed by independent review and any required repairs. Platform-specific CI and remote protection changes remain separate observable results; local tests do not prove them. No performance percentage is claimed without a before/after measurement.

Generated logs, bridge packets and temporary profiling data stay in the task directory outside the repository. Existing ignore entries cover local Python caches and node_modules; required source fixtures, templates and generated design handoff examples remain tracked.

## Change Log

- 2026-09-29: integrated MOD-E as `e505de93` and its no-op/blocked-reason repair as `ec770dcc`; original worker commits were `83614686` and `04a80417`. Only the document-index insertion conflicted; retained both parent rows and the Activation row. The parent reran all 65 Activation tests at `ec770dcc` (PASS, 0.861 seconds), with a 120-second process deadline; the worktree was clean. This verifies the source checker, not any real external product setup. Root Playwright 1.62.1 matches the lockfile and Chromium 151.0.7922.34 launched/closed successfully. No test server remains active. The 182-step workflow and release-cadence documentation commits are `136da8d5` and `c203ab4d`.

- 2026-09-29: baseline `136da8d`; aligned source-only development versus release validation and formal-release local installation cadence in AGENTS, runtime upgrade guidance and four READMEs. Full release coverage and installer backup/rollback remain required. No installation or external release was performed. The earlier workflow task passed all 182 numbered-step/link checks, skill spec, docs weight and whitespace validation; the first continuity command had an overescaped regex and was corrected before commit.

- 2026-09-29: architecture inspection found that the candidate runtime validation skips cross a mutation boundary. Keep precondition and postcondition checks; defer further skip optimization until a measured identity-bound snapshot change has its own regression evidence. Added the 182-step working-version workflow, explicit multi-writer section ownership and four-language guidance. This documentation does not claim the remaining branch/design/CI changes are already implemented. Baseline `6a4d2d5`; verification: numbered-step continuity, local link targets, skill spec, docs weight and diff checks (record final results at the next checkpoint).

- 2026-09-29: first implementation observation, baseline and observed HEAD `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`; switched to the owner-named branch. No prior working-tree changes. Independent research and an Opus read-only proposal review completed before approval; neither is a verification of the forthcoming implementation. Isolated assignments MOD-A (context), MOD-B (CI), MOD-E (Activation), and ARCH-MODERNIZE-1 (read-only migration architecture) launched. Tests and implementation remain pending.
