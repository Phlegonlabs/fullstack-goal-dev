"""Current role-bound reviews preserve the structured security-result gates."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import test_security_review_result as security_fixture
from agent_result_receipts import payload_digest
from agent_role_bindings import resolve_runtime_binding
from harness_manifest import plan_digest, validate_run
from harness_transition import ManifestError, _record_launch_observation, _record_review_attempt
from role_contract_fixtures import native_reviewer_binding


class RoleReviewResultTests(unittest.TestCase):
    def test_current_review_requires_exact_returned_payload_and_persists_receipt(self):
        fixture = security_fixture.SecurityReviewTransitionTests()
        self.addCleanup(fixture.doCleanups)
        plan, run = fixture.state()
        node = next(n for n in plan["graph"]["nodes"] if n["id"] == "N-SECURITY-REVIEW")
        node["runtime"]["worker_role"] = "reviewer"
        adapter = run["runtime_capabilities"]["runtime_adapter"]
        adapter["version_gate"]["required_harness_version"] = "0.58.0"
        policy = native_reviewer_binding()
        policy.update(model_provider="generic", model="review-model")
        adapter["role_bindings"] = {"reviewer": policy}
        digest = plan_digest(plan)
        run["plan"]["digest_sha256"] = digest
        for grant in run["authorizations"].values():
            if isinstance(grant.get("scope"), dict):
                grant["scope"]["plan_digest_sha256"] = digest
        worker = run["review_workers"][0]
        worker.update(plan_digest_sha256=digest, workspace_mode="shared_checkout",
                      runtime_binding=resolve_runtime_binding(node, run["runtime_capabilities"]))
        _record_launch_observation(plan, run, SimpleNamespace(
            assignment_kind="review", assignment_id=node["id"], node_id=node["id"],
            worker_id=worker["worker_id"], attempt_id=worker["attempt_id"],
            model_provider="generic", model="review-model", reasoning_effort="xhigh",
            worker_session_id="review-session", launch_observation="actual launch", host_observation="parent host readback",
            fallback_record=None,
        ))
        # The established security-result fixture isolates a reserved review;
        # it does not construct preceding mission integration history.
        self.assertFalse(any("runtime_binding" in e or "launch_records" in e
                             for e in validate_run(plan, run)))
        result = security_fixture.valid_result(fixture._security_head, fixture._security_head)
        result["scope"] = node["review"]["scope"]
        with tempfile.TemporaryDirectory() as temporary:
            args = fixture.args(fixture.write_result(temporary, result))
            before = copy.deepcopy(run)
            with self.assertRaisesRegex(ManifestError, "result-receipt"):
                _record_review_attempt(plan, run, args)
            self.assertEqual(before, run)
            payload = {"outcome": "pass", "findings": [], "security_result": result,
                       "contract_adoption_check": None}
            source = Path(temporary) / "host-response.json"
            raw = json.dumps({"schema_version": 1, "session_id": "review-session", "payload": payload}).encode()
            source.write_bytes(raw)
            receipt = {"kind": "returned_result", "session_id": "review-session", "source_ref": str(source),
                       "source_sha256": hashlib.sha256(raw).hexdigest(), "payload_sha256": payload_digest(payload)}
            receipt_path = Path(temporary) / "receipt.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            args.result_receipt = receipt_path
            _record_review_attempt(plan, run, args)
            self.assertEqual("worker_passed", run["review_workers"][0]["phase"])
            self.assertEqual(receipt, run["review_workers"][0]["result_receipt"])
            self.assertFalse(any("result_receipt" in e or "runtime_binding" in e
                                 for e in validate_run(plan, run)))
            run["review_workers"][0]["findings"] = ["substituted finding"]
            self.assertTrue(any("result_receipt" in e for e in validate_run(plan, run)))


if __name__ == "__main__":
    unittest.main()
