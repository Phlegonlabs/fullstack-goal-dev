"""Canonical fixtures for the role routing and receipt tests."""
import copy
import hashlib
import json
from pathlib import Path
from agent_result_receipts import payload_digest
from manifest_fixtures import (
    authorize_action, authorize_execution, native_capability_probe,
    plan_digest, sandbox_observation,
)


def capability(name: str) -> dict[str, str]:
    return {
        "status": "available",
        "evidence": f"observed {name} in a fresh probe",
        "probe_id": f"probe-{name}",
    }


def retain_failure(directory, worker, evidence, *, session=None, error_code="model_unavailable"):
    """A normalized parent-retained host failure, never child self-attestation."""
    payload = {
        "worker_id": worker["worker_id"], "attempt_id": worker["attempt_id"],
        "failure_classification": evidence["availability"]["classification"],
        "error_code": error_code, "observed_error": evidence["availability"]["observed_error"],
        "stopped": evidence["predecessor"]["stopped"],
        "termination_evidence": evidence["predecessor"]["stop_evidence"],
        "partial_work": evidence["partial_work"],
    }
    raw = json.dumps({"schema_version": 1, "session_id": session, "payload": payload}).encode()
    path = Path(directory) / (worker["worker_id"] + "-host-failure.json")
    path.write_bytes(raw)
    return {"kind": "runtime_failed" if session else "launch_failed", "session_id": session,
            "source_ref": str(path), "source_sha256": hashlib.sha256(raw).hexdigest(),
            "payload_sha256": payload_digest(payload)}


def bridge_binding(role: str = "contract_writer") -> dict[str, object]:
    return {
        "kind": "external_bridge",
        "bridge_identity": "host-bridge-1",
        "model_provider": "claude_code",
        "model": "claude-opus-5-5",
        "reasoning_effort": "high",
        "capability_probe": {
            "external_runtime_invoke": capability("invoke"),
            "external_terminal_result": capability("result"),
        },
        "probe_session_id": "bridge-probe-1",
        "worker_runtime": "subagent",
        "workspace_mode": "parent_managed_worktree",
        "completion_channel": "agent_result",
        "fallback_role": "backend_worker",
    }


def native_reviewer_binding() -> dict[str, object]:
    return {
        "kind": "native",
        "native_agent_type": "native-subagent",
        "model_provider": "codex",
        "model": None,
        "reasoning_effort": "xhigh",
        "capability_probe": {
            "direct_subagent_spawn": capability("spawn"),
            "direct_agent_result": capability("result"),
        },
        "worker_runtime": "subagent",
        "workspace_mode": "shared_checkout",
        "completion_channel": "agent_result",
    }


def native_writer_binding() -> dict[str, object]:
    binding = native_reviewer_binding()
    binding["native_agent_type"] = "native-writer"
    binding["model"] = "gpt-6-sol"
    binding["reasoning_effort"] = "high"
    binding["workspace_mode"] = "parent_managed_worktree"
    return binding


def refresh_plan_binding(
    plan: dict[str, object],
    run: dict[str, object],
) -> dict[str, object]:
    digest = plan_digest(plan)
    run["plan"]["digest_sha256"] = digest
    run["observed"]["sandbox"] = sandbox_observation(plan)
    return run


