# EPIC-architecture-loop-remote-execution: Integrate architecture and remote execution methods

Status: accepted (direction recorded; source implementation and Mac Mini pilot pending)

## Problem And Baseline

The owner wants pstack's architecture methods in the existing Harness and its
loop methods available for automation. Future workers should run error-report
checks and technical feature acceptance on a Mac Mini, other computers or servers.

- Observation: 2026-10-04 02:39 UTC-7.
- Repository: `product-delivery-harness`.
- Branch: `codex/harness-flow-modernization`.
- Baseline: `1782fa000b107396fd36787c7df7fad8a2141c82`, clean at entry.
- Source and observed installed Harness: `0.60.0`; loaded identity unobserved.
- No consumer PRD, product architecture or managed PLAN/RUN applies to this round.
- Current runtime contracts do not support arbitrary cross-machine dispatch.

## Accepted Scope

Decision source: the owner's acceptance, "我覺得可以。", and subsequent pilot
choice, "mac mini", and connection method, "tailscale", on 2026-10-04. These
accept the direction, first machine type and network; the execution channel
and executable target still need observation.

This first task records the agreed split, proposed integration and acceptance
checks in the linked document and its index. UI impact is `none`. One parent
writer owns this checkout. Effective machine instructions require atomic local
commits; there is no push, branch creation, installation or remote mutation here.

The document is a derived implementation proposal. It does not grant actions,
replace product approvals, add RUN fields or change installed skill behavior.

## Acceptance And Dependencies

| Scope | Expected outcome | Verification | Dependency |
| --- | --- | --- | --- |
| T1: Decision record | Separate product architecture, implementation design, execution, loop and remote responsibilities | Source references, Markdown links, diff and independent document review | Existing source/review evidence |
| Core integration | Caller-first design and scoped review methods in existing packets | Focused initial/enhancement/small-repair and approval-boundary checks | T2 in the linked proposal; source edits pending |
| Loop methods | Finite metrics, budgets, reconciliation and retained rejected experiments | Pause, uncertainty, exhaustion and candidate-change negatives | T3; no schedule created |
| Remote boundary | Versioned host/workspace/transport/result identity | Capability, duplicate, mismatch, disconnect and provenance negatives | T4; current schema remains unchanged |
| Mac Mini pilot | Fixed task with verifiable result/evidence return | Actual transport and platform checks, then technical acceptance | Tailscale peer observed online; execution channel, capabilities and target case pending |

## Document Impact

| Path | Impact | Recheck |
| --- | --- | --- |
| `docs/research/architecture-loop-remote-execution.md` | Accepted direction, future work and explicit gaps | Source links, review boundary and pilot scope |
| `docs/DOCUMENTS.md` | Discoverable proposal and Epic | Paths and pending status |
| Canonical skills and four READMEs | No change in T1 | Update together when an actual skill/rule/flow changes |

## Change Log

| Change / request | Reason and affected scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| 2026-10-04 owner acceptance, Mac Mini and Tailscale choice | Preserve the agreed architecture/loop/remote split; T1 documents only | `working-tree` at baseline `1782fa000b107396fd36787c7df7fad8a2141c82`; linked proposal | Seven local Markdown links and whitespace checks passed. Native Sol/xhigh document review DR-1 attempt 1 found no blockers. Source implementation and remote execution remain pending. |

## Results And Remaining Work

Detailed scope and ordered tasks: [integration proposal](../research/architecture-loop-remote-execution.md).

DR-1 reviewed the proposal at SHA-256
`ab9a2d7d37be11508891f33da011b76d926929e0c0abe3a27b5b16570977705b`,
the index at `8aefbeddb77181acbbbe49165594614d7ef54bae6e1b233dd0a276cd248b88cf`,
and the pre-results-update Epic at
`e7c854684688c7216b12920acd4a3a3c97714a35258fb6ca956cd35c8239d549`.
The proposal and index remain byte-identical; this Epic update records that
review and the actual checks. It is not a new runtime or release verdict.

Document sync returned `review_required` for unobserved loaded identity and
the first-observation baseline. No snapshot or loaded digest was invented.
Observed installed template 0.60.0 matches the source template hash
`0d5064d94c0072ad2d1f06f3b516dab328d425be79454df10b50ce6f44b2470e`;
shared rules are current by meaning with the repository's explicit overrides.

Codex project inventory observed only local projects. The owner selected
Tailscale, whose local status is Running and whose peer inventory shows one
matching Mac Mini online with OS macOS. Device endpoints stay out of tracked
documents. This proves neither remote execution nor platform capability.
Remote capabilities, skill identity, execution channel, target acceptance
scenario and actual execution remain unverified. Do not mark the Epic complete from this
documentation checkpoint or treat a transport smoke as feature acceptance.

No new artifact class requires an ignore rule. The proposal and Epic are tracked
source documents; no credentials, logs, caches or temporary process records are added.
