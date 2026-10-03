# EPIC-eval-contract-integration: Freeze eval policy and verify handoff

Status: in_progress; local source candidate only.

## Problem And Accepted Outcome

Future AI projects need an approved rubric, fixed denominator and pass rate,
then a delivered runner, dependency lock and runbook that another executor can
rerun. The owner accepted the [research proposal](../research/eval-contract-integration.md)
on 2026-10-03: "OK，那我們開始去接入提案。"

The parent owns this checkout's writes. This is direct source maintenance,
UI impact `none`, with no consumer PRD or managed PLAN/RUN. Local atomic commits
follow the machine instructions. Publication, promotion and installation need
their separate authority.

## Baseline And Dependencies

- Repository: `product-delivery-harness`, branch `codex/eval-contract-research`.
- Entry HEAD: `1d21e596c2f6a1bccd9828c678c3cbaf233d0a80`, clean.
- Live remote main observed on 2026-10-03:
  `bdae1d82acfd24cdeb2866f5480ff4d4d73b0b61`, source `0.58.0`.
- Installed Harness: `0.59.0`, a separate local development line. It is not
  incorporated here. Loaded-at-session-start skill identity is unobserved.
- Introduction boundary: candidate `0.60.0`. Legacy packages without the new
  marker keep their checks; a present marker always validates.
- Completed research stays in [its Epic](EPIC-eval-contract-research.md).

The independent read-only assignments EVAL-I-Q1/A1 (Product), EVAL-I-Q2/A1
(delivery gate) and EVAL-I-ARCH/A1 (architecture) returned matching entry
branch/SHA without changes. The configured explorers are FlashX/max and the
architect Astra/high; independent provider/session telemetry is unobserved.
No fallback was used. These explorations are not a formal review PASS.

## Sequential Tasks And Acceptance

| Task | Outcome | Checks |
| --- | --- | --- |
| EVAL-I-01 | PRD-owned `eval-policy/1`, explicit Product checker mode, frozen dataset/rubric/judge inputs and TEST joins | Policy/parser/package regressions; legacy omission, malformed markers, artifact hashes and approval binding |
| EVAL-I-02 | Derived `eval-contract/1`, deterministic report arithmetic and delivered runbook | Fixed trial coverage, rates/slices/critical failures, identities, usage/freshness and invalid evidence |
| EVAL-I-03 | Two self-contained reports registered to required quality/handoff scenarios; exact H1/H2 proof | Git/path/byte guards, clean-checkout receipt, no transitive evidence exemption |
| EVAL-I-04 | Mandatory >=0.60 readiness joins and always-run verifier graph | Current strict source route, gate argv/hash/topology and legacy compatibility |
| EVAL-I-05 | Consistent language/version surfaces and fixed-candidate verification | Complete required suite, browser/golden path, independent code/security review, document handoff audit |

No global threshold is selected. Product owners approve their metric, repeats,
slices, critical cases, grader, data rights, freshness and spending. Required
functional TESTs retain all-pass semantics. Missing/error/duplicate trials
cannot disappear from the denominator. Checker commands never execute runners.

## Document And Artifact Impact

Product SKILL/interview/output contract, a new eval policy reference and parser;
Harness checker, templates, acceptance/verification/source references and
readiness joins; all four READMEs and version surfaces. No scheduler or RUN
schema changes. The existing evidence root and parent ownership remain intact.
New source/templates/tests are tracked. Logs and review packets stay outside
the checkout; no new ignore class is introduced.

## Change Log

| Observation | Baseline / observed head | Scope and result | Verification / remaining work |
| --- | --- | --- | --- |
| 2026-10-03 entry | `1d21e59` / same clean head | Research accepted; explicit implementation scope above. No canonical source change yet | Local Git, live main and installed version observed. Implementation and all required checks pending |
| 2026-10-03 EVAL-I-01 | `9a707dd` / working-tree | Product policy parser, explicit checker flag, approved input validation, docs and four-language description | 9 policy tests and 79 existing package tests PASS; Product pyflakes, docs weight and diff checks PASS. Runner/checker/readiness still pending |
| 2026-10-03 EVAL-I-02 | `36c6169` / working-tree | Derived contract, self-contained report shape and pure deterministic recomputation; no execution or schema migration | 8 arithmetic/report tests PASS, including 95/100 boundary, critical/prohibited override, both metrics, duplicates, fake summaries and mutable readbacks. Git/acceptance join and readiness pending |

The large existing Product checker remains the package validation entrypoint;
eval parsing and input validation live in their own module (under 500 lines).
No new responsibility is added to its existing table/approval code.

## Handoff

Pending. No release, tag, push or local skill update has occurred.
