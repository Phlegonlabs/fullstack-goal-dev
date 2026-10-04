# Standalone README And Release Skills

Status: in_progress
Workflow: bounded direct source maintenance
UI impact: none (skill instructions and documentation; no product UI)

## Problem And Baseline

Projects need better visual README writing and release artifacts matched to their actual runtime. A JavaScript package is only one distribution option. The owner accepted the plan for independent `readme-studio` and `release-packager` sources, then requested implementation on 2026-10-04.

Entry observation: repository `product-delivery-harness`, detached HEAD `1782fa000b107396fd36787c7df7fad8a2141c82`, clean index and working tree. The owner selected `codex/readme-release-skills`, created from that exact HEAD. No consumer PRD, architecture, PLAN/RUN or product design package exists for this scope. Existing consolidation/release history remains outside it.

## Accepted Outcome And Boundaries

- RS-1: Brand-first README guidance, five dated primary-source cases, rendering and visual evidence checks, and three realistic writing scenarios.
- RS-2: Runtime-specific release preparation for Node/Bun, Python, Go/Rust, containers and native apps; verify actual artifacts and reconcile README/release facts.
- RS-3: Frontmatter, UI metadata, local references, four-language README entry points and independent behavioral/source review agree.

Sources live under `standalone-skills/`, outside the seven-skill Harness bundle, installers and digest. Use native build tools rather than a new packaging engine. Preparation does not grant publishing, installation, signing, deployment or lifecycle authority. No CI automation or local skill installation is in scope. Existing target-project authorization remains authoritative.

One parent writer owns this checkout. Read-only siblings independently research README sources (`README-REF-03/1`) and runtime packaging (`README-PKG-04/1`); behavioral validation and exact-candidate review follow. Worker model/provider observations are reported separately from requested role names. Local atomic commits are authorized by the owner's standing instructions. Each skill and its required four-language documentation form one logical commit; later repairs retain separate commits.

## Verification And Document Impact

Validate each skill with the existing skill-creator validator and Harness skill-spec checker. Check UI YAML and all local references. Exercise README decisions for a branded product, CLI and SDK, and release decisions for Node, Python, binary and container projects, including missing payload files, mismatched versions, install failure and absent platform capability. These are skill behavior scenarios, not proof that every native platform build ran here.

Update this Epic, the Documents index and the descriptive sections of all four READMEs. Keep existing release/version surfaces intact. Generated validation files and logs stay in a new checkout-external task directory; bytecode is already ignored. No new repository artifact class needs an ignore rule. Actual future visual README authoring follows the target host's frontend binding and includes before/after captures; this source-only task creates no visual product artifact.

## Change Log

| Observation / change | Evidence | Verification / remaining work |
| --- | --- | --- |
| 2026-10-04 entry and branch | Baseline above; owner explicitly selected `codex/readme-release-skills` | Clean after branch creation. Document-sync reports first observation, unknown loaded skill identity and historical retired-name references. Installed Harness version is `0.60.0`, digest `252229aff6fafa7ab1283ff5e052f800b31ee713b6b64ac0b66b6c852ef915af`; this does not identify startup-loaded bytes. No snapshot saved. |
| 2026-10-04 RS-1 source | Working-tree `readme-studio` entrypoint, UI metadata, case/rendering references and four-language README entry points; source commit follows | Skill-creator validation, standalone and canonical skill-spec checks, UI YAML/local links, whitespace and 60 existing Harness skill-contract tests passed. Logs: `C:/Users/mps19/AppData/Local/Temp/readme-release-20261004-7avuyl_1/readme-static-checks.log` and `readme-contract.log`. Independent `README-BEH-05/1` three-case decision test is pending. |
| 2026-10-04 reference reconciliation | `README-REF-03/1` refreshed five pinned GitHub sources and bounded Chromium article DOM; `README-PKG-04/1` returned runtime-family official sources | Confirmed source techniques, `<picture>` guidance and renderer/publish boundaries. DOM evidence is not screenshot/theme verification. Requested FlashX/max bindings are declared by host policy; independent provider/model attestation is unavailable. Parent owns all concurrent source edits. |
| 2026-10-04 RS-1 checkpoint | `1e3ab6bf6adefa6a53caaad9fb1b70801ba3cd99` — `feat(readme): add standalone brand-first writing skill` | Commit contains only RS-1 sources and required documentation. Clean index/worktree before starting RS-2. Disposable research browser closed through its session; no agent-browser-owned process/listener remained, exact launch PID was not captured. |
| 2026-10-04 RS-1 behavior | `README-BEH-05/1`, exact RS-1 skill bytes at `1e3ab6bf`; three read-only decision scenarios | Brand/product, CLI and SDK directions preserve real capabilities, language and platform facts. Follow-up: make frontend discovery and packed-versus-rendered registry image checks clearer. No product visual authoring or screenshots were produced. |
| 2026-10-04 RS-2 source and behavior | Working-tree `release-packager` entrypoint, UI metadata, runtime/artifact references and four-language entry points; `RELEASE-BEH-06/1` reports exact source hashes | Both skill validators, local links and UI metadata passed. Six read-only scenarios correctly identify omitted TypeScript files, missing Python data, absent/unverified binary targets, local-versus-remote image identity, a broken installed API and an unsigned Android APK. These validate skill decisions, not target builds. |
| 2026-10-04 native artifact checks | Checkout-external fixtures/logs under `C:/Users/mps19/AppData/Local/Temp/readme-release-20261004-7avuyl_1/` | Node tarball offline isolated install/API passed. Python wheel and sdist rebuild/install/resource-reading API passed. Bun Windows executable version/JSON smoke passed. Negative Node archive detects omitted runtime asset and version mismatch; install succeeds but API fails while source API passes. No registry or global install. Docker, Go and Cargo tools are absent here; their routes were scenario-validated only. |
| 2026-10-04 verification script repair | `native-package-checks.log` preserves first Python harness failure; `python-package-checks-r2.log` and `python-package-results-r2.json` retain corrected result | Setuptools backend mutates `sys.argv`; wrapper now freezes its output argument before backend calls and uses fresh output locations. Initial wheel discovery failed, corrected native checks passed. This was a test-wrapper defect, not a skill/source packaging failure. No failed check was relabeled PASS. |
| 2026-10-04 RS-2 checkpoint | `04ca78f10fe6cf66f49fb8e385d8c73aac0d9a3e` — `feat(release): add standalone runtime packaging skill` | Complete source scope and required four-language descriptions committed. Fresh 60-test Harness contract suite passed; clean index/worktree before the RS-1 follow-up. |
| 2026-10-04 RS-1 repair round 1 | Working-tree frontend-binding discovery and registry-image hosting clarification, with native inspection examples and four-language description | Responds to `README-BEH-05/1` ambiguity and the parent's registry-mechanics assessment: a packed image does not imply a hosted registry URL. Source/metadata/link checks and independent follow-up are required before completion. |

## Result And Remaining Work

Implementation, focused checks, independent behavior validation and source review are pending. No release, registry upload, installation, preview service or product approval has occurred.
