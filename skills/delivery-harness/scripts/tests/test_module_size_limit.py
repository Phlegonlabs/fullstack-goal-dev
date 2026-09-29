"""Consumer AGENTS bootstrap checks; no Harness-source size enforcement."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from configure_project_context import configure_context  # noqa: E402


SKILL_ROOT = Path(__file__).resolve().parents[2]
AGENTS_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "PROJECT_AGENTS.template.md"
CLAUDE_TEMPLATE = SKILL_ROOT / "assets" / "templates" / "PROJECT_CLAUDE.template.md"


class ModuleSizeLimitTests(unittest.TestCase):
    def test_shared_template_states_the_new_module_cap(self) -> None:
        template = AGENTS_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("### Module Size Limit", template)
        self.assertIn(
            "New code modules, including tests, are limited to 500 physical lines.",
            template,
        )
        self.assertIn("not the Harness skill-source repository", template)
        self.assertIn("### Keep It Simple (KISS / YAGNI)", template)
        self.assertIn("### First Principles", template)
        self.assertIn("Split a module before it exceeds the limit", template)
        self.assertIn("Do not write speculative compatibility code", template)
        self.assertNotIn("checkpoint, not a hard limit", template)

    def test_configurator_preserves_an_existing_agents_file(self) -> None:
        agents_bytes = b"# Owner rules\n- Keep this exact rule.\n"
        claude_bytes = b"@AGENTS.md\n"
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "AGENTS.md").write_bytes(agents_bytes)
            (root / "CLAUDE.md").write_bytes(claude_bytes)

            result = configure_context(root, AGENTS_TEMPLATE, CLAUDE_TEMPLATE)

            self.assertEqual([], result["created"])
            self.assertEqual(["AGENTS.md", "CLAUDE.md"], result["preserved"])
            self.assertEqual(agents_bytes, (root / "AGENTS.md").read_bytes())
            self.assertEqual(claude_bytes, (root / "CLAUDE.md").read_bytes())

    def test_consumer_bootstrap_installs_template_without_refactoring_code(self) -> None:
        source_bytes = b"# Existing consumer module\n" * 501
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "existing.py"
            source.write_bytes(source_bytes)
            result = configure_context(root, AGENTS_TEMPLATE, CLAUDE_TEMPLATE)
            self.assertEqual(["AGENTS.md", "CLAUDE.md"], result["created"])
            self.assertEqual(AGENTS_TEMPLATE.read_bytes(), (root / "AGENTS.md").read_bytes())
            self.assertEqual(source_bytes, source.read_bytes())


if __name__ == "__main__":
    raise SystemExit(unittest.main())
