"""Seeded project rules must agree with the canonical Harness contracts."""

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


if __name__ == "__main__":
    unittest.main()
