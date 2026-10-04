# Dual-Branch Promotion Contract

Use this contract after a direct change or managed RUN has produced one fixed, locally verified candidate SHA. For a Harness 0.38+ managed RUN, closeout candidate C is local-only; archive-only child A becomes the release candidate. The archived RUN remains immutable at C. Publishing A to its run branch and promoting A to `main` are separate post-RUN actions with separate action-time authorization.

The repository has three branch roles:

- a non-default run or feature branch holds one candidate and remains the managed RUN integration branch; and
- ordinary flow: `refs/heads/development` is a protected internal release branch and `refs/heads/main` is the protected production branch; and
- hotfix flow: `refs/heads/main` is both the frozen base and protected production branch, with a later separately authorized forward landing on `development`.

Never delete `main` or `development`. A platform environment named `development` still uses the exact candidate branch or immutable candidate SHA during managed execution and remains separate from production resources. The protected `development` release uses only its verified landing SHA after candidate A passes.

Do not edit or commit directly on `main` or `development`. Promote an exact already-committed SHA. Every fetch, branch creation, ref update, merge, push, external test, and branch deletion keeps its ordinary authorization boundary. Cleanup never deletes either protected branch, including an old-RUN wildcard `delete_branches` grant.

## Delivery Kind And Base

Classify the work as `initial_delivery`, `enhancement`, or `needs_owner_decision` for product and release semantics. A current managed PLAN declares `branch_policy` with `kind: ordinary` or `hotfix`, the canonical remote base ref, and the observed remote head's full SHA. Ordinary work freezes remote `development`; a hotfix freezes remote `main`. Start the non-default run branch from that frozen base, record the classification, base SHA, complete run-branch name, and any unresolved earlier candidate. A pinned pre-0.59 RUN keeps the main-only semantics recorded with it. Never advance the frozen PLAN base wave by wave, and never use a stale local protected ref as the base.

Plan-only validation checks an explicit `branch_policy` and active architecture marker together before RUN creation. An absent RUN is not a historical version pin. This structural check grants no execution or promotion; a paired RUN still enforces its version and candidate ancestry.

## Managed RUN Archive Before Promotion

At RUN close, candidate C is complete local work only. On that same resolved run branch, the parent reviews the dry run and applies `scripts/archive_run.py` with `--expected-main <full SHA>` and `--main-ref refs/heads/main` or `refs/remotes/<remote>/main`. `--apply` refuses missing or mismatched bindings, protected or detached branches, and a branch that does not match the RUN integration branch. It moves the coordination set without deleting it; it does not authorize a commit, push, promotion, or cleanup.

For Harness 0.38+, `archive_run.py --apply` also requires absolute external `--anchor-out`. It writes closed `ARCHIVE_RECEIPT.json` in the archive and a matching immutable anchor outside the checkout, binding every pre-move source, C, branch, and observed `main`; failure rolls back. Empty optional directories are deliberately skipped because the receipt inventory is regular-file-only. An interrupted apply leaves a durable `.ARCHIVE_TRANSACTION.json`; its moves are restricted to the closed PLAN/RUN/optional coordination allowlist and receipt-derived destination mapping before recovery opens a source. A transaction-wide DOCUMENTS destination lock and inode/content version token serialize compliant writers, while the platform exchange/backup primitive validates displaced bytes and restores or retains recovery artifacts on mismatch. Run `python "<delivery-harness-skill-root>/scripts/archive_run.py" --repo-root <checkout> --recover <archive>` before retrying, and recovery preserves any path whose identity or content is no longer transaction-owned. Commit only repository bookkeeping as A. Revalidate the archived PLAN/RUN, receipt, anchor, destinations, deterministic `docs/DOCUMENTS.md`, absent live sources, and unchanged outside paths. If separately authorized, `push_archived_candidate.py` uses `--archive-anchor <same path>` and keeps its request, pre-side-effect attempt, receipt, and trusted-host execution evidence outside the checkout as one closed lifecycle (the request, pre-side-effect attempt, and receipt outside the checkout). The request binds the exact canonical non-secret push URL, the machine-installed policy ID/hash/principal, and an OS-managed verifier path/hash; it returns `PENDING_TRUSTED_HOST_PUBLICATION` with a URL-only no-force argv before the receipt is written. It never treats caller-supplied prose or a ticket/ref string as authority and never invokes `git push`. A trusted host must independently reload the immutable request, revalidate authorization and endpoint immediately before the side effect with sanitized config, execute the exact URL, and write detached signed execution evidence. Recovery verifies that evidence and the exact A read-back before closing the receipt. Agents and the local executor must not run the emitted argv without that trusted boundary. The archived RUN grants nothing.

