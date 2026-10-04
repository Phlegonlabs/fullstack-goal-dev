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
from harness_manifest import validate_plan  # noqa: E402
from harness_manifest import _validate_verifier_executions  # noqa: E402
from manifest_fixtures import valid_plan  # noqa: E402
from manifest_fixtures import (  # noqa: E402
    manifest_markdown,
    retained_gate_execution,
    task as task_fixture,
    valid_run,
)
from platform_delivery_contract import (  # noqa: E402
    platform_delivery_shape_errors,
    validate_feature_acceptance,
    validate_platform_delivery,
)
from harness_contract_join import validate_frozen_contract_joins  # noqa: E402
import harness_contract_join as harness_contract_join_module  # noqa: E402
from select_ready_nodes import _incoming, _logical_reasons  # noqa: E402
from verifier_runtime import _validated_inputs  # noqa: E402
from render_review_packet import _relevant_acceptance_mappings  # noqa: E402
from validate_harness_plan import main as validate_plan_cli  # noqa: E402
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
        if "REQ-001" not in mission["trace_ids"]:
            mission["trace_ids"].append("REQ-001")
        if "ARCH-001" not in mission["trace_ids"]:
            mission["trace_ids"].append("ARCH-001")
        task = mission["tasks"][0]
        if "REQ-001" not in task["trace_ids"]:
            task["trace_ids"].append("REQ-001")
        if "ARCH-001" not in task["trace_ids"]:
            task["trace_ids"].append("ARCH-001")
            for row in task["acceptance_matrix"]:
                if "ARCH-001" not in row["trace_ids"]:
                    row["trace_ids"].append("ARCH-001")
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


