# General Runtime Adapter

Status: implemented and verified locally. Route: direct, one writer and one coherent verification sequence. UI impact: none.

Problem: one nominal adapter still routes by host name, pins model defaults and carries native launch templates and compatibility state.

Baseline: current branch enhancement-readable-wireframes-token-coverage at 6beb5e4; no tracked local changes before this task. The unrelated untracked scripts/ directory is preserved. This repository has no product PRD; canonical skills and the four READMEs own the contract.

Accepted outcome: one capability-based contract for every host. The agent maps observed native tools automatically. Preserve explicit provider eligibility, authorization, fresh context, isolated writes, exact-head review and parent-owned PLAN/RUN. Remove provider-specific defaults, native workflow templates and their compatibility path, as explicitly requested by the owner. Historical user RUN files remain untouched and require replanning before using removed runtime bindings.

Write scope: affected canonical skill code, references, templates and tests; four README descriptive sections; this Epic and DOCUMENTS; the obsolete root CLAUDE adapter pointer. No commit, branch/worktree creation, push, installation, release or cleanup authorization is inferred.

Dependencies: loaded installed-skill identity is unobserved; disk bytes are not a loaded identity. Document-sync first observation requires semantic review. Existing unfinished UI Epics are unrelated and retained.

Gitignore: no new generated artifact class. Pure packet-builder source and tests stay tracked; temporary verification logs stay outside the checkout. Existing Python cache rules apply.

Acceptance: unknown and named hosts use the same routing/options/probe rules; removed driver/state/templates are rejected or absent; missing evidence or authorization cannot dispatch; PRD product-input gates remain covered without a native runner. Run the full repository-required spec, lint, document-weight, unit and golden-path checks from the root. No live multi-host capability or exact-commit security PASS is claimed.

Result: provider-specific routing, model defaults and browser-surface catalogs are removed. The agent selects observed native capabilities through one contract. The three native workflow templates and workflow-run compatibility validator are removed; the PRD input gates and role packets now live in the pure `product_agent_graph.cjs` module. The four READMEs, skill entrypoints, context pointers and references describe the same behavior. Authorization, isolation, exact-SHA evidence and parent ownership remain enforced.

Verification on 2026-09-21, from the repository root:

| Check | Result |
| --- | --- |
| Dependency install, skill spec, pyflakes, document weight | PASS |
| Delivery Harness | 1,149 tests; OK, 16 skipped |
| Product Definition Builder | 217 tests; OK |
| UI Design Builder | 212 tests; OK |
| Design System Compiler | 99 tests; OK, 3 skipped |
| Product Activation | 56 tests; OK |
| SEO Growth Review | 16 tests; OK |
| Opt-in golden path | 1 test; OK |
| Working-tree and staged diff checks | PASS |
| Ignore rules and source inventory | PASS; no new ignore rule needed |

The skipped tests follow their environment or opt-in conditions on this Windows host; the golden path was run separately with its required flag. Capability fixtures cover generic, Codex, Claude, Pi, ZCode and an unknown host identity. This is contract coverage, not a live test of each host.

Final logs are outside the checkout under `%TEMP%/general-runtime-verified-vkaur62d/`, with the final Product Definition rerun under `%TEMP%/general-runtime-product-final-40xkiw8i/` and final static checks under `%TEMP%/general-runtime-final-static-p03z8se8/`. Earlier failures were corrected and the complete Harness suite was rerun successfully with stable source files. Document-sync loaded identity remains unobserved; no baseline or installed identity was fabricated. No commit, push, installation into the user's skills directory, or release was performed.

## 2026-09-23 reliability follow-up

Local main and local tag `v0.52.0` were observed at `baf7e22b05a7f2776ee8b205395204ff21cbdcb5`. This is a current local repository observation, not a rerun of the historical release checks above. The 0.53.0 browser, cross-skill, runtime and translation follow-up is tracked in [EPIC-runtime-and-verification-reliability.md](EPIC-runtime-and-verification-reliability.md); preserve the earlier results and remaining coverage distinctions.

## 2026-09-27 runtime-contract adoption repair

Working-tree record on branch `codex/runtime-contract-adoption` from `f8d52d987c1437ecbb8704fc2a20adbe5e24873a`. The owner authorized filling the Codex lazy-skill identity gap without falsely labeling installed bytes as loaded at session start.

The change adds RUN-v11-only `version_gate.status = "adopted"` with a session-bound `contract_adoption` receipt and immutable replacement history. `loaded_contract_digest` remains null; `installed_contract_digest` and the receipt must match. The guarded `adopt-runtime-contract` transition requires the RUN lock, a quiescent graph, an owner source, reading evidence, the expected digest of the reviewed bytes, a fresh installed-digest match, and an executing Harness `VERSION` at or above the RUN pin. Draft runs may record this metadata observation; complete and cancelled runs cannot. Later selections recompute the live seven-skill digest once when runtime-worker dispatch is possible and defer on drift. Worker directives and review packets carry the receipt so a fresh child independently recomputes, reads, and reports the fixed contract. Existing `current`, mismatch/restart, capability, authorization, source, action and review gates retain their prior meaning.

Owner source and reading evidence are recorded attestations, not cryptographic proof of model ingestion. The digest checks prove only the bytes observed at their measurement points.

Focused verification on 2026-09-27 passed eight tests: RUN-v11 schema separation, RUN-v10 rejection, one live hash per selection, drift deferral, documented deferral codes, guarded adoption/history/fresh-session behavior, expected-digest and active-work no-mutation, and reviewer-packet propagation. Evidence: `%TEMP%/pdh-identity-focus2-6aaeebeb28c84cbc9e6c9964efe3a2cc.log` and `C:/Users/mps19/Documents/Codex/2026-09-27/overbet-harness-takeover/work/identity-v10-rejection-20260927T140007Z.log`. Bounded static checks passed for skill specification, delivery-script pyflakes and docs weight under `identity-skill-spec-20260927T140019Z.log`, `identity-pyflakes-20260927T140019Z.log`, and `identity-docs-weight-20260927T140019Z.log` in the same work directory. Full repository regression, independent review, exact-commit handling, installation and release remain pending; none is claimed here.
