// ============================================================================
// views.js - code that draws results. Used by more than one page.
//
//   renderTruthTable(table)            Logic page
//   renderEquivalenceTable(result)     Logic page
//   renderInductionResult(result, id)  Proof Explorer page and Induction page
//
// Each function returns an element; the page decides where to put it.
// ============================================================================

// ---------- Truth tables ----------------------------------------------------

// `table` looks like:
//   { variables: ["P","Q"], normalized: "P → Q",
//     rows: [ { assignment: {P: true, Q: false}, result: false }, ... ] }
function renderTruthTable(table) {
  const headerCells = table.variables.map((name) => h("th", {}, name));
  headerCells.push(h("th", {}, table.normalized));

  const bodyRows = table.rows.map((row) => {
    const cells = table.variables.map((name) => h("td", {}, trueFalse(row.assignment[name])));
    cells.push(h("td", { class: row.result ? "cell-true" : "cell-false" }, trueFalse(row.result)));
    return h("tr", {}, cells);
  });

  return h(
    "div",
    { class: "table-wrap" },
    h("table", { class: "truth-table" }, h("thead", {}, h("tr", {}, headerCells)), h("tbody", {}, bodyRows))
  );
}

// `result` looks like:
//   { equivalent: true, variables: ["P","Q"],
//     rows: [ { assignment: {...}, left: true, right: true, match: true }, ... ] }
function renderEquivalenceTable(result) {
  const headerCells = result.variables.map((name) => h("th", {}, name));
  headerCells.push(h("th", {}, "Left side"), h("th", {}, "Right side"), h("th", {}, "Same?"));

  const bodyRows = result.rows.map((row) => {
    const cells = result.variables.map((name) => h("td", {}, trueFalse(row.assignment[name])));
    cells.push(
      h("td", {}, trueFalse(row.left)),
      h("td", {}, trueFalse(row.right)),
      h("td", { class: row.match ? "cell-true" : "cell-false" }, row.match ? "yes" : "no")
    );
    return h("tr", {}, cells);
  });

  return h(
    "div",
    { class: "table-wrap" },
    h("table", { class: "truth-table" }, h("thead", {}, h("tr", {}, headerCells)), h("tbody", {}, bodyRows))
  );
}

// ---------- Induction -------------------------------------------------------

// One short sentence describing a numeric spot check from the backend.
// The backend sends slightly different fields for different kinds of statement.
function describeSpotCheck(check) {
  if ("divisible_by" in check) {
    return "P(" + (check.k + 1) + ") has value " + check["P(k+1)_value"] +
      ", divisible by " + check.divisible_by;
  }
  return "P(" + (check.k + 1) + "): left side " + check.lhs + ", right side " + check.rhs;
}

// A little form: "check P(k+1) for a k that you choose".
// It only works for statements from the example library, because the backend
// needs an example id for this request.
function buildKChecker(exampleId, domainStart) {
  const MAX_K = 100; // keeps the numbers small so the answer is instant
  const output = h("div", { "aria-live": "polite" });

  const input = h("input", {
    type: "number",
    min: domainStart,
    max: MAX_K,
    step: 1,
    value: domainStart + 3,
  });

  const button = h("button", { class: "btn btn-secondary btn-small", type: "button" }, "Check this k");

  button.addEventListener("click", () => {
    const k = Number(input.value);
    if (input.value.trim() === "" || !Number.isInteger(k) || k < domainStart || k > MAX_K) {
      show(output, errorNotice("Enter a whole number from " + domainStart + " to " + MAX_K + "."));
      return;
    }
    runTask(output, [button], async () => {
      const data = await api.inductiveStep(exampleId, k);
      const check = data.numeric_spot_checks && data.numeric_spot_checks[0];
      if (!check) throw new Error("The backend did not return a check for this value.");
      show(
        output,
        h(
          "p",
          { class: "math " + (check.holds ? "cell-true" : "cell-false") },
          "k = " + check.k + ": " + (check.holds ? "holds ✓" : "fails ✗") + "  (" + describeSpotCheck(check) + ")"
        )
      );
    });
  });

  return h(
    "div",
    { class: "k-form" },
    h("label", {}, "Try your own value of k", input),
    button,
    output
  );
}

