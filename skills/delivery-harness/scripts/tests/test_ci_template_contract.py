from __future__ import annotations

import unittest
from pathlib import Path


TEMPLATE = (
    Path(__file__).resolve().parents[2]
    / "assets/templates/PROJECT_CI.template.yml"
)


class ProjectCITemplateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.template = TEMPLATE.read_text(encoding="utf-8")

    def test_feature_pushes_verify_once_through_pull_request(self) -> None:
        triggers = self.template.split("permissions:", 1)[0]
        self.assertIn("pull_request:", triggers)
        self.assertIn("merge_group:", triggers)
        self.assertIn("<protected-branch-1>", triggers)
        self.assertIn("<protected-branch-2>", triggers)
        self.assertIn("workflow_dispatch:", triggers)
        self.assertNotIn("- '**'", triggers)

    def test_manual_release_binds_a_canonical_full_sha(self) -> None:
        self.assertIn("release_sha:", self.template)
        self.assertIn("Full 40-character commit SHA", self.template)
        self.assertIn(
            "CANDIDATE_SHA: ${{ inputs.release_sha || github.event.pull_request.head.sha || github.sha }}",
            self.template,
        )
        self.assertEqual(2, self.template.count("ref: ${{ env.CANDIDATE_SHA }}"))
        self.assertIn("^[0-9a-f]{40}$", self.template)
        self.assertEqual(1, self.template.count('test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"'))

    def test_release_concurrency_is_frozen_by_sha(self) -> None:
        concurrency = self.template.split("concurrency:", 1)[1].split("env:", 1)[0]
        self.assertIn("inputs.release_sha", concurrency)
        self.assertIn("format('pr-{0}', github.event.pull_request.number)", concurrency)
        self.assertIn("github.ref", concurrency)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", concurrency)

    def test_diff_base_comes_from_the_event(self) -> None:
        self.assertIn("github.event.pull_request.base.sha", self.template)
        self.assertIn("github.event.merge_group.base_sha", self.template)
        self.assertIn("origin/$GITHUB_REF_NAME...HEAD", self.template)
        self.assertNotIn('base="origin/main"', self.template)

    def test_verify_is_a_stable_strict_aggregate(self) -> None:
        verify = self.template.split("\n  verify:\n", 1)[1]
        self.assertIn("needs: [checks, e2e]", verify)
        self.assertIn("if: always()", verify)
        self.assertIn("CHECKS_RESULT: ${{ needs.checks.result }}", verify)
        self.assertIn("E2E_RESULT: ${{ needs.e2e.result }}", verify)
        self.assertIn('[ "$result" != success ]', verify)

    def test_template_stays_consumer_neutral(self) -> None:
        self.assertIn("<verification-command>", self.template)
        self.assertIn("<e2e-command>", self.template)
        self.assertIn("<e2e-artifact-path>", self.template)
        self.assertNotIn("product-delivery-harness/scripts", self.template)
        self.assertNotIn("PDH_REQUIRE_BROWSER_TESTS", self.template)
        self.assertNotIn("claude", self.template.casefold())
        self.assertNotIn("glm-", self.template.casefold())


if __name__ == "__main__":
    unittest.main()
