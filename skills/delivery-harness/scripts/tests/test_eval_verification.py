import copy
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_verification as ev
from eval_delivery_fixtures import fixture


class EvalVerificationTests(unittest.TestCase):
    def setUp(self):
        self.policy, _, self.contract, self.approved, self.report, self.now = fixture()

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

    def test_derived_contract_cannot_weaken_policy(self):
        ev.validate_contract(self.contract, self.policy, self.report["prd_sha256"])
        self.contract["quality"]["test_id"] = "TEST-003"
        with self.assertRaises(ev.ep.PolicyError):
            ev.validate_contract(self.contract, self.policy, self.report["prd_sha256"])

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
