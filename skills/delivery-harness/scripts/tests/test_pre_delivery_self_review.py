"""Keep the documented author-review handoff connected across skills."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = "pre-delivery-self-review.md"


class PreDeliverySelfReviewTests(unittest.TestCase):
    def test_all_stage_owners_link_the_shared_contract(self):
        for relative in (
            "skills/product-definition-builder/SKILL.md",
            "skills/ui-design-builder/SKILL.md",
            "skills/delivery-harness/SKILL.md",
            "skills/delivery-harness/references/installed-commands.md",
            "skills/delivery-harness/assets/templates/PROJECT_AGENTS.template.md",
        ):
            with self.subTest(path=relative):
                self.assertIn(REFERENCE, (ROOT / relative).read_text(encoding="utf-8"))

    def test_contract_preserves_review_order_and_evidence_boundaries(self):
        source = (ROOT / "skills/delivery-harness/references" / REFERENCE).read_text(encoding="utf-8")
        sections = ["## PRD Self-Review", "## UI Structure And Direction Self-Review",
                    "## HiFi Self-Review", "## Harness Entry"]
        offsets = [source.index(section) for section in sections]
        self.assertEqual(offsets, sorted(offsets))
        for boundary in ("present-day catch-up", "never claim the review happened before",
                         "A closed approval alone never exempts", "390, 768, 1024 and 1440",
                         "not a fifth authored target", "parent semantic handoff check"):
            self.assertIn(boundary, source)

    def test_every_readme_routes_initial_review_and_scoped_work(self):
        for name in ("README.md", "README.zh-TW.md", "README.zh-CN.md", "README.es.md"):
            with self.subTest(path=name):
                source = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn(REFERENCE, source)
                self.assertIn('productself[', source)
                self.assertIn('directionself[', source)
                self.assertIn('hifiself[', source)
                self.assertRegex(source, r'ProductGate -->\|"[^\n]+"\| Harness\n')
                self.assertRegex(source, r'pgate -->\|"[^\n]+"\| route\n')


if __name__ == "__main__":
    unittest.main()