def add_ui_surface(
    plan: dict[str, object],
    *,
    surface_id: str,
    release_surface: str,
    owner_mission: str,
) -> dict[str, object]:
    """Add one PLAN surface and an explicit owner trace to mission and task."""

    surface = {
        "id": surface_id,
        "trace_ids": [f"REQ-{owner_mission[-1]}"],
        "route": f"/{surface_id.lower()}",
        "breakpoints": ["390", "768"],
        "states": ["ready"],
        "evidence_gate": "required",
        "release_surface": release_surface,
    }
    plan["ui_surfaces"].append(surface)
    mission = plan["missions"][int(owner_mission[-1]) - 1]
    mission["trace_ids"].append(surface_id)
    for task in mission["tasks"]:
        task["trace_ids"].append(surface_id)
    return surface


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
        errors = validate_feature_acceptance(
            plan,
            feature_test_authority={"PRD-001": {"TEST-001", "TEST-REGRESSION"}},
        )
        self.assertEqual([], errors)
        plan["traces"][0]["acceptance_gate_ids"] = []
        errors = validate_feature_acceptance(
            plan,
            feature_test_authority={"PRD-001": {"TEST-001", "TEST-REGRESSION"}},
        )
        self.assertTrue(
            any("must not be empty" in item for item in errors),
            errors,
        )

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
        errors = validate_feature_acceptance(
            mapped,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertEqual([], errors)

        omitted = copy.deepcopy(mapped)
        omitted["final_gates"][0]["acceptance_test_ids"] = ["TEST-001", "TEST-002"]
        errors = validate_feature_acceptance(
            omitted,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertTrue(any("TEST-REGRESSION" in item for item in errors), errors)

        invalid = copy.deepcopy(mapped)
        invalid["final_gates"][0]["acceptance_test_ids"].append("TEST-UNLISTED")
        errors = validate_feature_acceptance(
            invalid,
            feature_test_authority={
                "PRD-001": {"TEST-001", "TEST-002", "TEST-REGRESSION"}
            },
        )
        self.assertTrue(any("TEST-UNLISTED" in item for item in errors), errors)

    def test_combined_feature_and_platform_metadata_is_not_rejected(self) -> None:
        plan = platform_plan()
        add_feature_gate(plan)
        self.assertEqual([], validate_plan(plan))
        self.assertEqual(
            [],
            validate_feature_acceptance(
                plan,
                feature_test_authority={
                    "REQ-001": {
                        "TEST-001",
                        "TEST-002",
                        "TEST-M1-01",
                        "TEST-M1-02",
                    }
                },
            ),
        )

    def test_marked_not_required_contract_requires_feature_gates(self) -> None:
        plan = platform_plan()
        plan["traces"][0]["id"] = "PRD-001"
        plan["missions"][0]["trace_ids"][0] = "PRD-001"
        for task_entry in plan["missions"][0]["tasks"]:
            task_entry["trace_ids"][0] = "PRD-001"
            for row in task_entry["acceptance_matrix"]:
                row["trace_ids"][0] = "PRD-001"
        plan.pop("platform_delivery")
        errors = validate_platform_delivery(plan, contract(mode="not_required"))
        self.assertTrue(
            any("requires acceptance gates" in item for item in errors),
            errors,
        )

    def test_unmarked_historical_prd_feature_remains_compatible(self) -> None:
        plan = platform_plan()
        plan["traces"][0]["id"] = "PRD-001"
        plan["missions"][0]["trace_ids"][0] = "PRD-001"
        for task_entry in plan["missions"][0]["tasks"]:
            task_entry["trace_ids"][0] = "PRD-001"
            for row in task_entry["acceptance_matrix"]:
                row["trace_ids"][0] = "PRD-001"
        plan.pop("platform_delivery")
        self.assertEqual(
            [],
            validate_feature_acceptance(
                plan,
                feature_test_authority={"PRD-001": {"TEST-001"}},
            ),
        )

class UiStageOwnershipTests(unittest.TestCase):
    def assert_error(self, plan: dict[str, object], fragment: str) -> None:
        errors = validate_platform_delivery(plan, contract())
        self.assertTrue(
            any(fragment in item for item in errors),
            f"expected {fragment!r} in {errors!r}",
        )

    def test_explicit_ui_owner_must_match_its_stage(self) -> None:
        plan = platform_plan()
        add_ui_surface(
            plan,
            surface_id="UI-WEB",
            release_surface="web-app",
            owner_mission="M1",
        )
        add_ui_surface(
            plan,
            surface_id="UI-IOS",
            release_surface="ios-app",
            owner_mission="M2",
        )
        self.assertEqual([], validate_platform_delivery(plan, contract()))

        wrong = platform_plan()
        add_ui_surface(
            wrong,
            surface_id="UI-WEB",
            release_surface="web-app",
            owner_mission="M2",
        )
        self.assert_error(wrong, "wrong platform stage")

    def test_omitted_and_cross_stage_ui_owners_fail(self) -> None:
        omitted = platform_plan()
        surface = add_ui_surface(
            omitted,
            surface_id="UI-WEB",
            release_surface="web-app",
            owner_mission="M1",
        )
        for mission in omitted["missions"]:
            if "UI-WEB" in mission["trace_ids"]:
                mission["trace_ids"].remove("UI-WEB")
            for task in mission["tasks"]:
                if "UI-WEB" in task["trace_ids"]:
                    task["trace_ids"].remove("UI-WEB")
        surface["trace_ids"] = ["REQ-001"]
        self.assert_error(omitted, "no mission or effective-task trace owner")

        cross = platform_plan()
        add_ui_surface(
            cross,
            surface_id="UI-SHARED",
            release_surface="web-app",
            owner_mission="M1",
        )
        cross["missions"][1]["trace_ids"].append("UI-SHARED")
        cross["missions"][1]["tasks"][0]["trace_ids"].append("UI-SHARED")
        self.assert_error(cross, "cross platform stages")

    def test_superseded_task_trace_does_not_own_surface(self) -> None:
        plan = platform_plan()
        add_ui_surface(
            plan,
            surface_id="UI-WEB",
            release_surface="web-app",
            owner_mission="M1",
        )
        parent = plan["missions"][0]["tasks"][0]
        replacement = copy.deepcopy(parent)
        replacement["id"] = "M1/T03"
        replacement["parent_task"] = "M1/T01"
        parent["replaced_by"] = ["M1/T03"]
        plan["missions"][0]["tasks"].append(replacement)
        parent["trace_ids"].remove("UI-WEB")
        self.assertEqual([], validate_platform_delivery(plan, contract()))

    def test_shared_requirement_traces_do_not_infer_ui_ownership(self) -> None:
        plan = platform_plan()
        plan["ui_surfaces"].append(
            {
                "id": "UI-WEB",
                "trace_ids": ["REQ-001"],
                "route": "/web",
                "breakpoints": ["390", "768"],
                "states": ["ready"],
                "evidence_gate": "required",
                "release_surface": "web-app",
            }
        )
        self.assert_error(plan, "no mission or effective-task trace owner")


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

    def product_fixtures(self) -> tuple[str, str]:
        pdb_tests = (
            Path(__file__).resolve().parents[3]
            / "product-definition-builder" / "scripts" / "tests"
        )
        original_path = list(sys.path)
        if str(pdb_tests) not in sys.path:
            sys.path.insert(0, str(pdb_tests))
        try:
            from test_platform_delivery import (  # noqa: E402
                architecture as platform_architecture,
                prd as platform_prd,
                sequence,
            )
        finally:
            sys.path[:] = original_path
        return (
            platform_architecture(platform=sequence()),
            platform_prd(required=("TEST-001", "TEST-002")),
        )

    def not_required_architecture(self, status: str = "approved") -> str:
        pdb_tests = (
            Path(__file__).resolve().parents[3]
            / "product-definition-builder" / "scripts" / "tests"
        )
        original_path = list(sys.path)
        if str(pdb_tests) not in sys.path:
            sys.path.insert(0, str(pdb_tests))
        try:
            from test_platform_delivery import (  # noqa: E402
                architecture as platform_architecture,
                sequence,
            )
        finally:
            sys.path[:] = original_path
        stage_header = (
            "| Order | Stage | Release surfaces | Required TEST IDs | "
            "Completion signal |\n"
            "| --- | --- | --- | --- | --- |\n"
        )
        return platform_architecture(
            specifications=(("web-app", "hosted_web", "web"),),
            platform=sequence(
                mode="not_required — Fixture ships exactly one hosted surface",
                rows=stage_header,
                status=status,
            ),
        )

    def unmarked_architecture(self) -> str:
        pdb_tests = (
            Path(__file__).resolve().parents[3]
            / "product-definition-builder" / "scripts" / "tests"
        )
        original_path = list(sys.path)
        if str(pdb_tests) not in sys.path:
            sys.path.insert(0, str(pdb_tests))
        try:
            from test_platform_delivery import architecture as platform_architecture
        finally:
            sys.path[:] = original_path
        return platform_architecture()

    def add_planned_feature(self, plan: dict[str, object], prd: str) -> str:
        feature = {
            "id": "PRD-FEATURE",
            "source_ids": ["SRC-001"],
            "priority": "must",
            "requirement": "Complete the platform feature",
            "disposition": "planned",
            "rationale": None,
            "acceptance_gate_ids": ["final"],
        }
        plan["traces"].append(feature)
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
        plan["graph"]["edges"].append(
            {
                "id": "E-M1-REPAIR-FINAL",
                "kind": "dependency",
                "from": "N-M1",
                "to": "N-FINAL",
                "on_outcomes": ["pass"],
                "max_traversals": None,
            }
        )
        gate = plan["final_gates"][0]
        gate["acceptance_test_ids"] = sorted(
            set(gate["acceptance_test_ids"]) | {"TEST-FEATURE"}
        )
        return prd.replace(
            "| TEST-002 | Fixture obligation | integration | Yes | PRD-001 | "
            "Fixture signal passes |",
            "| TEST-002 | Fixture obligation | integration | Yes | PRD-001 | "
            "Fixture signal passes |\n"
            "| TEST-FEATURE | Feature works | integration | Yes | PRD-FEATURE | "
            "Feature passes |",
        )

    def materialized_platform_plan(
        self,
        root: Path,
        *,
        architecture: str,
        prd: str,
    ) -> dict[str, object]:
        plan = platform_plan()
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
                "notes": "platform fixture",
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
                "notes": "platform fixture",
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
                "notes": "platform fixture",
            },
        ]
        texts = {
            "docs/product/PRD.md": prd,
            "docs/product/architecture.md": architecture,
            "docs/product/stack-decisions.md": "# Stack\n",
        }
        for location, text in texts.items():
            path = root / location
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            source = next(
                item for item in plan["sources"] if item["location"] == location
            )
            source["content_sha256"] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        return plan

    def test_run_none_marked_platform_join_and_exact_byte_reuse(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            real_loader = harness_contract_join_module._load_platform_delivery_parser
            real_module = real_loader(
                harness_contract_join_module.sibling_builder_scripts_dir()
            )
            parser_calls: list[tuple[str, str, bool]] = []

            def parse(architecture_text: str, prd_text: str, *, require: bool):
                parser_calls.append((architecture_text, prd_text, require))
                return real_module.parse_platform_delivery(
                    architecture_text,
                    prd_text,
                    require=require,
                )

            spy_module = SimpleNamespace(parse_platform_delivery=parse)
            with patch(
                "harness_contract_join._load_platform_delivery_parser",
                return_value=spy_module,
            ):
                errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertEqual(1, len(parser_calls), errors)
        self.assertEqual(architecture, parser_calls[0][0])
        self.assertEqual(prd, parser_calls[0][1])
        self.assertTrue(parser_calls[0][2])
        self.assertFalse(
            any("unknown PLAN stage ID" in item for item in errors),
            errors,
        )
        self.assertFalse(
            any("is not reachable from previous platform completion" in item for item in errors),
            errors,
        )
        self.assertLessEqual(len(errors), 8, errors)

    def test_run_none_marked_unknown_stage_and_missing_handoff_fail(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            plan["platform_delivery"]["stages"][0]["id"] = "desktop"
            errors = validate_frozen_contract_joins(plan, root, run=None)

            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            plan["graph"]["edges"] = [
                edge
                for edge in plan["graph"]["edges"]
                if not (
                    edge["kind"] == "dependency"
                    and edge["from"] == "N-M1"
                    and edge["to"] == "N-M2"
                )
            ]
            errors.extend(validate_frozen_contract_joins(plan, root, run=None))
        self.assertTrue(
            any("unknown PLAN stage ID 'desktop'" in item for item in errors),
            errors,
        )
        self.assertTrue(
            any("is not reachable from previous platform completion" in item for item in errors),
            errors,
        )

    def test_legacy_pin_marked_platform_join_executes(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            _run = valid_run(plan)
            _run["runtime_capabilities"]["runtime_adapter"]["version_gate"][
                "required_harness_version"
            ] = "0.37.0"
            plan["graph"]["edges"] = [
                edge
                for edge in plan["graph"]["edges"]
                if not (
                    edge["kind"] == "dependency"
                    and edge["from"] == "N-M1"
                    and edge["to"] == "N-M2"
                )
            ]
            errors = validate_frozen_contract_joins(plan, root, run=_run)
        self.assertTrue(
            any("is not reachable from previous platform completion" in item for item in errors),
            errors,
        )

    def test_declared_mapping_missing_marker_and_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture="# Architecture\n",
                prd="# PRD\n",
            )
            errors = validate_frozen_contract_joins(plan, root, run=None)

            architecture_path = root / "docs/product/architecture.md"
            expected_hash = next(
                source["content_sha256"]
                for source in plan["sources"]
                if source["location"] == "docs/product/architecture.md"
            )
            architecture_path.write_text("# Drift\n", encoding="utf-8")
            errors.extend(validate_frozen_contract_joins(plan, root, run=None))
        self.assertTrue(
            any("requires platform-delivery/1" in item for item in errors),
            errors,
        )
        self.assertTrue(
            any(
                expected_hash in item
                and "frozen architecture bytes do not match content_sha256" in item
                for item in errors
            ),
            errors,
        )

    def test_public_combined_feature_and_platform_join_passes(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=self.add_planned_feature(platform_plan(), prd),
            )
            errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertFalse(any("platform delivery" in item for item in errors), errors)
        self.assertFalse(any("acceptance_gate_ids" in item for item in errors), errors)

    def test_marker_only_contract_is_adopted_without_mapping(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(root, architecture=architecture, prd=prd)
            plan.pop("platform_delivery")
            errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertTrue(
            any(
                "platform-delivery/1 requires PLAN platform_delivery stage mappings" in item
                for item in errors
            ),
            errors,
        )

    def test_adopted_contract_requires_approved_decision(self) -> None:
        architecture, prd = self.product_fixtures()
        draft_architecture = architecture.replace(
            "Decision status: approved", "Decision status: draft"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapped = self.materialized_platform_plan(
                root,
                architecture=draft_architecture,
                prd=prd,
            )
            mapped_errors = validate_frozen_contract_joins(mapped, root, run=None)

            marker_only = self.materialized_platform_plan(
                root,
                architecture=draft_architecture,
                prd=prd,
            )
            marker_only.pop("platform_delivery")
            marker_errors = validate_frozen_contract_joins(marker_only, root, run=None)

            unresolved = self.materialized_platform_plan(
                root,
                architecture=self.not_required_architecture("blocked"),
                prd=prd,
            )
            unresolved.pop("platform_delivery")
            unresolved_errors = validate_frozen_contract_joins(
                unresolved,
                root,
                run=None,
            )
        self.assertTrue(
            any("requires an approved platform contract" in item for item in mapped_errors),
            mapped_errors,
        )
        self.assertTrue(
            any("requires an approved decision" in item for item in marker_errors),
            marker_errors,
        )
        self.assertTrue(
            any("requires an approved decision" in item for item in unresolved_errors),
            unresolved_errors,
        )

    def test_commented_and_fenced_markers_remain_unmarked_legacy(self) -> None:
        _, prd = self.product_fixtures()
        architecture = (
            "<!-- Platform delivery contract: platform-delivery/1 -->\n\n"
            "```markdown\n"
            "## Platform Delivery Sequence\n"
            "Platform delivery contract: platform-delivery/1\n"
            "```\n\n"
            + self.unmarked_architecture()
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(root, architecture=architecture, prd=prd)
            plan.pop("platform_delivery")
            errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertFalse(
            any("platform-delivery/1 requires PLAN platform_delivery" in item for item in errors),
            errors,
        )

    def test_declared_prd_failures_return_structured_diagnostics(self) -> None:
        architecture, valid_prd = self.product_fixtures()
        invalid_utf8 = b"# PRD\n\xff\n\n## Test Obligations\n"
        cases = (
            ("omitted", "requires readable frozen PRD bytes"),
            ("duplicate", "requires exactly one frozen PRD source"),
            ("missing", "cannot read frozen PRD source"),
            ("hash mismatch", "bytes do not match content_sha256"),
            ("revision invalid", "source_revision must be a full Git SHA"),
            ("utf8 invalid", "adopted platform or feature authority requires readable"),
        )
        for case, fragment in cases:
            with self.subTest(case=case):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    if case == "utf8 invalid":
                        prd_path = root / "docs/product/PRD.md"
                        prd_path.parent.mkdir(parents=True)
                        prd_path.write_bytes(invalid_utf8)
                        plan = self.materialized_platform_plan(
                            root,
                            architecture=architecture,
                            prd=valid_prd,
                        )
                        source = plan["sources"][0]
                        source["content_sha256"] = hashlib.sha256(invalid_utf8).hexdigest()
                        prd_path.write_bytes(invalid_utf8)
                    else:
                        plan = self.materialized_platform_plan(
                            root,
                            architecture=architecture,
                            prd=valid_prd,
                        )
                    if case == "omitted":
                        plan["sources"] = [
                            source for source in plan["sources"]
                            if source["kind"] != "prd"
                        ]
                    elif case == "duplicate":
                        duplicate = copy.deepcopy(plan["sources"][0])
                        duplicate["id"] = "SRC-DUPLICATE"
                        plan["sources"].append(duplicate)
                    elif case == "missing":
                        (root / "docs/product/PRD.md").unlink()
                    elif case == "hash mismatch":
                        (root / "docs/product/PRD.md").write_text("# Changed\n", encoding="utf-8")
                    elif case == "revision invalid":
                        plan["sources"][0]["source_revision"] = "short"
                    plan.pop("platform_delivery")
                    errors = validate_frozen_contract_joins(plan, root, run=None)
                self.assertTrue(any(fragment in item for item in errors), errors)

    def test_declared_architecture_failures_return_structured_diagnostics(self) -> None:
        architecture, prd = self.product_fixtures()
        invalid_utf8 = b"# Architecture\n\xff\n"
        cases = (
            ("duplicate", "requires exactly one frozen architecture.md source"),
            ("missing", "cannot read frozen architecture source"),
            ("hash mismatch", "frozen architecture bytes do not match content_sha256"),
            ("revision invalid", "source_revision must be a full Git SHA"),
            ("utf8 invalid", "architecture: is not valid UTF-8"),
        )
        for case, fragment in cases:
            with self.subTest(case=case):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    plan = self.materialized_platform_plan(
                        root,
                        architecture=architecture,
                        prd=prd,
                    )
                    if case == "duplicate":
                        duplicate = copy.deepcopy(plan["sources"][1])
                        duplicate["id"] = "SRC-ARCH-DUPLICATE"
                        plan["sources"].append(duplicate)
                    elif case == "missing":
                        (root / "docs/product/architecture.md").unlink()
                    elif case == "hash mismatch":
                        (root / "docs/product/architecture.md").write_text(
                            "# Changed\n",
                            encoding="utf-8",
                        )
                    elif case == "revision invalid":
                        plan["sources"][1]["source_revision"] = "short"
                    elif case == "utf8 invalid":
                        architecture_path = root / "docs/product/architecture.md"
                        plan["sources"][1]["content_sha256"] = hashlib.sha256(
                            invalid_utf8
                        ).hexdigest()
                        architecture_path.write_bytes(invalid_utf8)
                    errors = validate_frozen_contract_joins(plan, root, run=None)
                self.assertTrue(any(fragment in item for item in errors), errors)

    def test_malformed_test_authority_fails_before_semantic_join(self) -> None:
        architecture, _prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapped = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd="# PRD\n",
            )
            mapped_errors = validate_frozen_contract_joins(mapped, root, run=None)

            marker_only = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd="# PRD\n",
            )
            marker_only.pop("platform_delivery")
            marker_errors = validate_frozen_contract_joins(marker_only, root, run=None)
        self.assertTrue(
            any(
                "canonical feature TEST authority failed safely" in item
                for item in mapped_errors
            ),
            mapped_errors,
        )
        self.assertTrue(
            any(
                "canonical feature TEST authority failed safely" in item
                for item in marker_errors
            ),
            marker_errors,
        )

    def test_platform_shape_failure_stops_before_semantic_traversal(self) -> None:
        for value in ("desktop", None, 7, []):
            with self.subTest(value=value):
                plan = platform_plan()
                plan["platform_delivery"]["stages"] = value
                shape_errors = platform_delivery_shape_errors(plan)
                self.assertTrue(shape_errors)
                semantic_errors = validate_platform_delivery(plan, contract())
                self.assertEqual(shape_errors, semantic_errors)

    def test_public_and_paired_routes_handle_invalid_platform_shape(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            plan["platform_delivery"]["stages"] = [None]
            public_errors = validate_frozen_contract_joins(plan, root, run=None)

            paired = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            paired["platform_delivery"]["stages"] = ["desktop"]
            paired_run = valid_run(paired)
            paired_run["runtime_capabilities"]["runtime_adapter"]["version_gate"][
                "required_harness_version"
            ] = "0.62.0"
            paired_errors = validate_frozen_contract_joins(
                paired,
                root,
                run=paired_run,
            )

            cli_plan_path = root / "PLAN.md"
            cli_plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            cli_plan["platform_delivery"]["stages"] = [None]
            cli_plan_path.write_text(
                manifest_markdown(
                    "## Harness Plan Manifest",
                    "harness_plan",
                    cli_plan,
                ),
                encoding="utf-8",
            )
            exit_code = validate_plan_cli([
                "--repo-root",
                str(root),
                "--plan",
                str(cli_plan_path),
            ])
        self.assertTrue(
            any("must contain exactly id" in item for item in public_errors),
            public_errors,
        )
        self.assertTrue(
            any("must contain exactly id" in item for item in paired_errors),
            paired_errors,
        )
        self.assertEqual(1, exit_code)

    def test_declared_architecture_materializes_once_on_failure(self) -> None:
        architecture, prd = self.product_fixtures()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = self.materialized_platform_plan(
                root,
                architecture=architecture,
                prd=prd,
            )
            architecture_path = root / "docs/product/architecture.md"
            architecture_path.write_text("# Changed\n", encoding="utf-8")
            real_resolver = harness_contract_join_module._resolve_source_bytes
            calls: list[str] = []

            def resolve(source, repo_root, *, label, strict=False):
                if label == "architecture":
                    calls.append(label)
                return real_resolver(
                    source,
                    repo_root,
                    label=label,
                    strict=strict,
                )

            with patch(
                "harness_contract_join._resolve_source_bytes",
                side_effect=resolve,
            ):
                errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertEqual(1, len(calls), errors)
        self.assertTrue(
            any("frozen architecture bytes do not match content_sha256" in item for item in errors),
            errors,
        )

    def test_unmarked_feature_metadata_is_optional_but_explicit_fields_join(self) -> None:
        plan, _run = self.join_plan()
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
            (root / "docs/product/PRD.md").write_bytes(prd)
            source = plan["sources"][0]
            source["content_sha256"] = hashlib.sha256(prd).hexdigest()
            legacy_errors = validate_frozen_contract_joins(plan, root, run=None)

            plan["traces"][-1]["acceptance_gate_ids"] = []
            explicit_errors = validate_frozen_contract_joins(plan, root, run=None)
        self.assertFalse(
            any("requires acceptance gates" in item for item in legacy_errors),
            legacy_errors,
        )
        self.assertTrue(
            any("must not be empty" in item for item in explicit_errors),
            explicit_errors,
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
