"""Retain terminal host failures without inventing a successful launch."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_launch_records import matching_launch_records
from agent_result_receipts import RECEIPT_KEYS, _source
from harness_core import ManifestError


AVAILABILITY_CODES = {"model_not_found", "model_unavailable", "provider_unavailable", "model_not_supported"}
FAILURE_KEYS = {"worker_id", "attempt_id", "failure_classification", "error_code",
                "observed_error", "stopped", "termination_evidence", "partial_work"}


def read_failure_receipt(run: dict[str, Any], reserved: dict[str, Any], kind: str,
                         receipt: Any) -> tuple[dict[str, Any] | None, list[str]]:
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
        return None, ["failure_receipt must contain the retained host receipt fields"]
    if receipt.get("kind") not in ("launch_failed", "runtime_failed"):
        return None, ["failure_receipt must identify a launch_failed or runtime_failed response"]
    launches = matching_launch_records(
        run, assignment_kind=kind,
        assignment_id=reserved.get("lease_id") if kind == "mission" else reserved.get("node_id"),
        attempt_id=reserved.get("attempt_id"), worker_id=reserved.get("worker_id"),
    )
    if receipt["kind"] == "launch_failed":
        if launches or receipt.get("session_id") is not None:
            return None, ["a failed start cannot claim a successful launch or session"]
    elif len(launches) != 1 or launches[0].get("session_id") != receipt.get("session_id"):
        return None, ["runtime failure must match the reserved launch session"]
    try:
        failure = _source(receipt)["payload"]
    except (OSError, ValueError, TypeError, RecursionError):
        return None, ["failure receipt retained source failed verification"]
    if not isinstance(failure, dict) or set(failure) != FAILURE_KEYS:
        return None, ["failure response has an unsupported shape"]
    if any(failure[key] != reserved.get(key) for key in ("worker_id", "attempt_id")):
        return None, ["failure response belongs to another reserved attempt"]
    for key in ("failure_classification", "error_code", "observed_error", "termination_evidence"):
        if not isinstance(failure[key], str) or not failure[key].strip():
            return None, [f"failure response {key} must be explicit"]
    if failure["stopped"] is not True:
        return None, ["failure response must confirm predecessor termination"]
    partial = failure["partial_work"]
    if (not isinstance(partial, dict) or set(partial) != {"status", "evidence"}
            or partial["status"] not in ("none", "reconciled")
            or not isinstance(partial["evidence"], str) or not partial["evidence"].strip()):
        return None, ["failure response requires partial-work reconciliation"]
    return failure, []


def load_failure_receipt(path: Any, run: dict[str, Any], reserved: dict[str, Any],
                         kind: str) -> dict[str, Any]:
    if path is None:
        raise ManifestError("parent-reported role-bound failure requires --failure-receipt")
    try:
        receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise ManifestError("cannot read --failure-receipt") from exc
    _, issues = read_failure_receipt(run, reserved, kind, receipt)
    if issues:
        raise ManifestError("invalid failure receipt: " + "; ".join(issues))
    return receipt
