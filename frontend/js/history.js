// ============================================================================
// history.js - the History page.
//
// Backend routes used here:
//   GET    /api/history        list saved proofs (newest first)
//   DELETE /api/history/<id>   delete one saved proof
// (Saving is done from the Proof Explorer page: POST /api/history.)
// ============================================================================

const listBox = document.getElementById("history-list");
const messageBox = document.getElementById("message");

function capitalize(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}

function buildEntry(entry) {
  const steps = entry.num_steps + (entry.num_steps === 1 ? " step" : " steps");

  const deleteButton = h("button", { type: "button", class: "btn btn-danger btn-small" }, "Delete");
  deleteButton.addEventListener("click", () => removeEntry(entry, deleteButton));

  return h(
    "li",
    { class: "history-item" },
    h(
      "div",
      {},
      h("p", {}, entry.statement),
      h(
        "span",
        { class: "item-note" },
        capitalize(entry.proof_method) + " proof, " + steps + ", saved " + formatDate(entry.created_at) + "  "
      ),
      statusLabel(entry.result)
    ),
    deleteButton
  );
}

async function loadHistory() {
  showLoading(listBox, "Loading your saved proofs...");
  let entries;
  try {
    entries = await api.listHistory();
  } catch (error) {
    show(listBox, errorNotice(error.message));
    return;
  }

  // Nothing saved yet: say what to do next.
  if (entries.length === 0) {
    show(
      listBox,
      h("div", { class: "empty" },
        h("p", {}, "You have not saved any proofs yet."),
        h("p", {}, "Open the ", h("a", { href: "proof-explorer.html" }, "Proof Explorer"),
          ", show a proof, and choose “Save to History”."))
    );
    return;
  }

  show(
    listBox,
    h("p", { class: "soft" }, entries.length + (entries.length === 1 ? " saved proof" : " saved proofs")),
    h("ul", { class: "item-list" }, entries.map(buildEntry))
  );
}

async function removeEntry(entry, button) {
  if (!window.confirm("Delete this saved proof?\n\n" + entry.statement)) return;

  button.disabled = true;
  show(messageBox);
  try {
    await api.deleteHistory(entry.id);
  } catch (error) {
    button.disabled = false;
    show(messageBox, errorNotice("Could not delete: " + error.message));
    return;
  }
  loadHistory();
}

loadHistory();
