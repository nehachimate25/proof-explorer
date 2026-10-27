// ============================================================================
// induction.js - the Induction page.
//
// Backend routes used here:
//   GET  /api/induction/examples            list of example statements
//   POST /api/induction/analyze             full induction for one example
//   POST /api/induction/analyze-statement   full induction for typed text
//   POST /api/induction/step                (inside views.js: "try your own k")
// ============================================================================

const statementInput = document.getElementById("statement");
const analyzeButton = document.getElementById("btn-analyze");
const examplesBox = document.getElementById("examples");
const output = document.getElementById("output");

let examples = [];        // the list from the backend
let selectedId = null;    // which example is highlighted
let requestCounter = 0;   // so an old slow answer never replaces a newer one

// ---------- the example list ----------

const exampleItems = {}; // example id -> { item, button }, so we can update them in place

// Build the list once.
function drawExamples() {
  const items = examples.map((example) => {
    const button = h(
      "button",
      { type: "button", class: "link-button math", onclick: () => selectExample(example.id) },
      example.statement
    );
    const item = h("li", {}, button, h("span", { class: "item-note" }, "Starts at n = " + example.domain_start));
    exampleItems[example.id] = { item, button };
    return item;
  });
  show(examplesBox, h("ul", { class: "item-list" }, items));
  markSelected();
}

// Highlight the chosen example without rebuilding the list
// (rebuilding would make the keyboard focus jump away).
function markSelected() {
  for (const [id, parts] of Object.entries(exampleItems)) {
    const isSelected = id === selectedId;
    parts.item.className = isSelected ? "selected" : "";
    parts.button.setAttribute("aria-pressed", isSelected ? "true" : "false");
  }
}

async function loadExamples() {
  showLoading(examplesBox, "Loading examples...");
  try {
    examples = await api.listInductionExamples();
  } catch (error) {
    show(examplesBox, errorNotice("The example list could not be loaded. " + error.message));
    return;
  }
  if (examples.length === 0) {
    show(examplesBox, h("p", { class: "empty" }, "The backend has no induction examples to show."));
    return;
  }
  drawExamples();
  selectExample(examples[0].id); // start with a worked example on screen
}

// ---------- an example from the list ----------

function selectExample(id) {
  selectedId = id;
  statementInput.value = "";
  markSelected();
  const myNumber = ++requestCounter;

  runTask(output, [analyzeButton], async () => {
    const result = await api.analyzeInduction(id);
    if (myNumber !== requestCounter) return;
    show(
      output,
      h("div", { class: "result" },
        h("h3", {}, h("span", { class: "math" }, result.statement)),
        renderInductionResult(result, id))
    );
  }, "Running the induction proof...");
}

// ---------- text typed by the user ----------

function analyzeTypedStatement() {
  const statement = statementInput.value.trim();
  if (statement === "") {
    show(output, errorNotice("Type a statement first, or choose an example above."));
    statementInput.focus();
    return;
  }

  selectedId = null;
  markSelected();
  const myNumber = ++requestCounter;

  runTask(output, [analyzeButton], async () => {
    const data = await api.analyzeInductionStatement(statement);
    if (myNumber !== requestCounter) return;

    // The backend answers { applicable: false, message } when induction is not suitable.
    if (!data.applicable) {
      show(
        output,
        h("div", { class: "notice warning" },
          h("p", {}, h("strong", {}, "Induction does not fit this statement. "), data.message),
          h("p", { class: "math" }, data.statement))
      );
      return;
    }

    const form = data.classification && data.classification.logical_form;
    show(
      output,
      h("div", { class: "result" },
        h("h3", {}, h("span", { class: "math" }, data.statement)),
        form ? h("p", { class: "math soft" }, form) : null,
        renderInductionResult(data))
    );
  }, "Running the induction proof...");
}

analyzeButton.addEventListener("click", analyzeTypedStatement);
statementInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") analyzeTypedStatement();
});

loadExamples();
