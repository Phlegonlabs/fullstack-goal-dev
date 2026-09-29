#!/usr/bin/env python3
"""Validate and resolve host-owned execution bindings."""

from __future__ import annotations

import copy
from agent_role_contract import (
    COMPLETION_KINDS,
    KNOWN_CAPABILITIES,
    RUNTIME_AXES,
    RUNTIME_BINDING_KEYS,
    RUNTIME_KINDS,
    WORKER_RUNTIME_KINDS,
    WORKSPACE_KINDS,
    _nonempty,
    binding_is_role_bound,
    is_worker_role_id,
    role_contract_enabled,
    worker_role,
)
from harness_core import (
    is_safe_model_token,
)
from harness_schema import (
    RUNTIME_REASONING_EFFORTS,
    is_valid_provider_id,
)
from typing import (
    Any,
)


def validate_role_bindings(
    run: Any,
) -> list[str]:
    """Validate adapter.role_bindings without widening legacy RUNs."""

    if not role_contract_enabled(run):
        return []
    runtime = run.get("runtime_capabilities")
    adapter = runtime.get("runtime_adapter") if isinstance(runtime, dict) else None
    if not isinstance(adapter, dict) or "role_bindings" not in adapter:
        return ["run.runtime_capabilities.runtime_adapter.role_bindings: is required for a 0.58+ role-contract RUN"]
    bindings = adapter.get("role_bindings")
    path = "run.runtime_capabilities.runtime_adapter.role_bindings"
    if not isinstance(bindings, dict):
        return [f"{path}: must be an object"]
    errors: list[str] = []
    invalid_roles = sorted(role for role in bindings if not is_worker_role_id(role))
    if invalid_roles:
        errors.append(f"{path}: role names must be lowercase host-safe ids: " + ", ".join(invalid_roles))
    seen_sessions: set[str] = set()
    for role in sorted(role for role in bindings if is_worker_role_id(role)):
        binding = bindings[role]
        role_path = f"{path}.{role}"
        if not isinstance(binding, dict):
            errors.append(f"{role_path}: must be an object")
            continue
        allowed_keys = {
            "kind",
            "native_agent_type",
            "bridge_identity",
            "model_provider",
            "model",
            "reasoning_effort",
            "capability_probe",
            "probe_session_id",
            "fallback_role",
            *RUNTIME_AXES,
        }
        extra = sorted(set(binding) - allowed_keys)
        missing = sorted(allowed_keys - set(binding) - {
            "native_agent_type",
            "bridge_identity",
            "probe_session_id",
            "fallback_role",
        })
        if extra:
            errors.append(f"{role_path}: unknown keys: {', '.join(extra)}")
        if missing:
            errors.append(f"{role_path}: missing keys: {', '.join(missing)}")
            continue
        kind = binding["kind"]
        if kind not in tuple(RUNTIME_KINDS):
            errors.append(f"{role_path}.kind: must be native or external_bridge")
        model_provider = binding["model_provider"]
        if not is_valid_provider_id(model_provider):
            errors.append(f"{role_path}.model_provider: has an unsupported value")
        model = binding["model"]
        if model is not None and not is_safe_model_token(model):
            errors.append(f"{role_path}.model: must be null or a safe model token")
        effort = binding["reasoning_effort"]
        if effort is not None and effort not in tuple(RUNTIME_REASONING_EFFORTS):
            errors.append(f"{role_path}.reasoning_effort: must be null or a supported effort")
        identity_key = "native_agent_type" if kind == "native" else "bridge_identity"
        other_identity = "bridge_identity" if kind == "native" else "native_agent_type"
        if other_identity in binding:
            errors.append(f"{role_path}.{other_identity}: must be omitted for {kind}")
        if not _nonempty(binding.get(identity_key)):
            errors.append(f"{role_path}.{identity_key}: must be a non-empty string")
        capability_probe = binding["capability_probe"]
        if not isinstance(capability_probe, dict):
            errors.append(f"{role_path}.capability_probe: must be an object")
        else:
            required = (
                {"external_runtime_invoke", "external_terminal_result"}
                if kind == "external_bridge"
                else (
                    {"direct_subagent_spawn", "direct_agent_result"}
                    if _native_driver(binding) == "subagents"
                    else set()
                )
            )
            unknown_caps = sorted(set(capability_probe) - KNOWN_CAPABILITIES)
            if unknown_caps:
                errors.append(f"{role_path}.capability_probe: unsupported capabilities: " + ", ".join(unknown_caps))
            missing_caps = sorted(required - set(capability_probe))
            if missing_caps:
                errors.append(f"{role_path}.capability_probe: missing required capabilities: " + ", ".join(missing_caps))
            for capability in sorted(set(capability_probe) & KNOWN_CAPABILITIES):
                observation = capability_probe[capability]
                observation_path = f"{role_path}.capability_probe.{capability}"
                if not isinstance(observation, dict) or set(observation) != {
                    "status", "evidence", "probe_id"
                }:
                    errors.append(f"{observation_path}: must contain status, evidence, and probe_id")
                    continue
                if observation["status"] != "available":
                    errors.append(f"{observation_path}.status: an advertised binding requires an available probe")
                if not _nonempty(observation["evidence"]):
                    errors.append(f"{observation_path}.evidence: must be a non-empty string")
                if not _nonempty(observation["probe_id"]):
                    errors.append(f"{observation_path}.probe_id: must be a non-empty string")
        probe_session_id = binding.get("probe_session_id")
        if kind == "external_bridge":
            if not _nonempty(probe_session_id):
                errors.append(f"{role_path}.probe_session_id: is required for external_bridge")
            elif probe_session_id in seen_sessions:
                errors.append(f"{role_path}.probe_session_id: must be unique across bridge probes")
            else:
                seen_sessions.add(probe_session_id)
        elif probe_session_id is not None:
            errors.append(f"{role_path}.probe_session_id: must be omitted for native")
        fallback_role = binding.get("fallback_role")
        if fallback_role is not None:
            if not is_worker_role_id(fallback_role) or fallback_role == role:
                errors.append(f"{role_path}.fallback_role: must be a different valid role")
            elif fallback_role not in bindings:
                errors.append(f"{role_path}.fallback_role: must name another configured binding")
        axes_errors = _validate_axes(binding, role_path)
        errors.extend(axes_errors)
    return sorted(set(errors))


