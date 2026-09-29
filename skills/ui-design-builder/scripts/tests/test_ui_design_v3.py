"""ui-design/3 full packages: required design-system package, studies and widths.

Fixture bytes are synthetic validator inputs, never product approvals or browser
observations.
"""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

from test_structure_publication import build_receipt, checker, digest
from test_ui_design_contract import capture_fixture
from test_wireframe_free_publication import current_publication

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "product-definition-builder" / "scripts"))
import check_product_package  # noqa: E402

STUDY_AUTHOR = "frontend_worker claude-opus-5-5 attempt-1"


def _study_html(title):
    csp = checker.check_wireframe_html.REQUIRED_HIFI_CSP
    return (f'<!doctype html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="{csp}">'
            f'<title>{title}</title><style>body{{margin:0;font:16px/1.5 serif}}</style></head>'
            f'<body><main><h1>{title}</h1><p>Synthetic rendered direction study for validator tests.</p></main></body></html>')


def intermediate_receipt(root, text, targets, *, results=None):
    """Synthetic ui-output/3 HiFi browser observation at in-between widths.

    It copies the fixture's HiFi surface observation and changes only its case
    matrix; it is validator input, not an actual browser run.
    """
    surface = re.search(r"^HiFi surface check: PASS — evidence=(\S+) @", text, re.M).group(1)
    source = json.loads((root / surface).read_text(encoding="utf-8"))
    output = json.loads((root / source["receipt"]["outputArtifact"]["path"]).read_text(encoding="utf-8"))
    states = sorted({case["state"] for case in output["matrix"]["cases"]})
    cases = [{"surface": "UI-001", "state": state, "target": target} for target in targets for state in states]
    output["matrix"] = {"cases": cases}
    output["results"] = results or [dict(case, result="PASS") for case in cases]
    out_path = root / "docs/evidence/hifi-intermediate-widths-output.json"
    out_path.write_text(json.dumps(output), encoding="utf-8")
    receipt = root / "docs/evidence/hifi-intermediate-widths.json"
    receipt.write_text(json.dumps(build_receipt(root, out_path.relative_to(root).as_posix())), encoding="utf-8")
    return f"{receipt.relative_to(root).as_posix()} @ sha256:{digest(receipt)}"


def v3_publication(root, *, action="compile", disposition="none"):
    """Derive a ui-design/3 package from the synthetic ui-design/2 fixture."""
    ui, prd, hifi = current_publication(root)
    text = ui.read_text(encoding="utf-8")
    text = text.replace("UI contract: ui-design/2", "UI contract: ui-design/3", 1)
    text = text.replace("Direction mode: one recommended direction", "Direction mode: three comparable directions")
    directions = root / "docs/design/directions/round-1"
    directions.mkdir(parents=True, exist_ok=True)
    rows = ["| Direction | UI surface | State | Target | Scenario | Content basis | Screenshot | Rationale |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    studies = ["### Direction studies", "",
               "| Direction | Study | Author | Self-check by | Self-check |", "| --- | --- | --- | --- | --- |"]
    palette = (("white", "black"), ("red", "blue"), ("green", "yellow"))
    for number, colors in enumerate(palette, 1):
        direction = f"VD-R1-0{number}"
        for (target, scenario, basis), color in zip(
                (("390", "primary", "Approved home copy and normal data"),
                 ("1200", "stress", "Approved home copy with bounded dense data")), colors):
            capture = directions / f"vd-0{number}-{scenario}.png"
            capture.write_bytes(capture_fixture(color))
            rows.append(f"| {direction} | UI-001 | ready | {target} | {scenario} | {basis} | "
                        f"{capture.relative_to(root).as_posix()} @ sha256:{digest(capture)} | Distinct hierarchy {number} |")
        study = directions / f"vd-0{number}.html"
        study.write_text(_study_html(f"Direction {number}"), encoding="utf-8")
        studies.append(f"| {direction} | {study.relative_to(root).as_posix()} @ sha256:{digest(study)} | "
                       f"{STUDY_AUTHOR} | {STUDY_AUTHOR} | pass |")
    start, end = text.index("### Direction comparison"), text.index("### Required motion evidence")
    text = (text[:start] + "### Direction comparison\n\n" + "\n".join(rows) + "\n\n"
            + "\n".join(studies) + "\n\n" + text[end:])
    evidence = intermediate_receipt(root, text, ("560", "980"))
    text = text.replace("HiFi score:", f"Intermediate width check: PASS — evidence={evidence}\nHiFi score:", 1)
    gate = text.index("## Design System Need Gate")
    head, tail = text[:gate], text[gate:]
    tail = tail.replace("Decision: not_required", "Decision: required", 1)
    tail = re.sub(r"^Existing design-system pair disposition: none", f"Existing design-system pair disposition: {disposition}",
                  tail, flags=re.M)
    tail = re.sub(r"^Replacement visual contract when_not_required:.*$",
                  f"Package action: {action}\nCompiled design system pair: pending — design-system-compiler", tail, flags=re.M)
    ui.write_text(head + tail, encoding="utf-8")
    return ui, prd, hifi


