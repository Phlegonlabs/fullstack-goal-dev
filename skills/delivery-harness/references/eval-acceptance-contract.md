# Eval Acceptance

Use the PRD's approved `eval-policy/1` from
`../../product-definition-builder/references/eval-policy-contract.md`. No fixed
global pass rate. Ordinary products retain deterministic TEST acceptance.

`eval-contract/1` has exactly `schema`, `prd_sha256`, `policy_sha256`, `quality`,
`handoff`, `delivery`. The last three fields equal PRD policy field-for-field;
`policy_sha256` hashes UTF-8 JSON with sorted keys, no extra separators and
`ensure_ascii=False`. It introduces no alternative thresholds. Start from
`EVAL_CONTRACT.template.json`; placeholders intentionally fail.

Two independent full runs at candidate H1 produce self-contained
`eval-report/1` files: `quality` and `handoff`. The latter comes from another
clean checkout following the delivered runbook. Register each file directly
under its required TEST/scenario in `delivery-results/1`; nested trace references
never widen H1/H2's allowed paths. Preserve failed reports separately under
existing authority. Do not silently replace trials or report only best-of-N.

## Report

`EVAL_REPORT.template.json` is a failing scaffold. Exact fields are `schema`,
`purpose`, `run_id`, `candidate_sha`, `contract_sha256`, `prd_sha256`,
`policy_sha256`, `started_at`, `finished_at`, `execution`, `artifacts`,
`provenance`, `trials`, `usage`. IDs differ between runs. Execution equals its
frozen delivery scenario. Artifacts maps every approved input and delivered
runner/grader/lockfile/runbook path to its exact SHA-256 at H1.

Provenance contains exactly `executor`, `job_id`, `checkout_sha`, `git_status`,
`setup`, `full`, `dependency_readbacks`. Both command receipts have `argv`,
`exit_code`, `observation`; record approved commands, actual exit 0 and captured
redacted output. Status is empty at exact H1. Readbacks map every declared
mutable dependency to `{identity, checked_at, observation}` during execution.
Freshness uses the checker clock and approved age; report writers cannot set it.

Each trial has exactly `case_id`, `trial_index` (1-based), `status`, `scores`,
`assertion_results`, `observed_subject`, `observed_grader`, `duration_ms`,
`usage`, `redacted_output`, `grading_observation`, `tool_observations`, `failure`.
Only `completed` counts as valid execution. Scores cover every rubric dimension
with in-range integers. Assertions cover every prohibited check with `pass` or
`fail`; any fail rejects acceptance. Critical trials all meet rubric minima.
Retain output, judge rationale, tool/end-state readbacks and quality failure
observations inline. Tool-free cases state what was permitted and observed.
Never include credentials, raw private records or heldout answers in subject logs.

Usage has `calls`, `cost_microunits`, `currency`, both per trial and per report;
totals recompute and obey policy limits. Runner enforces deadlines and budgets;
checker validates recorded duration, dates and spending. Review verifies truth.

## Arithmetic And Assertions

For `case_all_trials`, a case passes only when every planned trial meets rubric
minima. For `trial_pass_rate`, count each planned trial. Compare integers:
`passing * denominator >= population * numerator`. Failed quality samples stay
in the population. No rounding or excluded failures. Slices use frozen membership
and their own minima; overlaps never inflate the overall denominator. Missing,
duplicate, extra, skipped, timeout, error or malformed trials invalidate the run.

The quality scenario requires `eval-inputs-match`, `eval-complete`, `eval-rate`,
`eval-slices`, `eval-critical`; handoff requires `eval-handoff`. All assertions
and required functional scenarios still PASS. Both full reports independently
recompute quality. A self-written summary, `handoff_ok` flag, or consistent hash
cannot prove execution. Independent review inspects executor receipts, sample
coverage, judge calibration, tool outcomes and actual clean-checkout provenance.
