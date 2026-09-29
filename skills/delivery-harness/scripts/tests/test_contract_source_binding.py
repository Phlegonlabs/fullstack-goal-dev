"""Harness 0.59 binds ui-design/3, design-system/4 and one frozen derived HTML package.

Older pins keep their contracts: 0.56-0.58 consume ui-design/2 only. Fixture
bytes are synthetic validator inputs, not product approvals.
"""
from contextlib import contextmanager
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import harness_contract_join as join  # noqa: E402

SKILLS = Path(__file__).resolve().parents[3]


@contextmanager
def _sibling_paths():
    """Expose sibling-suite fixtures only while they run.

    This module sorts before test_skill_contract; a lingering sibling test dir
    would make discovery import the wrong suite's module of that name.
    """
    saved = list(sys.path)
    try:
        for folder in ("ui-design-builder/scripts/tests", "ui-design-builder/scripts",
                       "design-system-compiler/scripts/tests", "design-system-compiler/scripts",
                       "product-definition-builder/scripts/tests"):
            sys.path.insert(0, str(SKILLS / folder))
        yield
    finally:
        sys.path[:] = saved


def _fixtures():
    with _sibling_paths():
        # Import the sibling fixtures first: the strict-authority module's own
        # imports rewrite sys.path.
        import test_design_system_showcase as showcase_tests
        from test_ui_design_v3 import v3_publication
        import test_harness_strict_authority as legacy
        return legacy, showcase_tests, v3_publication


def _run_version(run, version):
    run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = version


class VersionSelectionTests(unittest.TestCase):
    def test_each_pin_consumes_exactly_one_ui_contract(self):
        def errors(version, pin, retained=False, current=True):
            run = None if pin is None else {"runtime_capabilities": {"runtime_adapter": {
                "version_gate": {"required_harness_version": pin}}}}
            return "\n".join(join._ui_contract_version_errors(version, run=run, current=current, retained=retained))

        self.assertEqual("", errors("ui-design/3", "0.59.0"))
        self.assertEqual("", errors("ui-design/3", "0.59.1-rc.1"))
        self.assertIn("requires UI contract: ui-design/3", errors("ui-design/2", "0.59.0"))
        self.assertEqual("", errors("ui-design/2", "0.59.0", retained=True))
        self.assertIn("pinned pre-0.59 RUN cannot consume ui-design/3", errors("ui-design/3", "0.58.0"))
        self.assertEqual("", errors("ui-design/2", "0.58.0"))
        self.assertIn("Harness 0.56+ requires UI contract: ui-design/2", errors("legacy", "0.59.0"))
        self.assertIn("pinned legacy RUN cannot consume ui-design/3", errors("ui-design/3", "0.55.0", current=False))
        self.assertEqual("", errors("ui-design/3", None))
        self.assertEqual("", errors("ui-design/2", None))
        self.assertFalse(join.ui_design_v3_required({"runtime_capabilities": {"runtime_adapter": {
            "version_gate": {"required_harness_version": "0.59"}}}}))


