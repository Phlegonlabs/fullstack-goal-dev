# Eval Runbook

Status: template; fill every placeholder before delivery.

## Scope And Frozen Inputs

- Product/TEST IDs: [quality and clean-checkout handoff obligations].
- Approved PRD, eval contract, dataset, rubric, subject and grader: [paths/hashes].
- Metric, denominator, repeats, slices and critical rule: [approved policy].
- Access/data rights: [synthetic or controlled-data owner and access process].
- Heldout protection: [how expected answers stay outside subject context].

## Setup

- Runtime/tool versions: [exact versions and platform].
- Locked dependencies and install command: [approved setup argv].
- Required environment variable names: [names only; use credential storage].
- Runner/grader/lockfile paths: [delivered paths].
- Mutable dependencies: [expected identities and current readback commands].
- Authorized environment, fixture namespace and owned resource IDs: [scope].

## Full Run And Quick Check

- Full command: [approved full argv; covers every case and repeat].
- Quick command: [diagnostic subset; cannot satisfy acceptance].
- Timeouts/call/cost caps and currency: [approved limits and stop behavior].
- Output: [self-contained redacted report; failed trials remain present].
- No trial replacements: preserve failures; a fresh full run gets a new run ID.

## Independent Clean-Checkout Handoff

Record a second executor/job receipt from a clean checkout at H1. Capture SHA,
empty Git status, dependency setup and full command argv/exit/output, artifact
hashes and mutable readbacks. Run every case/repeat again under the same policy.
Use a distinct run/job ID and `purpose: handoff`. A flag is not execution proof.

## Evidence Commit And Verification

Before H1, set byte-preserving attributes on approved inputs, frozen contracts,
delivered artifacts, register and `evidence/**`; verify `git check-attr text filter`.
Execute both runs at H1. The parent records their directly listed reports and
register, then commits only those evidence paths as H2. Run the eval checker,
delivery acceptance checker, independent review and final gates at clean H2.
Never execute descriptions inside the checker or add nested trace exemptions.

## Failure, Replay And Cleanup

- Replay one failed case for diagnosis: [command; does not replace acceptance].
- Grader/output/side-effect failures: [inspect retained observations and owner].
- Timeout/provider failure: [stop/readback, preserve report, new full run].
- Ambiguous mutation: [inspect idempotency key/state before any retry].
- Fixture cleanup: [delete only exact owned IDs under existing authority/readback].
- Version/config/prompt/rubric/data/runner changes: new candidate and fresh reports;
  policy changes use the product approval flow. Post-H2 managed repairs require
  formal PLAN revision. Preserve old evidence and approval history.