// `result` is the object from /api/induction/analyze (or the same shape inside
// other answers). `exampleId` is optional; when given, the "try your own k"
// form is shown.
function renderInductionResult(result, exampleId) {
  const base = result.base_case;
  const hypothesis = result.inductive_hypothesis;
  const step = result.inductive_step;
  const start = result.domain_start;

  if (!base || !hypothesis || !step) {
    return notice("warning", "The backend returned an incomplete induction result.");
  }

  const baseVerified = base.verification_status === "VERIFIED";
  const stepVerified = step.verification_status === "VERIFIED";
  const proved = result.final_status === "PROVED";

  // --- 1. Base case ---
  const baseDetails = [];
  baseDetails.push(h("p", {}, "Check the statement for the smallest value, n = " + base.n + "."));
  if (base.comparison) {
    baseDetails.push(
      h(
        "dl",
        { class: "facts math" },
        h("dt", {}, "Left side"), h("dd", {}, base.lhs_value),
        h("dt", {}, "Right side"), h("dd", {}, base.rhs_value)
      ),
      h(
        "p",
        { class: "math " + (base.match ? "cell-true" : "cell-false") },
        "Left " + base.comparison + " right: " + (base.match ? "holds" : "fails")
      )
    );
  } else {
    if (base.lhs_desc) {
      baseDetails.push(h("p", { class: "math" }, base.lhs_desc + " = " + base.lhs_value));
    }
    baseDetails.push(
      h("p", { class: "math " + (base.match ? "cell-true" : "cell-false") }, base.check || (base.match ? "holds" : "fails"))
    );
  }

  // The backend sends a label in capitals, such as
  // "INDUCTIVE HYPOTHESIS (an assumption, not a proven fact)".
  // The heading already says "Inductive hypothesis", so keep only the part in brackets.
  const bracketed = hypothesis.label && hypothesis.label.match(/\(([^)]+)\)/);
  const hypothesisLabel = bracketed
    ? bracketed[1].charAt(0).toUpperCase() + bracketed[1].slice(1) + "."
    : "";

  // --- 3. Inductive step ---
  const spotChecks = (step.numeric_spot_checks || []).map((check) =>
    h("li", { class: check.holds ? "holds" : "fails" }, "k = " + check.k + (check.holds ? " ✓" : " ✗"))
  );

  return h(
    "div",
    { class: "induction-result" },

    h(
      "div",
      { class: "induction-part" },
      h("h3", {}, "1. Base case ", statusLabel(base.verification_status)),
      baseDetails
    ),

    h(
      "div",
      { class: "induction-part" },
      h("h3", {}, "2. Inductive hypothesis"),
      hypothesisLabel ? h("p", { class: "soft" }, hypothesisLabel) : null,
      h("p", {}, hypothesis.text),
      h("p", { class: "math" }, hypothesis.hypothesis),
      hypothesis.note ? h("p", { class: "soft small" }, hypothesis.note) : null
    ),

    h(
      "div",
      { class: "induction-part" },
      h("h3", {}, "3. Inductive step ", statusLabel(step.verification_status)),
      h("p", {}, "Show that if P(k) is true, then P(k+1) is true."),
      // white-space: pre keeps the spacing the backend uses to line things up
      h("pre", { class: "algebra" }, (step.algebra || []).join("\n")),
      step.target ? h("p", {}, step.target) : null,
      h("p", { class: "soft small" }, "Numeric spot checks (extra evidence, not the proof itself):"),
      h("ul", { class: "spot-checks" }, spotChecks),
      exampleId ? buildKChecker(exampleId, start) : null
    ),

    h(
      "div",
      { class: "induction-part" },
      h("h3", {}, "Conclusion ", statusLabel(result.final_status)),
      h(
        "ul",
        { class: "check-list" },
        h("li", { class: baseVerified ? "ok" : "no" }, (baseVerified ? "✓" : "✗") + " Base case"),
        h("li", { class: "ok" }, "✓ Inductive hypothesis stated"),
        h("li", { class: stepVerified ? "ok" : "no" }, (stepVerified ? "✓" : "✗") + " Inductive step")
      ),
      proved
        ? h("p", {}, "Therefore P(n) is true for every integer n ≥ " + start + ".")
        : notice("warning", "This proof could not be verified automatically. Please check the steps above yourself.")
    )
  );
}