def _native_driver(binding: dict[str, Any]) -> str:
    runtime = binding.get("worker_runtime")
    return "app_threads" if runtime == "app_task" else "subagents"


def _validate_axes(binding: dict[str, Any], path: str) -> list[str]:
    worker_runtime = binding.get("worker_runtime")
    workspace = binding.get("workspace_mode")
    completion = binding.get("completion_channel")
    errors: list[str] = []
    if worker_runtime not in tuple(WORKER_RUNTIME_KINDS):
        errors.append(f"{path}.worker_runtime: has an unsupported value")
    if workspace not in tuple(WORKSPACE_KINDS):
        errors.append(f"{path}.workspace_mode: has an unsupported value")
    if completion not in tuple(COMPLETION_KINDS):
        errors.append(f"{path}.completion_channel: has an unsupported value")
    if worker_runtime == "app_task":
        if workspace != "app_managed_worktree" or completion != "thread_poll":
            errors.append(f"{path}: app_task requires app_managed_worktree/thread_poll")
    elif worker_runtime == "subagent":
        if workspace not in ("shared_checkout", "parent_managed_worktree") or completion not in (
            "agent_result", "report_file"
        ):
            errors.append(f"{path}: subagent requires a supported workspace and terminal channel")
    elif worker_runtime == "parent" and (
        workspace != "parent_managed_worktree" or completion != "agent_result"
    ):
        errors.append(f"{path}: parent requires parent_managed_worktree/agent_result")
    return errors


def role_binding(
    run: dict[str, Any],
    role: str | None,
) -> dict[str, Any] | None:
    """Return the host-policy binding for one logical role."""

    if not role_contract_enabled(run) or not is_worker_role_id(role):
        return None
    runtime = run.get("runtime_capabilities")
    adapter = runtime.get("runtime_adapter") if isinstance(runtime, dict) else None
    bindings = adapter.get("role_bindings") if isinstance(adapter, dict) else None
    binding = bindings.get(role) if isinstance(bindings, dict) else None
    return binding if isinstance(binding, dict) else None


def binding_for_runtime(runtime: dict[str, Any], role: str | None) -> dict[str, Any] | None:
    """Read a binding from runtime_capabilities inside the shared resolver."""

    if not is_worker_role_id(role):
        return None
    adapter = runtime.get("runtime_adapter") if isinstance(runtime, dict) else None
    bindings = adapter.get("role_bindings") if isinstance(adapter, dict) else None
    binding = bindings.get(role) if isinstance(bindings, dict) else None
    return binding if isinstance(binding, dict) else None


