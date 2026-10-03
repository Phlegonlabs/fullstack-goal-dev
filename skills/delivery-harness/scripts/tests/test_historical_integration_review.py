"""Recovery preserves terminal review history without accepting stale PASS."""
import copy
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness_manifest import validate_run
from harness_transition import _invalidate_stale_current_projections
import harness_transition as ht
import manifest_fixtures as mf
from test_security_review_result import valid_result


class HistoricalIntegrationReviewTests(unittest.TestCase):
    def fixture(self, outcome="pass", review_type=None):
        plan = mf.valid_plan()
        node_id = "N-VISUAL-REVIEW"
        node = copy.deepcopy(plan["graph"]["nodes"][1])
        node["id"] = node_id
        node["allowed_outcomes"] = ["pass", "fix_required", "retryable_failure", "contract_gap", "blocked"]
        node["review"].update(stage="integration", lineage_id="RL-INTEGRATION")
        if review_type:
            node["review"]["type"] = review_type
        plan["graph"]["nodes"].append(node)
        plan["graph"]["edges"].extend([
            {"id": "E-HIST-READY", "kind": "dependency", "from": "N-M2", "to": node_id, "on_outcomes": ["pass"], "max_traversals": None},
            {"id": "E-HIST-PASS", "kind": "route", "from": node_id, "to": "N-FINAL", "on_outcomes": ["pass"], "max_traversals": None},
        ])
        run = mf.valid_closeout_run(plan)
        mf.mark_complete(plan, run)
        run["status"] = "running"
        run["runtime_capabilities"]["runtime_adapter"]["detection_source"] = "observed"
        run["runtime_capabilities"]["runtime_adapter"]["capability_probe"] = mf.native_capability_probe(subagents=True)
        worker = next(w for w in run["review_workers"] if w["node_id"] == node_id)
        worker.update(worker_id="RW-OLD", attempt_id="ATT-OLD", reviewed_sha="a" * 40,
            review_path="C:/repo", outcome=outcome,
            phase="worker_passed" if outcome == "pass" else "blocked" if outcome == "blocked" else "worker_failed",
            findings=[] if outcome == "pass" else ["required coverage unavailable"])
        if review_type == "security":
            worker["base_sha"] = "a" * 40
            worker["security_result"] = valid_result("a" * 40, "a" * 40)
            worker["security_result"]["scope"] = node["review"]["scope"]
        run["graph_state"]["node_states"][node_id].update(phase="succeeded" if outcome == "pass" else "blocked",
            attempts=1, last_attempt_id="ATT-OLD", last_outcome=outcome,
            bound_worker_id="RW-OLD", blockers=[] if outcome == "pass" else ["review requires resolution"])
        run["attempt_log"].append({"attempt_id": "ATT-OLD", "mission_id": None,
            "task_id": None, "lease_id": None, "kind": "review", "result": outcome,
            "evidence": ["retained original review"], "failure_family_ids": [],
            "review_lineage_id": node["review"]["lineage_id"]})
        run["review_lineages"][node["review"]["lineage_id"]]["consumed_attempts"] = 1
        run["graph_state"]["edge_states"]["E-HIST-PASS"]["source_attempt_id"] = "ATT-OLD"
        if outcome != "pass":
            run["graph_state"]["edge_states"]["E-HIST-PASS"].update(
                status="dormant", traversals=0, source_attempt_id=None)
        retained = {attempt["attempt_id"] for attempt in run["attempt_log"]}
        nodes = {node["id"]: node for node in plan["graph"]["nodes"]}
        for identity_node, state in run["graph_state"]["node_states"].items():
            identity = state.get("last_attempt_id")
            if identity and identity not in retained and nodes[identity_node]["executor"] in {"local_command", "harness_parent"}:
                run["attempt_log"].append({"attempt_id": identity, "mission_id": None,
                    "task_id": None, "lease_id": None, "kind": "historical_graph_attempt",
                    "result": "pass", "evidence": ["retained fixture graph attempt"]})
                retained.add(identity)
        return plan, run

    def move_candidate(self, plan, run):
        run["integration"]["prior_head_shas"] = ["a" * 40]
        run["integration"]["integration_head_sha"] = "c" * 40
        _invalidate_stale_current_projections(plan, run, "a" * 40, "c" * 40)
        run["landing"]["continuity"]["head_sha"] = "c" * 40

    def head_errors(self, plan, run):
        return [e for e in validate_run(plan, run) if "review_workers" in e and "reviewed_sha" in e]

    def test_rearmed_candidate_preserves_detached_pass_bytes(self):
        plan, run = self.fixture()
        self.assertEqual([], validate_run(plan, run))
        retained = copy.deepcopy(run["review_workers"])
        attempts = copy.deepcopy(run["attempt_log"])
        self.move_candidate(plan, run)
        self.assertEqual(retained, run["review_workers"])
        self.assertEqual(attempts, run["attempt_log"])
        self.assertEqual("ready", run["graph_state"]["node_states"]["N-VISUAL-REVIEW"]["phase"])
        self.assertIsNone(run["graph_state"]["node_states"]["N-VISUAL-REVIEW"]["bound_worker_id"])
        self.assertEqual([], validate_run(plan, run))

    def test_old_pass_still_bound_as_current_is_rejected(self):
        plan, run = self.fixture()
        run["integration"]["prior_head_shas"] = ["a" * 40]
        run["integration"]["integration_head_sha"] = "c" * 40
        self.assertTrue(self.head_errors(plan, run))

    def test_detached_security_pass_keeps_exact_historical_result(self):
        plan, run = self.fixture(review_type="security")
        self.assertEqual([], validate_run(plan, run))
        retained = copy.deepcopy(run["review_workers"])
        self.move_candidate(plan, run)
        self.assertEqual(retained, run["review_workers"])
        self.assertEqual([], validate_run(plan, run))
        worker = next(w for w in run["review_workers"] if w["worker_id"] == "RW-OLD")
        worker["security_result"]["reviewed_sha"] = "c" * 40
        self.assertTrue(any("security_result" in e for e in validate_run(plan, run)))

    def test_detached_failed_review_keeps_history(self):
        for outcome in ("fix_required", "retryable_failure", "contract_gap"):
            with self.subTest(outcome=outcome):
                plan, run = self.fixture(outcome=outcome)
                self.assertEqual([], validate_run(plan, run))
                self.move_candidate(plan, run)
                self.assertEqual([], validate_run(plan, run))

    def interrupted_fixture(self):
        plan, run = self.fixture()
        worker = next(w for w in run["review_workers"] if w["worker_id"] == "RW-OLD")
        worker.update(phase="worker_running", outcome=None, findings=[], worker_runtime="subagent")
        worker["runtime_binding"]["driver"] = "subagents"
        run["attempt_log"] = [a for a in run["attempt_log"] if a["attempt_id"] != "ATT-OLD"]
        run["review_lineages"]["RL-INTEGRATION"]["consumed_attempts"] = 0
        state = run["graph_state"]["node_states"][worker["node_id"]]
        state.update(phase="running", last_outcome=None)
        run["graph_state"]["edge_states"]["E-HIST-PASS"].update(
            status="dormant", traversals=0, source_attempt_id=None)
        self.assertEqual([], validate_run(plan, run))
        ht._reconcile_interrupted_reviews(plan, run, ht.argparse.Namespace(
            worker_id=["RW-OLD"], reason="owning runtime confirmed stopped", source="test runtime stop"))
        self.assertEqual([], validate_run(plan, run))
        return plan, run

    def test_reconciled_interrupted_review_survives_move_and_closeout(self):
        plan, run = self.interrupted_fixture()
        retained = copy.deepcopy(next(w for w in run["review_workers"] if w["worker_id"] == "RW-OLD"))
        self.move_candidate(plan, run)
        self.assertEqual([], validate_run(plan, run))
        self.assertEqual(retained, next(w for w in run["review_workers"] if w["worker_id"] == "RW-OLD"))
        # Establish fresh candidate coverage with the complete closeout fixture.
        # Its helper does not retain detached workers, so explicitly append the
        # original interruption evidence after constructing fresh current gates.
        interruption_attempt = copy.deepcopy(next(a for a in run["attempt_log"] if a["attempt_id"] == "ATT-OLD"))
        run["attempt_log"] = [interruption_attempt]
        run["verifier_executions"] = []
        mf.mark_complete(plan, run)
        current = next(w for w in run["review_workers"] if w["node_id"] == "N-VISUAL-REVIEW")
        current.update(reviewed_sha="c" * 40, review_path="C:/repo")
        run["review_workers"].append(retained)
        run["status"] = "complete"
        self.assertEqual([], validate_run(plan, run), validate_run(plan, run))

    def test_missing_or_wrong_interruption_receipt_rejects_move(self):
        for mutation in ("missing", "lineage", "duplicate", "outcome"):
            with self.subTest(mutation=mutation):
                plan, run = self.interrupted_fixture()
                attempt = next(a for a in run["attempt_log"] if a["attempt_id"] == "ATT-OLD")
                if mutation == "missing":
                    attempt["evidence"].remove(ht.INTERRUPTED_REVIEW_RECEIPT)
                elif mutation == "lineage":
                    attempt["review_lineage_id"] = "OTHER"
                elif mutation == "duplicate":
                    run["attempt_log"].append(copy.deepcopy(attempt))
                else:
                    attempt["result"] = "pass"
                self.move_candidate(plan, run)
                self.assertTrue(self.head_errors(plan, run))

    def candidate_cli_move(self, outcome):
        plan, run = self.fixture(outcome=outcome)
        self.assertEqual([], validate_run(plan, run))
        ht._acquire_run_lock(run, ht.argparse.Namespace(session_id="parent-P", owner=None))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan_path, run_path = root / "PLAN.md", root / "RUN.md"
            plan_path.write_text(mf.manifest_markdown("## Harness Plan Manifest", "harness_plan", plan), encoding="utf-8")
            run_path.write_text(mf.manifest_markdown("## Harness Run State", "harness_run", run), encoding="utf-8")
            before = run_path.read_bytes()
            # Isolate candidate invalidation and atomic persistence from the
            # live Git/product repair joins, which have separate CLI fixtures.
            def move(plan, run, _arguments):
                self.move_candidate(plan, run)
                return {}
            errors = io.StringIO()
            with patch.object(ht, "_reconcile_candidate_head", side_effect=move), patch.object(ht, "validate_current_plan_run", side_effect=lambda plan, run, **kw: validate_run(plan, run)), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
                result = ht.main(["--plan", str(plan_path), "--run", str(run_path),
                    "--session-id", "parent-P", "reconcile-candidate-head",
                    "--candidate-sha", "c" * 40, "--repair-node-id", "N-REVIEW-M1",
                    "--repair-attempt-id", "ATT-REPAIR", "--repair-task-id", "M1/T1",
                    "--source", "test repair"])
            return result, errors.getvalue(), before, run_path.read_bytes()

    def test_blocked_sibling_candidate_move_does_not_save_run(self):
        result, errors, before, after = self.candidate_cli_move("blocked")
        self.assertEqual(2, result)
        self.assertIn("reviewed_sha", errors)
        self.assertEqual(before, after)

    def test_passed_sibling_candidate_move_saves_run(self):
        result, errors, before, after = self.candidate_cli_move("pass")
        self.assertEqual(0, result, errors)
        self.assertNotEqual(before, after)

    def test_missing_wrong_or_duplicate_retained_attempt_rejects_history(self):
        for mutation in ("missing", "lineage", "outcome", "duplicate", "active", "unrecorded"):
            with self.subTest(mutation=mutation):
                plan, run = self.fixture()
                self.move_candidate(plan, run)
                attempt = next(a for a in run["attempt_log"] if a["attempt_id"] == "ATT-OLD")
                if mutation == "missing":
                    run["attempt_log"].remove(attempt)
                elif mutation == "lineage":
                    attempt["review_lineage_id"] = "OTHER"
                elif mutation == "outcome":
                    attempt["result"] = "blocked"
                elif mutation == "duplicate":
                    run["attempt_log"].append(copy.deepcopy(attempt))
                elif mutation == "active":
                    next(w for w in run["review_workers"] if w["node_id"] == "N-VISUAL-REVIEW")["phase"] = "worker_running"
                else:
                    run["integration"]["prior_head_shas"] = []
                self.assertTrue(self.head_errors(plan, run))


if __name__ == "__main__":
    unittest.main()
