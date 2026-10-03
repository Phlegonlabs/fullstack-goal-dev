import copy
import datetime as dt
import hashlib
import sys
from pathlib import Path

_prior_path = list(sys.path)
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "product-definition-builder" / "scripts" / "tests"))
try:
    from eval_fixtures import inputs, prd, encoded
finally:
    sys.path[:] = _prior_path
from eval_verification import ep


def fixture(count=4):
    policy, files = inputs(count)
    prd_hash = hashlib.sha256(prd(policy).encode()).hexdigest()
    contract = {"schema": "eval-contract/1", "prd_sha256": prd_hash,
                "policy_sha256": ep.policy_digest(policy),
                **{name: copy.deepcopy(policy[name]) for name in ("quality", "handoff", "delivery")}}
    approved = ep.parse_inputs(policy, files.__getitem__)
    artifacts = {path: hashlib.sha256(("Delivered " + path).encode()).hexdigest()
                 for name, path in policy["delivery"].items() if isinstance(path, str)}
    artifacts.update({value["path"]: value["sha256"] for name, value in policy.items()
                      if name in {"dataset", "rubric", "grader", "subject"}})
    now = dt.datetime.now(dt.timezone.utc)
    report = {"schema": "eval-report/1", "purpose": "quality", "run_id": "quality-run-1",
              "candidate_sha": "a" * 40, "contract_sha256": hashlib.sha256(encoded(contract)).hexdigest(),
              "prd_sha256": prd_hash, "policy_sha256": ep.policy_digest(policy),
              "started_at": (now - dt.timedelta(seconds=10)).isoformat(),
              "finished_at": (now - dt.timedelta(seconds=1)).isoformat(),
              "execution": {"fixture": "Synthetic local execution"}, "artifacts": artifacts,
              "provenance": {"executor": "fixture-parent", "job_id": "job-quality-1", "checkout_sha": "a" * 40,
                             "git_status": "", "dependency_readbacks": {},
                             "setup": {"argv": policy["delivery"]["setup_argv"], "exit_code": 0, "observation": "Locked dependencies installed"},
                             "full": {"argv": policy["delivery"]["full_argv"], "exit_code": 0, "observation": "All planned trials captured"}},
              "usage": {"calls": count * 2, "cost_microunits": 0, "currency": "USD"},
              "trials": []}
    for case in approved["dataset"]:
        for index in range(1, 3):
            report["trials"].append({"case_id": case["case_id"], "trial_index": index, "status": "completed",
                "scores": {"correctness": 1}, "assertion_results": {"no-side-effect": "pass"},
                "observed_subject": "fixture-v1", "observed_grader": "exact-match-v1", "duration_ms": 1,
                "usage": {"calls": 1, "cost_microunits": 0, "currency": "USD"},
                "redacted_output": case["expected"], "grading_observation": "Expected text matches exactly",
                "tool_observations": "No tool actions permitted or observed", "failure": ""})
    return policy, files, contract, approved, report, now
