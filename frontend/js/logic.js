// ============================================================================
// logic.js - the Logic page.
//
// Backend routes used here:
//   POST /api/logic/truth-table             make a truth table
//   POST /api/logic/analyze                 tautology / contradiction / contingency
//   POST /api/logic/equivalence             compare two formulas
//   POST /api/logic/evaluate                evaluate one row of the table
//   POST /api/proof/contrapositive/transform  converse, inverse, contrapositive
// ============================================================================

// Symbol buttons. `text` is what gets typed into the box.
const SYMBOLS = [
  { text: "¬", name: "NOT" },
  { text: " ∧ ", name: "AND" },
  { text: " ∨ ", name: "OR" },
  { text: " → ", name: "IMPLIES" },
  { text: " ↔ ", name: "IF AND ONLY IF" },
  { text: "(", name: "open bracket" },
  { text: ")", name: "close bracket" },
];

// ---------- find the elements we need ----------
const formulaInput = document.getElementById("formula");
const formulaA = document.getElementById("formula-a");
const formulaB = document.getElementById("formula-b");
const oneOutput = document.getElementById("one-output");
const compareOutput = document.getElementById("compare-output");
const btnTable = document.getElementById("btn-table");
const btnClassify = document.getElementById("btn-classify");
const btnVariants = document.getElementById("btn-variants");
const btnCompare = document.getElementById("btn-compare");

const oneFormulaButtons = [btnTable, btnClassify, btnVariants];

// ---------- symbol buttons ----------
// Each toolbar types into whichever of its boxes was used last.
document.querySelectorAll(".symbol-row").forEach((row) => {
  const inputs = row.dataset.targets.split(" ").map((id) => document.getElementById(id));
  let activeInput = inputs[0];
  inputs.forEach((input) => input.addEventListener("focus", () => (activeInput = input)));

  SYMBOLS.forEach((symbol) => {
    row.append(
      h(
        "button",
        {
          type: "button",
          class: "symbol-btn",
          title: symbol.name,
          "aria-label": "Insert " + symbol.name,
          onclick: () => insertAtCursor(activeInput, symbol.text),
        },
        symbol.text.trim()
      )
    );
  });
});

// ---------- example formulas ----------
document.querySelectorAll("[data-example]").forEach((button) => {
  button.addEventListener("click", () => {
    formulaInput.value = button.dataset.example;
    formulaInput.focus();
  });
});

// ---------- helpers ----------

// Returns the trimmed text, or shows a message and returns null if it is empty.
function readFormula(input, output) {
  const text = input.value.trim();
  if (text === "") {
    show(output, errorNotice("Type a formula first, for example P → Q."));
    input.focus();
    return null;
  }
  return text;
}

// Call the backend; if the formula is wrong, replace the parser's message
// with a friendlier one.
async function callWithFriendlyErrors(apiCall) {
  try {
    return await apiCall();
  } catch (error) {
    throw new Error(friendlyFormulaError(error.message));
  }
}

function mathSpan(text) {
  return h("span", { class: "math" }, text);
}

// ---------- 1. Truth table ----------

// "Try one row": tick which letters are true and ask the backend for the result.
function buildRowChecker(table) {
  const boxes = table.variables.map((name) => h("input", { type: "checkbox" }));
  const checks = table.variables.map((name, i) => h("label", { class: "check" }, boxes[i], name + " is true"));
  const output = h("div", { "aria-live": "polite" });
  const button = h("button", { type: "button", class: "btn btn-secondary btn-small" }, "Evaluate this row");

  button.addEventListener("click", () => {
    const assignment = {};
    table.variables.forEach((name, i) => (assignment[name] = boxes[i].checked));

    runTask(output, [button], async () => {
      const data = await callWithFriendlyErrors(() => api.evaluateLogic(table.expression, assignment));
      const description = table.variables.map((name) => name + " = " + (assignment[name] ? "true" : "false")).join(", ");
      show(
        output,
        h("p", {}, "With " + description + ", ", mathSpan(table.normalized), " is ",
          h("strong", { class: data.result ? "cell-true" : "cell-false" }, data.result ? "true" : "false"), ".")
      );
    });
  });

  return h(
    "div",
    {},
    h("h3", {}, "Try one row"),
    h("p", { class: "soft small" }, "Tick the letters that should be true, then ask the backend for the value of the formula."),
    h("div", {}, checks),
    button,
    output
  );
}

