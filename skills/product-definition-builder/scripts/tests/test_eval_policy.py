import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_policy as ep
from contract_utils import canonical_product_bytes
from eval_fixtures import encoded, inputs, prd


class EvalPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy, self.files = inputs()

    def test_frozen_inputs_and_approval_binding(self):
        self.assertEqual([], ep.validate_eval_policy(prd(self.policy), required=True))
        ep.parse_inputs(self.policy, self.files.__getitem__)
        changed = copy.deepcopy(self.policy)
        changed["minimum_rate"]["numerator"] -= 1
        self.assertNotEqual(canonical_product_bytes(prd(self.policy), "a", "s"),
                            canonical_product_bytes(prd(changed), "a", "s"))

    def test_legacy_missing_and_explicit_mode(self):
        self.assertEqual([], ep.validate_eval_policy("legacy"))
        self.assertTrue(ep.validate_eval_policy("legacy", required=True))
        self.assertIsNone(ep.parse_eval_policy("````\n" + prd(self.policy) + "\n````"))

    def test_markers_must_be_active_unique_and_in_ai_section(self):
        valid = prd(self.policy)
        for candidate in (valid + valid, valid.replace(ep.END, ""), valid.replace("## AI and Automation", "## Other")):
            with self.subTest(candidate=candidate[:30]):
                self.assertTrue(ep.validate_eval_policy(candidate, required=True))

    def test_ai_cannot_waive_and_tests_are_required_traced_and_distinct(self):
        waived = {"schema": "eval-policy/1", "applicability": "not_required",
                  "reason": "Ordinary deterministic product has no AI", "owner": "Jacky Chan"}
        self.assertTrue(ep.validate_eval_policy(prd(waived)))
        self.assertEqual([], ep.validate_eval_policy(prd(waived).replace("Gate: required", "Gate: not_required"), required=True))
        for old, new in (("| Yes |", "| No |"), ("AI-EVALUATION", "OTHER")):
            self.assertTrue(ep.validate_eval_policy(prd(self.policy).replace(old, new)))

    def test_typed_policy_and_no_silent_extra_fields(self):
        for key, value in (("trials_per_case", True), ("retry_policy", "best-of-three"),
                           ("minimum_rate", {"numerator": 1, "denominator": 0}),
                           ("slices", [{"id": "core", "minimum_cases": 0, "minimum_rate": {"numerator": 1, "denominator": 1}}]),
                           ("extra", "ignored")):
            candidate = copy.deepcopy(self.policy)
            candidate[key] = value
            self.assertTrue(ep.validate_eval_policy(prd(candidate)))

    def test_duplicate_json_and_nonfinite_rejected(self):
        for raw in ('{"schema": 1, "schema": 2}', '{"score": NaN}'):
            with self.assertRaises(ep.PolicyError):
                ep.json_object(raw)

    def test_changed_inputs_rejected_without_weakened_hashes(self):
        for name in self.files:
            altered = dict(self.files)
            altered[name] += b" "
            with self.assertRaises(ep.PolicyError):
                ep.parse_inputs(self.policy, altered.__getitem__)

    def test_dataset_and_rubric_structure_validated(self):
        for path, raw in (("evals/cases.jsonl", self.files["evals/cases.jsonl"] * 2),
                          ("evals/rubric.json", encoded({"schema": "eval-rubric/1", "dimensions": [], "prohibited_assertions": {}}))):
            candidate = copy.deepcopy(self.policy)
            files = dict(self.files, **{path: raw})
            name = "dataset" if "cases" in path else "rubric"
            candidate[name]["sha256"] = hashlib.sha256(raw).hexdigest()
            with self.assertRaises(ep.PolicyError):
                ep.parse_inputs(candidate, files.__getitem__)

    def test_file_boundary_and_package_api(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, raw in self.files.items():
                path = root / name
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(raw)
            self.assertEqual([], ep.validate_eval_policy(prd(self.policy), repo_root=root))
            for path in ("../escape", ".env", "evals/auth-token.json", "evals\\cases.jsonl"):
                with self.assertRaises(ep.PolicyError):
                    ep.read_artifact(root, path)
        import check_product_package as package
        from test_product_package_checker import valid_prd, valid_architecture, valid_stack
        baseline = package.validate_texts(valid_prd(), valid_architecture(), valid_stack())
        explicit = package.validate_texts(valid_prd(), valid_architecture(), valid_stack(), eval_policy="eval-policy/1")
        self.assertFalse(any("eval-policy" in p for p in baseline))
        self.assertTrue(any("eval-policy" in p for p in explicit))


if __name__ == "__main__":
    unittest.main()
