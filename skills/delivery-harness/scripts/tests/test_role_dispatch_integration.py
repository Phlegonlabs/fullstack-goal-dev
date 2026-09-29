"""Exercise role reservations through complete RUN and launch validation."""
import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_role_bindings import validate_execution_binding, validate_role_bindings
from agent_launch_records import validate_launch_record_shape
from harness_manifest import validate_run
from harness_transition import ManifestError, _lease_worker, _record_launch_observation
from manifest_fixtures import valid_plan, valid_run
from role_contract_fixtures import (
    authorize_selection,
    capability,
    configure_role_run,
    native_writer_binding,
    refresh_plan_binding,
)
from select_ready_nodes import select_ready_nodes


def mission_reservation():
    plan = valid_plan()
    run = configure_role_run(plan, valid_run(plan))
    authorize_selection(run)
    run["active_wave"].update(wave_id="W1", status="active", batch_base_sha="a" * 40,
                              selected_missions=["M1"])
    run["integration"]["batch_base_sha"] = "a" * 40
    run["mission_states"]["M1"].update(phase="ready", base_sha="a" * 40)
    args = SimpleNamespace(
        mission_id="M1", node_id="N-M1", worker_id="worker-1", lease_id="lease-1",
        attempt_id="attempt-1", branch_ref="refs/heads/codex/m1",
        worktree_path="C:/repo/worktrees/m1", provider="codex", driver="external_bridge",
        model="claude-opus-5-5", reasoning_effort="high", worker_runtime="subagent",
        workspace_mode="parent_managed_worktree", completion_channel="agent_result",
        task_thread_id=None, report_path=None, fallback_record=None,
    )
    _lease_worker(plan, run, args)
    run["observed"]["git"]["worktrees"].append({
        "path": args.worktree_path, "branch_ref": args.branch_ref,
        "head_sha": "a" * 40, "managed_by": "parent", "dirty": False,
    })
    return plan, run, args


def launch_arguments():
    return SimpleNamespace(
        assignment_kind="mission", assignment_id="lease-1", node_id="N-M1",
        worker_id="worker-1", attempt_id="attempt-1", model_provider="claude_code",
        model="claude-opus-5-5", reasoning_effort="high", session_id="host-session-1",
        launch_observation="retained host start response", host_observation="parent host observation",
        fallback_record=None,
    )


