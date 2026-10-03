import copy
import hashlib
import re
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

    def test_approval_overlap_and_malformed_boundaries_rejected(self):
        approval_start = "<!-- product-definition-approval:start -->"
        approval_end = "<!-- product-definition-approval:end -->"
        valid = prd(self.policy)
        for candidate in (
                valid.replace(ep.START, approval_start + "\n" + ep.START).replace(ep.END, ep.END + "\n" + approval_end),
                valid.replace(ep.START, ep.START + "\n" + approval_start).replace(ep.END, approval_end + "\n" + ep.END),
                valid.replace(ep.START, approval_start + "\n" + ep.START).replace(ep.END, approval_end + "\n" + ep.END),
                valid + "\n" + approval_start, valid + "\n" + approval_end,
                valid + "\n" + approval_end + "\n" + approval_start):
            with self.subTest(candidate=candidate[:60]):
                self.assertTrue(ep.validate_eval_policy(candidate, required=True))
        self.assertEqual([], ep.validate_eval_policy(valid + "\n" + approval_start + "\n" + approval_end))

    def test_complete_approved_package_cannot_hide_threshold_in_approval(self):
        import check_product_package as package
        from test_product_package_checker import valid_prd, valid_architecture, valid_stack, strictize_approved_package
        policy_block = prd(self.policy).split(ep.START, 1)[1].split(ep.END, 1)[0]
        policy_block = ep.START + policy_block + ep.END
        normal = valid_prd().replace("## Business Rules", policy_block + "\n## Business Rules")
        normal, architecture, stack = strictize_approved_package(normal, valid_architecture(), valid_stack())
        self.assertEqual([], package.validate_texts(normal, architecture, stack,
                         require_filled=True, require_approved=True, eval_policy="eval-policy/1"))
        approval = re.search(r"<!-- product-definition-approval:start -->.*?<!-- product-definition-approval:end -->",
                             valid_prd(), re.S).group()
        source = valid_prd().replace(approval, "")
        enclosed = approval.replace("<!-- product-definition-approval:end -->",
                                    policy_block + "\n<!-- product-definition-approval:end -->")
        source = source.replace("## Business Rules", enclosed + "\n## Business Rules")
        source, architecture, stack = strictize_approved_package(source, valid_architecture(), valid_stack())
        weakened = source.replace('"numerator": 3', '"numerator": 2')
        self.assertEqual(canonical_product_bytes(source, architecture, stack),
                         canonical_product_bytes(weakened, architecture, stack))
        errors = package.validate_texts(weakened, architecture, stack,
                                      require_filled=True, require_approved=True, eval_policy="eval-policy/1")
        self.assertTrue(any("overlap" in error for error in errors), errors)

    def test_markers_must_be_active_unique_and_in_ai_section(self):
        valid = prd(self.policy)
        for candidate in (valid + valid, valid.replace(ep.END, ""), valid.replace("## AI and Automation", "## Other")):
            with self.subTest(candidate=candidate[:30]):
                self.assertTrue(ep.validate_eval_policy(candidate, required=True))

    def test_raw_digest_exclusion_matrix_cannot_hide_policy(self):
        import check_product_package as package
        from test_product_package_checker import valid_prd, valid_architecture, valid_stack, strictize_approved_package
        start = "<!-- product-definition-approval:start -->"
        block = ep.START + prd(self.policy).split(ep.START)[1].split(ep.END)[0] + ep.END
        for prefix in ("```markdown\n" + start + "\n```\n", "    " + start + "\n",
                       "<script>\n" + start + "\n</script>\n", "<!--\n" + start + "\n-->\n"):
            for newline in ("\n", "\r\n"):
                with self.subTest(prefix=prefix, newline=repr(newline)):
                    source = valid_prd().replace("## Business Rules", block + "\n## Business Rules")
                    source = source.replace("## AI and Automation", prefix + "## AI and Automation")
                    source, architecture, stack = strictize_approved_package(source, valid_architecture(), valid_stack())
                    source = source.replace("\n", newline)
                    weakened = source.replace('"numerator": 3', '"numerator": 2')
                    self.assertEqual(canonical_product_bytes(source, architecture, stack),
                                     canonical_product_bytes(weakened, architecture, stack))
                    errors = package.validate_texts(weakened, architecture, stack,
                        require_filled=True, require_approved=True, eval_policy="eval-policy/1")
                    self.assertTrue(any("eval-policy" in error for error in errors), errors)
        # Python splitlines recognizes these separators; the digest regex uses LF.
        for separator in ("\x0c", "\u2028", "\r"):
            candidate = prd(self.policy).replace(ep.START, "prefix" + separator + start + "\n" + ep.START)
            candidate += "\n<!-- product-definition-approval:end -->\n"
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
