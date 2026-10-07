"""Current graph regression scenarios using the canonical Product fixtures."""
import unittest

import test_readonly_assignments as fixtures


PRELUDE = r'''
const assert = require("node:assert/strict");
const fs = require("fs");
const {createProductAgentGraph} = require(process.argv[2]);
const api = require(process.argv[4]);
const args = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const clone = x => JSON.parse(JSON.stringify(x));
args.source_manifest = [{path: "docs/research", sha256: "a".repeat(64)}];
args.role_bindings = {};
for (const role of ["requirements", "architecture", "backend", "synthesis", "trace-verifier", "consistency-verifier", "market-research"]) {
  args.role_bindings[role] = {
    logical_role: role.endsWith("verifier") ? "reviewer" : role === "market-research" ? "market_researcher" : "code_architect",
    execution_role: role.endsWith("verifier") ? "reviewer" : role === "market-research" ? "market_researcher" : "code_architect",
    model: "fixture-model", effort: "high", authority: "parent-owned", runtime: "readonly-sandbox",
    runtime_kind: "native", required_tools: ["read"],
    authorization: {delegation: true, readonly_tools: true},
    capability: {launch_runtime: true, readonly_tools: true, tools: ["read"]},
  };
}
let serial = 0;
function response(task, body, status = "complete") {
  const a = task.assignment;
  const n = ++serial;
  const identity = {...a.requested_identity, worker_id: `W${n}`, session_id: `S${n}`};
  const result = {
    assignment_id: a.assignment_id, attempt_id: a.attempt_id, input_id: a.input_id,
    business_role: a.business_role, question_id: a.question_id,
    observed_identity: identity, status, result: body,
  };
  const launch = {
    assignment_id: a.assignment_id, attempt_id: a.attempt_id, input_id: a.input_id,
    reservation_id: `R${n}`, ...identity, ...a.binding_requirements,
  };
  return {result, launch};
}
const draftBody = {prd_markdown: "# PRD exact candidate", architecture_markdown: "# Architecture",
  stack_decisions_markdown: "# Stack", implementation_plan_markdown: null,
  trace_index: [], assumptions: [], open_questions: [], unresolved_conflicts: []};
function setup(options = args) {
  const graph = createProductAgentGraph(options);
  const analysis = graph.analyze().map(t => response(t, {role: t.assignment.business_role,
    status: "complete", sections: [], trace_ids: [], assumptions: [], open_questions: [], evidence: []}));
  const lanes = analysis.map(x => x.result).reverse();
  const launches = analysis.map(x => x.launch);
  const synthesisTask = graph.synthesize(lanes, launches);
  const synthesis = response(synthesisTask, draftBody);
  const tasks = graph.review(synthesis.result, [synthesis.launch]);
  const reviews = tasks.map(t => response(t, t.assignment.business_role === "market-research"
    ? {searched: "public sources", unresolved: "No useful evidence"}
    : {role: t.assignment.business_role, decision: "pass", findings: [], evidence: []},
    t.assignment.business_role === "market-research" ? "no_sources" : "complete"));
  return {graph, lanes, synthesis, tasks, results: reviews.map(x => x.result).reverse(),
    launches: [...launches, synthesis.launch, ...reviews.map(x => x.launch)]};
}
function finish(s, results = s.results, launches = s.launches) {
  return s.graph.finish(s.lanes, s.synthesis.result, results, launches);
}
'''


