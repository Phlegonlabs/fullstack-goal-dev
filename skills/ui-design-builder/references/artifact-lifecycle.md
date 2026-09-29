# UI Design Artifact Lifecycle

## Detect Existing UI Design

Before drafting, read the approved Product Definition package and inspect, in order:

- `docs/design/ui-design.md`;
- authorized direction-study captures under `docs/design/directions/<round>/`, referenced by the active comparison table;
- `docs/design/wireframes.html`;
- `docs/design/ui-references/`;
- `docs/design/design-system.md` and `docs/design/design-system.json`; and
- legacy `docs/product/wireframes.html` and `docs/product/design-system.*` when present.

If a staged UI package exists, ask whether to resume, publish, or discard it before starting a competing draft. Never delete or silently replace an existing UI artifact.

Before changing an existing file, identify its mode. The exact top-level value `UI contract: ui-design/3` selects a new full package and `ui-design/2` keeps the earlier wireframe-free package; absence retains legacy validation semantics. Never move or rewrite a historical wireframe merely because it is not part of the new flow.

## Updates And Full Rebuilds

Use `design-freshness.md` after applicable skill updates and before implementation. Record sources, hashes and changed-rule impact in existing evidence. Full rebuild with retained PRD follows `design-translation.md`; inventory old files without using their layout/style as creative authority. Do not overwrite canonical artifacts or inherit approvals simply because a new design was requested.

## Locations

Use `docs/design/.ui-staging/<run-id>/` only for unapproved drafts. Before collecting approvals, prepare an explicitly authorized separate publication checkout at the source HEAD, retaining its Git history and every upstream source. Put approval candidates at their final repository-relative paths inside that checkout. Do not record `.ui-staging` paths in approvals. New canonical publish locations are:

- `docs/design/ui-design.md`;
- referenced direction-study captures under `docs/design/directions/<round>/`;
- `docs/design/ui-references/<run-id>/index.html` when retention is approved; and
- `docs/design/design-system.md` plus `docs/design/design-system.json` when required.

The approved Product Definition remains under `docs/product/` in both checkouts. Preserve its exact bytes and all non-design source files; the publication checkout must retain the same HEAD and Git history so `Selected` stack source evidence can resolve. Do not use a documentation-only mirror.

From the source repository root, run `python "<ui-design-builder-skill-root>/scripts/check_ui_publication.py" --source-root <source-checkout> --repo-root <publication-checkout> --hifi docs/design/ui-references/<run-id>/index.html`. Add `--design-system-required` for a required pair. This read-only gate compares upstream bytes, runs the full approved Product checker, and runs normal final UI validation at the final logical paths. It never bypasses a path/hash check or creates human approval evidence. Run ordinary draft checks while approvals are pending; only the complete approved publication set can pass this gate.

After exact publication authorization, transfer the checked UI set to the same logical paths in the source checkout, preserving its bytes, sibling pages, evidence, and pair. Immediately rerun the same command with `--published` before claiming publication. It requires the published inventory to equal the checked checkout. Any content change, upstream drift, missing sibling, or path change requires reconciliation and renewed affected approvals. The helper does not create worktrees, commit, overwrite, move, or delete files.

## Publish And Archive

Show the exact source, destination, overwrite, and archive paths before publication. Product, direction, Visual, and Design System approvals do not authorize filesystem changes. Obtain exact publication authorization when it is not already present.

When an approved artifact supersedes a current UI artifact, archive the old file or complete pair under `docs/design/archived/<YYYYMMDD-HHMMSS>-<run-id>/` and update every live pointer. Move; never delete. Do not move a legacy `docs/product/` UI artifact merely to normalize its location without exact owner approval. New work may publish alongside a legacy artifact only when `ui-design.md` explicitly names which one is authoritative and the legacy one is marked superseded.

The HiFi entry and every page listed in its `ui-hifi/2` manifest publish and archive together as one closed package. Preserve their sibling filenames, inline every non-HTML asset, and retain the entry's `ui-hifi-copy/1` provenance JSON; there is no sidecar asset folder to track. Rehash each changed child page, then the entry, and renew affected interaction evidence and Visual Approval before publication. An unchanged index with a changed child is stale. Retain the complete package for the compiler and Harness; one copied index is insufficient. The existing exact path authorization applies to every page.

The design-system pair publishes and archives atomically. A new pair is `design-system/3` and has no wireframe binding. Legacy `design-system/1` remains inspection-only; `design-system/2` retains its original validation and approval semantics for legacy UI contracts. A `not_required` decision does not silently remove an existing pair; explicitly retain or retire it with owner approval.

For a required pair, retain `docs/design/design-system-preview.html` in the same authorized publication set. `check_ui_publication.py --design-system-required` checks it against the pair before and after transfer; a missing or edited view fails. Generate it with the compiler's `render_design_system_preview.py`. It is derived review output, not another authority or a product screen. An existing package gains this view through an authorized update without rewriting prior wireframe bytes or backfilling approval.

For a new required pair, the pending marker is a short-lived compiler handoff, not a publishable state. The compiler consumes the exact approved `ui-design/2` or `ui-design/3` and `ui-hifi/2` digests, writes Markdown and JSON together (plus the derived HTML package for `ui-design/3`), and the UI owner records both final hashes before the normal checker runs.
