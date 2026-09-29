"""Availability recovery needs a retained stopped failure, even before launch."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_role_bindings import resolve_runtime_binding
from agent_role_recovery import resolve_fallback_reservation
from manifest_fixtures import valid_plan, valid_run
from role_contract_fixtures import configure_role_run, retain_failure


def failed_attempt(kind):
    plan = valid_plan()
    run = configure_role_run(plan, valid_run(plan))
    role = "contract_writer" if kind == "mission" else "reviewer"
    node = next(n for n in plan["graph"]["nodes"]
                if n["id"] == ("N-M1" if kind == "mission" else "N-REVIEW-M1"))
    run["runtime_capabilities"]["runtime_adapter"]["role_bindings"][role]["fallback_role"] = "backend_worker"
    worker = {"worker_id": "failed-worker", "attempt_id": "failed-attempt", "phase": "worker_failed",
              "runtime_binding": resolve_runtime_binding(node, run["runtime_capabilities"])}
    worker.update({"mission_id": "M1", "lease_id": "old-lease"} if kind == "mission"
                  else {"node_id": node["id"]})
    run["workers" if kind == "mission" else "review_workers"] = [worker]
    evidence = {
        "fallback_from_role": role,
        "availability": {"classification": "model_provider_unavailable",
                         "observed_error": "requested model is unavailable", "policy_source": "host rules"},
        "predecessor": {"worker_id": worker["worker_id"], "stopped": True, "stop_evidence": "exit observed"},
        "partial_work": {"status": "none", "evidence": "unchanged checkout inspected"},
        "configured_fallback": {"role": "backend_worker", "model_provider": "codex", "model": "gpt-6-sol",
                                "reasoning_effort": "high", "policy_source": "host rules"},
        "predecessor_attempt_id": worker["attempt_id"],
    }
    return run, node, worker, evidence


class FailureReceiptTests(unittest.TestCase):
    def test_mission_and_review_failed_start_need_no_fabricated_launch(self):
        for kind in ("mission", "review"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                run, node, worker, evidence = failed_attempt(kind)
                worker["failure_receipt"] = retain_failure(temporary, worker, evidence)
                binding, errors = resolve_fallback_reservation(node, run, evidence, "fresh-attempt")
                self.assertEqual([], errors)
                self.assertEqual(evidence["fallback_from_role"], binding["worker_role"])
                self.assertEqual("backend_worker", binding["resolved_role"])
                self.assertFalse(run.get("launch_records"))

    def test_nonavailability_codes_never_authorize_fallback(self):
        for kind in ("mission", "review"):
            for code in ("quota_exhausted", "timeout", "quiet_stream", "test_failure", "permission_denied", "tool_missing"):
                with self.subTest(kind=kind, code=code), tempfile.TemporaryDirectory() as temporary:
                    run, node, worker, evidence = failed_attempt(kind)
                    worker["failure_receipt"] = retain_failure(temporary, worker, evidence, error_code=code)
                    binding, errors = resolve_fallback_reservation(node, run, evidence, "fresh-attempt")
                    self.assertIsNone(binding)
                    self.assertTrue(errors)

    def test_stale_attempt_live_predecessor_and_changed_evidence_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            run, node, worker, evidence = failed_attempt("mission")
            worker["failure_receipt"] = retain_failure(temporary, worker, evidence)
            self.assertTrue(resolve_fallback_reservation(node, run, evidence, worker["attempt_id"])[1])
            worker["phase"] = "worker_running"
            self.assertTrue(resolve_fallback_reservation(node, run, evidence, "new")[1])
            worker["phase"] = "worker_failed"
            changed = copy.deepcopy(evidence)
            changed["partial_work"]["evidence"] = "invented reconciliation"
            self.assertTrue(resolve_fallback_reservation(node, run, changed, "new")[1])
            changed = copy.deepcopy(evidence)
            changed["availability"]["observed_error"] = ""
            self.assertTrue(resolve_fallback_reservation(node, run, changed, "new")[1])


if __name__ == "__main__":
    unittest.main()
