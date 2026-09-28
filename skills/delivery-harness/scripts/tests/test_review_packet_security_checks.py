#!/usr/bin/env python3
"""The security review packet carries the PLAN required checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
for path in (TESTS_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from render_review_packet import render_packet  # noqa: E402
from security_review_result import validate_security_review_result  # noqa: E402
from test_harness_manifest import valid_plan, valid_run  # noqa: E402
from test_security_review_result import valid_result  # noqa: E402


KEY = "c" * 64


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _contract(packet: str) -> dict:
    block = packet.split("## Contract", 1)[1].split("```json", 1)[1]
    return json.loads(block.split("```", 1)[0])


class SecurityPacketCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "test@example.com")
        _git(self.root, "config", "user.name", "Harness Test")
        (self.root / "file.txt").write_text("base\n", encoding="utf-8")
        _git(self.root, "add", "file.txt")
        _git(self.root, "commit", "-qm", "base")
        self.base = _git(self.root, "rev-parse", "HEAD")
        (self.root / "file.txt").write_text("head\n", encoding="utf-8")
        _git(self.root, "commit", "-qam", "head")
        self.head = _git(self.root, "rev-parse", "HEAD")

        self.plan = valid_plan()
        self.run = valid_run(self.plan)
        self.run["integration"]["batch_base_sha"] = self.base
        self.run["integration"]["integration_head_sha"] = self.head
        self.run["mission_states"]["M1"]["head_sha"] = self.head
        node = next(
            item for item in self.plan["graph"]["nodes"] if item["id"] == "N-REVIEW-M1"
        )
        node["review"]["type"] = "security"
        node["review"]["stage"] = "integration"
        self.plan["security_review"] = {
            "status": "required",
            "skill_slot": "code_security_verification",
            "reason": None,
            "required_checks": ["sec-deps"],
        }

    def execution(self, **overrides: object) -> dict:
        value = {
            "verifier_id": "sec-deps",
            "layer": "batch",
            "status": "PASS",
            "exit_code": 0,
            "execution_key": KEY,
            "context": {"head_sha": self.head},
        }
        value.update(overrides)
        return value

    def test_result_built_from_packet_checks_validates(self) -> None:
        self.run["verifier_executions"] = [
            self.execution(),
            self.execution(execution_key="d" * 64, context={"head_sha": self.base}),
        ]

        contract = _contract(render_packet(self.plan, self.run, "N-REVIEW-M1", self.root))

        self.assertEqual(
            [{"id": "sec-deps", "execution_key": KEY}], contract["required_checks"]
        )
        result = valid_result(reviewed_sha=self.head, base_sha=self.base)
        result["checks"] = contract["required_checks"]
        self.assertEqual(
            [],
            validate_security_review_result(result, required_checks=["sec-deps"]),
        )

    def test_missing_or_stale_execution_gives_null_key_that_cannot_validate(self) -> None:
        for executions in (
            [],
            [self.execution(context={"head_sha": self.base})],
            [self.execution(status="FAIL", exit_code=1)],
            [self.execution(), self.execution(execution_key="d" * 64)],
        ):
            with self.subTest(executions=executions):
                self.run["verifier_executions"] = executions
                contract = _contract(
                    render_packet(self.plan, self.run, "N-REVIEW-M1", self.root)
                )
                self.assertEqual(
                    [{"id": "sec-deps", "execution_key": None}],
                    contract["required_checks"],
                )
                result = valid_result(reviewed_sha=self.head, base_sha=self.base)
                result["checks"] = contract["required_checks"]
                self.assertTrue(
                    validate_security_review_result(result, required_checks=["sec-deps"])
                )

    def test_non_security_packet_has_no_required_checks(self) -> None:
        self.run["verifier_executions"] = [self.execution()]
        node = next(
            item for item in self.plan["graph"]["nodes"] if item["id"] == "N-REVIEW-M1"
        )
        node["review"]["type"] = "backend_code"

        contract = _contract(render_packet(self.plan, self.run, "N-REVIEW-M1", self.root))

        self.assertEqual([], contract["required_checks"])


if __name__ == "__main__":
    unittest.main()
