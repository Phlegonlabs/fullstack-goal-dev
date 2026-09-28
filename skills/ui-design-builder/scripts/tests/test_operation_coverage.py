"""Required product actions must originate in PRD, not agreement between two incomplete designs."""
import json
from pathlib import Path
import re
import sys
import unittest
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "product-definition-builder" / "scripts"))
from operation_coverage import coverage_findings, hifi_coverage_findings, required_operations
import prd_operations


def prd(operation):
    return """<!-- ui-surface-contract:start -->
### UI-001 — Account
- """ + chr(96) + "route" + chr(96) + """: /account
- """ + chr(96) + "states" + chr(96) + """: ready
- """ + chr(96) + "responsive" + chr(96) + """: viewports: 390, 768, 1200
- """ + chr(96) + "copy" + chr(96) + """: approved
- """ + chr(96) + "operations" + chr(96) + ": " + json.dumps([operation]) + """
<!-- ui-surface-contract:end -->
"""


class OperationCoverageTests(unittest.TestCase):
    def setUp(self):
        self.operation = {"id": "OP-home", "trigger": "Home", "control": "home", "sourceState": "ready",
                          "destination": {"surface": "UI-001", "state": "ready"}, "presentation": "page"}
        self.wireframe = {"flows": [{"from": "UI-001", "sourceState": "ready", "trigger": "Home",
                                      "control": "home", "to": "UI-001", "presentation": "page",
                                      "destination": {"surface": "UI-001", "state": "ready"}}]}
        self.manifest = {"interactions": [{"id": "home", "source": {"surface": "UI-001", "state": "ready"},
                                           "control": "home", "destination": self.operation["destination"]}]}

    def test_required_action_joins_both_designs(self):
        self.assertEqual([], coverage_findings(prd(self.operation), self.wireframe, self.manifest))

    def test_documented_operation_example_joins_and_detects_missing_controls(self):
        reference = Path(__file__).resolve().parents[2] / "references/review-workflow.md"
        prefix = "- `operations`: "
        examples = [line.removeprefix(prefix) for line in reference.read_text(encoding="utf-8").splitlines()
                    if line.startswith(prefix)]
        self.assertEqual(1, len(examples))
        operations = json.loads(examples[0])
        self.assertEqual(1, len(operations))
        example_prd = prd(operations[0])
        self.assertEqual([], coverage_findings(example_prd, self.wireframe, self.manifest))
        self.assertEqual(2, len(coverage_findings(example_prd, {"flows": []}, {"interactions": []})))

    def test_both_designs_missing_home_still_fail(self):
        findings = coverage_findings(prd(self.operation), {"flows": []}, {"interactions": []})
        self.assertEqual(2, len(findings))
        self.assertTrue(all("OP-home" in value for value in findings))

    def test_wrong_destination_and_faked_state_fail(self):
        self.manifest["interactions"][0]["destination"] = {"surface": "UI-001", "state": "fake"}
        self.assertTrue(coverage_findings(prd(self.operation), self.wireframe, self.manifest))
        self.operation["destination"]["state"] = "fake"
        self.assertTrue(required_operations(prd(self.operation))[1])

    def test_matching_trigger_cannot_hide_wrong_presentation(self):
        self.wireframe["flows"][0]["presentation"] = "feedback"
        self.assertIn("presentation differs", "\n".join(
            coverage_findings(prd(self.operation), self.wireframe, self.manifest)))

    def test_matching_trigger_on_wrong_state_or_control_does_not_cover_operation(self):
        self.wireframe["flows"][0]["sourceState"] = "updated"
        self.assertIn("OP-home", "\n".join(coverage_findings(prd(self.operation), self.wireframe, self.manifest)))
        self.wireframe["flows"][0]["sourceState"] = "ready"
        self.wireframe["flows"][0]["control"] = "unrelated"
        self.assertIn("OP-home", "\n".join(coverage_findings(prd(self.operation), self.wireframe, self.manifest)))

    def test_matching_surface_but_wrong_destination_state_fails(self):
        self.wireframe["flows"][0]["destination"]["state"] = "updated"
        self.assertIn("destination state differs", "\n".join(
            coverage_findings(prd(self.operation), self.wireframe, self.manifest)))

    def test_undeclared_interaction_fails(self):
        self.manifest["interactions"].append({"id": "surprise", "source": {"surface": "UI-001", "state": "ready"},
                                             "control": "surprise", "destination": self.operation["destination"]})
        self.assertIn("lacks a PRD", "\n".join(coverage_findings(prd(self.operation), self.wireframe, self.manifest)))

    def test_whitespace_variant_heading_keeps_required_operations(self):
        for heading in ("###  UI-001", "###\tUI-001"):
            text = prd(self.operation).replace("### UI-001", heading)
            operations, errors = required_operations(text)
            self.assertEqual([], errors, heading)
            self.assertEqual(["OP-home"], [row["id"] for row in operations], heading)
            self.assertIn("OP-home: required operation is missing", "\n".join(
                hifi_coverage_findings(text, {"interactions": []})))

    def test_parsed_surface_without_operations_result_fails(self):
        narrow = re.compile(r"^### (UI-[A-Z0-9]+(?:-[A-Z0-9]+)*)\b.*$", re.M)
        text = prd(self.operation).replace("### UI-001", "###  UI-001")
        with mock.patch.object(prd_operations, "UI_HEADING_RE", narrow):
            self.assertIn("UI-001 has no PRD operations result", required_operations(text)[1])

    def test_missing_or_duplicate_anchor_fails(self):
        text = prd(self.operation)
        anchor = next(line for line in text.splitlines() if "operations" in line)
        self.assertTrue(required_operations(text.replace(anchor, ""))[1])
        self.assertTrue(required_operations(text.replace(anchor, anchor + "\n" + anchor))[1])


if __name__ == "__main__":
    unittest.main()
