#!/usr/bin/env python3
"""Focused tests for the platform-delivery PLAN and verifier joins."""

from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
import unittest


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from harness_core import _validate_verifier  # noqa: E402
from harness_manifest import _validate_verifier_executions  # noqa: E402
from manifest_fixtures import valid_plan  # noqa: E402
from manifest_fixtures import (  # noqa: E402
    retained_gate_execution,
    task as task_fixture,
    valid_run,
)
from platform_delivery_contract import (  # noqa: E402
    platform_delivery_shape_errors,
    validate_platform_delivery,
)
from harness_contract_join import validate_frozen_contract_joins  # noqa: E402
from select_ready_nodes import _incoming, _logical_reasons  # noqa: E402
from verifier_runtime import _validated_inputs  # noqa: E402
from render_review_packet import _relevant_acceptance_mappings  # noqa: E402
from delivery_acceptance_io import (  # noqa: E402
    AcceptanceError,
    parse_required_prd_test_authority,
)


def contract(mode: str = "whole_platform_sequential") -> SimpleNamespace:
    return SimpleNamespace(
        mode=mode,
        shared_arch_ids=("ARCH-001",),
        stages=(
            SimpleNamespace(
                id="web",
                order=1,
                surfaces=("web-app", "public-api"),
                test_ids=("TEST-001",),
            ),
            SimpleNamespace(
                id="ios",
                order=2,
                surfaces=("ios-app",),
                test_ids=("TEST-002",),
            ),
        ),
    )


def platform_plan() -> dict[str, object]:
    """A valid graph fixture mapped from web completion to iOS completion."""

    plan = valid_plan()
    plan["missions"][0]["trace_ids"].append("ARCH-001")
    for task in plan["missions"][0]["tasks"]:
        task["trace_ids"].append("ARCH-001")
    plan["traces"].append(
        {
            "id": "ARCH-001",
            "source_ids": ["SRC-002"],
            "priority": "must",
            "requirement": "Establish the shared platform interface",
            "disposition": "planned",
            "rationale": None,
        }
    )
    plan["platform_delivery"] = {
        "protocol": "platform-delivery/1",
        "stages": [
            {
                "id": "web",
                "mission_ids": ["M1"],
                "completion_mission_id": "M1",
                "integration_verifier_ids": ["integrate-m1"],
            },
            {
                "id": "ios",
                "mission_ids": ["M2"],
                "completion_mission_id": "M2",
                "integration_verifier_ids": ["integrate-m2"],
            },
        ],
    }
    plan["missions"][0]["integration_verifiers"][0]["acceptance_test_ids"] = ["TEST-001"]
    plan["missions"][1]["integration_verifiers"][0]["acceptance_test_ids"] = [
        "TEST-001",
        "TEST-002",
    ]
    plan["final_gates"][0]["acceptance_test_ids"] = ["TEST-001", "TEST-002"]
    return plan


def add_feature_gate(plan: dict[str, object]) -> None:
    """Give REQ-001 a dependency-only path from both carrying missions."""

    for index, mission in enumerate(plan["missions"]):
        task = mission["tasks"][0]
        task["trace_ids"].append("REQ-001")
        task["acceptance_matrix"].append(
            {
                "test_id": "TEST-001",
                "trace_ids": ["REQ-001"],
                "criterion": "The shared release regression passes",
            }
        )
        plan["graph"]["edges"].append(
            {
                "id": f"E-{mission['id']}-PLATFORM-FINAL",
                "kind": "dependency",
                "from": f"N-{mission['id']}",
                "to": "N-FINAL",
                "on_outcomes": ["pass"],
                "max_traversals": None,
            }
        )
    feature_tests = {
        row["test_id"]
        for mission in plan["missions"]
        for task in mission["tasks"]
        for row in task["acceptance_matrix"]
        if "REQ-001" in row["trace_ids"]
    }
    plan["final_gates"][0]["acceptance_test_ids"] = sorted(
        set(plan["final_gates"][0]["acceptance_test_ids"]) | feature_tests
    )
    plan["traces"][0]["acceptance_gate_ids"] = ["final"]


