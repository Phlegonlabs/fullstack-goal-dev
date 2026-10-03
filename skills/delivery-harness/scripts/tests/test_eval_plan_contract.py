import copy
import builtins
import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_plan_contract as pc
import harness_contract_join as join
from eval_delivery_fixtures import fixture, encoded, prd
from test_delivery_acceptance import execution
from eval_verification import QUALITY_ASSERTIONS, HANDOFF_ASSERTIONS


class EvalPlanContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        policy, files, contract, _, _, _ = fixture()
        self.policy = policy
        files["docs/product/PRD.md"] = prd(policy).encode()
        files["docs/verification/eval-contract.json"] = encoded(contract)
        delivery = {"schema": "delivery-acceptance/1", "prd_sha256": contract["prd_sha256"], "tests": []}
        for purpose, assertions in (("quality", QUALITY_ASSERTIONS), ("handoff", HANDOFF_ASSERTIONS)):
            context = execution()
            context["assertions"] = {name: "Frozen eval policy deterministically verified" for name in assertions}
            delivery["tests"].append({"test_id": policy[purpose]["test_id"], "scenarios": [{
                "id": policy[purpose]["scenario_id"], "execution": context,
                "platform": "cli", "auth_mode": "none", "environment": "local",
                "build": {"build_id": "fixture-eval-1", "config_digest": "b" * 64}, "fixtures": []}]})
        files["docs/verification/delivery-acceptance.json"] = encoded(delivery)
        for path, raw in files.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.plan = {"schema_version": 6, "sources": [], "final_gates": [], "graph": {"nodes": [], "edges": []}}
        for kind, path in (("prd", "docs/product/PRD.md"), ("eval contract", "docs/verification/eval-contract.json"),
                           ("delivery acceptance", "docs/verification/delivery-acceptance.json")):
            self.plan["sources"].append({"id": "SRC-" + str(len(self.plan["sources"]) + 1), "kind": kind,
                "location": path, "status": "frozen", "content_sha256": hashlib.sha256(files[path]).hexdigest()})
        common = {"--repo-root": ".", "--prd": "docs/product/PRD.md", "--results": pc.RESULTS_PATH}
        eval_args = {**common, "--prd-sha256": self.plan["sources"][0]["content_sha256"],
            "--contract": self.plan["sources"][1]["location"], "--contract-sha256": self.plan["sources"][1]["content_sha256"],
            "--delivery-contract": self.plan["sources"][2]["location"], "--delivery-contract-sha256": self.plan["sources"][2]["content_sha256"]}
        acceptance_args = {**common, "--contract": self.plan["sources"][2]["location"], "--contract-sha256": self.plan["sources"][2]["content_sha256"]}
        for name, script, options in (("final-check", "noop.py", {}), ("eval-acceptance", "check_eval_acceptance.py", eval_args),
                                      ("delivery-acceptance", "check_delivery_acceptance.py", acceptance_args), ("final-closeout", "noop.py", {})):
            argv = [sys.executable, str(Path(pc.__file__).with_name(script))]
            argv += [value for pair in options.items() for value in pair]
            if options:
                argv.append("--candidate-from-head")
            self.plan["final_gates"].append({"id": name, "cwd": ".", "argv": argv, "pass_signal": "exit 0",
                                             "execution": {"isolation": "host"}})
            self.plan["graph"]["nodes"].append({"id": "N-" + name, "kind": "verifier", "ref": name, "executor": "local_command"})
        for before, after in (("final-check", "eval-acceptance"), ("eval-acceptance", "delivery-acceptance"), ("delivery-acceptance", "final-closeout")):
            self.plan["graph"]["edges"].append({"kind": "dependency", "from": "N-" + before, "to": "N-" + after,
                                                "on_outcomes": ["pass"], "max_traversals": None})
        self.run = {"runtime_capabilities": {"runtime_adapter": {"version_gate": {"required_harness_version": "0.60.0"}}}}

    def check(self, plan=None, run=None):
        return pc.validate_eval_plan(plan or self.plan, self.root, run=run or self.run,
            source_rows=join._strict_source_rows, resolve_source=join._resolve_source_bytes)

    def test_complete_plan_and_plan_only_marker_adoption(self):
        self.assertEqual([], self.check())
        self.assertEqual([], pc.validate_eval_plan(self.plan, self.root, run=None,
            source_rows=join._strict_source_rows, resolve_source=join._resolve_source_bytes))

    def test_missing_sibling_import_returns_validation_error(self):
        original = builtins.__import__

        for error in (ImportError, OSError, SyntaxError):
            def missing(name, *arguments, **options):
                if name == "eval_plan_contract":
                    raise error("unavailable sibling")
                return original(name, *arguments, **options)

            with self.subTest(error=error), patch("builtins.__import__", side_effect=missing):
                errors = join.validate_frozen_contract_joins(self.plan, self.root, run=self.run)
            self.assertEqual(["eval-plan: installed sibling eval policy parser unavailable"], errors)

    def test_current_missing_marker_but_legacy_keeps_checks(self):
        path = self.root / "docs/product/PRD.md"
        path.write_text("legacy PRD\n", encoding="utf-8")
        self.plan["sources"][0]["content_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertTrue(self.check())
        legacy = copy.deepcopy(self.run)
        legacy["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.58.0"
        self.assertEqual([], self.check(run=legacy))

    def test_marker_on_old_pin_still_enforces_gate(self):
        self.run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.58.0"
        self.plan["final_gates"].pop(1)
        self.assertTrue(self.check())

    def test_extra_prd_row_cannot_disable_marker_adoption(self):
        for version in ("0.37.0", "0.59.0", "0.60.0", None):
            plan = copy.deepcopy(self.plan)
            plan["sources"].append({"id": "SRC-REFERENCE", "kind": "reference",
                                   "location": "docs/archive/PRD.md", "status": "draft"})
            plan["final_gates"].pop(1)
            run = copy.deepcopy(self.run) if version else None
            if run:
                run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = version
            errors = pc.validate_eval_plan(plan, self.root, run=run,
                source_rows=join._strict_source_rows, resolve_source=join._resolve_source_bytes)
            with self.subTest(version=version):
                self.assertTrue(errors)
                with patch.object(join, "_validate_product_frozen_contract_joins", return_value=[]):
                    self.assertTrue(join.validate_frozen_contract_joins(plan, self.root, run=run))

    def test_legacy_prd_kind_alias_and_ambiguous_marker_fail_closed(self):
        self.run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.37.0"
        original = self.root / "docs/product/PRD.md"
        alternate = self.root / "docs/product/requirements.md"
        alternate.write_bytes(original.read_bytes())
        plan = copy.deepcopy(self.plan)
        plan["sources"][0].update(kind="product requirements", location="docs/product/requirements.md")
        self.assertTrue(self.check(plan))
        plan = copy.deepcopy(self.plan)
        plan["sources"].append({**plan["sources"][0], "id": "SRC-OTHER", "kind": "product requirements",
                                "location": "docs/product/requirements.md"})
        self.assertTrue(any("ambiguous" in error for error in self.check(plan)))

    def test_authoritative_read_failures_never_mean_marker_absence(self):
        for version in ("0.37.0", "0.59.0", "0.60.0", None):
            run = copy.deepcopy(self.run) if version else None
            if run:
                run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = version
            for error in (pc.AcceptanceError("link"), pc.AcceptanceError("oversized"), OSError("unreadable")):
                with self.subTest(version=version, error=str(error)), patch.object(pc, "_read_bytes", side_effect=error):
                    self.assertTrue(pc.validate_eval_plan(self.plan, self.root, run=run,
                        source_rows=join._strict_source_rows, resolve_source=join._resolve_source_bytes))
        alternate = self.root / "docs/token-service/PRD.md"
        alternate.parent.mkdir()
        alternate.write_bytes((self.root / "docs/product/PRD.md").read_bytes())
        for version in ("0.37.0", None):
            plan = copy.deepcopy(self.plan)
            plan["sources"][0]["location"] = "docs/token-service/PRD.md"
            plan["final_gates"].pop(1)
            run = copy.deepcopy(self.run) if version else None
            if run:
                run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = version
            with patch.object(join, "_validate_product_frozen_contract_joins", return_value=[]):
                self.assertTrue(join.validate_frozen_contract_joins(plan, self.root, run=run))

    @unittest.skipIf(os.name == "nt", "POSIX symlink variant; read-failure matrix runs on all hosts")
    def test_legacy_linked_authority_fails_closed(self):
        linked = self.root / "docs/linked"
        linked.symlink_to(self.root / "docs/product", target_is_directory=True)
        self.plan["sources"][0]["location"] = "docs/linked/PRD.md"
        self.run["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.37.0"
        self.assertTrue(self.check())

    def test_extra_non_authority_reference_without_marker_is_ignored(self):
        for status in ("draft", "reference"):
            plan = copy.deepcopy(self.plan)
            plan["sources"].append({"id": "SRC-ARCHIVE", "kind": "reference", "status": status,
                                   "location": "docs/archive/PRD.md"})
            self.assertEqual([], self.check(plan))

    def test_non_ai_reasoned_exemption_needs_no_eval_gates(self):
        waived = {"schema": "eval-policy/1", "applicability": "not_required", "reason": "Deterministic software requires no AI quality sampling", "owner": "Jacky Chan"}
        raw = prd(waived).replace("Gate: required", "Gate: not_required").encode()
        (self.root / "docs/product/PRD.md").write_bytes(raw)
        self.plan["sources"] = self.plan["sources"][:1]
        self.plan["sources"][0]["content_sha256"] = hashlib.sha256(raw).hexdigest()
        self.plan["final_gates"] = []
        self.assertEqual([], self.check())

    def test_missing_source_gate_node_or_path_fails(self):
        for modify in (lambda p: p["sources"].pop(1), lambda p: p["sources"].pop(2),
                       lambda p: p["final_gates"].pop(1), lambda p: p["graph"]["nodes"].pop(1),
                       lambda p: p["graph"]["edges"].pop(1), lambda p: p["graph"]["edges"].pop(0)):
            plan = copy.deepcopy(self.plan)
            modify(plan)
            self.assertTrue(self.check(plan))

    def test_gate_argv_source_hash_and_selection_cannot_be_faked(self):
        for modify in (lambda g: g["argv"].__setitem__(1, "fake/check_eval_acceptance.py"),
                       lambda g: g["argv"].__setitem__(0, "true"),
                       lambda g: g["argv"].__setitem__(g["argv"].index("--prd-sha256") + 1, "a" * 64),
                       lambda g: g.update(selection={"mode": "changed_files"}),
                       lambda g: g["argv"].extend(["--contract-sha256", "a" * 64]),
                       lambda g: g.update(cwd="evals")):
            plan = copy.deepcopy(self.plan)
            modify(plan["final_gates"][1])
            self.assertTrue(self.check(plan))

    def test_changed_input_contract_and_frozen_source_fail(self):
        for name in ("evals/rubric.json", "docs/verification/eval-contract.json"):
            path = self.root / name
            raw = path.read_bytes()
            path.write_bytes(raw + b" ")
            self.assertTrue(self.check())
            path.write_bytes(raw)
        self.plan["sources"][1]["kind"] = "untrusted expectation"
        self.assertTrue(self.check())

    def test_relative_checker_cannot_resolve_against_parent_checkout(self):
        # The verifier runs in the consumer root, not this parent's source cwd.
        self.assertNotEqual(self.root.resolve(), Path.cwd().resolve())
        for index, script in ((1, "check_eval_acceptance.py"), (2, "check_delivery_acceptance.py")):
            plan = copy.deepcopy(self.plan)
            relative = "skills/delivery-harness/scripts/" + script
            self.assertTrue(Path(relative).is_file())
            plan["final_gates"][index]["argv"][1] = relative
            errors = self.check(plan)
            self.assertTrue(any("absolute installed checker" in error for error in errors), errors)

    def test_checker_execution_namespace_must_be_explicit_host(self):
        for index in (1, 2):
            for execution_policy in (None, {}, {"isolation": "container", "sandbox": {"image": "fixture@sha256:" + "a" * 64}},
                              {"isolation": "unknown"}, "host"):
                plan = copy.deepcopy(self.plan)
                plan["final_gates"][index]["execution"] = execution_policy
                with self.subTest(gate=index, execution=execution_policy):
                    self.assertTrue(self.check(plan))

    def test_gate_interpreter_cannot_resolve_through_project_or_path(self):
        self.assertEqual([], self.check())
        for index in (1, 2):
            for interpreter in ("python", "python3", "./python", "./python.exe", str(self.root / "python.exe")):
                plan = copy.deepcopy(self.plan)
                plan["final_gates"][index]["argv"][0] = interpreter
                with self.subTest(gate=index, interpreter=interpreter):
                    self.assertTrue(any("observed absolute Python" in error for error in self.check(plan)))

    def test_common_join_cannot_skip_eval_through_strict_early_return(self):
        self.plan["final_gates"].pop(1)
        with patch.object(join, "_validate_strict_frozen_contract_joins", return_value=[]):
            self.assertTrue(join.validate_frozen_contract_joins(self.plan, self.root, run=self.run))
        legacy = copy.deepcopy(self.run)
        legacy["runtime_capabilities"]["runtime_adapter"]["version_gate"]["required_harness_version"] = "0.37.0"
        with patch.object(join, "_validate_product_frozen_contract_joins", return_value=[]):
            self.assertTrue(join.validate_frozen_contract_joins(self.plan, self.root, run=legacy))


if __name__ == "__main__":
    unittest.main()
