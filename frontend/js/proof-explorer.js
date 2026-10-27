// ============================================================================
// proof-explorer.js - the Proof Explorer page.
//
// The page works in three stages:
//   1. ANALYZE  - the user types a statement; the backend classifies it.
//   2. CHOOSE   - we list the proof methods and say which ones fit.
//   3. PROVE    - the user picks a method and steps through the proof.
//
// Backend routes used here:
//   GET  /api/proof/examples        list of verified example statements
//   POST /api/proof/analyze         classify a statement
//   POST /api/proof/direct          proof of a library example (direct)
//   POST /api/proof/contrapositive  proof of a library example (contrapositive)
//   POST /api/proof/contradiction   proof of a library example (contradiction)
//   POST /api/proof/dynamic         proof of any other recognised statement
//   POST /api/proof/compare         compare methods for a library example
//   POST /api/history               save a finished proof
// ============================================================================

const statementInput = document.getElementById("statement");
const analyzeButton = document.getElementById("btn-analyze");
const output = document.getElementById("output");
const examplesSection = document.getElementById("examples-section");
const examplesBox = document.getElementById("examples");
const howItWorks = document.getElementById("how-it-works");

// What the page remembers between stages.
const state = {
  classification: null, // the answer from /api/proof/analyze
};

// A counter so an old, slow answer can never overwrite a newer one.
let analysisCounter = 0;

// ---------- text used on the page ----------

const METHOD_INFO = {
  direct: { title: "Direct proof", form: "P → Q", about: "Assume P, work forward, and arrive at Q." },
  contrapositive: { title: "Contrapositive", form: "¬Q → ¬P", about: "Prove the equivalent statement: if Q is false, then P is false." },
  contradiction: { title: "Contradiction", form: "assume ¬S, reach ⊥", about: "Assume the statement is false and show that this is impossible." },
  induction: { title: "Induction", form: "base case + step", about: "Check the first case, then show P(k) leads to P(k+1)." },
};
const METHOD_ORDER = ["direct", "contrapositive", "contradiction", "induction"];

const REASON_WHY = {
  Definition: "Uses the exact definition of a term in the statement.",
  Substitution: "Replaces a variable with an expression known to be equal to it.",
  "Algebraic simplification": "Uses ordinary algebra: expanding, factoring or arithmetic.",
  "Logical equivalence": "Uses a logical equivalence that holds for every truth assignment.",
  Assumption: "This is what we assume for this method. It is not yet a conclusion.",
  Contradiction: "Shows a result that conflicts with an earlier assumption.",
  "Inductive hypothesis": "Uses the assumption that the statement is true for n = k.",
  "Inductive step": "Shows the statement is also true for n = k + 1.",
};

const SUPPORT_NOTE = {
  VERIFIED: "Every step of the proofs below has been checked by the backend.",
  SUPPORTED: "The structure of this statement is recognised, but a full step-by-step proof is not generated for every method.",
};

// Statuses that /api/proof/dynamic and the example routes can return when they
// do NOT produce a proof, and the label we show for each.
const NO_PROOF_LABEL = {
  supported_only: "SUPPORTED",
  invalid: "INVALID",
  needs_review: "NEEDS_REVIEW",
  unsuitable: "NEEDS_REVIEW",
  unsupported: "NEEDS_REVIEW",
  not_found: "NEEDS_REVIEW",
};

// ---------- small building blocks ----------

function backButton(text, onClick) {
  return h("p", { class: "back-link" }, h("button", { type: "button", class: "link-button", onclick: onClick }, text));
}

function fact(label, value, extraClass) {
  return [h("dt", {}, label), h("dd", { class: extraClass || false }, value)];
}

// The table of facts about a statement (type, logical form, P, Q ...).
function analysisFacts(classification) {
  const info = classification.classification || {};
  const rows = [fact("Statement", classification.statement)];
  if (info.type) rows.push(fact("Type", info.type));
  if (info.logical_form) rows.push(fact("Logical form", info.logical_form, "math"));
  if (info.variable) rows.push(fact("Variable", info.variable, "math"));
  if (info.domain) rows.push(fact("Domain", info.domain, "math"));
  if (info.P) rows.push(fact("P", info.P));
  if (info.Q) rows.push(fact("Q", info.Q));
  return h("dl", { class: "facts" }, rows);
}

function isInduction(classification) {
  return (
    classification.kind === "induction" ||
    (classification.classification && classification.classification.type === "Induction Proposition")
  );
}

