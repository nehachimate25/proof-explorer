// ============================================================================
// api.js - every request to the Flask backend goes through this file.
//
// It is a plain script (not a module): loading it with a <script> tag creates
// one global object called `api`. Other files call it like this:
//
//     const table = await api.truthTable("P -> Q");
//
// Each function returns the "data" part of the backend's answer, or throws an
// Error with a readable message that the pages show to the user.
// ============================================================================

const API_BASE = "/api";

// Send one request and unpack the answer.
// The backend always answers with JSON shaped like
//     { "success": true,  "data": ... }     or
//     { "success": false, "error": "message" }
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(API_BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkError) {
    // fetch() only throws when the server cannot be reached at all.
    throw new Error(
      "Could not reach the server. Check that the backend is running (python run.py)."
    );
  }

  let body;
  try {
    body = await response.json();
  } catch (parseError) {
    throw new Error("The server sent an answer that could not be read.");
  }

  if (!response.ok || body.success === false) {
    throw new Error(body.error || "The request failed.");
  }
  return body.data;
}

// Shortcut for POST requests that send JSON.
function post(path, data) {
  return request(path, { method: "POST", body: JSON.stringify(data) });
}

const api = {
  // ----- Health check (this endpoint answers {status, service}, no "data") -----
  health: async function () {
    const response = await fetch(API_BASE + "/health");
    if (!response.ok) throw new Error("Health check failed.");
    return response.json();
  },

  // ----- Logic -----
  truthTable: (expression) => post("/logic/truth-table", { expression }),
  analyzeLogic: (expression) => post("/logic/analyze", { expression }),
  checkEquivalence: (expression1, expression2) =>
    post("/logic/equivalence", { expression1, expression2 }),
  evaluateLogic: (expression, assignment) =>
    post("/logic/evaluate", { expression, assignment }),

  // ----- Propositions -----
  analyzeProposition: (payload) => post("/proposition/analyze", payload),

  // ----- Proofs -----
  listProofExamples: () => request("/proof/examples"),
  analyzeStatement: (statement) => post("/proof/analyze", { statement }),
  runDynamic: (statement, method) => post("/proof/dynamic", { statement, method }),
  runDirect: (example_id) => post("/proof/direct", { example_id }),
  runContrapositive: (example_id) => post("/proof/contrapositive", { example_id }),
  transformConditional: (expression) =>
    post("/proof/contrapositive/transform", { expression }),
  runContradiction: (example_id) => post("/proof/contradiction", { example_id }),
  compareMethods: (example_id) => post("/proof/compare", { example_id }),

  // ----- Induction -----
  listInductionExamples: () => request("/induction/examples"),
  analyzeInduction: (example_id) => post("/induction/analyze", { example_id }),
  analyzeInductionStatement: (statement) =>
    post("/induction/analyze-statement", { statement }),
  baseCase: (example_id) => post("/induction/base-case", { example_id }),
  inductiveStep: (example_id, sample_k) =>
    post("/induction/step", { example_id, sample_k }),

  // ----- History -----
  listHistory: () => request("/history"),
  addHistory: (payload) => post("/history", payload),
  deleteHistory: (id) => request("/history/" + id, { method: "DELETE" }),
};