## Candidate Gate

Archive read-back uses a fresh non-repository Git process with system/global config disabled. Private endpoints that need credential helpers remain a trusted-host responsibility.

The archive anchor deterministically names the v3 publication receipt as `<anchor-stem>-publication-receipt.json`; correction lineage treats that receipt and its signed execution evidence as the objective publication state.

The external authorization names the administrator-installed machine policy ID/hash/principal (HKLM `SOFTWARE\ProductDeliveryHarness\ArchivePushAllowedSigners` on Windows or `/etc/product-delivery-harness/archive-push.allowed_signers` on POSIX) and the OS-managed verifier hash. If the policy is absent, install it through host administration; the local agent cannot choose a fake verifier or trust policy.

Candidate gates start only after the candidate SHA (A for a managed RUN; the fixed commit for a direct change) has passed every applicable task, integration, build/typecheck/test, E2E, UI, migration, security, and complete-diff gate. The checkout must be clean and the candidate must descend from the frozen PLAN base. A dirty checkout, uncommitted fix, missing required result, stale review, SHA mismatch, or non-fast-forward ancestry blocks promotion. Candidate-preview evidence binds its own immutable candidate SHA; it never substitutes for protected-branch evidence or advances the PLAN base.

Harness 0.38+ RUNs never use `integration_push`; that RUN state remains legacy read compatibility only. A post-archive branch receipt proves only exact A at the run ref. Archival grants no push, and the receipt grants no `main` update.

When the product needs internal deployed verification before production, deploy or expose an isolated non-production environment from the exact candidate branch or immutable candidate SHA. Use separate URLs, resources, data, secrets, auth, and payment modes. Record the deployed candidate SHA and run the required smoke, migration, integration, responsive, accessibility, and visual checks there. A preview build start, successful upload, green check from another SHA, or owner statement is not a PASS.

A repair creates a new committed candidate and invalidates the prior candidate, security, deployment, and UI evidence. Repeat archival bookkeeping if the repair changes the live coordination set, then repeat the complete candidate gate and any candidate-environment verification on the new exact SHA.

## Post-A Candidate Or Preview Failure

Once A is archived or published, its history and evidence are immutable. A failed candidate gate, preview deployment, smoke check, or other post-A result never amends A, rewrites the run branch, or edits the archived RUN. Record the failure and use the correction-continuation exception: on the same non-default run branch, create a fresh PLAN/RUN from exact A, import the prior verified scope plus the bounded repair, retain the required branch policy and original frozen provenance, and require new execution/action grants. The new PLAN carries exactly one frozen `prior archive candidate` source: its location is A's archived `ARCHIVE_RECEIPT.json`, `source_revision` is exact A, and `content_sha256` matches that blob; retain the external anchor and failed-gate evidence as historical inputs. The existing archive and publication validators—not a PLAN row alone—prove the receipt, anchor, publication state, exact A parentage, and A-to-C2 ancestry. Execute and review the repair until replacement closeout candidate C2 passes; archive C2 on that continuation branch with a new stamp and external anchor as archive-only A2. If A was published, A2 publication accepts only a freshly observed remote pre-state equal to A; if A was not published, the pre-state must remain absent. Revalidate A2, then repeat the trusted-host publication, candidate gates, and exact-SHA promotion path. A2 is a new lineage; it never reuses A's anchor, request, attempt, receipt, or history. This exception changes the continuation base; it does not waive the branch policy, architecture marker, or protected-branch rules.

## Promote To Main

For a 0.59+ dual-branch RUN, archival and later archive-candidate publication prove C descends from the frozen `PLAN.branch_policy.base_sha`. Archive creation still binds the exact observed `main` SHA in the receipt and external anchor. A later unrelated move of `main` does not invalidate run-branch publication; protected-branch promotion performs its own fresh exact-target checks. Pre-0.59 archives keep their expected-main ancestry and publication freshness rules. An unforwarded hotfix at `main` does not rewrite an ordinary candidate's frozen development base or waive no-force landing checks.

