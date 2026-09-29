// Pure identity checks. Only the host can supply trustworthy launch observations.
const {createHash} = require("node:crypto");
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]));
  return value;
}
function digest(value) {
  return `sha256:${createHash("sha256").update(JSON.stringify(canonical(value))).digest("hex")}`;
}
function frozenCopy(value) {
  const copy = JSON.parse(JSON.stringify(value));
  function freeze(item) {
    if (item && typeof item === "object") { Object.values(item).forEach(freeze); Object.freeze(item); }
    return item;
  }
  return freeze(copy);
}
function requireText(value, name) {
  if (typeof value !== "string" || !value.trim()) throw new Error(`${name} must be non-empty`);
}
function launchIndex(instances, records) {
  if (!Array.isArray(records) || records.length !== instances.length) throw new Error("required parent launch records are missing or unexpected");
  const expected = new Map(instances.map(a => [a.assignment_id, a]));
  const index = new Map();
  const reservations = new Set();
  const workers = new Set();
  const sessions = new Set();
  for (const record of records) {
    const a = expected.get(record?.assignment_id);
    if (!a || index.has(record.assignment_id)) throw new Error("unknown or duplicate parent launch assignment");
    for (const field of ["assignment_id", "attempt_id", "input_id"]) {
      if (record[field] !== a[field]) throw new Error(`parent launch ${field} mismatch`);
    }
    for (const field of ["authority", "runtime", "reservation_id", "execution_role", "model", "worker_id", "session_id"]) requireText(record[field], `parent launch ${field}`);
    for (const field of ["authority", "runtime"]) {
      if (record[field] !== a.binding_requirements[field]) throw new Error(`wrong launch ${field}`);
    }
    for (const field of ["execution_role", "model", "effort"]) {
      if (record[field] !== a.requested_identity[field]) throw new Error(`wrong launch ${field}`);
    }
    for (const [field, seen] of [["reservation_id", reservations], ["worker_id", workers], ["session_id", sessions]]) {
      if (seen.has(record[field])) throw new Error(`reused parent launch ${field}`);
      seen.add(record[field]);
    }
    index.set(a.assignment_id, record);
  }
  return index;
}
function matchObserved(instance, result, launch) {
  for (const field of ["execution_role", "model", "effort", "worker_id", "session_id"]) {
    if (result.observed_identity?.[field] !== launch[field]) throw new Error(`launch observation conflicts with the child observed ${field}`);
  }
}
module.exports = {digest, frozenCopy, requireText, launchIndex, matchObserved};