// ---------- start / reset ----------

function showStartScreen() {
  state.classification = null;
  analysisCounter++; // ignore any answer that is still on its way
  show(output);
  examplesSection.hidden = false;
  howItWorks.hidden = false;
}

function hideStartScreen() {
  examplesSection.hidden = true;
  howItWorks.hidden = true;
}

// ---------- the list of examples ----------

async function loadExamples() {
  showLoading(examplesBox, "Loading examples...");
  try {
    const examples = await api.listProofExamples();
    if (!examples.length) {
      show(examplesBox, h("p", { class: "empty" }, "The backend has no examples to show."));
      return;
    }
    const items = examples.map((example) =>
      h(
        "li",
        {},
        h(
          "button",
          { type: "button", class: "link-button", onclick: () => analyze(example.statement) },
          example.statement
        ),
        h(
          "span",
          { class: "item-note" },
          example.logical_form + ". Methods that fit: " + example.valid_methods.join(", ") + "."
        )
      )
    );
    show(examplesBox, h("ul", { class: "item-list" }, items));
  } catch (error) {
    show(examplesBox, errorNotice("The example list could not be loaded. " + error.message));
  }
}

// ---------- stage 1: analyze ----------

function analyze(text) {
  const statement = (text !== undefined ? text : statementInput.value).trim();
  if (statement === "") {
    hideStartScreen();
    show(output, errorNotice("Type a statement first, or choose one of the examples."));
    examplesSection.hidden = false;
    statementInput.focus();
    return;
  }
  statementInput.value = statement;

  const myNumber = ++analysisCounter;
  hideStartScreen();

  runTask(output, [analyzeButton], async () => {
    let result;
    try {
      result = await api.analyzeStatement(statement);
    } catch (error) {
      if (myNumber !== analysisCounter) return;
      show(output, errorNotice(error.message), backButton("Choose another statement", showStartScreen));
      return;
    }
    if (myNumber !== analysisCounter) return; // a newer request replaced this one
    state.classification = result;
    showClassification();
  }, "Analyzing the statement...");
}

// ---------- stage 2: show what the backend found ----------

function showClassification() {
  const c = state.classification;
  const goBack = backButton("Choose another statement", showStartScreen);

  // (a) The backend could not understand the statement.
  if (c.status === "INVALID" || c.status === "NEEDS_REVIEW") {
    show(
      output,
      goBack,
      h("div", { class: "result" },
        h("h3", {}, "This statement could not be checked ", statusLabel(c.status)),
        h("p", {}, c.message || "The backend could not work with this statement."))
    );
    return;
  }

  // (b) The statement is false: show the counterexample.
  if (c.status === "DISPROVED") {
    const info = c.classification || {};
    show(
      output,
      goBack,
      h("div", { class: "result" },
        h("h3", {}, "This statement is false ", statusLabel("DISPROVED")),
        analysisFacts(c),
        c.counterexample
          ? h("div", { class: "notice error" },
              h("p", {}, h("strong", {}, "Counterexample (n = " + c.counterexample.value + "). "),
                c.counterexample.explanation))
          : null,
        h("p", {}, c.reason || "A counterexample makes P true and Q false, so the statement cannot be proved."),
        info.P && info.Q ? h("p", { class: "soft small" }, "A statement “if P then Q” is false as soon as one case has P true and Q false.") : null)
    );
    return;
  }

  // (c) An induction statement: the backend already ran the whole induction.
  if (isInduction(c)) {
    show(
      output,
      goBack,
      h("div", { class: "result" },
        h("h3", {}, "This is a statement about every n, so induction is the natural method ", statusLabel(c.status)),
        analysisFacts(c),
        c.induction_result
          ? renderInductionResult(
              c.induction_result,
              c.source === "library" && c.kind === "induction" ? c.example_id : undefined
            )
          : notice("warning", "The backend did not return an induction proof for this statement."))
    );
    return;
  }

  // (d) A normal statement: list the proof methods.
  if (c.classification && c.methods) {
    showMethodChoice();
    return;
  }

  // (e) Anything else we did not expect: show what we know.
  show(
    output,
    goBack,
    h("div", { class: "result" },
      h("h3", {}, "Result ", statusLabel(c.status)),
      h("p", {}, c.message || "The backend gave no further details for this statement."))
  );
}

