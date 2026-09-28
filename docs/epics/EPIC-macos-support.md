# macOS Support

Status: in progress on `codex/macos-support`; not pushed to GitHub, not released.
Design workflow: maintenance
UI impact: none

## Scope And Accepted Outcome

The owner asked (2026-09-27) to make the skill bundle run on macOS and to test on the Mac mini. The macos CI job added in 0.55.0 is non-blocking because it failed 353 tests. Outcome: every required suite passes on macOS, and the macos job blocks again.

Owner decisions (2026-09-27):

- The macos CI job uses Apple's `/usr/bin/git`; the trusted-Git policy (root-owned, no links) is unchanged.
- The Mac mini uses its existing Homebrew Python 3.14 (`/opt/homebrew/bin/python3.14`) in a venv outside the repo (`~/.cache/pdh-venv`), with `/usr/bin` ahead of Homebrew on PATH.

| Requirement | Acceptance |
| --- | --- |
| MAC-1 | CI macos job uses a root-owned Git and blocks again once suites pass. |
| MAC-2 | Test temp roots do not traverse macOS `/var` → `/private/var`; the no-link path policy is unchanged. |
| MAC-3 | Descriptor-bound executable launch fails closed with its own error on macOS instead of EACCES at exec; any macOS alternative binding needs an owner decision and security review. |
| MAC-4 | Four READMEs state how to run the suites on macOS. |

## Baseline

Observed 2026-09-27: branch `codex/macos-support` cut from `origin/main` `2fa9b343` (v0.55.0). Pushed only to the Mac mini checkout (`macmini:Documents/GitHub/product-delivery-harness`, previously clean at `1c7939d`). Mac mini: macOS 26.6.2 arm64, `/usr/bin/git` 2.54.0 (Apple Git-157), Python 3.14.7.

Mac baseline at `2fa9b343` (default `TMPDIR`): Harness 1321 run, 98 failures, 26 errors, 28 skipped; UI Design 35 failures, 39 errors; Design System Compiler 9 failures; golden path 1 failure; Product Definition, Product Activation, SEO passed.

Same code with `TMPDIR` resolved to `/private/var/...`: UI Design, Design System Compiler and golden path pass; Harness has 4 failures and 18 errors. None of the unresolved-run rejections name a product-created temp dir (`harness-verifier-snapshot-`, `harness-git-isolated-`, `trusted-host-challenge-`, `harness-no-hooks-`, `harness-filtered-objects-`, `harness-trusted-host-`), so the `/var` failures come from test fixtures placing repositories under the symlinked temp root.

Remaining 22: descriptor-bound exec through `/dev/fd/N` returns EACCES on macOS (`verifier_runtime._RuntimeExecutableBinding`, `parity_capture` launcher, `push_archived_candidate` signature verifier); 4 `parity_capture` capture failures likely downstream; 1 cross-device link in `test_push_archived_candidate`.

## Change Log

### 2026-09-27 — branch `codex/macos-support`

- `20a43c01` ci(harness): macos job puts `/usr/bin` on `GITHUB_PATH` before setup-python; test asserts the step and order. Verified locally with `test_install_script.py -k macos` (OK); not yet run in CI.
- `74a048ab` ci(harness): macos job sets `TMPDIR` to its real path through `GITHUB_ENV`; four READMEs give the macOS test setup. Product temp dirs were not involved (see Baseline), so the no-link policy is unchanged.
- `c1dc379f` fix(harness): descriptor-bound exec refuses `/dev/fd` on darwin and raises the existing binding error in `verifier_runtime`, `parity_capture` (executables only) and `push_archived_candidate` (the signature verifier only; bound data files still read through `/dev/fd`). 26 tests that need descriptor exec skip on darwin with a stated reason; three darwin tests assert the fail-closed errors.
- Mac mini at `c1dc379f` (resolved `TMPDIR`, `/usr/bin/git`): Harness 1324 OK (54 skipped), Product Definition 240 OK, UI Design 293 OK (3 skipped), Design System Compiler 116 OK (2 skipped), Product Activation 56 OK, SEO 21 OK, golden path OK, skill spec and pyflakes pass.
- Windows: `test_push_archived_candidate` 35 OK, `test_verifier_runtime` 46 OK. `test_parity_capture` failed once (4 failures, 4 errors, 721 s, details not kept), then passed twice (17 OK, ~22 s); treated as a flaky browser timeout, not a regression.

Until MAC-3 has an owner-approved alternative, macOS cannot run sandboxed container verifiers, browser parity capture, or trusted-host signature verification; each fails closed with its own error.
