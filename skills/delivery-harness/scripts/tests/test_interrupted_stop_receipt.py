"""A current delegated mission cannot retry an unobserved live predecessor."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_failure_receipts import interrupted_retry_issues
from harness_core import ManifestError
from harness_transition import _lease_worker, _reconcile_interrupted, _record_launch_observation
from select_ready_nodes import select_ready_nodes
from role_contract_fixtures import retain_failure
from test_role_dispatch_integration import mission_reservation, launch_arguments


class InterruptedStopReceiptTests(unittest.TestCase):
    def fixture(self):
        plan, run, _ = mission_reservation()
        _record_launch_observation(plan, run, launch_arguments())
        run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.59.0"
        return plan, run, run["workers"][0]

    def receipt(self, directory, worker, *, stopped=True, partial="none", session="host-session-1"):
        evidence = {"availability": {"classification": "interrupted", "observed_error": "host cancelled worker"},
            "predecessor": {"stopped": stopped, "stop_evidence": "host terminal cancellation observed"},
            "partial_work": {"status": partial, "evidence": "checkout inspected"}}
        receipt = retain_failure(directory, worker, evidence, session=session, error_code="cancelled")
        path = Path(directory) / "receipt.json"
        path.write_text(json.dumps(receipt), encoding="utf-8")
        return path, receipt

    def test_confirmed_stop_preserves_receipt_and_allows_same_role_retry_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            _, run, worker = self.fixture()
            path, receipt = self.receipt(directory, worker)
            _reconcile_interrupted(run, SimpleNamespace(worker_id=worker["worker_id"], reason="cancelled", failure_receipt=path))
            self.assertEqual("blocked", worker["phase"])
            self.assertEqual(receipt, worker["failure_receipt"])
            self.assertEqual([], interrupted_retry_issues(run, run["attempt_log"][-1]))
            Path(receipt["source_ref"]).write_text("tampered", encoding="utf-8")
            self.assertTrue(interrupted_retry_issues(run, run["attempt_log"][-1]))

    def test_unknown_liveness_wrong_session_partial_work_or_missing_receipt_cannot_mutate(self):
        for case in ("missing", "live", "session", "partial", "attempt"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                _, run, worker = self.fixture()
                path, _ = self.receipt(directory, worker, stopped=case != "live",
                    partial="unknown" if case == "partial" else "none",
                    session="wrong" if case == "session" else "host-session-1")
                if case == "attempt":
                    worker["attempt_id"] = "wrong-attempt"
                before = copy.deepcopy(run)
                with self.assertRaises(ManifestError):
                    _reconcile_interrupted(run, SimpleNamespace(worker_id=worker["worker_id"], reason="interrupted",
                        failure_receipt=None if case == "missing" else path))
                self.assertEqual(before, run)

    def test_preexisting_marker_without_stop_evidence_blocks_current_retry(self):
        _, run, worker = self.fixture()
        marker = {"lease_id": worker["lease_id"], "mission_id": worker["mission_id"]}
        self.assertTrue(interrupted_retry_issues(run, marker))
        run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.58.0"
        self.assertEqual([], interrupted_retry_issues(run, marker))

    def test_selector_and_direct_lease_recheck_stopped_predecessor(self):
        with tempfile.TemporaryDirectory() as directory:
            plan, run, worker = self.fixture()
            path, _ = self.receipt(directory, worker)
            _reconcile_interrupted(run, SimpleNamespace(worker_id=worker["worker_id"], reason="cancelled", failure_receipt=path))
            _, _, original = mission_reservation()
            original.worker_id = "retry-worker"
            original.lease_id = "retry-lease"
            original.attempt_id = "retry-attempt"
            valid = copy.deepcopy(run)
            _lease_worker(plan, valid, original)
            self.assertEqual("retry-worker", valid["mission_states"]["M1"]["worker_id"])
            worker.pop("failure_receipt")
            before = copy.deepcopy(run)
            with self.assertRaises(ManifestError):
                _lease_worker(plan, run, original)
            self.assertEqual(before, run)
            result = select_ready_nodes(plan, run, manifest_already_validated=True)
            self.assertNotIn("N-M1", [item["node_id"] for item in result["dispatchable_nodes"]])


if __name__ == "__main__":
    unittest.main()