function showMethodChoice() {
  const c = state.classification;
  const canCompare = c.source === "library" && c.kind === "proof";

  const methodNames = METHOD_ORDER.filter((name) => name in c.methods);
  Object.keys(c.methods).forEach((name) => {
    if (!methodNames.includes(name)) methodNames.push(name); // unknown future methods
  });

  const methodRows = methodNames.map((name) => {
    const info = c.methods[name];
    const meta = METHOD_INFO[name] || { title: name, form: "", about: "" };
    const button = h(
      "button",
      { type: "button", class: "btn btn-secondary", disabled: !info.suitable,
        onclick: () => explore(name) },
      info.suitable ? "Show proof" : "Does not fit"
    );
    return h(
      "div",
      { class: "method" + (info.suitable ? "" : " unsuitable") },
      h("div", {},
        h("h3", {}, meta.title, " ", h("span", { class: "method-form" }, meta.form)),
        h("p", {}, info.reason || meta.about)),
      button
    );
  });

  const compareOutput = h("div", { "aria-live": "polite" });
  const compareButton = canCompare
    ? h("button", { type: "button", class: "btn btn-secondary" }, "Compare the methods")
    : null;
  if (compareButton) {
    compareButton.addEventListener("click", () => compareMethods(compareButton, compareOutput));
  }

  const note = c.message || SUPPORT_NOTE[c.status];

  show(
    output,
    backButton("Choose another statement", showStartScreen),
    h("section", {},
      h("h2", {}, "What the backend found ", statusLabel(c.status)),
      analysisFacts(c),
      note ? h("p", { class: "soft" }, note) : null),
    h("section", {},
      h("h2", {}, "Proof methods"),
      h("div", {}, methodRows),
      compareButton ? h("div", { class: "button-row" }, compareButton) : null,
      compareOutput)
  );
}

// ---------- compare methods (library statements only) ----------

function compareMethods(button, container) {
  runTask(container, [button], async () => {
    const data = await api.compareMethods(state.classification.example_id);
    if (!data.comparisons || data.comparisons.length === 0) {
      show(container, notice("warning", "There are no methods to compare for this statement."));
      return;
    }
    const rows = data.comparisons.map((row) =>
      h("tr", {},
        h("td", {}, (METHOD_INFO[row.method] || { title: row.method }).title),
        h("td", {}, row.num_steps),
        h("td", {}, row.difficulty),
        h("td", {}, statusLabel(row.result)),
        h("td", {}, row.logical_approach))
    );
    show(
      container,
      h("div", { class: "result" },
        h("h3", {}, "Comparison of methods"),
        h("div", { class: "table-wrap" },
          h("table", {},
            h("thead", {}, h("tr", {},
              h("th", {}, "Method"), h("th", {}, "Steps"), h("th", {}, "Difficulty"),
              h("th", {}, "Result"), h("th", {}, "Approach"))),
            h("tbody", {}, rows))))
    );
  }, "Comparing the methods...");
}

// ---------- stage 3: get and show a proof ----------

function explore(method) {
  const c = state.classification;
  const backToMethods = backButton("Choose a different method", showMethodChoice);

  runTask(output, [], async () => {
    let proof;
    try {
      const fromLibrary = c.source === "library" && c.kind === "proof";
      if (fromLibrary && method === "direct") proof = await api.runDirect(c.example_id);
      else if (fromLibrary && method === "contrapositive") proof = await api.runContrapositive(c.example_id);
      else if (fromLibrary && method === "contradiction") proof = await api.runContradiction(c.example_id);
      else proof = await api.runDynamic(c.statement, method);
    } catch (error) {
      show(output, backToMethods, errorNotice(error.message));
      return;
    }
    showProof(proof, backToMethods);
  }, "Preparing the proof...");
}

