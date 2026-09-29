"""Policy added by ``UI contract: ui-design/3`` for new full UI packages.

ui-design/2 keeps its original meaning. A ui-design/3 package always ships the
design-system Markdown/JSON/HTML package, records three rendered direction
studies by one author, and adds an observed intermediate-width HiFi receipt.
"""

from __future__ import annotations

import re
from typing import Any

UI_CONTRACT_V3 = "ui-design/3"
PACKAGE_ACTIONS = ("compile", "update", "reuse")
DISPOSITION_BY_ACTION = {"compile": {"none", "retire"}, "update": {"retain"}, "reuse": {"retain"}}
DIRECTION_STUDY_COLUMNS = ["Direction", "Study", "Author", "Self-check by", "Self-check"]
V3_DIRECTION_DECISIONS = {"modified-and-approved"}
STUDY_RE = re.compile(
    r"^(?P<path>docs/design/directions/(?P<round>[A-Za-z0-9][A-Za-z0-9_-]*)/"
    r"[A-Za-z0-9][A-Za-z0-9_-]*\.html) @ sha256:(?P<sha256>[0-9a-f]{64})$"
)


def package_action(values: list[str]) -> str | None:
    action = values[0].strip().casefold() if len(values) == 1 else None
    return action if action in PACKAGE_ACTIONS else None


def package_gate_findings(decision: str, action_values: list[str], disposition: str | None) -> list[str]:
    """A full ui-design/3 package cannot skip the design-system package."""

    problems: list[str] = []
    if decision != "required":
        problems.append("ui-design/3 full UI package requires Design System Need Gate Decision: required")
    if len(action_values) != 1:
        problems.append("ui-design/3 Design System Need Gate requires exactly one Package action")
        return problems
    action = package_action(action_values)
    if action is None:
        problems.append("ui-design/3 Package action must be one of " + ", ".join(PACKAGE_ACTIONS))
    elif disposition is not None and disposition not in DISPOSITION_BY_ACTION[action]:
        problems.append(
            f"ui-design/3 Package action {action} requires existing pair disposition "
            + " or ".join(sorted(DISPOSITION_BY_ACTION[action]))
        )
    return problems


def direction_study_rows(rows: list[list[str]], compared: set[str]) -> tuple[list[dict[str, str]], list[str]]:
    """Validate the Direction studies rows; return study identities to resolve."""

    problems: list[str] = []
    studies: list[dict[str, str]] = []
    seen: set[str] = set()
    rounds: set[str] = set()
    authors: set[str] = set()
    for direction, study, author, checked_by, result in rows:
        if direction in seen:
            problems.append("Direction studies must list each direction once")
        seen.add(direction)
        match = STUDY_RE.fullmatch(study)
        if match is None:
            problems.append(
                "Direction studies Study must be docs/design/directions/<round>/<name>.html @ sha256:<hex>"
            )
        else:
            rounds.add(match.group("round"))
            studies.append({"path": match.group("path"), "sha256": match.group("sha256"), "direction": direction})
        authors.add(author)
        if checked_by != author:
            problems.append(f"Direction studies {direction} self-check must be made by its own author")
        if result.casefold() != "pass":
            problems.append(f"Direction studies {direction} self-check must be pass before selection")
    if seen != compared or len(compared) != 3:
        problems.append("Direction studies must cover exactly the three compared directions")
    if len(rounds) > 1:
        problems.append("Direction studies must share one docs/design/directions/<round>/ folder")
    if len(authors) > 1:
        problems.append("Direction studies must be authored and self-checked by one frontend author")
    if len({item["sha256"] for item in studies}) != len(studies) or len({item["path"] for item in studies}) != len(studies):
        problems.append("Direction studies must be distinct rendered files")
    return studies, problems


def study_html_findings(html: str, path: str) -> list[str]:
    """Rendered studies are local self-contained HTML, like the HiFi projection."""

    import check_wireframe_html  # local import keeps this module dependency-light

    problems: list[str] = []
    if re.search(r"<html\b", html, re.I) is None or re.search(r"<body\b", html, re.I) is None:
        problems.append(f"Direction study {path} must be a rendered HTML document")
    parser = check_wireframe_html.ResourceParser()
    parser.feed(html)
    parser.close()
    if len(parser.content_security_policies) != 1:
        problems.append(f"Direction study {path} requires exactly one restrictive CSP meta")
    else:
        problems.extend(f"Direction study {path}: {item}" for item in
                        check_wireframe_html.validate_hifi_csp_policy(parser.content_security_policies[0]))
    if parser.link_tags or parser.css_imports or parser.external_resources or parser.external_css_resources:
        problems.append(f"Direction study {path} must not load linked, imported or external resources")
    if parser.active_security_surfaces:
        problems.append(f"Direction study {path} must not contain active external or executable surfaces")
    return problems


def _viewports(surface: dict[str, Any], scope: dict[str, Any]) -> list[float] | None:
    responsive = surface.get("responsive") or scope.get("responsive") or {}
    if not isinstance(responsive, dict) or responsive.get("kind") != "viewports":
        return None
    return sorted(float(value) for value in responsive.get("targets", []))


def intermediate_width_findings(cases: list[dict[str, str]], scope: dict[str, Any] | None) -> list[str]:
    """Coverage of a ui-evidence/3 HiFi browser receipt observed at in-between widths.

    The caller has already validated the receipt, its ui-output/3 observation and
    PASS results with the ordinary HiFi evidence rules; this checks only that its
    case matrix covers every adjacent pair of approved web widths.
    """

    scope = scope or {}
    surfaces = {str(item.get("id")): item for item in scope.get("surfaces", []) if isinstance(item, dict)}
    problems: list[str] = []
    covered: set[tuple[str, float, float]] = set()
    for case in cases:
        surface = surfaces.get(case.get("surface", ""))
        targets = _viewports(surface, scope) if surface is not None else None
        if surface is None or targets is None or case.get("state") not in surface.get("states", []):
            problems.append(f"Intermediate width check case {case.get('surface')}/{case.get('state')} "
                            "must name an approved web surface and state")
            continue
        try:
            width = float(case.get("target", ""))
        except ValueError:
            width = float("nan")
        pair = next(((low, high) for low, high in zip(targets, targets[1:]) if low < width < high), None)
        if pair is None:
            problems.append(f"Intermediate width check target {case.get('target')} for {case.get('surface')} "
                            "must lie strictly between two adjacent approved widths")
            continue
        covered.add((str(case["surface"]), *pair))
    for surface_id, surface in surfaces.items():
        targets = _viewports(surface, scope) or []
        for low, high in zip(targets, targets[1:]):
            if (surface_id, low, high) not in covered:
                problems.append(f"Intermediate width check is missing {surface_id} between {low:g}px and {high:g}px")
    return problems
