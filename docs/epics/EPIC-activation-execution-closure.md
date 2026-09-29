# EPIC-activation-execution-closure: Require external execution closeout

Status: local_candidate

## Problem And Baseline

The owner's reviewed flow assessment found that Activation runs often stopped at
a filled document. A filled or structurally valid record does not prove that an
authorized, executable external action was attempted, verified, or explicitly
blocked. Baseline: detached source checkout at
`bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`.

Decision source: owner-approved
`C:/Users/mps19/Documents/Codex/2026-09-29/harness-flow-review-01a0ed97/流程與提速評估.md`,
section 6.

## Accepted Scope

Add a read-only terminal closeout check. Every required ACT action must be
verified, or blocked with a concrete reason or the exact owner-deferral form.
Ready, configured, pending, uncertain, and stale required actions fail. An
accepted blocked action or owner deferral keeps the Record blocked; only a
record without one can be handoff-ready. The closeout command joins the
existing source, capability, digest, evidence, and readiness contracts. It does
not call providers, infer authorization, or add an SDK engine.

## Change Log

| Observation / change | Scope | Verification |
| --- | --- | --- |
| 2026-09-29 implementation working-tree | `skills/product-activation/SKILL.md`, activation contract, checker, tests, four README descriptions, this Epic and index. Added `--require-closeout`, owner-deferral syntax, release-identity evidence wording, and manual return read-back wording. No schema change; `/1` records remain readable. | Activation suite: 61 tests passed in 0.781s. Logs: `%TEMP%\\pdh-activation-closeout-focused9-err-20260929.log`; pyflakes, skill spec, docs weight, and diff check passed in `%TEMP%\\pdh-activation-closeout-static2-out-20260929.log`. Entry document sync ran with loaded identity unobserved and reported byte-drift review; `%TEMP%\\pdh-activation-closeout-document-sync-20260929.log`. Cross-skill and exact-candidate checks remain before release. |