function showProof(proof, backToMethods) {
  const c = state.classification;

  // A proof was produced and checked.
  if (proof.status === "verified") {
    show(
      output,
      backToMethods,
      h("section", {},
        h("h2", {}, (METHOD_INFO[proof.method] || { title: "Proof" }).title, " of the statement"),
        h("dl", { class: "facts" },
          fact("Statement", proof.statement),
          proof.logical_form ? fact("Logical form", proof.logical_form, "math") : null,
          proof.domain ? fact("Domain", proof.domain, "math") : null)),
      h("section", {}, buildStepViewer(proof), buildSaveControls(proof))
    );
    return;
  }

  // An induction proof (when induction was chosen from the method list).
  if (proof.status === "verified_induction") {
    const exampleId = c.source === "library" && c.kind === "induction" ? c.example_id : undefined;
    show(output, backToMethods, h("section", {}, h("h2", {}, "Proof by induction"), renderInductionResult(proof, exampleId)));
    return;
  }

  // No proof: the backend explains why.
  const label = NO_PROOF_LABEL[proof.status] || "NEEDS_REVIEW";
  show(
    output,
    backToMethods,
    h("div", { class: "result" },
      h("h3", {}, "No proof was produced ", statusLabel(label)),
      h("p", {}, proof.message || "The backend could not produce a proof with this method."))
  );
}

// ---------- the two-column proof ----------
//
// Looks like a proof in a textbook: a Statement column and a Reason column.
// One row is added each time the user clicks "Show next step".
function buildStepViewer(proof) {
  const steps = proof.steps || [];
  if (steps.length === 0) {
    return h("p", { class: "empty" }, "The backend returned no steps for this proof.");
  }

  let shown = 1;          // how many rows are visible
  let showedAll = false;  // true after "Show all steps"

  const progress = h("p", { class: "proof-progress", "aria-live": "polite" });
  const body = h("tbody");
  const conclusion = h("div");
  const nextButton = h("button", { type: "button", class: "btn" }, "Show next step");
  const allButton = h("button", { type: "button", class: "btn btn-secondary" }, "Show all steps");
  const restartButton = h("button", { type: "button", class: "btn btn-secondary" }, "Start over");

  function draw() {
    const finished = shown === steps.length;
    progress.textContent = "Showing step " + shown + " of " + steps.length;

    body.replaceChildren(
      ...steps.slice(0, shown).map((step, index) => {
        const isNewest = !showedAll && index === shown - 1;
        return h("tr", { class: isNewest ? "newest" : false },
          h("td", { class: "step-statement" },
            h("span", { class: "step-number" }, step.step_number + "."), step.statement),
          h("td", { class: "step-reason" },
            h("span", { class: "reason-name" }, step.reason),
            h("span", { class: "reason-why" }, REASON_WHY[step.reason] || "Follows from the earlier steps.")));
      })
    );

    nextButton.disabled = finished;
    allButton.disabled = finished;

    if (finished) {
      show(conclusion, h("div", { class: "conclusion" },
        h("p", {}, h("strong", {}, "Conclusion: "), proof.conclusion),
        statusLabel(proof.verification_status)));
    } else {
      show(conclusion);
    }
  }

  nextButton.addEventListener("click", () => { shown = Math.min(shown + 1, steps.length); draw(); });
  allButton.addEventListener("click", () => { shown = steps.length; showedAll = true; draw(); });
  restartButton.addEventListener("click", () => { shown = 1; showedAll = false; draw(); });

  draw();

  return h("div", {},
    progress,
    h("div", { class: "table-wrap" },
      h("table", { class: "proof-table" },
        h("thead", {}, h("tr", {}, h("th", {}, "Statement"), h("th", {}, "Reason"))),
        body)),
    h("div", { class: "button-row" }, nextButton, allButton, restartButton),
    conclusion
  );
}

// ---------- save to history ----------

function buildSaveControls(proof) {
  const message = h("div", { "aria-live": "polite" });
  const button = h("button", { type: "button", class: "btn btn-secondary" }, "Save to History");

  let saved = false;

  button.addEventListener("click", async () => {
    if (saved) return;
    await runTask(message, [button], async () => {
      await api.addHistory({
        statement: proof.statement,
        proof_method: proof.method,
        result: proof.verification_status,
        num_steps: (proof.steps || []).length,
      });
      saved = true;
      button.textContent = "Saved";
      show(message, notice("success", "Saved. You can find it on the ", h("a", { href: "history.html" }, "History page"), "."));
    }, "Saving...");
    // runTask switches the button back on when it finishes,
    // so switch it off again once the proof has been saved.
    if (saved) button.disabled = true;
  });

  return h("div", { class: "button-row" }, button, message);
}

// ---------- start-up ----------

analyzeButton.addEventListener("click", () => analyze());
statementInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") analyze();
});

loadExamples();

// The Home page links here with ?statement=... so the example opens directly.
const wantedStatement = new URLSearchParams(window.location.search).get("statement");
if (wantedStatement) {
  analyze(wantedStatement);
}
