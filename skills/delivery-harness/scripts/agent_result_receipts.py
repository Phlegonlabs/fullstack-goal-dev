"""Join retained parent-observed host responses to reserved agent attempts.

The host adapter, not child prose, supplies the normalized source envelope.
Hashes bind retained bytes; they do not authenticate an untrusted adapter.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agent_launch_records import matching_launch_records
from harness_core import ManifestError


RECEIPT_KEYS = {"kind", "session_id", "source_ref", "source_sha256", "payload_sha256"}
MAX_SOURCE_BYTES = 8 * 1024 * 1024


def payload_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _source(receipt: dict[str, Any]) -> dict[str, Any]:
    reference = receipt.get("source_ref")
    if not isinstance(reference, str) or not Path(reference).is_absolute():
        raise ValueError("source_ref must be an absolute retained host-response path")
    with Path(reference).open("rb") as stream:
        raw = stream.read(MAX_SOURCE_BYTES + 1)
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("retained host response exceeds the size limit")
    if hashlib.sha256(raw).hexdigest() != receipt.get("source_sha256"):
        raise ValueError("retained host-response bytes do not match source_sha256")
    source = json.loads(raw)
    if not isinstance(source, dict) or set(source) != {"schema_version", "session_id", "payload"}:
        raise ValueError("host response must contain schema_version, session_id and payload")
    if source["schema_version"] != 1 or isinstance(source["schema_version"], bool):
        raise ValueError("unsupported host-response schema_version")
    if source["session_id"] != receipt.get("session_id"):
        raise ValueError("host-response session does not match the receipt")
    if payload_digest(source["payload"]) != receipt.get("payload_sha256"):
        raise ValueError("host-response payload does not match payload_sha256")
    return source


def validate_result_receipt(
    run: dict[str, Any], reserved: dict[str, Any], kind: str,
    receipt: Any, payload: Any = None,
) -> list[str]:
    """Require actual returned bytes from the exact parent-observed session."""
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_KEYS:
        return ["result_receipt must contain exactly the returned-result receipt fields"]
    if receipt.get("kind") != "returned_result":
        return ["result_receipt.kind must be returned_result"]
    session = receipt.get("session_id")
    if not isinstance(session, str) or not session.strip():
        return ["result_receipt.session_id must be a non-empty host session"]
    matches = matching_launch_records(
        run, assignment_kind=kind,
        assignment_id=reserved.get("lease_id") if kind == "mission" else reserved.get("node_id"),
        attempt_id=reserved.get("attempt_id"), worker_id=reserved.get("worker_id"),
    )
    if len(matches) != 1 or matches[0].get("session_id") != session:
        return ["result_receipt has no matching reserved launch session"]
    try:
        source = _source(receipt)
        if payload is not None and source["payload"] != payload:
            return ["accepted payload differs from the retained host response"]
        if payload is None and reserved.get("phase") == "worker_passed":
            expected = (
                {"mission_id": reserved.get("mission_id"), "lease_id": reserved.get("lease_id"),
                 "head_sha": reserved.get("worker_head_sha"), "base_sha": reserved.get("batch_base_sha")}
                if kind == "mission" else
                {"outcome": reserved.get("outcome"), "findings": reserved.get("findings"),
                 "security_result": reserved.get("security_result")}
            )
            returned = source["payload"]
            if not isinstance(returned, dict) or any(returned.get(k) != v for k, v in expected.items()):
                return ["persisted accepted result differs from the retained host response"]
    except (OSError, ValueError, TypeError, RecursionError):
        return ["result_receipt retained source, session or payload failed verification"]
    return []


def load_result_receipt(path: Any, run: dict[str, Any], reserved: dict[str, Any],
                        kind: str, payload: Any) -> dict[str, Any]:
    if path is None:
        raise ManifestError("role-bound returned results require --result-receipt")
    try:
        receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise ManifestError("cannot read --result-receipt") from exc
    issues = validate_result_receipt(run, reserved, kind, receipt, payload)
    if issues:
        raise ManifestError("invalid result receipt: " + "; ".join(issues))
    return receipt
