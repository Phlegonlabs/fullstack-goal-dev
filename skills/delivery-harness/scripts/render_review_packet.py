#!/usr/bin/env python3
"""Render a deterministic, bounded review packet for one review node."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from harness_git import GitMetadataError, reject_object_substitution, run_git
from harness_manifest import ManifestError, load_plan, load_run, validate_current_plan_run


def _git(repo: Path, *args: str) -> str:
    result = run_git(repo, *args, text=True, timeout=30)
    if result.returncode != 0:
        raise ManifestError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def render_packet(
    plan: dict[str, Any],
    run: dict[str, Any],
    node_id: str,
    repo_root: Path,
    *,
    max_diff_bytes: int = 50000,
) -> str:
    try:
        reject_object_substitution(repo_root)
    except (GitMetadataError, OSError) as exc:
        raise ManifestError(str(exc)) from exc
    node = next(
        (item for item in plan["graph"]["nodes"] if item.get("id") == node_id),
        None,
    )
    if not isinstance(node, dict) or not isinstance(node.get("review"), dict):
        raise ManifestError(f"{node_id!r} is not a runtime review node")
    review = node["review"]
    lineage = run["review_lineages"][review["lineage_id"]]
    mission_ids = set(review["mission_ids"])
    missions = [item for item in plan["missions"] if item["id"] in mission_ids]
    base = run["integration"].get("batch_base_sha")
    head = run["integration"].get("integration_head_sha")
    if review.get("stage", "preintegration") == "preintegration" and len(missions) == 1:
        head = run["mission_states"][missions[0]["id"]].get("head_sha") or head
    if not isinstance(base, str) or not isinstance(head, str):
        raise ManifestError("review packet requires concrete base and reviewed head SHAs")
    diff = _git(repo_root, "diff", "--no-ext-diff", f"{base}..{head}")
    encoded = diff.encode("utf-8")
    truncated = len(encoded) > max_diff_bytes
    if truncated:
        diff = encoded[:max_diff_bytes].decode("utf-8", errors="replace")
        changed = _git(
            repo_root,
            "diff",
            "--name-only",
            f"{base}..{head}",
        ).strip()
    acceptance = [
        {"task_id": task["id"], "acceptance_matrix": task["acceptance_matrix"]}
        for mission in missions
        for task in mission["tasks"]
    ]
    version_gate = (
        run.get("runtime_capabilities", {}).get("runtime_adapter", {}).get("version_gate")
    )
    contract_adoption = (
        version_gate.get("contract_adoption")
        if isinstance(version_gate, dict)
        and version_gate.get("status") == "adopted"
        else None
    )
    # A security reviewer returns each PLAN required check with the key of
    # its one PASS execution at the reviewed head (null when there is none).
    required_checks = []
    security_policy = plan.get("security_review")
    if review["type"] == "security" and isinstance(security_policy, dict):
        for check_id in security_policy.get("required_checks", []):
            keys = [
                execution.get("execution_key")
                for execution in run.get("verifier_executions", [])
                if isinstance(execution, dict)
                and execution.get("verifier_id") == check_id
                and execution.get("layer") in {"batch", "final"}
                and execution.get("status") == "PASS"
                and execution.get("exit_code") == 0
                and isinstance(execution.get("context"), dict)
                and execution["context"].get("head_sha") == head
            ]
            required_checks.append(
                {"id": check_id, "execution_key": keys[0] if len(keys) == 1 else None}
            )
    packet_lines = [
        f"# Review packet: {node_id}",
        "",
        f"- Reviewed head: `{head}`",
        f"- Base: `{base}`",
        f"- Lineage: `{review['lineage_id']}` ({lineage['consumed_attempts']}/{lineage['base_allowance'] + lineage['additional_allowance']} consumed)",
        f"- Scope: {', '.join(review['scope'])}",
    ]
    if review.get("stage") == "integration":
        reviewed_heads = []
        for mission in missions:
            mission_head = (
                run.get("mission_states", {}).get(mission["id"], {}).get("head_sha")
            )
            if isinstance(mission_head, str) and mission_head:
                reviewed_heads.append(
                    f"- `{mission['id']}`: `{mission_head}`"
                    " (passed exact-head pre-integration review)"
                )
        if reviewed_heads:
            packet_lines += ["", "## Already-reviewed mission heads", "", *reviewed_heads]
        packet_lines += [
            "",
            "## Integration focus",
            "",
            "Each covered mission's content already passed its own exact-head"
            " pre-integration review. Focus this pass on what combination"
            " changed: merge seams, conflict resolutions, cross-mission"
            " interaction, and shared-contract boundaries.",
        ]
    if truncated:
        # The untruncated diff already carries every path. Keep an explicit
        # path list only when byte truncation could hide the tail.
        packet_lines += [
            "",
            "## Changed files",
            "",
            changed,
        ]
    packet_lines += [
        "",
        "## Contract",
        "",
        "```json",
        json.dumps(
            {
                "review_type": review["type"],
                "skill_binding_slot": (
                    "code_security_verification"
                    if review["type"] == "security"
                    else None
                ),
                "required_evidence": review["required_evidence"],
                "required_tools": review.get("required_tools", []),
                "required_checks": required_checks,
                "reviewer_tool_capabilities": {
                    tool_name: run.get("runtime_capabilities", {})
                    .get("reviewer_tools", {})
                    .get(tool_name)
                    for tool_name in review.get("required_tools", [])
                },
                "contract_adoption": contract_adoption,
                "acceptance": acceptance,
                "failure_families": lineage["failure_families"],
                "owner_decisions": lineage["owner_decisions"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        "```",
        (
            "Before any review action, independently recompute the seven-skill contract"
            " digest, compare it with `contract_adoption.contract_digest_sha256`, read"
            " the supplied fixed contract, and return your own reading evidence as"
            " `contract_adoption_check` (shape: `references/worker-result-contract.md`,"
            " Contract Adoption Check), beside your review result and never inside a"
            " security review result. Stop on a mismatch. An adoption receipt is not"
            " loaded-at-start evidence."
            if contract_adoption is not None
            else ""
        ),
        "",
        f"## Diff{' (truncated)' if truncated else ''}",
        "",
        "```diff",
        diff.rstrip(),
        "```",
        "",
    ]
    return "\n".join(packet_lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--max-diff-bytes", type=int, default=50000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.plan)
        run = load_run(args.run)
        errors = validate_current_plan_run(plan, run, repo_root=args.repo_root)
        if errors:
            raise ManifestError("invalid PLAN/RUN:\n" + "\n".join(errors))
        packet = render_packet(plan, run, args.node, args.repo_root, max_diff_bytes=args.max_diff_bytes)
        if args.out:
            if args.out.exists():
                raise ManifestError(f"refusing to overwrite {args.out}")
            args.out.write_text(packet, encoding="utf-8", newline="\n")
            print(f"wrote {args.out}")
        else:
            print(packet, end="")
    except (ManifestError, OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
