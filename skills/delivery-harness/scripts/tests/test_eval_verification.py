import copy
import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_verification as ev
from eval_delivery_fixtures import fixture


class EvalVerificationTests(unittest.TestCase):
    def setUp(self):
        self.policy, _, self.contract, self.approved, self.report, self.now = fixture()

    def test_missing_sibling_parser_returns_clear_import_error(self):
        before = list(sys.path)
        for error in (FileNotFoundError, ImportError, SyntaxError):
            with self.subTest(error=error), patch.dict(sys.modules):
                sys.modules.pop("pdh_eval_policy", None)
                with patch.object(ev.importlib.util, "spec_from_file_location", side_effect=error):
                    with self.assertRaisesRegex(ImportError, "installed sibling eval policy parser unavailable"):
                        ev.product_policy()
                self.assertEqual(before, sys.path)

    def check(self, report=None):
        current = report or self.report
        # Policy modifications in tests represent a separately approved fixture.
        current["policy_sha256"] = ev.ep.policy_digest(self.policy)
        return ev.validate_report(current, self.policy, self.approved, purpose=current["purpose"],
            candidate_sha="a" * 40, contract_sha256=self.report["contract_sha256"],
            prd_sha256=self.report["prd_sha256"], execution=self.report["execution"],
            artifacts=self.report["artifacts"], now=self.now)

    def fail_case(self, case):
        for row in self.report["trials"]:
            if row["case_id"] == case:
                row["scores"]["correctness"] = 0
                row["failure"] = "Synthetic wrong answer retained"

    def test_exact_boundary_and_quality_failures_count(self):
        self.fail_case("case-3")
        self.assertEqual(3, self.check()["passing"])
        self.fail_case("case-2")
        with self.assertRaisesRegex(ev.ep.PolicyError, "aggregate"):
            self.check()

    def test_95_of_100_and_no_rounding(self):
        self.policy, _, self.contract, self.approved, self.report, self.now = fixture(100)
        self.policy["minimum_rate"] = {"numerator": 95, "denominator": 100}
        self.policy["slices"][0]["minimum_rate"] = self.policy["minimum_rate"]
        for i in range(95, 100):
            self.fail_case(f"case-{i}")
        self.assertEqual(95, self.check()["passing"])
        self.fail_case("case-94")
        with self.assertRaises(ev.ep.PolicyError):
            self.check()

    def test_trial_metric_and_overlapping_slices(self):
        self.policy["metric"] = "trial_pass_rate"
        self.report["trials"][-1]["scores"]["correctness"] = 0
        self.report["trials"][-1]["failure"] = "Wrong answer"
        self.assertEqual({"passing": 7, "total": 8}, {k: self.check()[k] for k in ("passing", "total")})
        self.policy["slices"].append({"id": "overlap", "minimum_cases": 1, "minimum_rate": {"numerator": 1, "denominator": 1}})
        self.approved["dataset"][0]["slices"].append("overlap")
        self.assertEqual(2, self.check()["slices"]["overlap"]["total"])
        self.policy["slices"][-1]["minimum_cases"] = 2
        with self.assertRaisesRegex(ev.ep.PolicyError, "slice"):
            self.check()

    def test_critical_and_prohibited_override(self):
        self.fail_case("case-0")
        with self.assertRaisesRegex(ev.ep.PolicyError, "critical"):
            self.check()
        self.setUp()
        self.report["trials"][-1]["assertion_results"]["no-side-effect"] = "fail"
        with self.assertRaisesRegex(ev.ep.PolicyError, "prohibited"):
            self.check()

    def test_incomplete_duplicate_extra_and_execution_failures(self):
        original = copy.deepcopy(self.report)
        variants = []
        for status in ("skipped", "timeout", "grader-error", "unvalidated"):
            report = copy.deepcopy(original)
            report["trials"][0]["status"] = status
            variants.append(report)
        missing = copy.deepcopy(original)
        missing["trials"].pop()
        variants.append(missing)
        duplicate = copy.deepcopy(original)
        duplicate["trials"][-1] = duplicate["trials"][0]
        variants.append(duplicate)
        extra = copy.deepcopy(original)
        extra["trials"][0]["case_id"] = "unplanned"
        variants.append(extra)
        for report in variants:
            with self.subTest(status=report["trials"][0]["status"]), self.assertRaises(ev.ep.PolicyError):
                self.check(report)

    def test_fake_summary_score_identity_time_budget_and_handoff(self):
        for modify in (lambda r: r.update(summary={"pass": True}),
                       lambda r: r["trials"][0]["scores"].update(correctness=True),
                       lambda r: r["trials"][0].update(observed_grader="new-judge"),
                       lambda r: r["trials"][0].update(duration_ms=1001),
                       lambda r: r["usage"].update(calls=0),
                       lambda r: r.update(started_at=(self.now - dt.timedelta(hours=2)).isoformat()),
                       lambda r: r["provenance"].update(git_status=" M runner.py"),
                       lambda r: r["provenance"]["full"].update(argv=["python", "quick.py"]),
                       lambda r: r["provenance"]["setup"].update(exit_code=1)):
            report = copy.deepcopy(self.report)
            modify(report)
            with self.assertRaises(ev.ep.PolicyError):
                self.check(report)
        handoff = copy.deepcopy(self.report)
        handoff.update(purpose="handoff", run_id="handoff-run-1")
        self.assertEqual(4, self.check(handoff)["passing"])

    def test_calls_and_cost_caps_reject_correctly_recomputed_usage(self):
        for field, limit in (("calls", "max_calls"), ("cost_microunits", "max_cost_microunits")):
            with self.subTest(field=field):
                self.setUp()
                for trial in self.report["trials"]:
                    trial["usage"][field] = 2
                total = len(self.report["trials"]) * 2
                self.report["usage"][field] = total
                self.policy["limits"][limit] = total
                self.assertEqual(4, self.check()["passing"])
                self.policy["limits"][limit] = total - 1
                with self.assertRaisesRegex(ev.ep.PolicyError, "budget"):
                    self.check()

    def test_cost_total_must_recompute_with_room_in_budget(self):
        self.policy["limits"]["max_cost_microunits"] = 10
        self.report["trials"][0]["usage"]["cost_microunits"] = 1
        self.report["usage"]["cost_microunits"] = 1
        self.assertEqual(4, self.check()["passing"])
        self.report["usage"]["cost_microunits"] = 0
        with self.assertRaisesRegex(ev.ep.PolicyError, "recompute"):
            self.check()

    def test_trial_and_report_usage_require_approved_currency(self):
        for target in ("trial", "report"):
            with self.subTest(target=target):
                self.setUp()
                self.assertEqual(4, self.check()["passing"])
                usage = self.report["trials"][0]["usage"] if target == "trial" else self.report["usage"]
                usage["currency"] = "EUR"
                with self.assertRaisesRegex(ev.ep.PolicyError, "currency"):
                    self.check()

    def test_run_deadline_is_independent_of_freshness(self):
        self.report["started_at"] = (self.now - dt.timedelta(seconds=120)).isoformat()
        self.policy["limits"]["run_timeout_ms"] = 119000
        self.assertEqual(4, self.check()["passing"])
        self.policy["limits"]["run_timeout_ms"] -= 1
        with self.assertRaisesRegex(ev.ep.PolicyError, "deadline"):
            self.check()

    def test_freshness_is_independent_of_run_duration(self):
        self.report["started_at"] = (self.now - dt.timedelta(seconds=120)).isoformat()
        self.report["finished_at"] = (self.now - dt.timedelta(seconds=111)).isoformat()
        self.policy["freshness"]["max_age_seconds"] = 120
        self.assertEqual(4, self.check()["passing"])
        self.policy["freshness"]["max_age_seconds"] -= 1
        with self.assertRaisesRegex(ev.ep.PolicyError, "stale"):
            self.check()

    def test_future_finish_fails_with_fresh_inputs_and_short_duration(self):
        self.report["finished_at"] = self.now.isoformat()
        self.assertEqual(4, self.check()["passing"])
        self.report["finished_at"] = (self.now + dt.timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ev.ep.PolicyError, "future-dated"):
            self.check()

    def test_readback_must_be_inside_the_run_window(self):
        self.policy["freshness"]["dependencies"] = {"api": "snapshot-v1"}
        readback = {"identity": "snapshot-v1", "checked_at": self.report["started_at"],
                    "observation": "API configuration readback is snapshot-v1"}
        self.report["provenance"]["dependency_readbacks"] = {"api": readback}
        self.assertEqual(4, self.check()["passing"])
        for endpoint, offset in (("started_at", -1), ("finished_at", 1)):
            with self.subTest(endpoint=endpoint):
                readback["checked_at"] = (ev.timestamp(self.report[endpoint]) + dt.timedelta(seconds=offset)).isoformat()
                with self.assertRaisesRegex(ev.ep.PolicyError, "readback stale"):
                    self.check()

    def test_quality_failure_requires_retained_observation(self):
        self.fail_case("case-3")
        self.assertEqual(3, self.check()["passing"])
        self.report["trials"][-1]["failure"] = ""
        with self.assertRaisesRegex(ev.ep.PolicyError, "retained failure"):
            self.check()

    def test_slice_rate_cannot_hide_behind_passing_aggregate(self):
        for metric in ("case_all_trials", "trial_pass_rate"):
            with self.subTest(metric=metric):
                self.setUp()
                self.policy["metric"] = metric
                self.policy["slices"].append({"id": "focused", "minimum_cases": 2,
                    "minimum_rate": {"numerator": 1, "denominator": 1}})
                for case in self.approved["dataset"][1:3]:
                    case["slices"].append("focused")
                self.check()
                self.fail_case("case-1")
                with self.assertRaisesRegex(ev.ep.PolicyError, "slice"):
                    self.check()

    def test_observed_subject_cannot_substitute_another_identity(self):
        self.assertEqual(4, self.check()["passing"])
        self.report["trials"][0]["observed_subject"] = "different-subject"
        with self.assertRaisesRegex(ev.ep.PolicyError, "subject or grader"):
            self.check()

    def test_derived_contract_cannot_weaken_policy(self):
        ev.validate_contract(self.contract, self.policy, self.report["prd_sha256"])
        self.contract["quality"]["test_id"] = "TEST-003"
        with self.assertRaises(ev.ep.PolicyError):
            ev.validate_contract(self.contract, self.policy, self.report["prd_sha256"])

    def test_utc_overflow_returns_a_typed_timestamp_failure(self):
        self.assertEqual(dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc),
                         ev.timestamp("2026-01-01T01:00:00+01:00"))
        for value in ("0001-01-01T00:00:00+01:00", "9999-12-31T23:00:00-02:00"):
            with self.subTest(value=value), self.assertRaisesRegex(ev.ep.PolicyError, "invalid report timestamp"):
                ev.timestamp(value)

    def test_mutable_dependency_requires_current_identity_readback(self):
        self.policy["freshness"]["dependencies"] = {"api": "snapshot-v1"}
        with self.assertRaisesRegex(ev.ep.PolicyError, "readbacks"):
            self.check()
        self.report["provenance"]["dependency_readbacks"] = {"api": {"identity": "snapshot-v1",
            "checked_at": self.report["started_at"], "observation": "API configuration readback is snapshot-v1"}}
        self.check()
        self.report["provenance"]["dependency_readbacks"]["api"]["identity"] = "snapshot-v2"
        with self.assertRaises(ev.ep.PolicyError):
            self.check()


if __name__ == "__main__":
    unittest.main()
