from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "ci_diff_base.py"


class CIDiffBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name).resolve()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "ci@example.com")
        self.git("config", "user.name", "CI")
        self.write("clean.txt", "clean line\n")
        self.git("add", "clean.txt")
        self.git("commit", "-m", "base")
        self.base = self.rev_parse("HEAD")
        self.write("dirty.txt", "candidate line with trailing spaces   \n")
        self.git("add", "dirty.txt")
        self.git("commit", "-m", "candidate")
        self.candidate = self.rev_parse("HEAD")

    def tearDown(self) -> None:
        # TemporaryDirectory can otherwise race Windows Git read handles.
        self._temporary.cleanup()

    def git(self, *arguments: str) -> str:
        result = self.git_raw(*arguments)
        self.assertEqual(0, result.returncode, result.stderr)
        return result.stdout.strip()

    def git_raw(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )
        return result

    def rev_parse(self, reference: str) -> str:
        return self.git("rev-parse", reference)

    def write(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8", newline="\n")

    def helper(self, event: str, candidate: str, base: str | None) -> subprocess.CompletedProcess[str]:
        arguments = [
            "python",
            str(SCRIPT),
            "resolve",
            "--event",
            event,
            "--candidate",
            candidate,
        ]
        if base is not None:
            arguments.extend(["--base", base])
        return subprocess.run(
            arguments,
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )

    def test_manual_base_requires_a_verified_ancestor(self) -> None:
        result = self.helper("workflow_dispatch", self.candidate, self.base)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.base, result.stdout.strip())
        whitespace = self.git_raw("diff", "--check", self.base, self.candidate).stdout
        self.assertIn("trailing whitespace", whitespace)

    def test_manual_base_rejects_an_unrelated_root(self) -> None:
        self.write("unrelated.txt", "unrelated\n")
        self.git("add", "unrelated.txt")
        self.git("checkout", "--orphan", "unrelated")
        self.git("commit", "-m", "unrelated root")
        unrelated = self.rev_parse("HEAD")
        result = self.helper("workflow_dispatch", unrelated, self.base)
        self.assertEqual(2, result.returncode)
        self.assertIn("not an ancestor", result.stderr)

    def test_pull_request_and_push_bases_resolve(self) -> None:
        for event in ("pull_request", "merge_group"):
            with self.subTest(event=event):
                result = self.helper(event, self.candidate, self.base)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(self.base, result.stdout.strip())
        existing_push = self.helper("push", self.candidate, self.base)
        self.assertEqual(0, existing_push.returncode, existing_push.stderr)
        self.assertEqual(self.base, existing_push.stdout.strip())

    def test_pull_request_uses_merge_base_to_exclude_advanced_base_only_edits(self) -> None:
        self.git("checkout", "-q", "--detach", self.base)
        self.write("base_only.txt", "advanced on base with trailing spaces   \n")
        self.git("add", "base_only.txt")
        self.git("commit", "-m", "advanced base")
        advanced_base = self.rev_parse("HEAD")
        merge_base = self.git("merge-base", advanced_base, self.candidate)
        result = self.helper("pull_request", self.candidate, advanced_base)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(merge_base, result.stdout.strip())
        self.assertNotEqual(advanced_base, result.stdout.strip())
        direct_files = self.git("diff", "--name-only", advanced_base, self.candidate)
        merge_files = self.git("diff", "--name-only", merge_base, self.candidate)
        self.assertIn("base_only.txt", direct_files)
        self.assertIn("dirty.txt", direct_files)
        self.assertIn("dirty.txt", merge_files)
        self.assertNotIn("base_only.txt", merge_files)

    def test_initial_push_uses_git_empty_tree_without_self_diff(self) -> None:
        result = self.helper("push", self.candidate, "0" * 40)
        self.assertEqual(0, result.returncode, result.stderr)
        empty_tree = result.stdout.strip()
        self.assertEqual(40, len(empty_tree))
        whitespace = self.git_raw("diff", "--check", empty_tree, self.candidate).stdout
        self.assertIn("trailing whitespace", whitespace)

    def test_missing_or_unresolvable_bases_fail_closed(self) -> None:
        missing = self.helper("workflow_dispatch", self.candidate, None)
        self.assertEqual(2, missing.returncode)
        self.assertIn("requires base_sha", missing.stderr)
        unresolved = self.helper("pull_request", self.candidate, "f" * 40)
        self.assertEqual(2, unresolved.returncode)
        self.assertIn("failed", unresolved.stderr)


if __name__ == "__main__":
    unittest.main()
