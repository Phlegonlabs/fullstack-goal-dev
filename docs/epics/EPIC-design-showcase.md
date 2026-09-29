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