Run-branch publication of A, protected-development landing, and `main` promotion use different controls on purpose. Publication goes through the trusted host because its signed evidence and v3 receipt are the durable publication state that archive and correction lineage read later (A2 checks the remote pre-state against it). A protected-branch update writes no archive receipt; it is a plain no-force push under its own action-time authorization naming the protected ref, remote, and exact SHA, with fetch and read-back. Promotion does not require prior run-branch publication. Publish A first only when a candidate environment must build from the remote run branch. A publication request, receipt or trusted-host grant never authorizes either protected branch.

For ordinary flow, land the candidate-gated exact A on protected `development` first. If a required PR server creates landing SHA S, fetch S immediately, require its tree to equal A's tree, and rerun the complete required suite and fresh security review on S; otherwise S is exact A. Freeze S as the full release evidence, then separately authorize promotion of that exact verified SHA to `main`.

A hotfix promotes candidate-gated exact A to `main` and verifies production against A. It then forward-integrates A into protected `development` under a separate action-time authorization. This is a no-force merge, not a demand that `development` equal `main`: preserve every unrelated current `development` commit, prove A is ancestry, resolve conflicts on a reviewed candidate, and read back the new development SHA T. A merge commit changes the tree, so rerun the required development gates and fresh security review on exact T before claiming internal-release readiness. Production remains reviewed at A and `main`; development remains T.

Promotion to `main` is allowed only when all of these are true:

1. In ordinary flow, protected `development` already records the fully verified release SHA S. A hotfix requires candidate A at `main`, with forward integration to development complete or separately scheduled as an explicit unresolved owner action.
2. A fresh fetch proves the remote `main` head still equals its recorded pre-promotion head and the intended release SHA descends from the frozen original base.
3. Every required local, candidate-environment, and protected-development gate passes on the exact release SHA.
4. The `main` update is a fast-forward to that exact SHA. A merge, rebase, squash, conflict repair, generated-file change, or server-created commit changes the candidate and invalidates earlier exact-SHA evidence.
5. Separate action-time authorization names `main`, the remote, and the exact release SHA. Authorization for the run branch, deployment, or `development` does not cover it.
6. Push without force, fetch/read back remote `main`, and require it to equal the authorized candidate SHA.
7. Verify production read-only against exact A and run the surface-specific smoke. Hosted-browser UI uses `parity_capture.py` against the production URL. Browser extensions use extension automation; native and desktop targets use platform UI tests or labeled manual device captures. Every capture binds the typed target, artifact, SHA, authority hashes, and production evidence separately from candidate PASS. Only after production verification may activation readiness, verified measurement handoff, outcome review, and SEO pass their own gates. Earlier `product-activation` preparation may configure deployment prerequisites at a fixed implementation SHA under separate exact external-action authorization; it cannot claim readiness.

If branch protection requires a pull request, merge queue, or server-created commit and cannot preserve the candidate SHA, follow that mechanism only under its own authorization after the candidate gate passes. Fetch the resulting protected-branch SHA immediately, require its tree to equal the verified candidate tree, and treat that server-created SHA as the branch's release candidate. Rerun the complete required suite and fresh security review on that exact SHA before promotion, tagging, publishing a release, or claiming completion. A failure is repaired by a new candidate branch and PR; never force-push or rewrite a protected branch to erase the failed landing.

## Protected Branches

`main` and ordinary-flow `development` are permanent protected branches. Cleanup authorization, archive publication, or promotion never deletes either one. A separate destructive decision still cannot make an old RUN grant cover a protected target; a future repository policy change would require a fresh explicit owner instruction and new exact validation.

## Outcome And Required Evidence

A completed ordinary release leaves the exact verified candidate at protected `development` and then protected `main`. A completed hotfix leaves exact A at `main`; its separately authorized forward integration records a distinct development SHA T containing A plus retained development work. For a managed RUN, the implementation candidate is archive-only commit A. Any candidate-preview evidence names the candidate branch/SHA rather than a protected branch. Report:

- delivery kind, run branch, candidate SHA, and candidate-gate results;
- frozen PLAN base and observed protected-branch heads before and after each landing;
- protected-development landing SHA S or forward-integration SHA T and read-back when applicable;
- candidate-environment deployment SHA and smoke results when applicable;
- `main` authorization source, fast-forward/ancestry proof, push, and read-back;
- production deployment SHA and smoke result when applicable;
- post-production activation, outcome-review, and SEO readiness/evidence results when applicable;
- protected-branch read-back proving both refs remain present.

Unexpected remote movement, failed ancestry, non-fast-forward state, different server-created SHA, failed gate, or a missing protected branch stops the operation. Preserve the evidence and ask for an explicit reconciliation plan; never force-push or silently rewrite history.
