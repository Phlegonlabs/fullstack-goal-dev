#!/usr/bin/env python3
"""Validate the optional PLAN-v6 dual-branch release policy."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from harness_git import run_git
from harness_core import is_full_sha
from harness_schema import run_required_harness_version, version_at_least


PROTOCOL = "dual-branch/1"
DUAL_BRANCH_VERSION = (0, 59, 0)
DUAL_BRANCH_MARKER = f"Release source policy: {PROTOCOL}"
DUAL_BRANCH_MARKER_RE = re.compile(rf"^{re.escape(DUAL_BRANCH_MARKER)}\s*$", re.MULTILINE)
REMOTE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def branch_policy_required(run: dict[str, Any] | None) -> bool:
    """Current joins require the branch policy; malformed pins keep old rules."""

    return bool(
        isinstance(run, dict)
        and version_at_least(run_required_harness_version(run), DUAL_BRANCH_VERSION)
    )


def validate_branch_policy_shape(plan: dict[str, Any]) -> list[str]:
    """Return exact-shape findings without consulting Git."""

    errors: list[str] = []
    policy = plan.get("branch_policy")
    path = "plan.branch_policy"
    if not isinstance(policy, dict):
        return [f"{path}: Harness 0.59+ requires a branch policy object"]
    if set(policy) != {"protocol", "kind", "base_ref", "base_sha"}:
        return [
            f"{path}: must contain exactly protocol, kind, base_ref, and base_sha"
        ]
    if policy["protocol"] != PROTOCOL:
        errors.append(f"{path}.protocol: must be {PROTOCOL!r}")
    kind = policy["kind"]
    base_ref = policy["base_ref"]
    if kind not in {"ordinary", "hotfix"}:
        errors.append(f"{path}.kind: must be ordinary or hotfix")
        return errors
    if isinstance(base_ref, str):
        match = re.fullmatch(
            r"refs/remotes/([a-z0-9][a-z0-9._-]*)/(development|main)", base_ref
        )
        if match is None:
            errors.append(f"{path}.base_ref: must name refs/remotes/<remote>/development or refs/remotes/<remote>/main")
            return errors
        protected = match.group(2)
        expected_protected = "development" if kind == "ordinary" else "main"
        if protected != expected_protected:
            errors.append(
                f"{path}.base_ref: {kind} base must be refs/remotes/{match.group(1)}/{expected_protected}"
            )
    else:
        errors.append(f"{path}.base_ref: must be a canonical remote ref")
    if not is_full_sha(policy["base_sha"]):
        errors.append(f"{path}.base_sha: must be a full lowercase Git SHA")
    return errors


def initial_or_candidate_head(run: dict[str, Any] | None) -> str | None:
    """Prefer the current candidate; fall back to the observed initial head."""

    if not isinstance(run, dict):
        return None
    integration = run.get("integration")
    if not isinstance(integration, dict):
        return None
    for key in ("integration_head_sha", "batch_base_sha"):
        value = integration.get(key)
        if is_full_sha(value):
            return value
    return None


def validate_branch_policy_ancestry(
    plan: dict[str, Any],
    repo_root: str | Path,
    *,
    run: dict[str, Any] | None = None,
) -> list[str]:
    """Prove the frozen base is local and ancestral to the first candidate."""

    shape_errors = validate_branch_policy_shape(plan)
    if shape_errors:
        return shape_errors
    base_sha = plan["branch_policy"]["base_sha"]
    head_sha = initial_or_candidate_head(run)
    if head_sha is None:
        return []
    result = run_git(
        Path(repo_root),
        "merge-base",
        "--is-ancestor",
        base_sha,
        head_sha,
        timeout=30,
    )
    if result.returncode == 0:
        return []
    detail = result.stderr.strip() or "git merge-base --is-ancestor failed"
    return [
        "plan.branch_policy.base_sha: is not an ancestor of the initial or "
        f"candidate head {head_sha} ({detail})"
    ]


def has_prior_archive_candidate_source(plan: dict[str, Any]) -> bool:
    """Recognize the retained exact-A correction-source exception."""

    rows = [
        source
        for source in (plan.get("sources") or [])
        if isinstance(source, dict)
        and " ".join(str(source.get("kind", "")).replace("_", " ").replace("-", " ").split()).casefold()
        == "prior archive candidate"
    ]
    if len(rows) != 1:
        return False
    source = rows[0]
    filename = str(source.get("location", "")).replace("\\", "/").rsplit("/", 1)[-1]
    return (
        source.get("status") == "frozen"
        and filename.casefold() == "archive_receipt.json"
        and is_full_sha(source.get("source_revision"))
        and isinstance(source.get("content_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", source["content_sha256"]) is not None
    )


def validate_branch_policy_join(
    plan: dict[str, Any],
    architecture_text: str,
    repo_root: str | Path,
    *,
    run: dict[str, Any] | None = None,
    active_text: Callable[[str], str] | None = None,
) -> list[str]:
    """Apply the current join only for a valid 0.59+ version pin."""

    if not branch_policy_required(run):
        return []
    if has_prior_archive_candidate_source(plan):
        return []
    active = architecture_text if active_text is None else active_text(architecture_text)
    errors: list[str] = []
    if DUAL_BRANCH_MARKER_RE.search(active) is None:
        errors.append(
            "architecture: Harness 0.59+ current joins require an active "
            f"{DUAL_BRANCH_MARKER!r} marker"
        )
    errors.extend(validate_branch_policy_shape(plan))
    errors.extend(
        validate_branch_policy_ancestry(plan, repo_root, run=run)
    )
    return errors