def resolve_runtime_binding(
    node: dict[str, Any],
    runtime: dict[str, Any],
) -> dict[str, Any] | None:
    """Resolve one node using parent-host eligibility and role-policy axes.

    `provider` remains the PLAN-authorized parent host. `model_provider`
    records the actual model provider. No missing or incompatible option is
    silently replaced by another model.
    """

    policy = node.get("runtime")
    host = runtime.get("runtime_adapter", {}).get("provider")
    role = worker_role(node)
    allowed = policy.get("allowed_providers", []) if isinstance(policy, dict) else []
    if host not in allowed:
        return None
    binding = binding_for_runtime(runtime, role)
    if binding is None:
        return None
    driver = (
        "external_bridge"
        if binding["kind"] == "external_bridge"
        else _native_driver(binding)
    )
    configured = policy.get("provider_options", {}).get(host, {}) if isinstance(policy, dict) else {}
    configured_model = configured.get("model") if isinstance(configured, dict) else None
    configured_effort = configured.get("reasoning_effort") if isinstance(configured, dict) else None
    if configured_model is not None and configured_model != binding.get("model"):
        return None
    if configured_effort is not None and configured_effort != binding.get("reasoning_effort"):
        return None
    option_source = "plan_provider_options" if configured_model is not None or configured_effort is not None else "role_binding_default"
    result = {
        "provider": host,
        "driver": driver,
        "source": "external_bridge" if binding["kind"] == "external_bridge" else "host",
        "worker_role": role,
        "resolved_role": role,
        "model_provider": binding["model_provider"],
        "native_agent_type": binding.get("native_agent_type"),
        "bridge_identity": binding.get("bridge_identity"),
        "model": binding.get("model"),
        "reasoning_effort": binding.get("reasoning_effort"),
        "option_source": option_source,
        "capability_probe": copy.deepcopy(binding.get("capability_probe", {})),
        "probe_session_id": binding.get("probe_session_id"),
    }
    result.update({key: binding[key] for key in RUNTIME_AXES})
    return result


def validate_execution_binding(
    path: str,
    binding: dict[str, Any],
    node: dict[str, Any],
    runtime: dict[str, Any],
) -> list[str]:
    """Validate a persisted lease/reservation against the same resolver."""

    if binding.get("worker_role") != worker_role(node):
        return [f"{path}.worker_role: must match the PLAN logical role"]
    if binding.get("fallback_from_role") not in (None, worker_role(node)):
        return [f"{path}.fallback_from_role: must match the PLAN logical role"]
    resolved_role = binding.get("resolved_role") if binding_is_role_bound(binding) else None
    expected = (
        resolve_runtime_binding(node, runtime)
        if not resolved_role or resolved_role == worker_role(node)
        else None
    )
    if expected is None and binding_is_role_bound(binding) and binding.get("fallback_from_role"):
        original_policy = binding_for_runtime(runtime, binding.get("fallback_from_role"))
        target_policy = binding_for_runtime(runtime, resolved_role)
        if original_policy is None or original_policy.get("fallback_role") != resolved_role:
            return [f"{path}.resolved_role: is not the configured fallback target"]
        if target_policy is None:
            return [f"{path}.worker_role: has no configured fallback binding"]
        expected = {
            "provider": runtime.get("runtime_adapter", {}).get("provider"),
            "driver": "external_bridge" if target_policy["kind"] == "external_bridge" else _native_driver(target_policy),
            "source": "external_bridge" if target_policy["kind"] == "external_bridge" else "host",
            "worker_role": binding.get("worker_role"),
            "resolved_role": resolved_role,
            "fallback_from_role": binding.get("fallback_from_role"),
            "model_provider": target_policy.get("model_provider"),
            "native_agent_type": target_policy.get("native_agent_type"),
            "bridge_identity": target_policy.get("bridge_identity"),
            "model": target_policy.get("model"),
            "reasoning_effort": target_policy.get("reasoning_effort"),
            "option_source": "role_binding_default",
            "capability_probe": target_policy.get("capability_probe"),
            "probe_session_id": target_policy.get("probe_session_id"),
            **{key: target_policy[key] for key in RUNTIME_AXES},
        }
    if expected is None:
        return [f"{path}: must match the resolved role binding"]
    expected_keys = set(RUNTIME_BINDING_KEYS) - (
        {"fallback_from_role"} if "fallback_from_role" not in expected else set()
    )
    if set(binding) != expected_keys:
        return [f"{path}: must contain exactly the role-contract binding fields"]
    identity_keys = {
        "provider",
        "driver",
        "source",
        "worker_role",
        "resolved_role",
        "model_provider",
        "native_agent_type",
        "bridge_identity",
        "model",
        "reasoning_effort",
        "option_source",
        "fallback_from_role",
        "probe_session_id",
        *RUNTIME_AXES,
    }
    for key in identity_keys:
        if binding.get(key) != expected.get(key):
            return [f"{path}.{key}: must match the resolved role binding"]
    return []
