#!/usr/bin/env python3
"""Focused tests for the dual-branch PLAN policy and release-source marker."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from branch_policy import (  # noqa: E402
    DUAL_BRANCH_MARKER,
    has_prior_archive_candidate_source,
    validate_branch_policy_ancestry,
    validate_branch_policy_join,
    validate_branch_policy_shape,
)
from manifest_fixtures import valid_plan, valid_run  # noqa: E402


ARCHITECTURE = "# Architecture\n\n## Release Targets\n\n" + DUAL_BRANCH_MARKER + "\n"


def branch_policy(kind: str = "ordinary", base_sha: str = "a" * 40) -> dict[str, str]:
    protected = "development" if kind == "ordinary" else "main"
    return {
        "protocol": "dual-branch/1",
        "kind": kind,
        "base_ref": f"refs/remotes/origin/{protected}",
        "base_sha": base_sha,
    }


def run_at(version: str) -> dict[str, object]:
    plan = valid_plan()
    run = valid_run(plan)
    gate = run["runtime_capabilities"]["runtime_adapter"]["version_gate"]
    gate["required_harness_version"] = version
    return run


class BranchPolicyTests(unittest.TestCase):
    def test_old_and_malformed_pins_do_not_require_policy_or_marker(self) -> None:
        plan = valid_plan()
        with tempfile.TemporaryDirectory() as directory:
            for version in ("0.58.0", None, "broken", "0.6.0"):
                run = valid_run(plan)
                gate = run["runtime_capabilities"]["runtime_adapter"]["version_gate"]
                if version is None:
                    gate.pop("required_harness_version")
                else:
                    gate["required_harness_version"] = version
                self.assertEqual(
                    [],
                    validate_branch_policy_join(plan, "# Architecture\n", directory, run=run),
                )

    def test_current_join_requires_exact_shape_and_marker(self) -> None:
        plan = valid_plan()
        errors = validate_branch_policy_join(
            plan,
            "# Architecture\n",
            ".",
            run=run_at("0.59.0"),
        )
        self.assertTrue(any("active 'Release source policy: dual-branch/1'" in item for item in errors), errors)
        self.assertTrue(any("requires a branch policy object" in item for item in errors), errors)

        plan["branch_policy"] = branch_policy("ordinary", "b" * 40)
        plan["branch_policy"]["base_ref"] = "refs/remotes/origin/main"
        errors = validate_branch_policy_join(
            plan, ARCHITECTURE, ".", run=run_at("0.59.0")
        )
        self.assertTrue(any("ordinary base must be" in item for item in errors), errors)

        for invalid in (
            {"protocol": "dual-branch/2", "kind": "ordinary", "base_ref": "refs/remotes/origin/development", "base_sha": "a" * 40},
            {"protocol": "dual-branch/1", "kind": "release", "base_ref": "refs/remotes/origin/development", "base_sha": "a" * 40},
            {"protocol": "dual-branch/1", "kind": "ordinary", "base_ref": "refs/heads/development", "base_sha": "a" * 40},
            {"protocol": "dual-branch/1", "kind": "ordinary", "base_ref": "refs/remotes/origin/main", "base_sha": "a" * 40},
            {"protocol": "dual-branch/1", "kind": "ordinary", "base_ref": "refs/remotes/origin/development", "base_sha": "abc"},
        ):
            with self.subTest(policy=invalid):
                errors = validate_branch_policy_shape({"branch_policy": invalid})
                self.assertTrue(errors)

    def test_current_join_proves_local_frozen_base_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", "-b", "feature"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Branch Test"], cwd=root, check=True)
            (root / "base.txt").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "base.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            (root / "candidate.txt").write_text("candidate\n", encoding="utf-8")
            subprocess.run(["git", "add", "candidate.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=root, check=True)
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            subprocess.run(["git", "update-ref", "refs/remotes/origin/development", base], cwd=root, check=True)

            plan = valid_plan()
            plan["branch_policy"] = branch_policy(base_sha=base)
            run = run_at("0.59.0")
            run["integration"]["batch_base_sha"] = head
            run["integration"]["integration_head_sha"] = head
            self.assertEqual(
                [], validate_branch_policy_join(plan, ARCHITECTURE, root, run=run)
            )

            stale = branch_policy(base_sha="c" * 40)
            errors = validate_branch_policy_ancestry(
                {"branch_policy": stale}, root, run=run
            )
            self.assertTrue(any("is not an ancestor" in item for item in errors), errors)

            # A later wave may advance the integration head, but the frozen
            # PLAN base remains the original commit.
            run["integration"]["batch_base_sha"] = base
            self.assertEqual(
                [], validate_branch_policy_ancestry(plan, root, run=run)
            )

    def test_exact_prior_archive_correction_is_exempt(self) -> None:
        plan = valid_plan()
        source = {
            "id": "SRC-PRIOR-A",
            "kind": "prior archive candidate",
            "location": "archive/RUN/ARCHIVE_RECEIPT.json",
            "owner": "parent",
            "status": "frozen",
            "content_sha256": "f" * 64,
            "source_revision": "d" * 40,
            "staged_revision": None,
            "notes": "exact failed archive candidate",
        }
        self.assertFalse(has_prior_archive_candidate_source(plan))
        plan["sources"].append(source)
        self.assertTrue(has_prior_archive_candidate_source(plan))
        self.assertEqual(
            [], validate_branch_policy_join(plan, "# Architecture\n", ".", run=run_at("0.59.0"))
        )

        source["source_revision"] = "not-a-sha"
        self.assertFalse(has_prior_archive_candidate_source(plan))
        errors = validate_branch_policy_join(plan, "# Architecture\n", ".", run=run_at("0.59.0"))
        self.assertTrue(any("active 'Release source policy" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
