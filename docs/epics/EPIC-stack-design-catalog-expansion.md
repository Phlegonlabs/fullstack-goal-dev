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

Use one parent writer and three sequential atomic changes: stack comparisons, design and motion, then Cloudflare coverage. Local commits follow the owner's standing atomic-commit instruction. This scope grants no push, promotion, release, local skill installation, blanket dependency installation, product-stack choice or UI approval. No PLAN/RUN is needed.

The design change proceeds before Cloudflare while the extra official-verification owner choice remains pending; the outcomes have no product dependency on each other. The earlier `UI-LOCAL-04` and official design-foundation sibling reports are retained on the same entry baseline, alongside the parent's verified source links. The failed additional design probe is not relabeled successful.

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
| 2026-10-02 stack checkpoint | Record the first task commit and proceed to the independent design scope | `156d8496ba584d409b0915917fe819695561a4b0`; 32 original dirty entries remain and the index is empty after commit | Stack task passed its focused checks. New design guide/catalog entries are working-tree evidence until their focused check and atomic commit |
| 2026-10-02 CAT-3 | Add four framework-specific foundations, eight visual directions, five discovery sites, React Bits/Anime.js and manual original-site intake; retain reference-principle confirmation | Working-tree design delta from `156d8496ba584d409b0915917fe819695561a4b0`; no UI artifact or canonical SKILL edit | Reference library 9/9, skill specification, docs-weight and scoped whitespace checks passed. No new dependency, connector, schema or product design gate. Additional FlashX design probe failed with 429; earlier same-baseline read-only reports and inspected publisher links are retained |
| 2026-10-02 design checkpoint | Record the second atomic outcome; preserve the same unrelated recovery work | `7db8255a65549c7b952e90bf6a5cc817dc14fea9`; 32 original dirty entries remain and the index is empty | Design/source guide checks passed. Cloudflare additions follow the prior official-coverage report plus parent source reconciliation, not a provider fallback |
| 2026-10-02 CAT-2 source reconciliation | Add the discussed platform capabilities, dated maturity, framework/CLI/skill choices and four-language description | Working-tree delta after `7db8255a65549c7b952e90bf6a5cc817dc14fea9`; official source links are in the catalog | Parent verified Basin GA, K2 beta, Artifacts open beta, McpAgent deprecation and current vinext compatibility wording. The additional FlashX refresh failed with 429 and remains unsuccessful; prior same-baseline official research is retained. Optional Astra recheck awaits owner choice; no provider switch |
| 2026-10-02 CAT-2 verification | Check catalog routes, boundaries and the observed local skill inventory | Reference-library 9/9, skill specification and scoped whitespace checks passed from the repository root; Cloudflare phase logs retained outside the checkout | The official 16-skill list has 14 matching SKILL.md files in each local `.agents/skills` and `.codex/skills` root; `basin` and `k2` are absent. Presence does not establish loaded identity or upstream byte equality. No installation was performed; independent source review follows the atomic commit |

## Results And Remaining Work

Implementation and focused verification are pending. Read-only document sync reported `review_required`: first observation, unobserved loaded skill identity and historical legacy-name references in the READMEs. The installed digest is `cdd97b1151213988ca89c1fafd19af28405c2c046ddea96cd28405bb4635ab7a`; it does not establish the session's loaded identity. No snapshot was written and no approval was inferred.
