# Design System Showcase And Full UI Packages

Status: in progress on a detached worker checkout; local atomic commits, not integrated or released.
Design workflow: enhancement
UI impact: none (skill contracts, validators and a derived review artifact; no product UI).

## Accepted Outcome

Batch D of the approved flow review (`流程與提速評估.md`, sections 1 and 8, 2026-09-29). New full UI packages deliver a complete Markdown/JSON/HTML design system. The HTML shows every approved token, range and registered component with its variants, states, interactions, responsive behavior and motion, derived from the approved HiFi source rather than guessed from names. Three rendered directions come from one self-checking author in the existing `docs/design/directions/<round>/` folder; the full HiFi covers approved and intermediate widths.

Versioning: `ui-design/3` pairs with `design-system/4`. `ui-design/2` → `design-system/3` and all older contracts keep their original behavior and approvals. Harness 0.59+ new full-UI RUNs require the new pair plus one frozen derived HTML source; pre-0.59 pins cannot consume `ui-design/3`.

## Baseline And Authority

- Observed 2026-09-29: detached worker checkout at `bdae1d82` (0.58.0), clean. Parent-owned integration; this worker is the sole writer of this checkout.
- Authority: implementation inside the assigned skill/test/doc scope and local atomic commits. No push, install, branch, deletion, release or version bump. Parent owns integration, version surfaces and files outside the scope.

## Requirements And Checks

| ID | Acceptance |
| --- | --- |
| DS-1 | `ui-design/3` requires Need Gate `required` with a closed `Package action` (compile, update or reuse); `ui-design/2` `not_required` approvals stay valid. |
| DS-2 | Three rendered studies by one self-checking author; intermediate-width HiFi evidence. |
| DS-3 | `design-system/4` registry maps every primitive variant, component state, motion variant and responsive target to approved HiFi source or an explicit reason; stale, missing or unresolved specimens fail. |
| DS-4 | `design-system-preview.html` for `design-system/4` is a sandboxed, keyboard-usable gallery with motion replay/stop/reduced motion; legacy preview bytes are unchanged. |
| DS-5 | Harness 0.59+ joins require the new pair and frozen HTML; older pins keep their meaning. |

## Change Log

- 2026-09-29 working-tree, commit A: added `ui-design/3` recognition and policy (`ui_design_v3.py`), `--ui-contract ui-design/3`, `design-system/4` expectation for `/3`, and publication `reuse` byte identity. Focused tests: `test_ui_design_v3` (7) pass; UI suite 318 and Product suite 254 pass after replacing a test example that treated `ui-design/3` as unknown.
- 2026-09-29 working-tree, commit B: added `design-system/4` with a closed `ds-showcase/1` source map (`design_system_showcase.py`), coverage/resolution checks in the pair checker, and the specimen-book renderer (`design_system_gallery.py`, `design_system_gallery_assets.py`) behind the existing `render_design_system_preview.py` path. `design-system/3` and older previews keep their exact bytes. Plates are `srcdoc` frames with `sandbox="allow-scripts"`; the page CSP pins every script by hash and allows no network or frame navigation. A synthetic fixture (`tests/showcase_fixture.py`, committed demo under `tests/fixtures/showcase-demo/`) is labeled as not an approved product. Verification: compiler suite 132 OK (4 platform skips) including a real Chromium run of the demo (no console errors, requests or popups; size, width, state, menu, contained navigation, motion replay, reduced motion, keyboard and no page overflow at 1280/390 px); UI suite 318 OK. Author visual self-review from screenshots found and fixed non-shrinking plates, stretched stages, broken hash wrapping and sprawling fact tables. Module checkpoint: static chrome moved to its own module; the pair checker stays one integration entrypoint for its existing API.
- 2026-09-29 `8db5d76b` fix: a specimen inside a target-specific state view renders at that view's target, as the reviewer runtime does (regression test added; committed demo bytes unchanged).
- 2026-09-29 working-tree, commit C: Harness join (UI portions of `harness_contract_join.py` only). Pinned 0.59+ RUNs require `ui-design/3` for new full UI; a frozen maintenance or `Design workflow: enhancement` task record keeps a retained `ui-design/2` package. Pins 0.56–0.58 reject `ui-design/3`. `ui-design/3` requires `design-system/4` and exactly one frozen `docs/design/design-system-preview.html` (kind `design system preview`) equal to a fresh render of the frozen pair; headless PLANs cannot freeze it. New `test_contract_source_binding.py` (6) passes with the strict-authority (22), wireframe-free join (5) and Harness skill-contract (60) suites.
- Out-of-scope blocker for a clean end-to-end 0.59 join: `skills/delivery-harness/scripts/harness_design_contract.py` lines 85 and 341 accept only `{"design-system/2", "design-system/3"}`, so `validate_ui_surface_design_registry` sends a `design-system/4` registry down the schema-1 path (`design-system.json schema must be 'design-system/1'`). This is the only remaining finding for the complete fixture; the test pins it as the sole allowed gap. Parent fix: add `"design-system/4"` to both sets.
- 2026-09-29 commit D: four README descriptive sections (feature summary, skill table, design-system paragraph, cross-skill modes and zero-to-one steps) describe `ui-design/3`, `design-system/4`, the specimen book and the Harness 0.59 join. Version badges and history are unchanged; the parent owns the release bump. The example UI prompt still names `ui-design/2` because `test_readme_structure.py` (outside this scope) requires that literal.
- Other out-of-scope documentation still describing `ui-design/2` as the only new-package contract: `skills/product-definition-builder/SKILL.md` (steps 15 and the direction-round preflight), `skills/delivery-harness/SKILL.md` and its `contract-and-traceability`, `design-input-updates` and `verification-gates` references, the Harness templates, root `AGENTS.md` ("Compile a design-system pair only when the Need Gate requires it") and `test_readme_structure.py`. Commits: `166b2963` (A), `be292c2f` (B), `8db5d76b` (fix), `9067ab2e` (C).
