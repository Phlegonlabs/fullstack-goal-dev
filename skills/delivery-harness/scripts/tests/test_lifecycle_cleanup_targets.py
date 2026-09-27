#!/usr/bin/env python3
"""Cleanup lifecycle nodes record exact targets and never delete protected branches."""

from __future__ import annotations

import sys
import unittest
from argparse import Namespace
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import harness_transition  # noqa: E402
import manifest_fixtures as mf  # noqa: E402
from harness_authorization import authorization_covers, is_protected_branch_target  # noqa: E402
from harness_core import ManifestError  # noqa: E402
from harness_manifest import (  # noqa: E402
    plan_digest,
    validate_current_plan_run,
    validate_plan,
    validate_run,
)
from harness_schema import EXACT_TARGET_LIFECYCLE_ACTIONS  # noqa: E402
from select_ready_nodes import _dispatch_reasons  # noqa: E402


NODE_ID = "N-DELETE-BRANCH"


def lifecycle_pair(target: str | None, grant_targets: list[str], ref: str = "delete_branches"):
    """Return a running PLAN/RUN pair with one dormant cleanup root node."""

    plan = mf.valid_plan()
    run = mf.valid_run(plan)
    mf.authorize_execution(run, ["M1", "M2"])
    run.update({"status": "running", "plan_readiness": "ready"})
    run["observed"]["git"].update(
        {
            "parent_branch": "codex/test",
            "parent_head_sha": "a" * 40,
            "parent_dirty": False,
            "default_branch": "trunk",
        }
    )
    run["integration"].update(
        {
            "branch": "codex/test",
            "batch_base_sha": "a" * 40,
            "integration_head_sha": "a" * 40,
        }
    )
    node = {
        "id": NODE_ID,
        "kind": "lifecycle",
        "ref": ref,
        "executor": "harness_parent",
        "allowed_outcomes": ["pass", "blocked"],
        "max_attempts": 2,
        "runtime": None,
    }
    if target is not None:
        node["target"] = target
    plan["graph"]["nodes"].append(node)
    plan["graph"]["entry_nodes"].append(NODE_ID)
    run["graph_state"]["node_states"][NODE_ID] = {
        "phase": "dormant",
        "attempts": 0,
        "last_attempt_id": None,
        "last_outcome": None,
        "bound_worker_id": None,
        "blockers": [],
    }
    digest = plan_digest(plan)
    run["plan"]["digest_sha256"] = digest
    run["execution_authorization_scope"]["plan_digest_sha256"] = digest
    run["observed"]["sandbox"]["plan_digest_sha256"] = digest
    mf.authorize_action(run, ref, ["M1", "M2"], grant_targets)
    return plan, run


def set_required_version(run, version: str) -> None:
    run["runtime_capabilities"]["runtime_adapter"]["version_gate"][
        "required_harness_version"
    ] = version


def reserve(plan, run, attempt_id: str = "ATT-DELETE"):
    return harness_transition._reserve_node_attempt(
        plan,
        run,
        Namespace(node_id=NODE_ID, attempt_id=attempt_id, evidence=["reserve"]),
    )


def record(plan, run, outcome: str, attempt_id: str = "ATT-DELETE"):
    return harness_transition._record_node_result(
        plan,
        run,
        Namespace(
            node_id=NODE_ID,
            attempt_id=attempt_id,
            outcome=outcome,
            evidence=["branch deleted"],
            blocker=[] if outcome == "pass" else ["side effect uncertain"],
            verifier_result=[],
            repo_root=None,
        ),
    )


def reserve_legacy_wildcard(run, attempt_id: str = "ATT-LEGACY") -> None:
    """Record a pre-fix reservation that has no exact target."""

    run["graph_state"]["node_states"][NODE_ID].update(
        {"phase": "running", "attempts": 1, "last_attempt_id": attempt_id}
    )
    run["attempt_log"].append(
        {
            "attempt_id": attempt_id,
            "node_id": NODE_ID,
            "mission_id": None,
            "task_id": None,
            "lease_id": None,
            "kind": "node_attempt",
            "result": "reserved",
            "evidence": ["legacy reserve"],
            "node_dispatch": {"target": "*", "authorized_head_sha": None},
        }
    )


