"""Seeded project rules must agree with the canonical Harness contracts."""

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = SKILL_ROOT.parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


class ProjectTemplateRuleTests(unittest.TestCase):
    def test_routine_maintenance_is_limited_to_none_or_style_ui_impact(self) -> None:
        # review-workflow.md accepts a maintenance record only with UI impact
        # none or style; structural changes keep their design gates.
        template = read("assets/templates/PROJECT_AGENTS.template.md")
        self.assertIn("Routine maintenance with UI impact `none` or `style`", template)
        self.assertIn("A structural impact (`structure` or `both`) follows affected design gates", template)
        self.assertNotIn("Routine maintenance updates the actual product", template)

        skill = read("SKILL.md")
        self.assertIn("Routine maintenance (UI impact `none` or `style`)", skill)
        self.assertIn("`structure`/`both` changes use the affected design gates", skill)

        contract = read("references/ui-implementation-contract.md")
        self.assertIn("Routine maintenance is valid only with UI impact `none` or `style`", contract)
        self.assertIn("In routine maintenance, which allows only `none` or `style`", contract)

        agents = REPO_ROOT / "AGENTS.md"
        if agents.is_file() and (REPO_ROOT / "install.sh").is_file():
            self.assertIn(
                "Routine maintenance with UI impact `none` or `style`",
                agents.read_text(encoding="utf-8"),
            )

    def test_managed_default_branch_must_be_main(self) -> None:
        # archive_run.py and the promotion contract bind only `main` refs, so
        # the template states that as a precondition instead of asking agents
        # to resolve an arbitrary default branch name.
        template = read("assets/templates/PROJECT_AGENTS.template.md")
        self.assertIn("Managed Harness requires the default branch to be named `main`", template)
        self.assertIn("If it differs, stop before managed work and ask the owner.", template)
        self.assertNotIn("never assume its name", template)
        self.assertNotIn("real default branch", template)

    def test_repo_restore_rule_uses_the_installer(self) -> None:
        # The installers have no restore mode, and manual moves are banned, so
        # a bad install is replaced by installing the previous release.
        agents = REPO_ROOT / "AGENTS.md"
        if not (agents.is_file() and (REPO_ROOT / "install.sh").is_file()):
            self.skipTest("no source repository checkout")
        text = agents.read_text(encoding="utf-8")
        self.assertIn(
            "restore by re-running the installer from a checkout of the previous release tag",
            text,
        )
        self.assertNotIn("Restore the backup if verification fails", text)

    def test_repo_instructions_cover_every_shared_template_section(self) -> None:
        # The handoff audit compares repo AGENTS.md/CLAUDE.md with the seeded
        # templates. Each template section is present or named as a
        # deliberate source-repo omission, so the audit has a clear answer.
        agents = REPO_ROOT / "AGENTS.md"
        if not (agents.is_file() and (REPO_ROOT / "install.sh").is_file()):
            self.skipTest("no source repository checkout")
        root_agents = agents.read_text(encoding="utf-8")
        omitted = root_agents.split("This source repository intentionally omits", 1)[1]
        omitted = omitted.split("\n", 1)[0]
        headings = re.findall(r"^## (.+)$", root_agents, re.MULTILINE)
        template = read("assets/templates/PROJECT_AGENTS.template.md")
        for heading in re.findall(r"^## (.+)$", template, re.MULTILINE):
            with self.subTest(heading=heading):
                self.assertTrue(heading in headings or heading in omitted, heading)
        self.assertIn("Select the record before implementation", root_agents)

        root_claude = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        claude_template = read("assets/templates/PROJECT_CLAUDE.template.md")
        for line in claude_template.splitlines():
            if line.startswith("- "):
                with self.subTest(line=line[:60]):
                    self.assertIn(line, root_claude)


if __name__ == "__main__":
    unittest.main()
