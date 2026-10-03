import contextlib
import copy
import hashlib
import io
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_eval_acceptance as checker
import manifest_fixtures as mf
from eval_delivery_fixtures import fixture, encoded, prd
from test_delivery_acceptance import execution
from eval_verification import QUALITY_ASSERTIONS, HANDOFF_ASSERTIONS


class EvalMissingParserTests(unittest.TestCase):
    def test_cli_missing_sibling_returns_json_failure_without_traceback(self):
        output = io.StringIO()
        with patch.dict(sys.modules, {"eval_verification": None}), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(checker.__file__, run_name="__main__")
        self.assertEqual(1, result.exception.code)
        self.assertEqual("FAIL", json.loads(output.getvalue())["status"])


class EvalAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        mf.init_repo(self.root, "README.md")
        self.policy, files, self.contract, _, report, _ = fixture()
        self.write(".gitattributes", b"* -text -filter\n")
        self.prd_path = "docs/product/PRD.md"
        self.contract_path = "docs/verification/eval-contract.json"
        self.delivery_path = "docs/verification/delivery-acceptance.json"
        self.results_path = "docs/verification/delivery-results.json"
        self.write(self.prd_path, prd(self.policy).encode())
        self.write(self.contract_path, encoded(self.contract))
        for path, raw in files.items():
            self.write(path, raw)
        for name in ("runner", "grader", "lockfile", "runbook"):
            path = self.policy["delivery"][name]
            self.write(path, ("Delivered " + path).encode())
        self.delivery = {"schema": "delivery-acceptance/1", "prd_sha256": self.contract["prd_sha256"], "tests": []}
        self.register = {"schema": "delivery-results/1", "candidate_sha": "", "results": []}
        self.reports = {}
        for purpose, assertions in (("quality", QUALITY_ASSERTIONS), ("handoff", HANDOFF_ASSERTIONS)):
            declared = self.policy[purpose]
            context = execution()
            context["assertions"] = {name: "Frozen eval policy verified by deterministic checker" for name in sorted(assertions)}
            scenario = {"id": declared["scenario_id"], "execution": context,
                        "platform": "cli", "auth_mode": "none", "environment": "local",
                        "build": {"build_id": "fixture-eval-1", "config_digest": "b" * 64}, "fixtures": []}
            self.delivery["tests"].append({"test_id": declared["test_id"], "scenarios": [scenario]})
            current = copy.deepcopy(report)
            current.update(purpose=purpose, run_id=purpose + "-run-1", execution=context)
            current["provenance"]["job_id"] = "job-" + purpose + "-1"
            self.reports[purpose] = current
            self.register["results"].append({"test_id": declared["test_id"], "scenario_id": scenario["id"],
                **{name: scenario[name] for name in ("execution", "platform", "auth_mode", "environment", "build")},
                "status": "pass", "assertion_results": {name: "pass" for name in assertions},
                "fixture_cleanup": "not_required", "evidence": {"path": declared["report"], "sha256": ""}})
        self.write(self.delivery_path, encoded(self.delivery))
        self.h1 = self.commit("product candidate")
        self.register["candidate_sha"] = self.h1
        for report in self.reports.values():
            report["candidate_sha"] = self.h1
            report["provenance"]["checkout_sha"] = self.h1
        self.save_reports()
        self.h2 = self.commit("directly registered evidence")

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)

    def commit(self, message):
        mf.git(self.root, "add", "-A")
        mf.git(self.root, "commit", "-qm", message)
        return mf.git(self.root, "rev-parse", "HEAD")

    def save_reports(self):
        for purpose, report in self.reports.items():
            path = self.policy[purpose]["report"]
            raw = encoded(report)
            self.write(path, raw)
            for row in self.register["results"]:
                if row["test_id"] == self.policy[purpose]["test_id"]:
                    row["evidence"]["sha256"] = hashlib.sha256(raw).hexdigest()
        self.write(self.results_path, encoded(self.register))

    def invoke(self, overrides=None):
        values = {"--repo-root": str(self.root), "--prd": self.prd_path,
            "--prd-sha256": self.contract["prd_sha256"], "--contract": self.contract_path,
            "--contract-sha256": hashlib.sha256(encoded(self.contract)).hexdigest(),
            "--delivery-contract": self.delivery_path,
            "--delivery-contract-sha256": hashlib.sha256(encoded(self.delivery)).hexdigest(), "--results": self.results_path}
        values.update(overrides or {})
        argv = [value for pair in values.items() for value in pair] + ["--candidate-from-head"]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = checker.main(argv)
        return code, json.loads(output.getvalue())

    def test_h1_h2_full_quality_and_handoff_pass(self):
        code, result = self.invoke()
        self.assertEqual((0, []), (code, result["errors"]))
        self.assertEqual(self.h1, result["candidate_sha"])
        self.assertEqual(self.h2, result["checked_head_sha"])
        self.assertEqual(8, result["reports"]["handoff"]["planned_trials"])

    def test_frozen_inputs_cannot_be_replaced(self):
        code, result = self.invoke({"--prd-sha256": "f" * 64})
        self.assertEqual(1, code)
        self.assertIn("frozen", str(result))

    def test_changed_uncommitted_report_and_product_after_h1_fail(self):
        self.write(self.policy["quality"]["report"], b"{}")
        self.assertEqual(1, self.invoke()[0])
        self.save_reports()
        self.write(self.policy["delivery"]["runner"], b"new runner version")
        self.commit("runner repair")
        code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertTrue(any(word in str(result) for word in ("bytes", "candidate", "context")))

    def test_same_trial_report_cannot_satisfy_handoff(self):
        self.reports["handoff"]["run_id"] = self.reports["quality"]["run_id"]
        self.save_reports()
        self.commit("invalid handoff evidence")
        self.assertEqual(1, self.invoke()[0])

    def test_missing_handoff_or_assertion_join_fails(self):
        self.register["results"].pop()
        self.save_reports()
        self.commit("missing handoff")
        self.assertEqual(1, self.invoke()[0])

    def test_prohibited_outcome_in_handoff_is_recomputed(self):
        self.reports["handoff"]["trials"][0]["assertion_results"]["no-side-effect"] = "fail"
        self.save_reports()
        self.commit("prohibited outcome")
        code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertIn("prohibited", str(result))

    def test_unregistered_outside_root_and_transitive_trace_rejected(self):
        self.register["results"][0]["evidence"]["path"] = "evals/cases.jsonl"
        self.write(self.results_path, encoded(self.register))
        self.commit("invalid evidence root")
        self.assertEqual(1, self.invoke()[0])

    def test_moving_head_and_exact_byte_guards(self):
        with patch.object(checker.acceptance, "_head_sha", side_effect=[self.h2, "f" * 40]):
            code, result = self.invoke()
        self.assertEqual(1, code)
        self.assertIn("HEAD changed", str(result))
        with patch.object(checker.acceptance, "_committed_file_errors", return_value=["bytes differ from HEAD"]):
            self.assertEqual(1, self.invoke()[0])

    def test_symlink_secret_and_duplicate_json_fail(self):
        for path in ("../outside.json", ".env", "evals/auth-token.json"):
            self.assertEqual(1, self.invoke({"--contract": path})[0])
        path = self.policy["quality"]["report"]
        self.write(path, b'{"schema":1,"schema":2}')
        self.commit("duplicate evidence keys")
        self.assertEqual(1, self.invoke()[0])


if __name__ == "__main__":
    unittest.main()
