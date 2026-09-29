"""A child identity echo cannot replace retained host result evidence."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_result_receipts import payload_digest, validate_result_receipt
from harness_transition import _record_launch_observation
from test_role_dispatch_integration import mission_reservation, launch_arguments
from harness_worker_result_transition import record_worker_result
from harness_core import ManifestError


class ResultReceiptTests(unittest.TestCase):
    def test_record_rejects_missing_receipt_before_observation_or_mutation(self):
        plan, run, _ = mission_reservation()
        before = copy.deepcopy(run)
        # This admission test intentionally needs only the node identity:
        # missing provenance must fail before filesystem observation/schema work.
        with tempfile.TemporaryDirectory() as temporary:
            result_path = Path(temporary) / "node.json"
            result_path.write_text(json.dumps({"node_id": "N-M1"}), encoding="utf-8")
            args = SimpleNamespace(repo_root=Path(temporary), node_result=result_path)
            with patch("harness_worker_result_transition._observe_bound_worker") as observe:
                with self.assertRaisesRegex(ManifestError, "result-receipt"):
                    record_worker_result(plan, run, args)
                observe.assert_not_called()
        self.assertEqual(before, run)

    def test_mission_and_review_require_matching_host_session_and_bytes(self):
        for kind in ("mission", "review"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                plan, run, _ = mission_reservation()
                _record_launch_observation(plan, run, launch_arguments())
                worker = copy.deepcopy(run["workers"][0])
                launch = run["launch_records"][0]
                if kind == "review":
                    worker.update(node_id="N-R1", reviewed_sha="a" * 40, base_sha="b" * 40)
                    launch.update(assignment_kind="review", assignment_id="N-R1",
                                  node_id="N-R1", reviewed_sha="a" * 40, base_sha="b" * 40)
                payload = {"outcome": "pass", "findings": []}
                source = Path(temporary) / "host-result.json"
                raw = json.dumps({"schema_version": 1, "session_id": "host-session-1",
                                  "payload": payload}).encode()
                source.write_bytes(raw)
                receipt = {"kind": "returned_result", "session_id": "host-session-1",
                           "source_ref": str(source), "source_sha256": hashlib.sha256(raw).hexdigest(),
                           "payload_sha256": payload_digest(payload)}
                self.assertEqual([], validate_result_receipt(run, worker, kind, receipt, payload))
                self.assertTrue(validate_result_receipt(run, worker, kind, None, payload))
                for field, wrong in (("session_id", "another-session"),
                                     ("source_sha256", "0" * 64),
                                     ("payload_sha256", "0" * 64)):
                    changed = {**receipt, field: wrong}
                    self.assertTrue(validate_result_receipt(run, worker, kind, changed, payload))
                self.assertTrue(validate_result_receipt(run, worker, kind, receipt,
                                                       {"outcome": "fix_required", "findings": ["bug"]}))
                source.write_text(json.dumps({"schema_version": 1, "session_id": "forged",
                                              "payload": payload}), encoding="utf-8")
                self.assertTrue(validate_result_receipt(run, worker, kind, receipt, payload))


if __name__ == "__main__":
    unittest.main()