def three_platform_plan() -> dict[str, object]:
    """Build web -> iOS -> Android mappings with mission graph nodes."""

    plan = platform_plan()
    android_mission = {
        "id": "M3",
        "trace_ids": ["REQ-003"],
        "tasks": [task_fixture("M3", 1, "REQ-003", "src/c/one.py")],
        "integration_verifiers": [
            {
                "id": "integrate-m3",
                "cwd": ".",
                "argv": ["tool", "integration"],
                "pass_signal": "exit 0",
                "execution": {
                    "isolation": "host",
                    "parallel_safe": False,
                    "resources": [],
                },
                "acceptance_test_ids": ["TEST-001", "TEST-002", "TEST-003"],
            }
        ],
    }
    plan["missions"].append(android_mission)
    plan["graph"]["nodes"].append(
        {
            "id": "N-M3",
            "kind": "mission",
            "ref": "M3",
            "executor": "runtime_worker",
                "max_attempts": 2,
        }
    )
    plan["platform_delivery"]["stages"].append(
        {
            "id": "android",
            "mission_ids": ["M3"],
            "completion_mission_id": "M3",
            "integration_verifier_ids": ["integrate-m3"],
        }
    )
    plan["graph"]["edges"].append(
        {
            "id": "E-M2-M3",
            "kind": "dependency",
            "from": "N-M2",
            "to": "N-M3",
            "on_outcomes": ["pass"],
            "max_traversals": None,
        }
    )
    return plan


def three_stage_contract() -> SimpleNamespace:
    value = contract()
    return SimpleNamespace(
        mode=value.mode,
        shared_arch_ids=value.shared_arch_ids,
        stages=(
            *value.stages,
            SimpleNamespace(
                id="android",
                order=3,
                surfaces=("android-app",),
                test_ids=("TEST-003",),
            ),
        ),
    )


class PlatformPlanShapeTests(unittest.TestCase):
    def test_optional_shape_is_empty_and_malformed_shapes_fail(self) -> None:
        self.assertEqual([], platform_delivery_shape_errors(valid_plan()))
        plan = platform_plan()
        self.assertEqual([], platform_delivery_shape_errors(plan))

        plan["platform_delivery"]["extra"] = True
        self.assertTrue(
            any("must contain exactly" in item for item in platform_delivery_shape_errors(plan))
        )

    def test_reordered_stage_mapping_list_keeps_architecture_authority(self) -> None:
        plan = platform_plan()
        reversed_plan = copy.deepcopy(plan)
        reversed_plan["platform_delivery"]["stages"].reverse()
        contract_value = contract()
        self.assertEqual(
            validate_platform_delivery(plan, contract_value),
            validate_platform_delivery(reversed_plan, contract_value),
        )
        # Stage two still depends on stage one through the fixture graph.
        self.assertFalse(
            any(
                "is not reachable from previous platform completion" in item
                for item in validate_platform_delivery(reversed_plan, contract_value)
            )
        )


