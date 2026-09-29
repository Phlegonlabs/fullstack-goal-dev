from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from ci_test_shards import balance_files, candidate_files, discover_files


def find_repo_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".github/workflows/harness-ci.yml").is_file():
            return candidate
    raise AssertionError("source workflow is unavailable")


class CICandidateGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = find_repo_root()
        self.workflow = (self.repo_root / ".github/workflows/harness-ci.yml").read_text(
            encoding="utf-8"
        )

    def test_feature_push_and_pr_do_not_duplicate_ci(self) -> None:
        trigger = self.workflow.split("jobs:", 1)[0]
        self.assertIn("pull_request:", trigger)
        self.assertIn("merge_group:", trigger)
        self.assertIn("- main", trigger)
        self.assertIn("- development", trigger)
        self.assertNotIn("- '**'", trigger)

    def test_all_events_share_one_canonical_candidate(self) -> None:
        self.assertIn(
            "CANDIDATE_SHA: ${{ inputs.candidate_sha || github.event.pull_request.head.sha || github.sha }}",
            self.workflow,
        )
        self.assertEqual(10, self.workflow.count("ref: ${{ env.CANDIDATE_SHA }}"))
        self.assertEqual(7, self.workflow.count('test "$(git rev-parse HEAD)" = "$CANDIDATE_SHA"'))
        self.assertEqual(2, self.workflow.count('-ne $env:CANDIDATE_SHA'))
        self.assertIn("Full 40-character commit SHA", self.workflow)
        self.assertIn("^[0-9a-f]{40}$", self.workflow)

    def test_release_concurrency_is_frozen_by_candidate_sha(self) -> None:
        concurrency = self.workflow.split("concurrency:", 1)[1].split("env:", 1)[0]
        self.assertIn("inputs.candidate_sha", concurrency)
        self.assertIn("format('pr-{0}', github.event.pull_request.number)", concurrency)
        self.assertIn("github.ref", concurrency)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", concurrency)

    def test_diff_uses_actual_event_base(self) -> None:
        self.assertIn("github.event.pull_request.base.sha", self.workflow)
        self.assertIn("github.event.merge_group.base_sha", self.workflow)
        self.assertIn("origin/$GITHUB_REF_NAME...HEAD", self.workflow)
        self.assertNotIn('base="origin/main"', self.workflow)

    def test_validate_requires_every_matrix_result(self) -> None:
        validate = self.workflow.split("\n  validate:\n", 1)[1]
        required_jobs = [
            "quality",
            "linux-harness",
            "linux-other",
            "linux-browser",
            "golden-path",
            "macos-harness",
            "macos-other",
            "windows-native",
            "windows-installer",
        ]
        for job in required_jobs:
            with self.subTest(job=job):
                self.assertIn(f"- {job}", validate)
                self.assertIn(f"_RESULT: ${{{{ needs.{job}.result }}}}", validate)
        self.assertIn("if: always()", validate)
        self.assertIn("ci_test_shards.py gate", validate)

    def test_posix_shards_discover_harness_files_exactly_once(self) -> None:
        discovered = discover_files(self.repo_root, "harness")
        timings = {
            name: float(index + 1)
            for index, name in enumerate(sorted(discovered, reverse=True))
        }
        shards = balance_files(discovered, timings, 4)
        planned = [name for shard in shards for name in shard]
        self.assertEqual(discovered, sorted(planned))
        self.assertEqual(len(discovered), len(set(planned)))
        self.assertEqual(4, len(shards))
        self.assertTrue(all(shards))

    def test_windows_native_shard_set_is_explicit_and_complete(self) -> None:
        discovered = discover_files(self.repo_root, "harness")
        selected = candidate_files(self.repo_root, "harness", "windows", discovered)
        timings = {name: 1.0 for name in selected}
        shards = balance_files(selected, timings, 4)
        planned = [name for shard in shards for name in shard]
        self.assertEqual(12, len(selected))
        self.assertEqual(sorted(selected), sorted(planned))
        self.assertTrue(all(shards))


if __name__ == "__main__":
    unittest.main()