class CleanupLifecycleTargetTests(unittest.TestCase):
    def test_wildcard_grant_covers_exact_branch_but_not_protected_ones(self) -> None:
        _plan, run = lifecycle_pair("branch:codex/done", ["*"])
        self.assertTrue(
            authorization_covers(run, "delete_branches", "M1", "branch:codex/done")
        )
        for protected in (
            "branch:main",
            "branch:refs/heads/main",
            "branch:development",
            "branch:trunk",
            "branch:refs/heads/trunk",
        ):
            with self.subTest(target=protected):
                self.assertFalse(
                    authorization_covers(run, "delete_branches", "M1", protected)
                )

    def test_ledger_rejects_protected_delete_branch_targets(self) -> None:
        for protected in ("branch:main", "branch:development", "branch:refs/heads/trunk"):
            with self.subTest(target=protected):
                plan, run = lifecycle_pair("branch:codex/done", [protected])
                errors = validate_current_plan_run(plan, run)
                self.assertTrue(
                    any("delete_branches cannot target main" in error for error in errors),
                    errors,
                )
        plan, run = lifecycle_pair("branch:codex/done", ["*", "branch:codex/done"])
        self.assertEqual([], validate_current_plan_run(plan, run))

    def test_reserve_requires_exact_target_and_records_it(self) -> None:
        # The selector defers a target-less cleanup node for every RUN, so
        # reserve refuses it even where the PLAN rule does not apply.
        plan, run = lifecycle_pair(None, ["*"])
        with self.assertRaisesRegex(ManifestError, r"not dispatchable \(action_not_authorized\)"):
            reserve(plan, run)

        plan, run = lifecycle_pair("branch:codex/done", ["*"])
        receipt = reserve(plan, run)
        self.assertEqual("running", receipt["phase"])
        self.assertEqual(
            "branch:codex/done", run["attempt_log"][-1]["node_dispatch"]["target"]
        )
        record(plan, run, "pass")
        self.assertEqual([], validate_current_plan_run(plan, run))

    def test_cleanup_node_without_target_is_rejected_only_from_0_55(self) -> None:
        # PLAN-only validation (also run on archived candidates) never checks
        # this; validate_run checks it for 0.55.0+ RUNs only.
        for ref in sorted(EXACT_TARGET_LIFECYCLE_ACTIONS):
            with self.subTest(ref=ref):
                plan, run = lifecycle_pair(None, ["*"], ref=ref)
                message = (
                    "plan.graph.nodes[7].target: "
                    f"{ref} requires an exact non-wildcard authorization target"
                )
                self.assertNotIn(message, validate_plan(plan))
                set_required_version(run, "0.54.5")
                self.assertNotIn(message, validate_run(plan, run))
                set_required_version(run, "0.55.0")
                self.assertIn(message, validate_run(plan, run))

    def test_selector_never_dispatches_cleanup_node_without_target(self) -> None:
        plan, run = lifecycle_pair(None, ["*"])
        node = plan["graph"]["nodes"][-1]
        missions = {mission["id"]: mission for mission in plan["missions"]}
        self.assertIn(
            "action_not_authorized", _dispatch_reasons(node, None, plan, run, missions)
        )
        node["target"] = "branch:codex/done"
        self.assertNotIn(
            "action_not_authorized", _dispatch_reasons(node, None, plan, run, missions)
        )

    def test_reserve_refuses_protected_branch_under_wildcard_grant(self) -> None:
        plan, run = lifecycle_pair("branch:main", ["*"])
        with self.assertRaisesRegex(ManifestError, "action_not_authorized"):
            reserve(plan, run)

    def test_default_branch_protection_ignores_case(self) -> None:
        run = {"observed": {"git": {"default_branch": "master"}}}
        for target in ("branch:Master", "branch:refs/heads/MASTER", "branch:master"):
            with self.subTest(target=target):
                self.assertTrue(is_protected_branch_target(run, target))
        self.assertFalse(is_protected_branch_target(run, "branch:master2"))
        self.assertFalse(is_protected_branch_target(run, "branch:codex/done"))

    def test_wildcard_reservation_cannot_pass_but_can_block(self) -> None:
        plan, run = lifecycle_pair(None, ["*"])
        reserve_legacy_wildcard(run)
        with self.assertRaisesRegex(ManifestError, "requires an exact PLAN target"):
            record(plan, run, "pass", attempt_id="ATT-LEGACY")
        receipt = record(plan, run, "blocked", attempt_id="ATT-LEGACY")
        self.assertEqual("blocked", receipt["phase"])

    def test_wildcard_cleanup_pass_is_rejected_only_from_0_55(self) -> None:
        # A RUN closed under 0.54.5 may hold a "*" cleanup PASS recorded
        # before the rule existed; it must still validate.
        plan, run = lifecycle_pair(None, ["*"])
        reserve_legacy_wildcard(run)
        run["graph_state"]["node_states"][NODE_ID].update(
            {"phase": "succeeded", "last_outcome": "pass"}
        )
        run["attempt_log"][-1]["result"] = "pass"
        run["status"] = "complete"
        message = (
            "run.attempt_log[0].node_dispatch.target: "
            "delete_branches PASS requires an exact recorded target, not *"
        )
        set_required_version(run, "0.54.5")
        old_errors = validate_run(plan, run)
        set_required_version(run, "0.55.0")
        new_errors = validate_run(plan, run)
        # Other version gates fire on this fixture at both versions; only the
        # cleanup rule differs.
        self.assertNotIn(message, old_errors)
        self.assertIn(message, new_errors)


if __name__ == "__main__":
    unittest.main()