class PlatformMappingTests(unittest.TestCase):
    def assert_error(self, plan: dict[str, object], fragment: str) -> None:
        errors = validate_platform_delivery(plan, contract())
        self.assertTrue(
            any(fragment in item for item in errors),
            f"expected {fragment!r} in {errors!r}",
        )

    def test_valid_web_then_ios_and_reversed_architecture_orders(self) -> None:
        self.assertEqual([], validate_platform_delivery(platform_plan(), contract()))
        reversed_plan = platform_plan()
        reversed_plan["platform_delivery"]["stages"].reverse()
        reversed_plan["missions"][0]["trace_ids"].remove("ARCH-001")
        reversed_plan["missions"][1]["trace_ids"].append("ARCH-001")
        reversed_plan["missions"][0]["integration_verifiers"][0][
            "acceptance_test_ids"
        ] = ["TEST-001", "TEST-002"]
        reversed_plan["missions"][1]["integration_verifiers"][0][
            "acceptance_test_ids"
        ] = ["TEST-002"]
        for edge in reversed_plan["graph"]["edges"]:
            if edge["from"] == "N-M1" and edge["to"] == "N-M2":
                edge["from"], edge["to"] = edge["to"], edge["from"]
        reversed_contract = SimpleNamespace(
            mode="whole_platform_sequential",
            shared_arch_ids=("ARCH-001",),
            stages=(
                SimpleNamespace(
                    id="ios", order=1, surfaces=("ios-app",), test_ids=("TEST-002",)
                ),
                SimpleNamespace(
                    id="web",
                    order=2,
                    surfaces=("web-app", "public-api"),
                    test_ids=("TEST-001",),
                ),
            ),
        )
        self.assertEqual(
            [],
            validate_platform_delivery(reversed_plan, reversed_contract),
        )

    def test_unknown_duplicate_and_unmapped_missions_fail(self) -> None:
        plan = platform_plan()
        plan["platform_delivery"]["stages"][0]["mission_ids"].append("M99")
        self.assert_error(plan, "unknown mission 'M99'")

        duplicate = platform_plan()
        duplicate["platform_delivery"]["stages"][1]["mission_ids"].append("M1")
        self.assert_error(duplicate, "already assigned")

        unmapped = platform_plan()
        unmapped["ui_surfaces"].append(
            {
                "id": "UI-OTHER",
                "trace_ids": ["REQ-001"],
                "route": "/other",
                "breakpoints": ["390", "768"],
                "states": ["ready"],
                "evidence_gate": "required",
                "release_surface": "desktop-app",
            }
        )
        self.assert_error(unmapped, "release surfaces absent")

    def test_shared_foundation_must_start_first_stage(self) -> None:
        plan = platform_plan()
        plan["platform_delivery"]["stages"][0]["mission_ids"] = ["M2"]
        plan["platform_delivery"]["stages"][1]["mission_ids"].append("M1")
        self.assert_error(plan, "shared ARCH foundations missing")

        later_shared = platform_plan()
        later_shared["missions"][1]["trace_ids"].append("ARCH-001")
        self.assertEqual([], validate_platform_delivery(later_shared, contract()))

    def test_dependency_paths_are_the_only_stage_handoff(self) -> None:
        plan = platform_plan()
        plan["graph"]["edges"] = [
            edge
            for edge in plan["graph"]["edges"]
            if not (
                edge["kind"] == "dependency"
                and edge["from"] == "N-M1"
                and edge["to"] == "N-M2"
            )
        ]
        self.assert_error(plan, "is not reachable from previous platform completion")

        route_only = platform_plan()
        for edge in route_only["graph"]["edges"]:
            if edge["from"] == "N-M1" and edge["to"] == "N-M2":
                edge["kind"] = "route"
                edge["max_traversals"] = 1
        self.assert_error(route_only, "is not reachable from previous platform completion")

    def test_middle_stage_completion_requires_dependency_path(self) -> None:
        plan = platform_plan()
        android_mission = {
            "id": "M3",
            "trace_ids": ["REQ-003"],
            "integration_verifiers": [
                {
                    "id": "integrate-m3",
                    "cwd": ".",
                    "argv": ["tool", "integration"],
                    "pass_signal": "exit 0",
                    "acceptance_test_ids": ["TEST-001", "TEST-002", "TEST-003"],
                }
            ],
        }
        plan["missions"].append(android_mission)
        plan["graph"]["nodes"].append(
            {
                "id": "N-M3",
                "kind": "mission",
                "ref": "M3",
                "executor": "runtime_worker",
                "max_attempts": 2,
            }
        )
        plan["platform_delivery"]["stages"].append(
            {
                "id": "android",
                "mission_ids": ["M3"],
                "completion_mission_id": "M3",
                "integration_verifier_ids": ["integrate-m3"],
            }
        )
        plan["graph"]["edges"].append(
            {
                "id": "E-M2-M3",
                "kind": "route",
                "from": "N-M2",
                "to": "N-M3",
                "on_outcomes": ["pass"],
                "max_traversals": 1,
            }
        )
        android = SimpleNamespace(
            id="android", order=3, surfaces=("android-app",), test_ids=("TEST-003",)
        )
        value = contract()
        value.stages += (android,)
        errors = validate_platform_delivery(plan, value)
        self.assertTrue(
            any(
                "mission 'M3' is not reachable from previous platform completion 'M2'"
                in item
                for item in errors
            ),
            errors,
        )

    def test_raw_stage_ids_must_exactly_match_architecture(self) -> None:
        plan = platform_plan()
        plan["platform_delivery"]["stages"].pop(1)
        plan["platform_delivery"]["stages"].append(
            {
                "id": "android",
                "mission_ids": ["M1"],
                "completion_mission_id": "M1",
                "integration_verifier_ids": ["integrate-m1"],
            }
        )
        errors = validate_platform_delivery(plan, contract())
        self.assertTrue(any("unknown PLAN stage ID 'android'" in item for item in errors))
        self.assertTrue(any("architecture stage ID absent from PLAN: 'ios'" in item for item in errors))


