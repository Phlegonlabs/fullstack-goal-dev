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

- 2026-09-29: checked the official Bootstrap Cheatsheet, Storybook Controls and Carbon Motion pages and retained the template-reference links in the workflow. They inform the gallery presentation only; they do not change the approved product stack. Parent isolated PowerShell installer migration/rollback/parity preflight passed one test in 74 seconds at `64e2d8e8`; this installed only into test temporary directories, not active local skills. Full final-candidate verification remains pending.

- 2026-09-29: checkpoint at `3f02386`, clean `codex/harness-flow-modernization`. Integrated all MOD-A/B/C/E work and the five MOD-D commits, preserving independent task history. Parent browser check passed 12 showcase tests with required Chromium; settled screenshots show actual source components. Source CI now retains macOS UI, requires Linux UI and Design System browsers, streams logs and rejects zero discovered coverage. The Windows timing sample is scheduling evidence only: installer failures and publisher timeouts are not PASS. The frontend bridge reached its 3600-second deadline during full testing; its model was `claude-opus-5-5`, no permission denials, and its process tree exited. Scoped frontend and backend follow-ups repair reuse/provenance and UI3/DS4 joins; final complete suite and exact-SHA independent review remain pending. Added the showcase template to the workflow inventory and aligned security review scheduling prose. No remote ref, release, installation or host restart occurred.

- 2026-09-29: prepared unreleased 0.59.0 metadata across package/lockfile, Harness VERSION, RUNBOOK default and four README badges/history. The current-version new-run suite passed all 11 tests and the release-surface consistency check passed. This is a candidate version, not a main promotion or tag. Bootstrap commits through `94d0e8c` were integrated as `1fb06ad`, `747ccd9f`, `f1a7297` and `b009c1a7`; parent context tests passed all 13 cases. Index-only conflicts retained all independent rows and the later factual release observations.

- 2026-09-29: checkpoint at `4b84903` found the current index still described 0.57/0.58 work as unreleased candidates. Local tag peeling and bounded main history show `v0.57.0` at `b591a618` and `v0.58.0` at baseline `bdae1d82`. Updated only current index status and appended later observations to those Epics; preserved their historical verification and authorization records. No new remote release or installation claim is made.

- 2026-09-29: integrated dual-branch parser, PLAN policy validation, strict join repairs and live templates as `bbdf4d55`, `fb441bab`, `7f035cea` and `3ba4b47c`. Parent branch-policy regression passed (6 tests). Clarified acceptance/security timing and permitted same-candidate overlap without weakening frozen expectations, H1/H2 proof, independent review or fresh-state checks. No scheduler bypass or generic cross-SHA result cache was added.

- 2026-09-29: added the full existing-template use map to the workflow and four README pointers, distinguishing active, optional and historical Wireframe artifacts. Template inventory inspection also found live main-only text in GOAL and duplicate CI triggers in PROJECT_CI; MOD-C and MOD-B respectively own their fixes. No historical Wireframe stage is reintroduced.

- 2026-09-29: baseline `7a0fa8f`; updated this repository's Git Flow and review rules to the owner's permanent development/main policy, preserving isolated authoring, explicit protected-ref authorization, task ancestry and historical RUN semantics. Both branches are never deletion targets. This bootstrap work began from v0.58.0 main because remote development was absent at the prior read-back. Remote creation/protection and changing the existing squash-only rule remain unperformed actions, not implied by these document changes.

- 2026-09-29: integrated MOD-E as `e505de93` and its no-op/blocked-reason repair as `ec770dcc`; original worker commits were `83614686` and `04a80417`. Only the document-index insertion conflicted; retained both parent rows and the Activation row. The parent reran all 65 Activation tests at `ec770dcc` (PASS, 0.861 seconds), with a 120-second process deadline; the worktree was clean. This verifies the source checker, not any real external product setup. Root Playwright 1.62.1 matches the lockfile and Chromium 151.0.7922.34 launched/closed successfully. No test server remains active. The 182-step workflow and release-cadence documentation commits are `136da8d5` and `c203ab4d`.

- 2026-09-29: baseline `136da8d`; aligned source-only development versus release validation and formal-release local installation cadence in AGENTS, runtime upgrade guidance and four READMEs. Full release coverage and installer backup/rollback remain required. No installation or external release was performed. The earlier workflow task passed all 182 numbered-step/link checks, skill spec, docs weight and whitespace validation; the first continuity command had an overescaped regex and was corrected before commit.

- 2026-09-29: architecture inspection found that the candidate runtime validation skips cross a mutation boundary. Keep precondition and postcondition checks; defer further skip optimization until a measured identity-bound snapshot change has its own regression evidence. Added the 182-step working-version workflow, explicit multi-writer section ownership and four-language guidance. This documentation does not claim the remaining branch/design/CI changes are already implemented. Baseline `6a4d2d5`; verification: numbered-step continuity, local link targets, skill spec, docs weight and diff checks (record final results at the next checkpoint).

- 2026-09-29: first implementation observation, baseline and observed HEAD `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`; switched to the owner-named branch. No prior working-tree changes. Independent research and an Opus read-only proposal review completed before approval; neither is a verification of the forthcoming implementation. Isolated assignments MOD-A (context), MOD-B (CI), MOD-E (Activation), and ARCH-MODERNIZE-1 (read-only migration architecture) launched. Tests and implementation remain pending.
