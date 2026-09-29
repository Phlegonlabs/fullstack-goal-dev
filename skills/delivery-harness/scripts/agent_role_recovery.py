#!/usr/bin/env python3
"""Resolve explicitly authorized availability-only recovery."""

from __future__ import annotations

import copy
from agent_role_bindings import (
    _native_driver,
    binding_for_runtime,
    resolve_runtime_binding,
)
from agent_role_contract import (
    LAUNCH_FALLBACK_KEYS,
    RUNTIME_AXES,
    role_contract_gate_enabled,
    _nonempty,
    worker_role,
)
from typing import (
    Any,
)


def fallback_runtime_binding(
    node: dict[str, Any],
    runtime: dict[str, Any],
    *,
    original_binding: dict[str, Any],
    fallback_evidence: dict[str, Any],
    new_attempt_id: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Resolve an explicitly declared fallback binding; never switch silently."""

    if not role_contract_gate_enabled(runtime):
        return None, ["fallback requires a 0.58+ role-contract RUN"]
    if not isinstance(original_binding, dict) or not isinstance(fallback_evidence, dict):
        return None, ["fallback requires a primary binding and explicit evidence"]
    original_role = original_binding.get("worker_role")
    original_policy = binding_for_runtime(runtime, original_role)
    if original_policy is None:
        return None, ["predecessor has no configured primary role binding"]
    target_role = original_policy.get("fallback_role")
    target_policy = binding_for_runtime(runtime, target_role)
    if target_policy is None:
        return None, ["predecessor fallback_role does not resolve to a configured binding"]
    evidence_keys = set(fallback_evidence)
    required_evidence_keys = set(LAUNCH_FALLBACK_KEYS)
    if evidence_keys != required_evidence_keys:
        return None, [
            "fallback evidence must contain exactly: "
            + ", ".join(sorted(required_evidence_keys))
        ]
    if (fallback_evidence.get("fallback_from_role") != worker_role(node)
            or not _nonempty(new_attempt_id)
            or not _nonempty(fallback_evidence.get("predecessor_attempt_id"))
            or new_attempt_id == fallback_evidence.get("predecessor_attempt_id")):
        return None, ["fallback requires the same logical role and a fresh attempt"]
    availability = fallback_evidence["availability"]
    if not isinstance(availability, dict) or set(availability) != {
        "classification", "observed_error", "policy_source"
    } or availability.get("classification") != "model_provider_unavailable":
        return None, ["fallback requires a positively classified model/provider availability error"]
    if not all(_nonempty(availability.get(key)) for key in ("observed_error", "policy_source")):
        return None, ["fallback requires actual error and policy evidence"]
    predecessor = fallback_evidence["predecessor"]
    if not isinstance(predecessor, dict) or set(predecessor) != {
        "worker_id", "stopped", "stop_evidence"
    } or predecessor.get("stopped") is not True:
        return None, ["fallback requires confirmed predecessor termination"]
    if not all(_nonempty(predecessor.get(key)) for key in ("worker_id", "stop_evidence")):
        return None, ["fallback requires an identified stopped predecessor"]
    partial = fallback_evidence["partial_work"]
    if (not isinstance(partial, dict) or set(partial) != {"status", "evidence"}
            or partial.get("status") not in ("none", "reconciled") or not _nonempty(partial.get("evidence"))):
        return None, ["fallback requires explicit partial-work reconciliation"]
    configured = fallback_evidence["configured_fallback"]
    if not isinstance(configured, dict) or set(configured) != {
        "role", "model_provider", "model", "reasoning_effort", "policy_source"
    }:
        return None, ["fallback requires its declared target mapping"]
    if (
        not _nonempty(configured.get("policy_source"))
        or configured.get("role") != target_role
        or configured.get("model_provider") != target_policy.get("model_provider")
        or configured.get("model") != target_policy.get("model")
        or configured.get("reasoning_effort") != target_policy.get("reasoning_effort")
    ):
        return None, ["configured fallback does not equal the declared target binding"]
    policy = node.get("runtime")
    host = runtime.get("runtime_adapter", {}).get("provider")
    if host not in (policy.get("allowed_providers", []) if isinstance(policy, dict) else []):
        return None, ["fallback host is not allowed by the PLAN node"]
    configured = policy.get("provider_options", {}).get(host, {}) if isinstance(policy, dict) else {}
    configured_model = configured.get("model") if isinstance(configured, dict) else None
    configured_effort = configured.get("reasoning_effort") if isinstance(configured, dict) else None
    if configured_model is not None and configured_model != target_policy.get("model"):
        return None, ["PLAN provider options conflict with the configured fallback model"]
    if configured_effort is not None and configured_effort != target_policy.get("reasoning_effort"):
        return None, ["PLAN provider options conflict with the configured fallback effort"]
    candidate = {
        "provider": host,
        "driver": (
            "external_bridge"
            if target_policy["kind"] == "external_bridge"
            else _native_driver(target_policy)
        ),
        "source": "external_bridge" if target_policy["kind"] == "external_bridge" else "host",
        "worker_role": original_role,
        "resolved_role": target_role,
        "fallback_from_role": original_role,
        "model_provider": target_policy["model_provider"],
        "native_agent_type": target_policy.get("native_agent_type"),
        "bridge_identity": target_policy.get("bridge_identity"),
        "model": target_policy.get("model"),
        "reasoning_effort": target_policy.get("reasoning_effort"),
        "option_source": "role_binding_default",
        "capability_probe": copy.deepcopy(target_policy.get("capability_probe", {})),
        "probe_session_id": target_policy.get("probe_session_id"),
    }
    candidate.update({key: target_policy[key] for key in RUNTIME_AXES})
    return candidate, []


def resolve_fallback_reservation(node: dict[str, Any], run: dict[str, Any],
                                 evidence: Any, new_attempt_id: str):
    """Resolve recovery only from an exact retained, stopped host failure."""
    from agent_failure_receipts import AVAILABILITY_CODES, read_failure_receipt

    runtime = run.get("runtime_capabilities", {})
    binding, issues = fallback_runtime_binding(
        node, runtime, original_binding=resolve_runtime_binding(node, runtime),
        fallback_evidence=evidence, new_attempt_id=new_attempt_id,
    )
    if issues:
        return None, issues
    kind = "mission" if node.get("kind") == "mission" else "review"
    candidates = run.get("workers" if kind == "mission" else "review_workers", [])
    predecessors = [w for w in candidates if isinstance(w, dict)
                    and w.get("worker_id") == evidence["predecessor"]["worker_id"]
                    and w.get("attempt_id") == evidence["predecessor_attempt_id"]
                    and (w.get("mission_id") == node.get("ref") if kind == "mission"
                         else w.get("node_id") == node.get("id"))]
    if len(predecessors) != 1 or predecessors[0].get("phase") not in ("worker_failed", "blocked"):
        return None, ["fallback requires one terminal predecessor for this node"]
    predecessor = predecessors[0]
    if predecessor.get("runtime_binding", {}).get("resolved_role") != worker_role(node):
        return None, ["fallback cannot chain from another fallback"]
    failure, issues = read_failure_receipt(run, predecessor, kind, predecessor.get("failure_receipt"))
    if issues:
        return None, issues
    if (failure["failure_classification"] != "model_provider_unavailable"
            or failure["error_code"] not in AVAILABILITY_CODES):
        return None, ["retained host failure is not explicit model/provider unavailability"]
    if (evidence["availability"]["observed_error"] != failure["observed_error"]
            or evidence["predecessor"]["stop_evidence"] != failure["termination_evidence"]
            or evidence["partial_work"] != failure["partial_work"]):
        return None, ["fallback evidence differs from the retained host failure"]
    return binding, []