class PlatformVerifierTests(unittest.TestCase):
    def assert_error(self, plan: dict[str, object], fragment: str) -> None:
        errors = validate_platform_delivery(plan, contract())
        self.assertTrue(
            any(fragment in item for item in errors),
            f"expected {fragment!r} in {errors!r}",
        )

    def test_completion_verifier_must_own_and_cover_upstream_tests(self) -> None:
        plan = platform_plan()
        plan["platform_delivery"]["stages"][1]["integration_verifier_ids"] = [
            "integrate-m1"
        ]
        self.assert_error(plan, "not owned by completion mission")

        coverage = platform_plan()
        coverage["missions"][1]["integration_verifiers"][0][
            "acceptance_test_ids"
        ] = ["TEST-002"]
        self.assert_error(coverage, "must cover the full upstream platform TEST set")

        fresh = platform_plan()
        fresh["missions"][1]["integration_verifiers"][0]["cache"] = {
            "mode": "session_exact",
            "environment_keys": [],
            "deterministic_local": True,
        }
        self.assert_error(fresh, "must run fresh")

    def test_extra_completion_test_requires_canonical_prd_authority(self) -> None:
        plan = platform_plan()
        plan["missions"][1]["integration_verifiers"][0][
            "acceptance_test_ids"
        ] = ["TEST-001", "TEST-002", "TEST-REGRESSION"]
        errors = validate_platform_delivery(
            plan,
            contract(),
            required_test_ids={"TEST-001", "TEST-002", "TEST-REGRESSION"},
        )
        self.assertFalse(any("non-required TEST IDs" in item for item in errors), errors)
        errors = validate_platform_delivery(
            plan,
            contract(),
            required_test_ids={"TEST-001", "TEST-002"},
        )
        self.assertTrue(any("TEST-REGRESSION" in item for item in errors), errors)

    def test_unrelated_integration_verifier_annotation_stays_optional(self) -> None:
        plan = platform_plan()
        plan["missions"][1]["integration_verifiers"].append(
            copy.deepcopy(plan["missions"][1]["integration_verifiers"][0])
        )
        unrelated = plan["missions"][1]["integration_verifiers"][-1]
        unrelated["id"] = "unrelated-m2"
        unrelated.pop("acceptance_test_ids")
        errors = validate_platform_delivery(plan, contract())
        self.assertFalse(any("must not be empty" in item for item in errors), errors)

    def test_final_platform_coverage_may_include_extra_required_tests(self) -> None:
        plan = platform_plan()
        plan["final_gates"][0]["acceptance_test_ids"] = [
            "TEST-001",
            "TEST-002",
            "TEST-SHARED",
        ]
        self.assertEqual([], validate_platform_delivery(plan, contract()))

        incomplete = platform_plan()
        incomplete["final_gates"][0]["acceptance_test_ids"] = ["TEST-001"]
        self.assert_error(incomplete, "TEST-002")


