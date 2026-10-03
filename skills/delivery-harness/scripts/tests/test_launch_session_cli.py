"""Parent locks and child launch identities survive the public CLI path."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import harness_transition as ht
from harness_manifest import load_run, validate_run
from manifest_fixtures import manifest_markdown
from test_role_dispatch_integration import mission_reservation


class LaunchSessionCliTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.plan, self.run, _ = mission_reservation()
        ht._acquire_run_lock(self.run, ht.argparse.Namespace(session_id="parent-P", owner=None))
        self.plan_path = self.root / "PLAN.md"
        self.run_path = self.root / "RUN.md"
        self.plan_path.write_text(manifest_markdown("## Harness Plan Manifest", "harness_plan", self.plan), encoding="utf-8")
        self.save(self.run)

    def save(self, run):
        self.run_path.write_text(manifest_markdown("## Harness Run State", "harness_run", run), encoding="utf-8")

    def arguments(self, parent="parent-P", child="child-C1"):
        return ["--plan", str(self.plan_path), "--run", str(self.run_path),
                "--session-id", parent, "record-launch-observation",
                "--assignment-kind", "mission", "--assignment-id", "lease-1",
                "--node-id", "N-M1", "--worker-id", "worker-1",
                "--attempt-id", "attempt-1", "--model-provider", "claude_code",
                "--model", "claude-opus-5-5", "--reasoning-effort", "high",
                "--worker-session-id", child, "--launch-observation", "host start",
                "--host-observation", "parent read host response"]

    def call(self, arguments):
        # These synthetic reservations isolate the CLI transaction from the
        # separate live frozen-product/Git join, while retaining full RUN validation.
        with patch.object(ht, "validate_current_plan_run", side_effect=lambda plan, run, **kw: validate_run(plan, run)), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return ht.main(arguments)

    def test_public_cli_keeps_parent_lock_and_child_launch_distinct(self):
        self.assertEqual(0, self.call(self.arguments()))
        run = load_run(self.run_path)
        self.assertEqual("parent-P", run["run_lock"]["session_id"])
        self.assertEqual("child-C1", run["launch_records"][0]["session_id"])
        self.assertEqual([], validate_run(self.plan, run))

    def test_wrong_parent_or_model_or_attempt_does_not_write_run(self):
        mutations = [("--session-id", "foreign"), ("--model", "wrong"),
                     ("--attempt-id", "wrong")]
        for flag, value in mutations:
            with self.subTest(flag=flag):
                arguments = self.arguments()
                arguments[arguments.index(flag) + 1] = value
                before = self.run_path.read_bytes()
                self.assertEqual(2, self.call(arguments))
                self.assertEqual(before, self.run_path.read_bytes())

    def test_missing_child_is_rejected(self):
        arguments = self.arguments()
        offset = arguments.index("--worker-session-id")
        del arguments[offset:offset + 2]
        before = self.run_path.read_bytes()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.call(arguments)
        self.assertEqual(before, self.run_path.read_bytes())
    def test_old_child_flag_is_rejected_even_with_required_child_present(self):
        arguments = self.arguments() + ["--session-id", "ambiguous-child"]
        before = self.run_path.read_bytes()
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.call(arguments)
        self.assertEqual(before, self.run_path.read_bytes())

    def test_second_sibling_cannot_reuse_first_child_session(self):
        self.assertEqual(0, self.call(self.arguments()))
        run = load_run(self.run_path)
        _, _, original = mission_reservation()
        args = SimpleNamespace(**vars(original))
        args.mission_id = "M2"
        args.node_id = "N-M2"
        args.worker_id = "worker-2"
        args.lease_id = "lease-2"
        args.attempt_id = "attempt-2"
        args.branch_ref = "refs/heads/codex/m2"
        args.worktree_path = "C:/repo/worktrees/m2"
        from agent_role_bindings import resolve_runtime_binding
        node = next(n for n in self.plan["graph"]["nodes"] if n["id"] == "N-M2")
        binding = resolve_runtime_binding(node, run["runtime_capabilities"])
        for key in ("provider", "driver", "model", "reasoning_effort", "worker_runtime", "workspace_mode", "completion_channel"):
            setattr(args, key, binding[key])
        run["active_wave"]["selected_missions"].append("M2")
        run["mission_states"]["M2"].update(phase="ready", base_sha="a" * 40)
        ht._lease_worker(self.plan, run, args)
        run["observed"]["git"]["worktrees"].append({"path": args.worktree_path,
            "branch_ref": args.branch_ref, "head_sha": "a" * 40, "managed_by": "parent", "dirty": False})
        self.save(run)
        arguments = self.arguments()
        for flag, value in (("--assignment-id", "lease-2"), ("--node-id", "N-M2"),
                            ("--worker-id", "worker-2"), ("--attempt-id", "attempt-2"),
                            ("--model-provider", binding["model_provider"]),
                            ("--model", binding["model"] or "observed-native-model"),
                            ("--reasoning-effort", binding["reasoning_effort"] or "high")):
            arguments[arguments.index(flag) + 1] = value
        before = self.run_path.read_bytes()
        self.assertEqual(2, self.call(arguments))
        self.assertEqual(before, self.run_path.read_bytes())
        arguments[arguments.index("--worker-session-id") + 1] = "child-C2"
        self.assertEqual(0, self.call(arguments))
        self.assertEqual(["child-C1", "child-C2"], [r["session_id"] for r in load_run(self.run_path)["launch_records"]])


if __name__ == "__main__":
    unittest.main()
