"""Small synthetic approved inputs shared by eval policy and delivery tests."""
import hashlib
import json


def encoded(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def inputs(count=4):
    cases = [{"case_id": f"case-{i}", "split": "heldout", "slices": ["core"],
              "critical": i == 0, "input": f"Synthetic question {i}",
              "expected": f"Synthetic answer {i}"} for i in range(count)]
    files = {
        "evals/cases.jsonl": b"".join(encoded(c) for c in cases),
        "evals/rubric.json": encoded({"schema": "eval-rubric/1", "dimensions": [
            {"id": "correctness", "minimum": 0, "maximum": 1, "passing_score": 1,
             "anchors": {"0": "Incorrect answer", "1": "Correct answer"}}],
            "prohibited_assertions": {"no-side-effect": "No unauthorized mutation"}}),
        "evals/judge.json": encoded({"schema": "eval-grader/1", "kind": "deterministic",
                                   "identity": "exact-match-v1", "instructions": "Compare exact expected output",
                                   "calibration": "Four manually checked synthetic answers"}),
        "evals/subject.json": encoded({"schema": "eval-subject/1", "identity": "fixture-v1",
                                     "configuration": "Local deterministic synthetic runner"}),
    }
    policy = {
        "schema": "eval-policy/1", "applicability": "required",
        "reason": "AI output must meet a frozen quality bar", "owner": "Jacky Chan",
        "quality": {"test_id": "TEST-001", "scenario_id": "eval-quality",
                    "report": "docs/verification/evidence/eval/quality.json"},
        "handoff": {"test_id": "TEST-002", "scenario_id": "eval-handoff",
                    "report": "docs/verification/evidence/eval/handoff.json"},
        "metric": "case_all_trials", "trials_per_case": 2,
        "minimum_rate": {"numerator": 3, "denominator": 4},
        "slices": [{"id": "core", "minimum_cases": count,
                    "minimum_rate": {"numerator": 3, "denominator": 4}}],
        "critical_rule": "all_trials_pass", "retry_policy": "none",
        "freshness": {"max_age_seconds": 3600, "dependencies": {}},
        "limits": {"trial_timeout_ms": 1000, "run_timeout_ms": 60000, "max_calls": count * 2,
                   "max_cost_microunits": 0, "currency": "USD"},
        "delivery": {"runner": "evals/run.py", "grader": "evals/grade.py",
                     "lockfile": "requirements-eval.lock", "runbook": "docs/verification/EVAL_RUNBOOK.md",
                     "setup_argv": ["python", "-m", "pip", "install", "-r", "requirements-eval.lock"],
                     "full_argv": ["python", "evals/run.py", "--full"]},
    }
    for name, path in (("dataset", "evals/cases.jsonl"), ("rubric", "evals/rubric.json"),
                       ("grader", "evals/judge.json"), ("subject", "evals/subject.json")):
        policy[name] = {"path": path, "sha256": hashlib.sha256(files[path]).hexdigest()}
    return policy, files


def prd(policy):
    body = json.dumps(policy, indent=2)
    return ("## AI and Automation\nAI and Automation Gate: required — Synthetic output quality, decided by Jacky Chan\n"
            "<!-- eval-policy:start -->\n```json\n" + body + "\n```\n<!-- eval-policy:end -->\n"
            "## Test Obligations\n| TEST ID | Obligation | Test type | Required | Upstream trace IDs | Expected signal |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| TEST-001 | Full quality run | contract | Yes | PRD-001, AI-EVALUATION | Frozen rate passes |\n"
            "| TEST-002 | Clean checkout run | operational | Yes | PRD-001, AI-EVALUATION | Full run passes |\n")