class FrozenPackageJoinTests(unittest.TestCase):
    def fixture(self, root, *, pin="0.59.0", preview=True):
        legacy, showcase_tests, _ = _fixtures()
        plan, run, _ = legacy.StrictAuthorityJoinTests._ui_fixture(root, required=False)
        # Rebuild the UI package as ui-design/3 with a real design-system/4 pair.
        with _sibling_paths():
            _, design, hifi = showcase_tests.PairIntegrationTests.build(None, root)
            from render_design_system_preview import render_view
        markdown, registry = design / "design-system.md", design / "design-system.json"
        ui = design / "ui-design.md"
        digest = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (markdown, registry)}
        ui.write_text(ui.read_text(encoding="utf-8").replace(
            "Compiled design system pair: pending — design-system-compiler",
            f"Compiled design system pair: docs/design/design-system.md @ sha256:{digest[markdown]} "
            f"and docs/design/design-system.json @ sha256:{digest[registry]}"), encoding="utf-8")
        view = design / "design-system-preview.html"
        view.write_bytes(render_view(registry.read_bytes(), markdown.read_bytes(), root).encode("utf-8"))
        paths = {"prd": root / "docs/product/PRD.md", "architecture": root / "docs/product/architecture.md",
                 "stack decisions": root / "docs/product/stack-decisions.md", "ui design": ui,
                 "approved ui target": hifi, "design system": markdown, "design system json": registry}
        if preview:
            paths["design system preview"] = view
        plan["sources"] = [legacy.StrictAuthorityJoinTests._row("SRC-" + str(index), kind, path, root)
                           for index, (kind, path) in enumerate(paths.items())]
        for trace in plan["traces"]:
            trace["source_ids"] = ["SRC-0"]
        _run_version(run, pin)
        return plan, run, view, legacy

    def test_new_full_ui_needs_ui_design_three_and_its_frozen_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, view, _ = self.fixture(root)
            findings = join.validate_frozen_contract_joins(plan, root, run=run)
            # harness_design_contract.py (outside this change's scope) still routes
            # design-system/4 through its schema-1 registry check; the parent owns
            # that two-line fix. Nothing else may fail for a complete package.
            self.assertLessEqual(set(findings), {"design-system.json schema must be 'design-system/1'"})
            view.write_bytes(view.read_bytes() + b"<!-- hand edit -->")
            plan["sources"][-1]["content_sha256"] = hashlib.sha256(view.read_bytes()).hexdigest()
            self.assertIn("frozen design-system-preview.html is stale or modified",
                          "\n".join(join.validate_frozen_contract_joins(plan, root, run=run)))

    def test_missing_html_and_older_pins_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, _, _ = self.fixture(root, preview=False)
            self.assertIn("requires exactly one frozen design-system-preview.html",
                          "\n".join(join.validate_frozen_contract_joins(plan, root, run=run)))
            _run_version(run, "0.58.0")
            self.assertIn("pinned pre-0.59 RUN cannot consume ui-design/3",
                          "\n".join(join.validate_frozen_contract_joins(plan, root, run=run)))

    def test_headless_plan_cannot_freeze_the_html_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, _, _ = self.fixture(root)
            plan["ui_surfaces"] = []
            self.assertIn("headless PLAN must not freeze design-system-preview source",
                          "\n".join(join.validate_frozen_contract_joins(plan, root, run=run)))

    def test_enhancement_record_keeps_a_retained_ui_design_two_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy, _, _ = _fixtures()
            plan, _, _ = legacy.StrictAuthorityJoinTests._ui_fixture(root, required=False)
            record = root / "docs/epics/EPIC-enhancement.md"
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text("```\nDesign workflow: maintenance\n```\nDesign workflow: enhancement\n", encoding="utf-8")
            for arguments in (("init", "-q"), ("config", "core.autocrlf", "false"), ("add", "docs/epics/EPIC-enhancement.md"),
                              ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "record")):
                subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True, timeout=15)
            row = legacy.StrictAuthorityJoinTests._row("SRC-TASK", "task record", record, root)
            row["source_revision"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                                    capture_output=True, text=True, timeout=15).stdout.strip()
            plan["sources"].append(row)
            self.assertEqual("enhancement", join._frozen_task_workflow(plan, root))
            plan["sources"].pop()
            self.assertIsNone(join._frozen_task_workflow(plan, root))

    def test_source_spec_names_the_canonical_html_path(self):
        spec = join._STRICT_SOURCE_SPECS["design-system-preview"]
        self.assertEqual(("design system preview", "docs/design/design-system-preview.html"),
                         (spec["kind"], spec["canonical"]))
        self.assertEqual({"ui-design/3": "design-system/4", "ui-design/2": "design-system/3"},
                         join.DESIGN_SYSTEM_SCHEMA_BY_UI)


if __name__ == "__main__":
    unittest.main()
