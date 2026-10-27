// ============================================================================
// propositions.js - the Propositions page.
//
// Backend route used here:
//   POST /api/proposition/analyze
//        { statement, P, Q, operator }   or   { expression }
// ============================================================================

const statementInput = document.getElementById("statement");
const partP = document.getElementById("part-p");
const partQ = document.getElementById("part-q");
const operatorSelect = document.getElementById("operator");
const rawFormula = document.getElementById("raw-formula");
const btnAnalyze = document.getElementById("btn-analyze");
const btnFormula = document.getElementById("btn-formula");
const output = document.getElementById("output");

const buttons = [btnAnalyze, btnFormula];

// A short plain-English meaning for each kind of proposition.
const TYPE_MEANING = {
  Conditional: "Says that if P is true, then Q is true. It is false only when P is true and Q is false.",
  Biconditional: "Says that P and Q are either both true or both false.",
  Conjunction: "True only when both parts are true.",
  Disjunction: "True when at least one part is true.",
  Negation: "True exactly when P is false.",
  "Atomic proposition": "A single statement with no connectives such as and, or, not.",
  "Compound proposition": "Built from simpler statements using connectives.",
};

// "¬" works on P alone, so Q is not needed.
function updateQBox() {
  const isNegation = operatorSelect.value === "¬";
  partQ.disabled = isNegation;
}
operatorSelect.addEventListener("change", updateQBox);
updateQBox();

function renderResult(result) {
  const facts = [
    h("dt", {}, "Type"), h("dd", {}, h("strong", {}, result.proposition_type)),
    h("dt", {}, "Logical form"), h("dd", { class: "math" }, result.logical_form),
  ];
  if (result.P) facts.push(h("dt", {}, "P"), h("dd", {}, result.P));
  if (result.Q) facts.push(h("dt", {}, "Q"), h("dd", {}, result.Q));
  if (result.variables && result.variables.length) {
    facts.push(h("dt", {}, "Letters used"), h("dd", { class: "math" }, result.variables.join(", ")));
  }

  return h(
    "div",
    { class: "result" },
    h("h3", {}, "Result"),
    h("dl", { class: "facts" }, facts),
    TYPE_MEANING[result.proposition_type] ? h("p", {}, TYPE_MEANING[result.proposition_type]) : null
  );
}

// ---------- structured form: statement, P, Q, operator ----------
btnAnalyze.addEventListener("click", () => {
  const p = partP.value.trim();
  const q = partQ.value.trim();
  const operator = operatorSelect.value;

  // Check the form before bothering the backend.
  if (p === "") {
    show(output, errorNotice("Fill in P first. P is the first part of your statement."));
    partP.focus();
    return;
  }
  if (operator !== "¬" && q === "") {
    show(output, errorNotice("Fill in Q, or choose ¬ if your statement only has a P."));
    partQ.focus();
    return;
  }

  runTask(output, buttons, async () => {
    const result = await api.analyzeProposition({
      statement: statementInput.value.trim(),
      P: p,
      Q: operator === "¬" ? "" : q, // never send Q together with "not"
      operator: operator,
    });
    show(output, renderResult(result));
  });
});

// ---------- direct formula ----------
btnFormula.addEventListener("click", () => {
  const formula = rawFormula.value.trim();
  if (formula === "") {
    show(output, errorNotice("Type a formula first, for example (P ∧ Q) → R."));
    rawFormula.focus();
    return;
  }

  runTask(output, buttons, async () => {
    try {
      show(output, renderResult(await api.analyzeProposition({ expression: formula })));
    } catch (error) {
      throw new Error(friendlyFormulaError(error.message));
    }
  });
});

rawFormula.addEventListener("keydown", (event) => {
  if (event.key === "Enter") btnFormula.click();
});