def add_security_review(
    plan: dict[str, object],
    run: dict[str, object],
) -> None:
    """Give the fixture one valid integration security review for 0.58 gates."""

    model_review = next(
        item
        for item in plan["graph"]["nodes"]
        if item["id"] == "N-REVIEW-M1"
    )
    node = copy.deepcopy(model_review)
    node.update(
        {
            "id": "N-SECURITY-REVIEW",
            "ref": "batch",
            "allowed_outcomes": ["pass", "retryable_failure", "blocked", "contract_gap"],
        }
    )
    node["review"] = {
        "stage": "integration",
        "type": "security",
        "lineage_id": "REVIEW-SECURITY",
        "mission_ids": ["M1", "M2"],
        "scope": ["src/a/**", "src/ab/**"],
        "required_evidence": ["reviewed_sha", "findings"],
    }
    node["runtime"]["worker_role"] = "reviewer"
    plan["graph"]["nodes"].append(node)
    for source in ("N-REVIEW-PASS-M1", "N-REVIEW-PASS-M2"):
        edge_id = f"E-{source}-SECURITY"
        plan["graph"]["edges"].append(
            {
                "id": edge_id,
                "kind": "dependency",
                "from": source,
                "to": node["id"],
                "on_outcomes": ["pass"],
                "max_traversals": None,
            }
        )
        run["graph_state"]["edge_states"][edge_id] = {
            "status": "dormant",
            "traversals": 0,
            "source_attempt_id": None,
        }
    plan["required_reviews"].append("security")
    plan["security_review"] = {
        "status": "required",
        "skill_slot": "code_security_verification",
        "reason": None,
        "required_checks": [],
    }
    run["graph_state"]["node_states"][node["id"]] = {
        "phase": "dormant",
        "attempts": 0,
        "last_attempt_id": None,
        "last_outcome": None,
        "bound_worker_id": None,
        "blockers": [],
    }
    run["review_lineages"]["REVIEW-SECURITY"] = {
        "review_type": "security",
        "mission_ids": ["M1", "M2"],
        "base_allowance": 2,
        "additional_allowance": 0,
        "consumed_attempts": 0,
        "failure_families": [],
        "owner_decisions": [],
    }


def configure_role_run(
    plan: dict[str, object],
    run: dict[str, object],
) -> dict[str, object]:
    run["runtime_capabilities"].update(
        {
            "worker_runtime": "subagent",
            "workspace_mode": "parent_managed_worktree",
            "completion_channel": "agent_result",
            "max_parallel_workers": 2,
            "runtime_adapter": {
                "provider": "codex",
                "available_drivers": ["subagents", "sequential_parent"],
                "detection_source": "observed",
                "capability_probe": native_capability_probe(subagents=True),
                "role_bindings": {
                    "contract_writer": bridge_binding(),
                    "backend_worker": native_writer_binding(),
                    "reviewer": native_reviewer_binding(),
                },
                "version_gate": {
                    **run["runtime_capabilities"]["runtime_adapter"]["version_gate"],
                    "harness_version": "0.58.0",
                    "required_harness_version": "0.58.0",
                },
            },
        }
    )
    run["observed"]["runtime"].update(
        {
            "available_worker_slots": 2,
            "isolation_capacity": 2,
        }
    )
    plan["graph"]["entry_nodes"] = ["N-M1", "N-M2"]
    plan["graph"]["edges"] = [
        edge
        for edge in plan["graph"]["edges"]
        if (edge["from"], edge["to"]) != ("N-M1", "N-M2")
    ]
    run["graph_state"]["edge_states"].pop("E-M1-M2", None)
    for node in plan["graph"]["nodes"]:
        if node["kind"] == "mission":
            node["runtime"]["worker_role"] = "contract_writer"
        elif node["executor"] == "runtime_worker":
            node["runtime"]["worker_role"] = "reviewer"
    plan["graph"]["nodes"][3]["runtime"]["worker_role"] = "backend_worker"
    add_security_review(plan, run)
    return refresh_plan_binding(plan, run)


def authorize_selection(
    run: dict[str, object],
    *,
    invoke: bool = True,
    spawn: bool = True,
    targets: list[str] | None = None,
) -> None:
    mission_ids = sorted(run["mission_states"])
    authorize_execution(run, mission_ids, status="running")
    local_targets = targets or ["*"]
    if spawn:
        authorize_action(run, "spawn_subagents", mission_ids, list(local_targets))
    if invoke:
        authorize_action(run, "invoke_external_runtime", mission_ids, list(local_targets))
    for action in (
        "create_local_worktrees",
        "create_local_branches",
        "create_local_commits",
        "integrate_locally",
    ):
        authorize_action(run, action, mission_ids, ["*"])
