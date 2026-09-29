# EPIC-context-template-merge: Safe AGENTS bootstrap merge

Status: in_progress

## Problem And Baseline

At detached baseline `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61` (Harness 0.58.0), `configure_project_context.py` created missing context files but left every existing `AGENTS.md` untouched. A target could therefore remain without current shared guidance after an authorized bootstrap. The approved review in `C:/Users/mps19/Documents/Codex/2026-09-29/harness-flow-review-01a0ed97/流程與提速評估.md` identified the merge gap and host-specific installer wording. The checkout started clean at that baseline.

## Accepted Scope

Implement an explicit, idempotent AGENTS merge for authorized bootstrap only. An absent AGENTS file receives the current template. An existing file keeps its owner policy, paths, bindings and overrides; the tool may append only absent top-level template sections in a reviewable block. Same-heading differences are unresolved semantic divergences, not automatic wins. Keep the no-reparse checks and exclusive creation path; use a bounded atomic replacement for merge. Update the bootstrap/Product Definition instructions, worker UI-author sentence, host-neutral frontend-design acquisition wording, four README descriptions, focused tests, this Epic and its index row. The parent-owned root AGENTS Git Flow and branch policy are out of scope.

## Acceptance And Dependencies

| ID | Expected outcome | Verification |
| --- | --- | --- |
| CTM-01 | A missing AGENTS file uses the current template while CLAUDE uses its distinct template | Existing bootstrap tests |
| CTM-02 | Existing local rules and overrides stay authoritative; only missing shared sections are added | New focused merge tests |
| CTM-03 | Same-heading differences remain explicit and merge is idempotent; check mode does not write | New focused merge tests |
| CTM-04 | UI authoring remains capability-bound to the host frontend author and dependency wording is host-neutral | Harness/Product contract and external dependency tests |
| CTM-05 | English source instructions and four README descriptions agree | Contract tests and descriptive-document review |

## Document Impact

Delivery Harness context/bootstrap guidance, document-sync handoff guidance, Product Definition publish step, worker goal template, dependency manifest/checker, installer messages and all four READMEs carry the same behavior. This Epic and `docs/DOCUMENTS.md` record the source-maintenance outcome. No product PRD exists for this repository work.

## Change Log

| Change / request | Reason and affected scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| 2026-09-29 MOD-A implementation | Owner-approved batch A: add safe context merge and explicit conflict reporting; keep host roles capability-bound and remove Codex-specific frontend-design acquisition wording | Working-tree candidate on baseline `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`; atomic task commit is the change containing this Epic | Focused bootstrap, Harness contract, Product contract and external dependency tests passed before the task commit. Full required suite, independent review, promotion, installation and release remain with the parent. No push, install, branch creation or deletion is authorized here. |

## Verification Before Commit

Focused tests passed: `test_configure_project_context.py` (9), delivery `test_skill_contract.py` (60), Product Definition `test_skill_contract.py` (96), and `test_external_skill_dependencies.py` (9). `check_skill_spec.py`, changed-file pyflakes, `docs_weight.py`, `git diff --check`, CRLF-normalized `bash -n install.sh`, and PowerShell parser validation passed. Scoped document sync is `review_required`, as expected for first baseline review and unobserved session-loaded skill identity; its legacy-name findings are in the four READMEs' release history and remain for parent semantic disposition. The complete required suite, independent review, exact-head release verification and installation are not claimed.