class GraphIdentityTests(unittest.TestCase):
    run_node = fixtures.ReadonlyAssignmentPacketTests.run_node

    def scenario(self, code):
        return self.run_node(PRELUDE + code + '\nprocess.stdout.write(JSON.stringify({ok:true}));',
                             fixtures.canonical_graph_request(), fixtures.GRAPH_PATH, [str(fixtures.MODULE_PATH)])

    def test_disabled_research_needs_no_research_binding_or_capability(self):
        self.scenario(r'''
args.market_research = false;
args.research_question_inventory = [];
args.research_skip_reason = "Owner declined optional research before delegation";
delete args.role_bindings["market-research"];
for (const key of Object.keys(args)) if (key.startsWith("readonly_") || key === "requested_research_identity") delete args[key];
const s = setup();
assert.equal(s.tasks.length, 2);
assert.deepEqual(finish(s).research, []);
assert.equal(finish(s).status, "candidate_ready");
assert.throws(() => createProductAgentGraph({...args, research_question_inventory: undefined}));
assert.throws(() => createProductAgentGraph({...args, research_delegation_required: true}));
''')

    def test_caller_and_state_method_routes_to_technical_roles_only(self):
        self.scenario(r'''
args.role_bindings["frontend-platform"] = clone(args.role_bindings.architecture);
args.browser_frontend = true;
const graph = createProductAgentGraph(args);
const tasks = graph.analyze();
const technical = ["architecture", "backend", "frontend-platform"];
assert.equal(tasks.filter(t => technical.includes(t.assignment.business_role)).length, 3);
for (const task of tasks) {
  const applies = technical.includes(task.assignment.business_role);
  assert.equal(task.prompt.includes("#caller-and-state-method"), applies);
  assert.ok(task.prompt.includes("Read only"));
  if (applies) {
    assert.ok(task.prompt.indexOf("concrete caller example") < task.prompt.indexOf("conceptual interfaces"));
    assert.ok(task.prompt.includes("Keep implementation signatures and types downstream"));
    assert.ok(task.prompt.includes("Reuse accepted local-repair designs and existing approval checkpoints"));
  }
}
const s = setup();
const result = finish(s);
assert.equal(result.status, "candidate_ready");
assert.equal(result.readonly_assignment_mode, "readonly-assignments/1");
''')

    def test_full_graph_accepts_reordering_and_blocks_missing_or_stale_identities(self):
        self.scenario(r'''
const s = setup();
assert.equal(finish(s).status, "candidate_ready");
assert.throws(() => finish(s, s.results.slice(1)));
for (const field of ["assignment_id", "attempt_id", "input_id", "business_role"]) {
  const bad = clone(s.results); bad[0][field] = "wrong";
  assert.throws(() => finish(s, bad));
}
const badLanes = clone(s.lanes); badLanes[0].input_id = "stale";
assert.throws(() => s.graph.synthesize(badLanes, s.launches.slice(0, 3)));
const badDraft = clone(s.synthesis.result); badDraft.result.prd_markdown += "changed";
assert.throws(() => s.graph.finish(s.lanes, badDraft, s.results, s.launches));
''')

    def test_review_binds_exact_draft_sources_and_complete_research_instructions(self):
        self.scenario(r'''
const s = setup();
const research = s.tasks.filter(t => t.assignment.business_role === "market-research");
assert.equal(research.length, 2);
for (const t of research) {
  for (const text of [draftBody.prd_markdown, "Research Disclosure Check", "market-research-guide.md", "RA-*", "Read only", "publisher", "pending"])
    assert.ok(t.prompt.includes(text), text);
  assert.deepEqual(t.assignment.input.source_manifest, args.source_manifest);
  assert.deepEqual(t.assignment.input.draft, draftBody);
}
const changed = clone(args); changed.source_manifest[0].sha256 = "b".repeat(64);
const other = setup(changed);
assert.notEqual(research[0].assignment.input_id, other.tasks.find(t => t.assignment.business_role === "market-research").assignment.input_id);
assert.throws(() => finish(other, s.results));
s.graph.review(s.synthesis.result, [s.synthesis.launch]);
assert.throws(() => finish(s));
''')

    def test_parent_records_are_required_and_bound_to_attempt_and_actual_launch(self):
        self.scenario(r'''
const s = setup();
const echoed = clone(s.results);
for (const result of echoed) result.launch_observation = s.launches.find(l => l.assignment_id === result.assignment_id);
assert.throws(() => finish(s, echoed, []));
for (const field of ["assignment_id", "attempt_id", "input_id", "authority", "runtime", "execution_role", "model", "effort", "worker_id", "session_id"]) {
  const records = clone(s.launches); records.at(-1)[field] = "wrong";
  assert.throws(() => finish(s, s.results, records), field);
}
const reused = clone(s.launches); reused.at(-1).reservation_id = reused.at(-2).reservation_id;
assert.throws(() => finish(s, s.results, reused));
const duplicate = clone(s.results); duplicate[0] = duplicate[1];
assert.throws(() => finish(s, duplicate));
const missing = clone(args); delete missing.role_bindings.architecture;
assert.throws(() => setup(missing));
const external = clone(args); external.role_bindings.synthesis.runtime_kind = "external";
assert.throws(() => setup(external));
const noTool = clone(args); noTool.role_bindings.architecture.required_tools = ["unavailable-tool"];
assert.throws(() => setup(noTool));
''')

    def test_required_dependency_failure_and_mutated_inputs_do_not_pass(self):
        self.scenario(r'''
const s = setup();
const blocked = clone(s.results);
blocked.find(r => r.business_role === "market-research").status = "blocked";
blocked.find(r => r.business_role === "market-research").result = {reason: "Required web tool unavailable"};
assert.equal(finish(s, blocked).status, "needs_revision");
const failedLanes = clone(s.lanes); failedLanes[0].status = "blocked";
assert.throws(() => s.graph.synthesize(failedLanes, s.launches.slice(0, 3)));
const changedLanes = clone(s.lanes); changedLanes[0].result.evidence.push("different evidence");
assert.throws(() => s.graph.finish(changedLanes, s.synthesis.result, s.results, s.launches));
const before = JSON.stringify(s.graph.analyze());
args.source_manifest[0].sha256 = "c".repeat(64);
args.interview_summary = "changed by caller";
assert.equal(JSON.stringify(s.graph.analyze()), before);
const badRole = clone(args); badRole.role_bindings["trace-verifier"].logical_role = "implementer";
assert.throws(() => setup(badRole));
''')

    def test_current_instructions_require_producer_self_check_and_existing_evidence(self):
        product = (fixtures.SKILL_ROOT / "references/stages/product-definition.md").read_text(encoding="utf-8")
        ui_root = fixtures.SKILL_ROOT.parent / "ui-design-builder"
        ui = (ui_root / "references" / "stages" / "ui-design.md").read_text(encoding="utf-8")
        workflow = (ui_root / "references" / "review-workflow.md").read_text(encoding="utf-8")
        for content in (product, ui, workflow):
            self.assertIn("same producing agent", content)
            self.assertIn("equal self-check agent identity", content)
            self.assertIn("final candidate hash", content)
        self.assertIn("joinReadonlyResults(plan, results, parentLaunchRecords)", workflow)
        self.assertIn("reviewer lacking required browser capability remains blocked", workflow)
        graph = (fixtures.SKILL_ROOT / "references" / "agent-work-graph.md").read_text(encoding="utf-8")
        self.assertNotIn("use the sequential parent fallback", graph)
        self.assertNotIn("completes that role sequentially", graph)