def preflight(ui, root, prd, hifi):
    return checker._validate_for_design_system_preflight(ui, repo_root=root, prd_path=prd,
                                                         wireframes_path=None, hifi_path=hifi)


class UiDesignV3Tests(unittest.TestCase):
    def test_full_package_passes_compiler_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ui, prd, hifi = v3_publication(root)
            self.assertEqual("ui-design/3", checker.ui_contract_version(ui.read_text(encoding="utf-8")))
            self.assertEqual([], preflight(ui, root, prd, hifi))
            view, findings = checker.parse_ui_contract_view(ui.read_text(encoding="utf-8"))
            self.assertEqual([], findings)
            self.assertEqual("compile", view["gate"]["package_action"])
            # The pending marker never passes the ordinary gate.
            self.assertIn("only valid during the exact compiler preflight", "\n".join(checker.validate(
                ui, repo_root=root, prd_path=prd, hifi_path=hifi, require_visual_approved=True)))

    def test_package_gate_rejects_skips_and_mismatched_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ui, prd, hifi = v3_publication(root)
            base = ui.read_text(encoding="utf-8")
            cases = {
                "not_required": (base.replace("Decision: required", "Decision: not_required"),
                                 "requires Design System Need Gate Decision: required"),
                "no action": (re.sub(r"^Package action:.*\n", "", base, flags=re.M), "exactly one Package action"),
                "open action": (base.replace("Package action: compile", "Package action: skip"), "Package action must be one of"),
                "reuse without pair": (base.replace("Package action: compile", "Package action: reuse"),
                                       "Package action reuse requires existing pair disposition retain"),
            }
            for label, (text, expected) in cases.items():
                with self.subTest(label):
                    ui.write_text(text, encoding="utf-8")
                    self.assertIn(expected, "\n".join(preflight(ui, root, prd, hifi)))

    def test_studies_need_three_rendered_directions_by_one_self_checking_author(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ui, prd, hifi = v3_publication(root)
            base = ui.read_text(encoding="utf-8")
            rows =[line for line in base.splitlines() if line.startswith("| VD-R1-03 | docs/design/directions")]
            cases = {
                "single mode": (base.replace("Direction mode: three comparable directions", "Direction mode: one recommended direction"),
                                "requires Direction mode: three comparable directions"),
                "other checker": (base.replace(f"{STUDY_AUTHOR} | pass |", "independent reviewer | pass |", 1),
                                  "self-check must be made by its own author"),
                "split authors": (base.replace(rows[0], rows[0].replace(STUDY_AUTHOR, "second author")),
                                  "one frontend author"),
                "failed self-check": (base.replace(f"{STUDY_AUTHOR} | pass |", f"{STUDY_AUTHOR} | blocked |", 1),
                                      "self-check must be pass"),
                "missing study": (base.replace(rows[0] + "\n", ""), "exactly the three compared directions"),
                "outside round": (base.replace("docs/design/directions/round-1/vd-01.html", "docs/design/vd-01.html"),
                                  "docs/design/directions/<round>/<name>.html"),
            }
            for label, (text, expected) in cases.items():
                with self.subTest(label):
                    ui.write_text(text, encoding="utf-8")
                    self.assertIn(expected, "\n".join(preflight(ui, root, prd, hifi)))
            ui.write_text(base, encoding="utf-8")
            study = root / "docs/design/directions/round-1/vd-02.html"
            study.write_text(study.read_text(encoding="utf-8") + "<!-- edited -->", encoding="utf-8")
            self.assertIn("Direction study", "\n".join(preflight(ui, root, prd, hifi)))

    def test_study_html_must_be_self_contained(self):
        findings = "\n".join(checker.ui_design_v3.study_html_findings(
            _study_html("x").replace("</head>", '<link rel="stylesheet" href="https://cdn.invalid/a.css"></head>'),
            "docs/design/directions/r/x.html"))
        self.assertIn("must not load linked, imported or external resources", findings)

    def test_intermediate_widths_cover_every_adjacent_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ui, prd, hifi = v3_publication(root)
            self.assertEqual([], preflight(ui, root, prd, hifi))
            base = ui.read_text(encoding="utf-8")
            field = re.search(r"^Intermediate width check: PASS — evidence=(.+)$", base, re.M).group(1)

            def check(evidence):
                ui.write_text(base.replace(field, evidence), encoding="utf-8")
                return "\n".join(preflight(ui, root, prd, hifi))

            for label, targets, expected in (
                ("gap", ("560",), "between 768px and 1200px"),
                ("edge width", ("390", "980"), "strictly between two adjacent approved widths"),
            ):
                with self.subTest(label):
                    self.assertIn(expected, check(intermediate_receipt(root, base, targets)))
            with self.subTest("failed observation"):
                failed = [{"surface": "UI-001", "state": "ready", "target": "560", "result": "FAIL"}]
                self.assertIn("Intermediate width check evidence must record", check(
                    intermediate_receipt(root, base, ("560", "980"), results=failed)))
            with self.subTest("declared but unobserved width"):
                evidence = intermediate_receipt(root, base, ("560", "980"), results=[
                    {"surface": "UI-001", "state": "ready", "target": "560", "result": "PASS"}])
                receipt = root / "docs/evidence/hifi-intermediate-widths.json"
                data = json.loads(receipt.read_text(encoding="utf-8"))
                self.assertEqual("MISSING", data["result"])
                data["result"] = "PASS"  # a hand-edited summary must not supply coverage
                receipt.write_text(json.dumps(data), encoding="utf-8")
                self.assertIn("must observe exactly its matrix cases",
                              check(f"docs/evidence/hifi-intermediate-widths.json @ sha256:{digest(receipt)}"))
                self.assertTrue(evidence)
            with self.subTest("stale subject"):
                evidence = intermediate_receipt(root, base, ("560", "980"))
                output = root / "docs/evidence/hifi-intermediate-widths-output.json"
                data = json.loads(output.read_text(encoding="utf-8"))
                data["subject"]["sha256"] = "0" * 64
                output.write_text(json.dumps(data), encoding="utf-8")
                self.assertIn("Intermediate width check", check(evidence))
            with self.subTest("hand-written boolean record"):
                legacy = root / "docs/evidence/intermediate-widths.json"
                legacy.write_text(json.dumps({"schema": "ui-intermediate-widths/1", "subject": {}, "cases": [
                    {"surface": "UI-001", "width": 560, "between": [390, 768], "horizontalOverflow": False,
                     "clipping": False, "result": "PASS"}]}), encoding="utf-8")
                self.assertIn("Intermediate width check evidence has an invalid", check(
                    f"docs/evidence/intermediate-widths.json @ sha256:{digest(legacy)}"))
            ui.write_text(re.sub(r"^Intermediate width check:.*\n", "", base, flags=re.M), encoding="utf-8")
            self.assertIn("Intermediate width check must use", "\n".join(preflight(ui, root, prd, hifi)))

    def test_version_family_and_schema_mapping_stay_closed(self):
        self.assertEqual("design-system/4", checker.expected_design_system_schema("ui-design/3"))
        self.assertEqual("design-system/3", checker.expected_design_system_schema("ui-design/2"))
        self.assertEqual("design-system/2", checker.expected_design_system_schema("legacy"))
        with self.assertRaises(ValueError):
            checker.ui_contract_version("# UI Design Contract\n\nUI contract: ui-design/4\n")
        view, _ = checker.parse_ui_contract_view("# UI Design Contract\n\nUI contract: ui-design/2\n")
        self.assertNotIn("package_action", view["gate"])

    def test_product_preflight_accepts_only_known_ui_contracts(self):
        self.assertEqual("ui-design/3", check_product_package.parse_args(
            ["--prd", "p", "--architecture", "a", "--stack-decisions", "s", "--ui-contract", "ui-design/3"]).ui_contract)
        with self.assertRaises(ValueError):
            check_product_package.validate_texts("", "", "", ui_contract="ui-design/9")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, prd, _ = v3_publication(root)
            paths = (prd, root / "docs/product/architecture.md", root / "docs/product/stack-decisions.md")
            self.assertEqual(check_product_package.validate(*paths, require_filled=True, require_approved=True,
                                                            repo_root=root, ui_contract="ui-design/2"),
                             check_product_package.validate(*paths, require_filled=True, require_approved=True,
                                                            repo_root=root, ui_contract="ui-design/3"))


if __name__ == "__main__":
    unittest.main()
