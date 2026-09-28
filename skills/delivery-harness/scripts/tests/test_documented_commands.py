"""Exercise consumer command examples with real parsers and source scans."""

import contextlib
import io
import json
from pathlib import Path
import re
import shlex
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import check_ui_contract  # noqa: E402
import harness_transition  # noqa: E402


class DocumentedCommandTests(unittest.TestCase):
    def commands(self, reference, script):
        text = (SCRIPTS.parent / "references" / reference).read_text(encoding="utf-8")
        examples = [shlex.split(value) for value in re.findall(r"`(python [^`]+)`", text)
                    if f"/{script}" in value]
        self.assertTrue(examples, f"Missing executable {script} example in {reference}")
        return examples

    def test_documented_review_skip_parses_without_state_mutation(self):
        examples = self.commands("verification-gates.md", "harness_transition.py")
        skips = [parts for parts in examples if "skip-integration-review" in parts]
        self.assertEqual(1, len(skips))
        parsed = harness_transition.build_parser().parse_args(skips[0][2:])
        self.assertEqual("skip-integration-review", parsed.command)
        self.assertEqual(Path("<root>"), parsed.repo_root)
        self.assertEqual(Path("<PLAN.md>"), parsed.plan)
        self.assertEqual(Path("<RUN.md>"), parsed.run)

    def test_documented_ui_scans_check_real_source_and_reject_raw_values(self):
        for reference in ("ui-implementation-contract.md", "verification-gates.md"):
            for command in self.commands(reference, "check_ui_contract.py"):
                with self.subTest(reference=reference), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    source = root / "src"
                    source.mkdir()
                    page = source / "page.css"
                    page.write_text(".content { color: var(--text); }", encoding="utf-8")
                    registry = root / "design-system.json"
                    registry.write_text(json.dumps({"tokenSources": [], "primitiveSources": [],
                                                    "primitives": {}, "motionVariants": [],
                                                    "viewports": [390, 768, 1440]}),
                                        encoding="utf-8")
                    values = {"<root>": str(root), "<design-system.json>": str(registry),
                              "<product-source-dir>": str(source)}
                    argv = [values.get(part, part) for part in command[2:]]
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        result = check_ui_contract.main(argv)
                    self.assertEqual(0, result, output.getvalue())
                    page.write_text(".content { color: #123456; padding: 13px; }", encoding="utf-8")
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(1, check_ui_contract.main(argv))


if __name__ == "__main__":
    unittest.main()