class RoleDispatchIntegrationTests(unittest.TestCase):
    def test_malformed_role_and_launch_scalars_return_errors_not_exceptions(self):
        plan, run, _ = mission_reservation()
        _record_launch_observation(plan, run, launch_arguments())
        for malformed in ([], {}):
            for key in ("kind", "worker_runtime", "workspace_mode", "completion_channel", "reasoning_effort"):
                candidate = copy.deepcopy(run)
                candidate["runtime_capabilities"]["runtime_adapter"]["role_bindings"]["contract_writer"][key] = malformed
                self.assertTrue(validate_role_bindings(candidate))
            for key in ("assignment_kind", "worker_runtime", "workspace_mode", "completion_channel", "reasoning_effort", "requested_reasoning_effort"):
                record = {**run["launch_records"][0], key: malformed}
                self.assertTrue(validate_launch_record_shape(record, "record"))

    def test_new_role_lease_validates_as_complete_run(self):
        plan, run, _ = mission_reservation()
        self.assertEqual([], validate_run(plan, run))

    def test_recorded_launch_validates_as_complete_run(self):
        plan, run, _ = mission_reservation()
        _record_launch_observation(plan, run, launch_arguments())
        self.assertEqual([], validate_run(plan, run))

    def test_observed_model_mismatch_rejects_without_mutation(self):
        plan, run, _ = mission_reservation()
        args = launch_arguments()
        args.model = "wrong-model"
        before = copy.deepcopy(run)
        with self.assertRaises(ManifestError):
            _record_launch_observation(plan, run, args)
        self.assertEqual(before, run)

    def test_declared_generic_role_cannot_override_frontend_requirement(self):
        plan = valid_plan()
        run = configure_role_run(plan, valid_run(plan))
        plan["missions"][0]["required_skills"].append("frontend-design")
        refresh_plan_binding(plan, run)
        authorize_selection(run)
        self.assertEqual([], validate_run(plan, run))
        result = select_ready_nodes(plan, run, manifest_already_validated=True)
        ready = [item["node_id"] for item in result["dispatchable_nodes"]]
        self.assertNotIn("N-M1", ready)
        self.assertIn("N-M2", ready)

    def test_style_impact_needs_frontend_but_api_mission_stays_eligible(self):
        plan = valid_plan()
        run = configure_role_run(plan, valid_run(plan))
        run["ui_impact_summary"] = [
            {"mission_id": "M1", "impact": "style"},
            {"mission_id": "M2", "impact": "none"},
        ]
        authorize_selection(run)
        self.assertEqual([], validate_run(plan, run))
        result = select_ready_nodes(plan, run, manifest_already_validated=True)
        ready = [item["node_id"] for item in result["dispatchable_nodes"]]
        self.assertNotIn("N-M1", ready)
        self.assertIn("N-M2", ready)

    def test_isolated_role_binding_overrides_global_shared_checkout(self):
        plan = valid_plan()
        run = configure_role_run(plan, valid_run(plan))
        run["runtime_capabilities"]["workspace_mode"] = "shared_checkout"
        authorize_selection(run)
        self.assertEqual([], validate_run(plan, run))
        result = select_ready_nodes(plan, run, manifest_already_validated=True)
        ready = [item["node_id"] for item in result["dispatchable_nodes"]]
        deferred = {
            item["node_id"]: item["reason_codes"] for item in result["deferred_nodes"]
        }
        self.assertIn("N-M1", ready)
        self.assertNotIn("workspace_not_isolated", deferred.get("N-M1", []))

    def test_shared_role_binding_defers_under_globally_isolated_run(self):
        plan = valid_plan()
        run = configure_role_run(plan, valid_run(plan))
        run["runtime_capabilities"]["runtime_adapter"]["role_bindings"][
            "contract_writer"
        ]["workspace_mode"] = "shared_checkout"
        authorize_selection(run)
        self.assertEqual([], validate_run(plan, run))
        result = select_ready_nodes(plan, run, manifest_already_validated=True)
        ready = [item["node_id"] for item in result["dispatchable_nodes"]]
        deferred = {
            item["node_id"]: item["reason_codes"] for item in result["deferred_nodes"]
        }
        self.assertIn("workspace_not_isolated", deferred["N-M1"])
        self.assertIn("N-M2", ready)

    def test_app_task_role_binding_requires_observed_app_capabilities(self):
        plan = valid_plan()
        run = configure_role_run(plan, valid_run(plan))
        binding = native_writer_binding()
        binding.update(
            {
                "worker_runtime": "app_task",
                "workspace_mode": "app_managed_worktree",
                "completion_channel": "thread_poll",
            }
        )
        run["runtime_capabilities"]["runtime_adapter"]["role_bindings"][
            "backend_worker"
        ] = binding

        errors = validate_role_bindings(run)

        self.assertTrue(
            any(
                "missing required capabilities:" in error
                and "app_project_list" in error
                for error in errors
            )
        )
        binding["capability_probe"].update(
            {
                name: capability(name)
                for name in (
                    "app_project_list",
                    "app_thread_create",
                    "app_thread_read",
                    "app_thread_message",
                    "app_thread_wait",
                    "app_managed_worktree",
                )
            }
        )
        self.assertEqual([], validate_role_bindings(run))

    def test_fallback_binding_cannot_change_logical_node_role(self):
        plan, run, _ = mission_reservation()
        binding = copy.deepcopy(run["workers"][0]["runtime_binding"])
        binding.update(worker_role="backend_worker", fallback_from_role="contract_writer",
                       resolved_role="backend_worker")
        node = next(node for node in plan["graph"]["nodes"] if node["id"] == "N-M1")
        self.assertTrue(validate_execution_binding("binding", binding, node,
                                                  run["runtime_capabilities"]))


if __name__ == "__main__":
    unittest.main()
