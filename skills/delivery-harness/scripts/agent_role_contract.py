#!/usr/bin/env python3
"""Version gates, logical role identities and shared field names."""

from __future__ import annotations

import re
from harness_schema import (
    is_valid_provider_id,
    run_required_harness_version,
    version_at_least,
)
from typing import (
    Any,
)


ROLE_CONTRACT_VERSION = (0, 58, 0)


WORKER_ROLES = {
    "backend_worker",
    "code_architect",
    "code_explorer",
    "frontend_worker",
    "implementer",
    "market_researcher",
    "reviewer",
    "test_runner",
}


WORKER_ROLE_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


RUNTIME_KINDS = {"native", "external_bridge"}


RUNTIME_AXES = ("worker_runtime", "workspace_mode", "completion_channel")


WORKER_RUNTIME_KINDS = {"parent", "subagent", "app_task"}


WORKSPACE_KINDS = {"shared_checkout", "parent_managed_worktree", "app_managed_worktree"}


COMPLETION_KINDS = {"agent_result", "thread_poll", "report_file", "user_relay"}


NATIVE_CAPABILITIES = {
    "direct_subagent_spawn",
    "direct_agent_result",
    "app_project_list",
    "app_thread_create",
    "app_thread_read",
    "app_thread_message",
    "app_thread_wait",
    "app_managed_worktree",
}


BRIDGE_CAPABILITIES = {"external_runtime_invoke", "external_terminal_result"}


KNOWN_CAPABILITIES = NATIVE_CAPABILITIES | BRIDGE_CAPABILITIES


RUNTIME_BINDING_KEYS = {
    "provider",
    "driver",
    "source",
    "model",
    "reasoning_effort",
    "option_source",
    "worker_role",
    "resolved_role",
    "fallback_from_role",
    "model_provider",
    "native_agent_type",
    "bridge_identity",
    "capability_probe",
    "probe_session_id",
    *RUNTIME_AXES,
}


LAUNCH_RECORD_KEYS = {
    "plan_revision",
    "plan_digest_sha256",
    "assignment_kind",
    "assignment_id",
    "node_id",
    "attempt_id",
    "worker_id",
    "worker_role",
    "resolved_role",
    "source_sha",
    "base_sha",
    "reviewed_sha",
    "worker_runtime",
    "workspace_mode",
    "completion_channel",
    "requested_model",
    "requested_reasoning_effort",
    "model_provider",
    "model",
    "reasoning_effort",
    "session_id",
    "launch_observation",
    "host_observation",
}


LAUNCH_FALLBACK_KEYS = {
    "fallback_from_role",
    "availability",
    "predecessor",
    "partial_work",
    "configured_fallback",
    "predecessor_attempt_id",
}


def role_contract_enabled(run: Any) -> bool:
    """True only for RUN-v11 pinned to the first role-contract release."""

    return (
        isinstance(run, dict)
        and run.get("schema_version") == 11
        and version_at_least(
            run_required_harness_version(run), ROLE_CONTRACT_VERSION
        )
    )


def role_contract_gate_enabled(runtime: Any) -> bool:
    """Check the adapter gate when only runtime_capabilities are in scope."""

    adapter = runtime.get("runtime_adapter") if isinstance(runtime, dict) else None
    gate = adapter.get("version_gate") if isinstance(adapter, dict) else None
    return version_at_least(
        gate.get("required_harness_version") if isinstance(gate, dict) else None,
        ROLE_CONTRACT_VERSION,
    )


def worker_role(node: Any) -> str | None:
    """Read the logical role declared by a runtime_worker graph node."""

    runtime = node.get("runtime") if isinstance(node, dict) else None
    value = runtime.get("worker_role") if isinstance(runtime, dict) else None
    return value if is_worker_role_id(value) else None


def mandatory_worker_role(node: Any, mission: Any = None, ui_impact: Any = None) -> str | None:
    """Return the role that cannot be silently replaced on this node."""

    if not isinstance(node, dict) or node.get("executor") != "runtime_worker":
        return None
    if node.get("kind") == "verifier":
        return "reviewer"
    if node.get("kind") == "mission" and isinstance(mission, dict):
        required_skills = mission.get("required_skills", [])
        if isinstance(required_skills, list) and (
            "ui-design-builder" in required_skills
            or "frontend-design" in required_skills
            or ui_impact in ("style", "structure", "both")
        ):
            return "frontend_worker"
    return worker_role(node)


def is_worker_role_id(value: Any) -> bool:
    """Accept portable standard roles and a validated host-defined role name."""

    return isinstance(value, str) and WORKER_ROLE_RE.fullmatch(value) is not None


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def binding_is_role_bound(binding: Any) -> bool:
    """Distinguish a versioned role binding from the legacy native shape."""

    return (
        isinstance(binding, dict)
        and is_worker_role_id(binding.get("worker_role"))
        and is_valid_provider_id(binding.get("model_provider"))
    )