class FeatureGateTests(unittest.TestCase):
    def assert_error(self, plan: dict[str, object], fragment: str) -> None:
        errors = validate_platform_delivery(plan, contract())
        self.assertTrue(
            any(fragment in item for item in errors),
            f"expected {fragment!r} in {errors!r}",
        )

    def test_applicable_platform_trace_requires_mapping(self) -> None:
        plan = platform_plan()
        plan["traces"].append(
            {
                "id": "PRD-PLATFORM",
                "source_ids": ["SRC-001"],
                "priority": "must",
                "requirement": "Complete the platform feature",
                "disposition": "planned",
                "rationale": None,
            }
        )
        plan["missions"][0]["trace_ids"].append("PRD-PLATFORM")
        plan["missions"][0]["tasks"][0]["trace_ids"].append("PRD-PLATFORM")
        plan["missions"][0]["tasks"][0]["acceptance_matrix"].append(
            {
                "test_id": "TEST-001",
                "trace_ids": ["PRD-PLATFORM"],
                "criterion": "The shared release regression passes",
            }
        )
        self.assert_error(plan, "requires acceptance gates")

        mapped = copy.deepcopy(plan)
        mapped["graph"]["edges"].append(
            {
                "id": "E-M1-PLATFORM-FINAL",
                "kind": "dependency",
                "from": "N-M1",
                "to": "N-FINAL",
                "on_outcomes": ["pass"],
                "max_traversals": None,
            }
        )
        next(
            trace
            for trace in mapped["traces"]
            if trace["id"] == "PRD-PLATFORM"
        )["acceptance_gate_ids"] = ["final"]
        mapped["final_gates"][0]["acceptance_test_ids"] = [
            "TEST-M1-01",
            "TEST-M1-02",
            "TEST-001",
            "TEST-002",
        ]
        self.assertEqual([], validate_platform_delivery(mapped, contract()))

    def test_gate_test_coverage_and_dependency_are_enforced(self) -> None:
        plan = platform_plan()
        add_feature_gate(plan)
        plan["final_gates"][0]["acceptance_test_ids"] = ["TEST-002"]
        self.assert_error(plan, "canonical feature TEST obligation")

        route_only = platform_plan()
        add_feature_gate(route_only)
        route_only["graph"]["edges"] = [
            edge
            for edge in route_only["graph"]["edges"]
            if not (
                edge["from"] == "N-M2"
                and edge["to"] == "N-FINAL"
                and edge["kind"] == "dependency"
            )
        ]
        route_only["graph"]["edges"].append(
            {
                "id": "E-M2-PLATFORM-FINAL-ROUTE",
                "kind": "route",
                "from": "N-M2",
                "to": "N-FINAL",
                "on_outcomes": ["pass"],
                "max_traversals": 1,
            }
        )
        self.assert_error(route_only, "does not precede accepting gate")

    def test_conditional_or_nonmust_feature_gate_fails(self) -> None:
        plan = platform_plan()
        add_feature_gate(plan)
        plan["final_gates"][0]["selection"] = {
            "mode": "changed_files",
            "scopes": ["src/**"],
        }
        self.assert_error(plan, "must run fresh")

        nonmust = platform_plan()
        nonmust["traces"][0]["priority"] = "should"
        nonmust["traces"][0]["acceptance_gate_ids"] = ["final"]
        self.assert_error(nonmust, "only on planned must traces")

    def test_standalone_prd_feature_authority_is_enforced(self) -> None:
        plan = platform_plan()
        plan["traces"][0]["id"] = "PRD-001"
        plan["missions"][0]["trace_ids"][0] = "PRD-001"
        for task_entry in plan["missions"][0]["tasks"]:
            task_entry["trace_ids"][0] = "PRD-001"
            for row in task_entry["acceptance_matrix"]:
                row["trace_ids"][0] = "PRD-001"
        errors = validate_platform_delivery(
            plan,
            None,
            feature_test_authority={"PRD-001": {"TEST-001", "TEST-REGRESSION"}},
        )
        self.assertTrue(any("requires acceptance gates" in item for item in errors))

        mapped = copy.deepcopy(plan)
        for task_entry in mapped["missions"][0]["tasks"]:
            task_entry["acceptance_matrix"].append(
                {
                    "test_id": "TEST-REGRESSION",
                    "trace_ids": ["PRD-001"],
                    "criterion": "The required regression passes",
                }
            )
        for mission in mapped["missions"]:
            mapped["graph"]["edges"].append(
                {
                    "id": f"E-{mission['id']}-PRD-FINAL",
                    "kind": "dependency",
                    "from": f"N-{mission['id']}",
                    "to": "N-FINAL",
                    "on_outcomes": ["pass"],
                    "max_traversals": None,
                }
            )
        mapped["traces"][0]["acceptance_gate_ids"] = ["final"]
        mapped.pop("platform_delivery")
        mapped["final_gates"][0]["acceptance_test_ids"] = [
            "TEST-001",
            "TEST-002",
            "TEST-REGRESSION",
        ]
        errors = validate_platform_delivery(
            mapped,
            None,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertEqual([], errors)

        omitted = copy.deepcopy(mapped)
        omitted["final_gates"][0]["acceptance_test_ids"] = ["TEST-001", "TEST-002"]
        errors = validate_platform_delivery(
            omitted,
            None,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertTrue(any("TEST-REGRESSION" in item for item in errors), errors)

        invalid = copy.deepcopy(mapped)
        invalid["final_gates"][0]["acceptance_test_ids"].append("TEST-UNLISTED")
        errors = validate_platform_delivery(
            invalid,
            None,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertTrue(any("TEST-UNLISTED" in item for item in errors), errors)


class PlatformCompatibilityTests(unittest.TestCase):
    def test_unmarked_plan_is_legacy(self) -> None:
        self.assertEqual([], validate_platform_delivery(valid_plan(), None))

    def test_declared_mapping_requires_contract(self) -> None:
        self.assertTrue(
            any(
                "requires an approved platform-delivery/1" in item
                for item in validate_platform_delivery(platform_plan(), None)
            )
        )

    def test_not_required_rejects_stage_mapping(self) -> None:
        errors = validate_platform_delivery(platform_plan(), contract(mode="not_required"))
        self.assertTrue(
            any("cannot declare stage mappings" in item for item in errors),
            errors,
        )


class VerifierAnnotationTests(unittest.TestCase):
    def test_runtime_normalizes_and_retains_without_key_shape_change(self) -> None:
        plan = platform_plan()
        declaration = plan["missions"][1]["integration_verifiers"][0]
        declaration["acceptance_test_ids"] = ["TEST-002", "TEST-001"]
        declaration["execution"]["isolation"] = "host"
        declaration["execution"]["parallel_safe"] = False
        declaration["execution"].pop("sandbox", None)
        declaration["argv"] = [sys.executable, "integration"]
        context = {
            "run_id": "RUN",
            "plan_revision": 1,
            "plan_digest_sha256": "a" * 64,
            "graph_revision": 1,
            "batch_base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "changed_files": [],
            "trust_domain": "parent_local",
            "checkout_role": "integration",
            "checkout_dirty": False,
            "cache_safe": False,
            "layer": "mission_integration",
            "mission_id": "M2",
            "task_id": None,
            "attempt_id": None,
            "lease_id": None,
        }
        cwd, argv, normalized, key_inputs = _validated_inputs(
            declaration,
            context,
            Path("."),
            {},
        )
        self.assertEqual(cwd, Path(".").resolve())
        self.assertEqual(argv, declaration["argv"])
        self.assertEqual(normalized["acceptance_test_ids"], ["TEST-001", "TEST-002"])
        self.assertNotIn("acceptance_test_ids", key_inputs)

        errors: list[str] = []
        _validate_verifier(errors, "verifier", declaration)
        self.assertEqual([], errors)

        malformed = copy.deepcopy(declaration)
        malformed["acceptance_test_ids"] = ["TEST-001", "TEST-001"]
        errors = []
        _validate_verifier(errors, "verifier", malformed)
        self.assertTrue(any("duplicates" in item for item in errors))

    def test_retained_execution_annotation_must_match_plan(self) -> None:
        plan = platform_plan()
        declaration = plan["missions"][0]["integration_verifiers"][0]
        declaration["acceptance_test_ids"] = ["TEST-001"]
        run = valid_run(plan)
        execution = retained_gate_execution(
            plan,
            run,
            declaration,
            layer="mission_integration",
            execution_id="EXEC-ANNOTATED",
            mission_id="M1",
            head_sha=run["mission_states"]["M1"]["integrated_sha"],
        )
        run["verifier_executions"] = [execution]
        errors: list[str] = []
        _validate_verifier_executions(errors, plan, run)
        self.assertFalse(
            any("acceptance_test_ids" in item for item in errors),
            errors,
        )

        execution["verifier"]["acceptance_test_ids"] = ["TEST-002"]
        errors = []
        _validate_verifier_executions(errors, plan, run)
        self.assertTrue(
            any(
                "must exactly match the PLAN verifier declaration" in item
                for item in errors
            ),
            errors,
        )

        execution["verifier"]["acceptance_test_ids"] = [None]
        errors = []
        _validate_verifier_executions(errors, plan, run)
        self.assertTrue(
            any("must be a list of non-empty strings" in item for item in errors),
            errors,
        )


class RuntimePlatformHandoffTests(unittest.TestCase):
    def test_worker_pass_does_not_unlock_third_integration(self) -> None:
        plan = three_platform_plan()
        run = valid_run(plan)
        run["mission_states"]["M1"].update(
            {
                "phase": "integrated",
                "integration_gate": "PASS",
                "integrated_sha": "a" * 40,
            }
        )
        run["mission_states"]["M2"].update(
            {
                "phase": "worker_passed",
                "integration_gate": "planned",
                "integrated_sha": None,
            }
        )
        run["graph_state"]["node_states"]["N-M1"].update(
            {"phase": "succeeded", "last_outcome": "pass"}
        )

        node = next(item for item in plan["graph"]["nodes"] if item["id"] == "N-M3")
        before = _logical_reasons(node, plan, run, *_incoming(plan))
        self.assertIn("dependency_not_satisfied", before)

        run["mission_states"]["M2"].update(
            {
                "phase": "integrated",
                "integration_gate": "PASS",
                "integrated_sha": "b" * 40,
            }
        )
        run["graph_state"]["node_states"]["N-M2"].update(
            {"phase": "succeeded", "last_outcome": "pass"}
        )
        after = _logical_reasons(node, plan, run, *_incoming(plan))
        self.assertNotIn("dependency_not_satisfied", after)

    def test_three_integration_passes_retain_exact_mission_heads(self) -> None:
        plan = three_platform_plan()
        run = valid_run(plan)
        mission_heads = {
            "M1": "a" * 40,
            "M2": "b" * 40,
            "M3": "c" * 40,
        }
        for mission_id, head_sha in mission_heads.items():
            run["mission_states"][mission_id].update(
                {
                    "phase": "integrated",
                    "integration_gate": "PASS",
                    "integrated_sha": head_sha,
                }
            )
            declaration = plan["missions"][
                int(mission_id[-1]) - 1
            ]["integration_verifiers"][0]
            run["verifier_executions"].append(
                retained_gate_execution(
                    plan,
                    run,
                    declaration,
                    layer="mission_integration",
                    execution_id=f"EXEC-{mission_id}",
                    mission_id=mission_id,
                    head_sha=head_sha,
                )
            )

        errors: list[str] = []
        _validate_verifier_executions(errors, plan, run)
        self.assertFalse(
            any("must match the mission integrated_sha" in item for item in errors),
            errors,
        )

        wrong = next(
            execution
            for execution in run["verifier_executions"]
            if execution["mission_id"] == "M2"
        )
        wrong["context"]["head_sha"] = "d" * 40
        errors = []
        _validate_verifier_executions(errors, plan, run)
        self.assertTrue(
            any("must match the mission integrated_sha" in item for item in errors),
            errors,
        )


class FrozenSourceJoinTests(unittest.TestCase):
    def join_plan(self) -> tuple[dict[str, object], dict[str, object]]:
        plan = valid_plan()
        run = valid_run(plan)
        run["runtime_capabilities"]["runtime_adapter"]["version_gate"][
            "required_harness_version"
        ] = "0.62.0"
        plan["sources"] = [
            {
                "id": "SRC-001",
                "kind": "prd",
                "location": "docs/product/PRD.md",
                "owner": "owner",
                "status": "frozen",
                "content_sha256": "a" * 64,
                "source_revision": None,
                "staged_revision": None,
                "notes": "fixture",
            },
            {
                "id": "SRC-002",
                "kind": "architecture",
                "location": "docs/product/architecture.md",
                "owner": "owner",
                "status": "frozen",
                "content_sha256": "b" * 64,
                "source_revision": None,
                "staged_revision": None,
                "notes": "fixture",
            },
            {
                "id": "SRC-003",
                "kind": "stack decisions",
                "location": "docs/product/stack-decisions.md",
                "owner": "owner",
                "status": "frozen",
                "content_sha256": "c" * 64,
                "source_revision": None,
                "staged_revision": None,
                "notes": "fixture",
            },
        ]
        return plan, run

    def test_visible_malformed_marker_fails_before_ui_return(self) -> None:
        plan, run = self.join_plan()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            texts = {
                "docs/product/PRD.md": "# PRD\n",
                "docs/product/architecture.md": (
                    "# Architecture\n\n"
                    "Platform delivery contract: platform-delivery/1\n"
                ),
                "docs/product/stack-decisions.md": "# Stack\n",
            }
            for location, text in texts.items():
                path = root / location
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                source = next(
                    item
                    for item in plan["sources"]
                    if item["location"] == location
                )
                source["content_sha256"] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
            errors = validate_frozen_contract_joins(plan, root, run=run)
        self.assertTrue(
            any(
                "requires an active Platform Delivery Sequence" in item
                for item in errors
            ),
            errors,
        )

    def test_missing_canonical_platform_parser_fails_closed(self) -> None:
        plan, run = self.join_plan()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            texts = {
                "docs/product/PRD.md": "# PRD\n",
                "docs/product/architecture.md": "# Architecture\n",
                "docs/product/stack-decisions.md": "# Stack\n",
            }
            for location, text in texts.items():
                path = root / location
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
                source = next(
                    item
                    for item in plan["sources"]
                    if item["location"] == location
                )
                source["content_sha256"] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
            with patch(
                "harness_contract_join._load_platform_delivery_parser",
                return_value=None,
            ):
                errors = validate_frozen_contract_joins(plan, root, run=run)
        self.assertTrue(
            any("canonical parser is unavailable" in item for item in errors),
            errors,
        )

    def test_canonical_prd_authority_groups_required_tests(self) -> None:
        prd = b"""# PRD

## Test Obligations
| TEST ID | Obligation | Test type | Required | Upstream trace IDs | Expected signal |
| --- | --- | --- | --- | --- | --- |
| TEST-001 | Works | integration | Yes | PRD-001, PRD-002 | Signal passes |
| TEST-REGRESSION | Regression | integration | Yes | PRD-001 | Signal passes |
| TEST-OPTIONAL | Optional | integration | No | PRD-001 | Signal observed |
"""
        self.assertEqual(
            {
                "PRD-001": {"TEST-001", "TEST-REGRESSION"},
                "PRD-002": {"TEST-001"},
            },
            parse_required_prd_test_authority(prd),
        )
        with self.assertRaises(AcceptanceError):
            parse_required_prd_test_authority(b"# PRD\n")

    def test_headless_prd_feature_gate_is_checked_before_legacy_return(self) -> None:
        plan, run = self.join_plan()
        plan["traces"].append(
            {
                "id": "PRD-FEATURE",
                "source_ids": ["SRC-001"],
                "priority": "must",
                "requirement": "Complete the headless feature",
                "disposition": "planned",
                "rationale": None,
            }
        )
        plan["missions"][0]["trace_ids"].append("PRD-FEATURE")
        feature_task = plan["missions"][0]["tasks"][0]
        feature_task["trace_ids"].append("PRD-FEATURE")
        feature_task["acceptance_matrix"].append(
            {
                "test_id": "TEST-FEATURE",
                "trace_ids": ["PRD-FEATURE"],
                "criterion": "The feature result is observable",
            }
        )
        prd = b"""# PRD

## Test Obligations
| TEST ID | Obligation | Test type | Required | Upstream trace IDs | Expected signal |
| --- | --- | --- | --- | --- | --- |
| TEST-FEATURE | Feature works | integration | Yes | PRD-FEATURE | Result passes |
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs/product").mkdir(parents=True)
            architecture = root / "docs/product/architecture.md"
            architecture.write_text("# Architecture\n", encoding="utf-8")
            stack = root / "docs/product/stack-decisions.md"
            stack.write_text("# Stack\n", encoding="utf-8")
            prd_path = root / "docs/product/PRD.md"
            prd_path.write_bytes(prd)
            source = plan["sources"][0]
            source["content_sha256"] = hashlib.sha256(prd).hexdigest()
            errors = validate_frozen_contract_joins(plan, root, run=run)
        self.assertTrue(
            any("requires acceptance gates" in item for item in errors),
            errors,
        )


class ReviewPacketMappingTests(unittest.TestCase):
    def test_relevant_gate_to_test_mapping_is_bounded(self) -> None:
        plan = platform_plan()
        plan["missions"][0]["tasks"][0]["acceptance_matrix"].append(
            {
                "test_id": "TEST-001",
                "trace_ids": ["REQ-001"],
                "criterion": "The shared release regression passes",
            }
        )
        missions = list(plan["missions"])
        mappings, truncated = _relevant_acceptance_mappings(plan, missions)
        self.assertFalse(truncated)
        self.assertEqual(
            [
                {
                    "layer": "final",
                    "verifier_id": "final",
                    "acceptance_test_ids": ["TEST-001", "TEST-002"],
                },
                {
                    "layer": "mission_integration",
                    "mission_id": "M1",
                    "verifier_id": "integrate-m1",
                    "acceptance_test_ids": ["TEST-001"],
                },
                {
                    "layer": "mission_integration",
                    "mission_id": "M2",
                    "verifier_id": "integrate-m2",
                    "acceptance_test_ids": ["TEST-001", "TEST-002"],
                },
            ],
            mappings,
        )


if __name__ == "__main__":
    unittest.main()
