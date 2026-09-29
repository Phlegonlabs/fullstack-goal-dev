# EPIC-branch-policy: dual-branch managed release policy

Status: in_progress

## Problem And Baseline

The 0.58 flow required every initial delivery and enhancement to start from remote `main` and refused `development` everywhere. The approved workflow needs ordinary releases to build from a frozen `development` base and hotfixes from `main`, while keeping both protected branches permanent and preserving local-only RUNs.

Baseline: repository checkout at detached `bdae1d82`, Harness 0.58.0, with no branch-policy field or dual-branch architecture marker.

## Accepted Scope

The approved MOD-C task authorizes source branch-policy implementation, affected Product Definition release contracts, current references/templates, four README descriptive sections, and this Epic. It authorizes local atomic commits and parent integration; pushes, installation, deletion, protected-branch mutation, frontend UI portions, root AGENTS, version bump, and final release suite are out of scope.

The accepted interface is:

- `PLAN.branch_policy` contains exactly protocol `dual-branch/1`, kind `ordinary|hotfix`, canonical `refs/remotes/<remote>/development` or `/main`, and the frozen full base SHA.
- 0.59+ current joins require the policy, the active architecture marker, and local base ancestry. Pre-0.59 pins keep old semantics; malformed pins grant nothing.
- Wave re-anchoring advances `integration` state only. The PLAN base stays frozen.
- Exact-A corrections retain their receipt-bound continuation exception but still carry policy/marker and strong archive provenance.
- Archive receipt/anchor/publication formats, `expected_main`, and `main_ref` remain unchanged.
- `main`, ordinary `development`, and the observed default branch are refused for cleanup, local and remote spellings included.

## Acceptance And Dependencies

| Requirement / TEST ID | Expected outcome | Verification / environment | Dependency |
| --- | --- | --- | --- |
| HARNESS-BRANCH-001 | Valid and malformed policy shapes, base refs, and old/malformed pins are distinguished | `test_branch_policy.py` | none |
| HARNESS-BRANCH-002 | Current joins use the canonical active parser and reject ambiguous/unknown markers | `test_validate_harness_plan.py`, `test_product_package_checker.py` | none |
| HARNESS-BRANCH-003 | Current RUN/archive validation fails without the policy even before a repo-root authority join | `test_harness_manifest.py` and archive/publisher validators | parent 0.59 version bump |
| HARNESS-BRANCH-004 | Local and remote protected targets cannot pass delete authorization | `test_lifecycle_cleanup_targets.py` | none |
| HARNESS-BRANCH-005 | New RUN/template and current docs describe the same flow | `test_new_run.py`, `test_skill_contract.py` | parent integration |

## Document Impact

| Changed source / requirement | Affected live artifact | Required recheck |
| --- | --- | --- |
| Dual-branch release policy | Harness PLAN/RUN contracts and templates | focused/final Harness suites |
| Architecture marker and protocol | Product Definition output, interview, agent graph, playbook | Product parser and contract tests |
| Protected landing/promotion flow | Promotion, deployment, execution-state, worktree, operating rules, READMEs | final docs/contract suite |

## Change Log

| Change / request | Reason and affected scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| Add dual-branch architecture parser | `release_targets.py`, marker protocol, and focused regression | `439ba7704980890a0922a4f14977f761ec08d45e` | 80 product-package tests passed |
| Add PLAN policy and 0.59 join | New helper, exact shape, frozen-base ancestry, strict marker join, and manifest validation | `1970e2351af9bf7bc65646bd7e122312f52a34fc` | 4 policy and 117 manifest tests passed |
| Harden joins, markers, types, corrections, and cleanup | Private parser registration, exact marker counts, old-pin mismatch, correction provenance, `validate_run` policy check, remote protected cleanup targets | `56d035f2323b1ec3ed0deae177f688b6692b87b1` | 6 policy, 32 strict PLAN, 11 new-run, 117 manifest, 80 product tests passed |
| Align live templates and contract tests | PLAN, Goal, Mission Runbook, Project Agents, Deployment, and contract assertions | `d96a84940541e9a92e074addcab6c5ae76209058` | 11 new-run, 4 project-template, 60 Harness contract tests passed |
| Update canonical live flow docs and READMEs | Branch-promotion, deployment, execution-state, worktree, operating rules, Product Definition sources, agent graph, four current README bullets | `working-tree` after `d96a8494` | 97 Product Definition contract tests passed; Harness contract and cleanup tests passed in working tree; parent integration and 0.59 final suite remain |

## Results And Remaining Work

Four local commits are ready for sequential integration: `439ba770`, `1970e235`, `56d035f2`, and `d96a8494`. The working tree adds canonical docs, README bullets, and this record.

Remaining: parent integration, frontend overlap reconciliation, independent exact-head review, 0.59 version bump, full required suite, release documentation/version-history ownership, and any final security review. No push, install, branch deletion, worktree removal, or protected-branch mutation was performed.
