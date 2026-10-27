// ============================================================================
// common.js - small helpers used by every page.
//
// Load order on each page (see the <script> tags at the bottom of the HTML):
//     api.js  ->  common.js  ->  views.js  ->  the page's own file
// ============================================================================

// ---------- 1. Building HTML safely ----------------------------------------
//
// h("p", { class: "soft" }, "Hello ", h("b", {}, "world"))
// creates   <p class="soft">Hello <b>world</b></p>
//
// Strings become plain text (never HTML), so text that comes from the user or
// the backend can not inject markup into the page.
function h(tag, attributes, ...children) {
  const element = document.createElement(tag);

  for (const [name, value] of Object.entries(attributes || {})) {
    if (value === false || value === null || value === undefined) continue;
    if (name === "class") {
      element.className = value;
    } else if (name.startsWith("on") && typeof value === "function") {
      element.addEventListener(name.slice(2), value); // onclick -> "click"
    } else if (value === true) {
      element.setAttribute(name, "");
    } else {
      element.setAttribute(name, value);
    }
  }

  appendChildren(element, children);
  return element;
}

function appendChildren(parent, children) {
  for (const child of children) {
    if (child === null || child === undefined || child === false) continue;
    if (Array.isArray(child)) {
      appendChildren(parent, child);
    } else if (child instanceof Node) {
      parent.appendChild(child);
    } else {
      parent.appendChild(document.createTextNode(String(child)));
    }
  }
}

// Remove everything inside an element, then put new content in.
function show(container, ...children) {
  container.replaceChildren();
  appendChildren(container, children);
}

// ---------- 2. Loading, errors, empty results ------------------------------

function showLoading(container, text) {
  show(container, h("p", { class: "loading", role: "status" }, text || "Working..."));
}

function showError(container, message) {
  show(container, errorNotice(message));
}

function errorNotice(message) {
  return h("div", { class: "notice error", role: "alert" }, h("p", {}, message));
}

function notice(kind, ...children) {
  // kind is "warning", "success" or "error"
  return h("div", { class: "notice " + kind }, h("p", {}, children));
}

// Run an async task while the given buttons are switched off.
//   output  : the element that shows "Working..." and, if the task fails, the error
//   buttons : buttons to disable until the task finishes (stops double clicks)
async function runTask(output, buttons, task, loadingText) {
  buttons.forEach((button) => (button.disabled = true));
  if (output) showLoading(output, loadingText);
  try {
    await task();
  } catch (error) {
    if (output) showError(output, error.message);
  } finally {
    buttons.forEach((button) => (button.disabled = false));
  }
}

// ---------- 3. Small display helpers ---------------------------------------

// "VERIFIED" -> a coloured label with a readable word.
function statusLabel(status) {
  const known = {
    VERIFIED: ["Verified", "status-good"],
    PROVED: ["Proved", "status-good"],
    SUPPORTED: ["Supported", "status-info"],
    DISPROVED: ["Disproved", "status-bad"],
    INVALID: ["Invalid", "status-bad"],
    NEEDS_REVIEW: ["Needs review", "status-review"],
    "NEEDS REVIEW": ["Needs review", "status-review"],
  };
  const [text, cssClass] = known[status] || ["Needs review", "status-review"];
  return h("span", { class: "status " + cssClass }, text);
}

function trueFalse(value) {
  return value ? "T" : "F";
}

// Put a symbol into a text box where the cursor is (instead of at the end).
function insertAtCursor(input, text) {
  const start = input.selectionStart ?? input.value.length;
  const end = input.selectionEnd ?? input.value.length;
  input.value = input.value.slice(0, start) + text + input.value.slice(end);
  const cursor = start + text.length;
  input.focus();
  input.setSelectionRange(cursor, cursor);
}

// The database stores UTC time like "2026-10-13 18:51:17".
// Show it in the visitor's own time zone.
function formatDate(databaseTime) {
  const date = new Date(String(databaseTime).replace(" ", "T") + "Z");
  if (Number.isNaN(date.getTime())) return String(databaseTime);
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

// The formula parser in the backend reports mistakes in programmer language.
// This turns the most common ones into something a student can act on.
// (The backend itself is not changed; only the text shown to the user is.)
function friendlyFormulaError(message) {
  if (message.includes("(None, None)") || message.startsWith("Expected RPAREN")) {
    return "The formula ends too early or has an unclosed bracket. Check that every operator has a formula on both sides and every ( has a matching ).";
  }
  if (message.startsWith("Unexpected token at end")) {
    return "There is an extra letter or symbol in the formula. Two letters need an operator between them, for example P ∧ Q.";
  }
  if (message === "Empty expression") {
    return "Type a formula first, for example P → Q.";
  }
  return message;
}

// ---------- 4. Header, footer and backend check ----------------------------

const PAGES = [
  { file: "index.html", label: "Home" },
  { file: "logic.html", label: "Logic" },
  { file: "propositions.html", label: "Propositions" },
  { file: "proof-explorer.html", label: "Proof Explorer" },
  { file: "induction.html", label: "Induction" },
  { file: "history.html", label: "History" },
  { file: "help.html", label: "Help" },
  { file: "about.html", label: "About" },
];

function currentPageFile() {
  const last = window.location.pathname.split("/").pop();
  return last === "" ? "index.html" : last;
}

function buildHeader() {
  const holder = document.getElementById("site-header");
  if (!holder) return;
  const here = currentPageFile();

  const links = PAGES.map((page) =>
    h("a", { href: page.file, "aria-current": page.file === here ? "page" : false }, page.label)
  );

  show(
    holder,
    h(
      "div",
      { class: "site-header-inner" },
      h("a", { class: "brand", href: "index.html" }, "Proof Explorer"),
      h("nav", { class: "site-nav", "aria-label": "Main" }, links)
    )
  );
}

function buildFooter() {
  const holder = document.getElementById("site-footer");
  if (!holder) return;
  show(
    holder,
    "Every result is calculated by the Python backend on your own computer. No account and no AI service is used."
  );
}

// If the backend is not running, say so clearly at the top of the page
// instead of letting every button fail with a confusing message.
async function checkBackend() {
  try {
    await api.health();
  } catch (error) {
    const main = document.querySelector("main");
    if (!main) return;
    main.prepend(
      h(
        "div",
        { class: "notice error", role: "alert" },
        h(
          "p",
          {},
          "The backend is not responding, so nothing on this page will work yet. ",
          "Start it with ",
          h("code", {}, "python run.py"),
          " and then reload the page."
        )
      )
    );
  }
}

buildHeader();
buildFooter();
checkBackend();
