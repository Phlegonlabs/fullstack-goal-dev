# Stack And Design Catalog Expansion

Status: in_progress
Workflow: bounded direct source maintenance
UI impact: none

## Problem And Baseline

The optional reference library has 19 domains, but TanStack coverage, complete application-stack comparisons, Cloudflare capability coverage and design-reference discovery need the additions researched in this conversation. This extends [the reference-library Epic](EPIC-reference-flow-integration.md); its released history stays intact.

First observation on 2026-10-02: repository `product-delivery-harness`, branch `codex/harness-flow-modernization`, HEAD `e6e6d1e9f743f48889b3e11dce4f0c3f5d5d27ed`. There are 32 existing dirty paths and no staged files. Those recovery changes are outside this task; their index and README edits must not enter these commits. The source repository has no current consumer PRD, architecture or UI package.

## Accepted Scope

The owner requested: “把以上那些全部都調整，然後加進去”. Add the discussed stack, platform, frontend, design and motion candidates to the existing catalog and the applicable selection/reference guides. Keep the 19-domain layout and existing stage owners. Update the four README descriptions and this record.

The owner's earlier instruction keeps design discovery manual: search the websites, share chosen example links or screenshots, and inspect the original website when available. Do not connect design-reference MCP servers. MotionSites means `https://motionsites.ai/` provisionally; the owner supplied its name, not a URL.

Use one parent writer and three sequential atomic changes: stack comparisons, Cloudflare coverage, then design and motion. Local commits follow the owner's standing atomic-commit instruction. This scope grants no push, promotion, release, local skill installation, blanket dependency installation, product-stack choice or UI approval. No PLAN/RUN is needed.

## Acceptance And Dependencies

| Requirement | Expected outcome | Verification | Dependency |
| --- | --- | --- | --- |
| CAT-1 | TanStack Start/Router, the remaining ecosystem and alternative stack compositions are discoverable, with layer boundaries and adoption checks | Official sources, catalog tests, selection-guide review | Existing Product Definition stack checkpoint |
| CAT-2 | Cloudflare compute, data, AI, workflows, security, tools and newer candidates have clear responsibilities and dated maturity limits | Official-source reconciliation and catalog tests | Account availability remains project-specific |
| CAT-3 | Component foundations, eight visual directions, seven named reference/tool sources and manual intake are covered | Reference/link tests and semantic review | Existing stack and UI gates |
| CAT-4 | Internal links, four-language descriptions and Epic/index agree; unrelated dirty work is preserved | Skill specification, documentation checks, scoped diff and Git audit | CAT-1–CAT-3 |

## Document Impact

| Changed source | Affected artifacts | Required recheck |
| --- | --- | --- |
| Architecture/TanStack research | Catalog architecture/frontend, frontend stack-selection guide, catalog index/sources | Layer separation, official links, optional boundaries |
| Cloudflare research | Cloudflare catalog and source index | Capabilities, maturity, installed-versus-upstream distinction |
| Design/motion research and manual-browsing instruction | Design/components/motion catalog and UI reference guide | Source roles, license/dependency boundaries, existing reference approval |
| All additions | Four READMEs, this Epic and Documents index | Language parity and task-local staged diff |

## Change Log

| Change / request | Reason and scope | Commit / evidence | Verification and remaining work |
| --- | --- | --- | --- |
| 2026-10-02 entry | Accept catalog additions, freeze the source scope and preserve recovery work | Baseline HEAD above; original source hashes and bytes retained in a checkout-external task directory | Earlier read-only sibling research remains evidence. Additional Cloudflare and design probes hit FlashX 429 quota; no automatic provider switch. Owner choice for additional official verification is pending |
| 2026-10-02 CAT-1 | Add two frontend candidates, 18 TanStack library roles, Starter/Builder and eight complete-stack comparisons; add the selection-guide pointer and four-language description | Working-tree delta against the baseline; atomic stack commit follows verification | Reference library 9/9, stack option map 7/7, skill specification and whitespace checks passed. `CATALOG-STACK-05/1` returned read-only file/hash evidence; observed session declared GLM-5.3-FlashX, independent model attestation unavailable. No package checker/schema/runtime change |

## Results And Remaining Work

Implementation and focused verification are pending. Read-only document sync reported `review_required`: first observation, unobserved loaded skill identity and historical legacy-name references in the READMEs. The installed digest is `cdd97b1151213988ca89c1fafd19af28405c2c046ddea96cd28405bb4635ab7a`; it does not establish the session's loaded identity. No snapshot was written and no approval was inferred.
