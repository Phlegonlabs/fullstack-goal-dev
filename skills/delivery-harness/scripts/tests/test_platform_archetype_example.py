#!/usr/bin/env python3
"""The worked M1 mission in platform-archetypes.md must stay valid to copy."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import harness_core  # noqa: E402

ARCHETYPES = SCRIPTS_DIR.parent / "references" / "platform-archetypes.md"


def worked_mission() -> dict:
    text = ARCHETYPES.read_text(encoding="utf-8")
    start = text.index("```json", text.index("### Worked `M1 workspace-foundation`")) + len("```json")
    return json.loads(text[start : text.index("```", start)])


class WorkedMissionVerifierTests(unittest.TestCase):
    def test_every_verifier_declares_execution_and_exit_0(self) -> None:
        mission = worked_mission()
        verifiers = [
            *mission["worker_verifiers"],
            *mission["integration_verifiers"],
            *(verifier for task in mission["tasks"] for verifier in task["verifiers"]),
        ]
        self.assertEqual(len(verifiers), 5)
        for verifier in verifiers:
            with self.subTest(verifier=verifier["id"]):
                errors: list = []
                harness_core._validate_verifier(
                    errors,
                    verifier["id"],
                    verifier,
                    selection_scopes=mission["write_scope"],
                    execution_required=True,
                )
                self.assertEqual(errors, [])
                # PASS is decided by exit code, so the signal must say only that.
                self.assertEqual(verifier["pass_signal"], "exit 0")


if __name__ == "__main__":
    unittest.main()
