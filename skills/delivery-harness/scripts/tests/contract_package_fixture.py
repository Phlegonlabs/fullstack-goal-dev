"""Build the genuine current UI3/DS4 fixture used by golden-path tests."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


def current_package(root: Path, *, pin: str = "0.59.0") -> dict[str, Any]:
    """Return a validated ordinary-flow package and canonical paths."""

    saved_path = list(sys.path)
    if str(TESTS_DIR) not in sys.path:
        sys.path.insert(0, str(TESTS_DIR))
    try:
        import test_contract_source_binding as contract_fixture
    finally:
        sys.path[:] = saved_path

    fixture = object.__new__(contract_fixture.FrozenPackageJoinTests)
    plan, run, _view, _legacy = contract_fixture.FrozenPackageJoinTests.fixture(
        fixture, root, pin=pin
    )

    paths = {
        "prd": root / "docs/product/PRD.md",
        "architecture": root / "docs/product/architecture.md",
        "stack": root / "docs/product/stack-decisions.md",
        "ui": root / "docs/design/ui-design.md",
        "target": next(
            Path(root / row["location"])
            for row in plan["sources"]
            if row["kind"] == "approved ui target"
        ),
        "design_markdown": root / "docs/design/design-system.md",
        "design_json": root / "docs/design/design-system.json",
        "preview": root / "docs/design/design-system-preview.html",
    }
    design_json_id = next(
        row["id"] for row in plan["sources"] if row["kind"] == "design system json"
    )
    registry = json.loads(paths["design_json"].read_text(encoding="utf-8"))
    ds_trace_id = next(
        rule for rule in registry.get("signatureRules", []) if isinstance(rule, str)
    )
    if not any(trace.get("id") == ds_trace_id for trace in plan["traces"]):
        plan["traces"].append(
            {
                "id": ds_trace_id,
                "source_ids": [design_json_id],
                "priority": "must",
                "requirement": "Apply the registered design-system signature rule",
                "disposition": "planned",
                "rationale": None,
            }
        )
    for surface in plan["ui_surfaces"]:
        if ds_trace_id not in surface["trace_ids"]:
            surface["trace_ids"].append(ds_trace_id)

    plan["security_review"] = {
        "status": "required",
        "skill_slot": "code_security_verification",
        "reason": None,
    }
    from test_graph_orchestration import add_security_review

    add_security_review(plan)
    for mission in plan["missions"]:
        mission["write_scope"] = ["docs/README.md"]
        if ds_trace_id not in mission["trace_ids"]:
            mission["trace_ids"].append(ds_trace_id)
        for task in mission["tasks"]:
            task["write_scope"] = ["docs/README.md"]
            if ds_trace_id not in task["trace_ids"]:
                task["trace_ids"].append(ds_trace_id)
            for acceptance in task["acceptance_matrix"]:
                if ds_trace_id not in acceptance["trace_ids"]:
                    acceptance["trace_ids"].append(ds_trace_id)
    for node in plan["graph"]["nodes"]:
        if isinstance(node.get("review"), dict):
            node["review"]["scope"] = ["docs/README.md"]

    return {"plan": plan, "run": run, "paths": paths}