btnTable.addEventListener("click", () => {
  const formula = readFormula(formulaInput, oneOutput);
  if (!formula) return;

  runTask(oneOutput, oneFormulaButtons, async () => {
    const table = await callWithFriendlyErrors(() => api.truthTable(formula));
    show(
      oneOutput,
      h(
        "div",
        { class: "result" },
        h("h3", {}, "Truth table for ", mathSpan(table.normalized)),
        h("p", { class: "soft small" }, table.rows.length + " rows, one for each combination of true (T) and false (F)."),
        renderTruthTable(table),
        buildRowChecker(table)
      )
    );
  }, "Building the truth table...");
});

// ---------- 2. Tautology / contradiction ----------

const CLASSIFICATION_TEXT = {
  Tautology: {
    css: "status-good",
    meaning: "It is true in every row, so it is true whatever P, Q and R stand for.",
  },
  Contradiction: {
    css: "status-bad",
    meaning: "It is false in every row, so it can never be true.",
  },
  Contingency: {
    css: "status-review",
    meaning: "It is true in some rows and false in others, so its truth depends on the values of the letters.",
  },
};

btnClassify.addEventListener("click", () => {
  const formula = readFormula(formulaInput, oneOutput);
  if (!formula) return;

  runTask(oneOutput, oneFormulaButtons, async () => {
    const result = await callWithFriendlyErrors(() => api.analyzeLogic(formula));
    const info = CLASSIFICATION_TEXT[result.classification] || { css: "status-review", meaning: "" };
    show(
      oneOutput,
      h(
        "div",
        { class: "result" },
        h("h3", {}, mathSpan(result.normalized), " is a ", h("span", { class: "status " + info.css }, result.classification)),
        h("p", {}, info.meaning),
        renderTruthTable(result)
      )
    );
  }, "Checking every row...");
});

// ---------- 3. Converse, inverse, contrapositive ----------

btnVariants.addEventListener("click", () => {
  const formula = readFormula(formulaInput, oneOutput);
  if (!formula) return;

  runTask(oneOutput, oneFormulaButtons, async () => {
    const result = await callWithFriendlyErrors(() => api.transformConditional(formula));
    show(
      oneOutput,
      h(
        "div",
        { class: "result" },
        h("h3", {}, "Related statements"),
        h(
          "dl",
          { class: "facts math" },
          h("dt", {}, "Original"), h("dd", {}, result.original),
          h("dt", {}, "Converse"), h("dd", {}, result.converse),
          h("dt", {}, "Inverse"), h("dd", {}, result.inverse),
          h("dt", {}, "Contrapositive"), h("dd", {}, result.contrapositive)
        ),
        result.equivalence_verified
          ? notice("success", "The contrapositive matches the original in every row below, so the two are logically equivalent. This is why proving the contrapositive proves the original.")
          : notice("warning", "The contrapositive did not match the original in every row."),
        renderEquivalenceTable(result.equivalence_table),
        h("p", { class: "soft small" }, "The converse and the inverse are different statements. In general they are not equivalent to the original.")
      )
    );
  }, "Working out the related statements...");
});

// ---------- 4. Compare two formulas ----------

btnCompare.addEventListener("click", () => {
  const first = readFormula(formulaA, compareOutput);
  if (!first) return;
  const second = readFormula(formulaB, compareOutput);
  if (!second) return;

  runTask(compareOutput, [btnCompare], async () => {
    const result = await callWithFriendlyErrors(() => api.checkEquivalence(first, second));
    show(
      compareOutput,
      h(
        "div",
        { class: "result" },
        h(
          "h3",
          {},
          mathSpan(result.normalized1), " and ", mathSpan(result.normalized2), " are ",
          h("span", { class: "status " + (result.equivalent ? "status-good" : "status-bad") },
            result.equivalent ? "equivalent" : "not equivalent")
        ),
        h("p", {}, result.equivalent
          ? "They have the same truth value in every row."
          : "They differ in at least one row (marked \"no\" in the last column)."),
        renderEquivalenceTable(result)
      )
    );
  }, "Comparing every row...");
});

// ---------- Enter key ----------
formulaInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") btnTable.click();
});
[formulaA, formulaB].forEach((input) =>
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") btnCompare.click();
  })
);
