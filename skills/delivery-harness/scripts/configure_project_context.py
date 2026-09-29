#!/usr/bin/env python3
"""Safely add host-specific project context files without overwriting local rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from check_skill_bindings import PIN_RE, STAGE_SLOTS, bound_skill_name, parse_binding_contract


TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "assets" / "templates"
DEFAULT_AGENTS_TEMPLATE = TEMPLATES_DIR / "PROJECT_AGENTS.template.md"
DEFAULT_CLAUDE_TEMPLATE = TEMPLATES_DIR / "PROJECT_CLAUDE.template.md"
MERGE_HEADING = "# Project Delivery Harness Shared Guidance"
MERGE_INTRO = (
    "Added by `configure_project_context.py --merge-agents`. Local rules above "
    "stay authoritative. Resolve any reported same-heading divergence by "
    "meaning; do not overwrite the local rules or bindings."
)
UNRESOLVED_PLACEHOLDER_MARKERS = (
    "<fill>",
    "<bundled",
    "<or your own",
    "<hash of",
    "<resolve",
    "<full-tree",
    "<databases",
)


def _present(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _assert_no_reparse_components(path: Path) -> None:
    current = Path(path)
    while True:
        try:
            if current.is_symlink() or bool(
                getattr(current.stat(), "st_file_attributes", 0) & 0x0400
            ):
                raise ValueError(f"context path contains a symlink or reparse point: {current}")
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise ValueError(f"cannot inspect context path {current}: {exc}") from exc
        parent = current.parent
        if parent == current:
            return
        current = parent


def _write_new(path: Path, content: bytes) -> None:
    _assert_no_reparse_components(path.parent)
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _level_two_sections(text: str) -> dict[str, str]:
    """Return shared-rule sections keyed by their exact top-level heading."""

    sections: dict[str, str] = {}
    current: list[str] | None = None
    heading = ""
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            if current is not None:
                sections[heading] = "".join(current)
            heading = line[3:].strip()
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        sections[heading] = "".join(current)
    return sections


def _atomic_replace(path: Path, content: bytes, expected: bytes) -> None:
    """Replace a regular file only while it still has the observed bytes."""

    _assert_no_reparse_components(path)
    if path.read_bytes() != expected:
        raise ValueError(f"context file changed during merge: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.merge-", dir=path.parent, suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.read_bytes() != expected:
            raise ValueError(f"context file changed during merge: {path}")
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def inspect_context(root: Path) -> dict[str, object]:
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    override = root / "AGENTS.override.md"
    return {
        "root": str(root),
        "agents_present": _present(agents),
        "claude_present": _present(claude),
        "agents_override_present": _present(override),
        "missing": [
            name
            for name, path in (("AGENTS.md", agents), ("CLAUDE.md", claude))
            if not _present(path)
        ],
    }


def configure_context(
    root: Path,
    agents_template: Path = DEFAULT_AGENTS_TEMPLATE,
    claude_template: Path = DEFAULT_CLAUDE_TEMPLATE,
    merge_agents: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    try:
        resolved_root = root.resolve(strict=True)
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot resolve target root: {exc}") from exc
    if not resolved_root.is_dir():
        raise ValueError(f"target root is not a directory: {resolved_root}")
    resolved_agents_template = agents_template.resolve(strict=True)
    resolved_claude_template = claude_template.resolve(strict=True)
    _assert_no_reparse_components(resolved_root)
    for template in (resolved_agents_template, resolved_claude_template):
        if not template.is_file():
            raise ValueError(f"context template is not a file: {template}")

    agents = resolved_root / "AGENTS.md"
    claude = resolved_root / "CLAUDE.md"
    created: list[str] = []
    merge: dict[str, object] = {
        "requested": merge_agents,
        "safe_additions": [],
        "unresolved_divergences": [],
        "semantic_review_required": False,
    }

    if merge_agents and _present(agents):
        _assert_no_reparse_components(agents)
        try:
            existing_bytes = agents.read_bytes()
            existing_text = existing_bytes.decode("utf-8")
            template_text = resolved_agents_template.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"cannot merge AGENTS.md as UTF-8: {exc}") from exc

        existing_sections = _level_two_sections(existing_text)
        template_sections = _level_two_sections(template_text)
        missing = [
            heading for heading in template_sections if heading not in existing_sections
        ]
        divergent = [
            heading
            for heading, template_section in template_sections.items()
            if heading in existing_sections
            and existing_sections[heading] != template_section
        ]
        merge["safe_additions"] = missing
        divergences = [
            {
                "heading": heading,
                "existing_sha256": _sha256(existing_sections[heading].encode("utf-8")),
                "template_sha256": _sha256(template_sections[heading].encode("utf-8")),
            }
            for heading in divergent
        ]
        if missing and any(
            line.strip() == MERGE_HEADING for line in existing_text.splitlines()
        ):
            divergences.append(
                {
                    "heading": MERGE_HEADING,
                    "existing_sha256": _sha256(existing_bytes),
                    "template_sha256": _sha256(template_text.encode("utf-8")),
                }
            )
        merge["unresolved_divergences"] = divergences
        merge["semantic_review_required"] = bool(missing or divergent)

        if missing and not dry_run and not any(
            line.strip() == MERGE_HEADING for line in existing_text.splitlines()
        ):
            tail = "" if existing_bytes.endswith(b"\n") else "\n\n"
            block = "\n".join(
                (
                    MERGE_HEADING,
                    "",
                    MERGE_INTRO,
                    "",
                    *(template_sections[heading] for heading in missing),
                )
            )
            if not block.endswith("\n"):
                block += "\n"
            merged = existing_bytes + tail.encode("utf-8") + block.encode("utf-8")
            _atomic_replace(agents, merged, existing_bytes)

    if not dry_run:
        if not _present(agents):
            _write_new(agents, resolved_agents_template.read_bytes())
            created.append("AGENTS.md")
        if not _present(claude):
            _write_new(claude, resolved_claude_template.read_bytes())
            created.append("CLAUDE.md")

    result = inspect_context(resolved_root)
    result["created"] = created
    result["preserved"] = [
        name for name in ("AGENTS.md", "CLAUDE.md") if name not in created
    ]
    result["agents_merge"] = merge
    return result


def unresolved_placeholders(root: Path, *, stage: str = "all") -> list[str]:
    """Unresolved template markers in a seeded AGENTS.md, with line numbers."""

    agents = root / "AGENTS.md"
    if not _present(agents):
        return []
    findings: list[str] = []
    try:
        text = agents.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"AGENTS.md is not valid UTF-8: {exc}") from exc
    for number, line in enumerate(text.splitlines(), start=1):
        for marker in UNRESOLVED_PLACEHOLDER_MARKERS:
            if marker in line:
                findings.append(f"line {number}: unresolved placeholder {marker!r}")
    rows, binding_findings = parse_binding_contract(text, stage=stage)
    findings.extend(f"skill bindings: {finding}" for finding in binding_findings)
    for slot, cell, pin, number in rows:
        if slot not in STAGE_SLOTS[stage] and cell.strip("`") == pin == "pending":
            continue
        if bound_skill_name(cell) is None or PIN_RE.fullmatch(pin) is None:
            findings.append(
                f"line {number}: unresolved Skill Bindings row for slot {slot!r}"
            )
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="Target repository root")
    parser.add_argument("--stage", choices=sorted(STAGE_SLOTS), default="all")
    parser.add_argument(
        "--agents-template",
        type=Path,
        default=DEFAULT_AGENTS_TEMPLATE,
        help="AGENTS.md template for Codex and Pi project governance",
    )
    parser.add_argument(
        "--claude-template",
        type=Path,
        default=DEFAULT_CLAUDE_TEMPLATE,
        help="CLAUDE.md template for the Claude Code project overlay",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "report context state without writing; exit 1 when either root file "
            "is missing, a merge has additions, or same-heading rules diverge"
        ),
    )
    parser.add_argument(
        "--merge-agents",
        action="store_true",
        help=(
            "on an authorized bootstrap, add missing shared AGENTS.md sections; "
            "preserve local rules and report same-heading differences"
        ),
    )
    parser.add_argument(
        "--require-resolved",
        action="store_true",
        help=(
            "with --check: also fail while a seeded AGENTS.md still carries "
            "unresolved template placeholders (bindings, deployment record)"
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = args.root.resolve(strict=True)
        result = configure_context(
            root,
            args.agents_template,
            args.claude_template,
            merge_agents=args.merge_agents,
            dry_run=args.check,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 2
    unresolved: list[str] = []
    if args.require_resolved:
        unresolved = unresolved_placeholders(root, stage=args.stage)
        result["unresolved_placeholders"] = unresolved
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.check and (result["missing"] or unresolved):
        return 1
    if args.check and args.merge_agents:
        merge = result["agents_merge"]
        if merge["safe_additions"] or merge["unresolved_divergences"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
