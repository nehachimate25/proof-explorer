# Mathematical Proof Verification and Proof Method Explorer

An interactive Discrete Mathematics proof laboratory built for a B.Tech
Information Technology project. It covers four syllabus areas —
**Logic, Propositions, Proofs, and Mathematical Induction** — and, crucially,
explains *how* a statement is verified step by step rather than only
returning TRUE/FALSE.

## Why this is trustworthy

Mathematical correctness comes from a **deterministic verification engine**,
not from an AI model:

- **Logic** — a real recursive-descent parser evaluates every possible truth
  assignment (2ⁿ rows) to build truth tables and decide tautology /
  contradiction / equivalence. No guessing.
- **Proofs** — direct, contrapositive, and contradiction proofs come from a
  verified proof library *and* a dynamic rule-based pattern analyzer
  (`backend/analyzers/`). Any statement matching a recognized pattern
  (parity, divisibility, sums, irrationality, induction) gets a genuine,
  hand-verified algebraic proof — not just statements that are byte-for-byte
  in a static library. The system will refuse to run an unsuitable method
  (e.g. direct proof for "√2 is irrational") and explains why.
- **Induction** — base cases and inductive steps are checked with Python's
  exact `Fraction` arithmetic, not narration or floating point. Recognized
  dynamically from flexible phrasing (not just exact example-ID lookups).
- If a statement isn't recognized by any pattern, the app says so plainly
  (NEEDS_REVIEW / INVALID) instead of fabricating a proof.

No paid API is required anywhere in this project.

## Support levels

Every analysis returns one of four honest support levels:

| Level | Meaning |
|---|---|
| `VERIFIED` | Deterministic rule/proof template; every step has been checked. |
| `SUPPORTED` | Pattern recognized, structured explanation given, but full formal proof isn't auto-generated. |
| `NEEDS_REVIEW` | Partially understood; the engine can't safely complete it. |
| `INVALID` | Empty, malformed, or not a mathematical statement. |

The static example libraries (`proof_engine/library.py`,
`induction/library.py`) are an **optimization / verified-reference
shortcut** — an exact match there is a fast path to a known-good proof.
They are **not** a gatekeeper: any statement, matched or not, is routed
through the dynamic analyzer in `backend/analyzers/` for pattern-based
verification. A statement is never rejected just because it isn't in a
library.

## Project structure

```
proof-explorer/
├── run.py             Starts everything: the backend API and the web pages
├── check_app.py       Quick self-test (python check_app.py)
├── frontend/          Plain HTML, CSS and JavaScript (no build step)
│   ├── index.html, logic.html, propositions.html, proof-explorer.html,
│   │   induction.html, history.html, help.html, about.html
│   ├── css/style.css      All styling, in one file
│   └── js/
│       ├── api.js            Every request to the backend (uses fetch)
│       ├── common.js         Navigation, loading and error helpers
│       ├── views.js          Truth tables and induction results (shared)
│       └── logic.js, propositions.js, proof-explorer.js,
│           induction.js, history.js   One script per page
├── backend/           Flask + SQLite (unchanged)
│   ├── app.py
│   ├── routes/            logic, proposition, proof, induction, history
│   ├── logic/              parser.py, truth_table.py, evaluator.py
│   ├── analyzers/          statement_analyzer.py (master dispatcher), normalizer.py,
│   │                       conditional_analyzer.py, parity_analyzer.py,
│   │                       divisibility_analyzer.py, induction_analyzer.py,
│   │                       irrationality_analyzer.py, logic_analyzer.py
│   ├── proof_engine/       library.py, direct.py, contrapositive.py, contradiction.py,
│   │                       validator.py, dynamic_proof.py
│   ├── induction/           library.py, base_case.py, hypothesis.py, inductive_step.py,
│   │                        pipeline.py
│   ├── validators/         statement_classifier.py (merged library + dynamic routing)
│   ├── models/              history.py
│   └── database/            db.py (SQLite)
└── README.md
```

## How to run it (Windows + VS Code)

You need **Python 3.9 or newer**. Check with `python --version` in a terminal.
If it is missing, install it from https://www.python.org/downloads/ and tick
**"Add python.exe to PATH"** in the installer. You do **not** need Node.js or
npm any more.

1. **Open the folder.** In VS Code choose *File > Open Folder...* and pick the
   `proof-explorer` folder (the one that contains `run.py`).
2. **Open a terminal.** *Terminal > New Terminal*.
3. **Create a virtual environment** (only the first time):
   ```
   python -m venv venv
   ```
4. **Switch it on:**
   ```
   venv\Scripts\activate
   ```
   You should now see `(venv)` at the start of the prompt.
   If PowerShell says scripts are disabled, run this once and try again:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
   (or just choose *Command Prompt* from the terminal's drop-down list instead).
5. **Install the two backend packages** (only the first time):
   ```
   pip install -r backend\requirements.txt
   ```
6. **Start the app:**
   ```
   python run.py
   ```
7. **Open http://localhost:5000** in your browser.

Press `Ctrl+C` in the terminal to stop it. Next time you only need steps 2, 4
and 6.

If VS Code asks which Python to use, pick the one inside `venv`
(*Ctrl+Shift+P > Python: Select Interpreter*).

### Check that everything works

With the virtual environment switched on:

```
python check_app.py
```

It tests the health endpoint, every page, and every API route, and prints
`PASS` or `FAIL` for each. You can also open
http://localhost:5000/api/health while the app is running; it should show
`{"status": "ok", ...}`.

### How the pieces fit together

`backend/app.py` is the original Flask app and has not been changed. `run.py`
imports it and adds one thing: it also serves the files in `frontend/`. So
the web pages and the API both live at `localhost:5000`. A request to
`/api/...` goes to the backend routes exactly as before, and the pages use the
browser's built-in `fetch` function to call them. There is no proxy, no build
step, and nothing to compile: edit a file in `frontend/`, save, and refresh
the browser.

(`python backend/app.py` still starts the API on its own, but then nothing
serves the web pages. Use `python run.py`.)

## Dependencies

Python (backend, unchanged): `Flask==3.0.3`, `Flask-Cors==4.0.1`.

Frontend: none. The pages use only HTML, CSS and JavaScript that every
browser already understands. No fonts or scripts are downloaded from the
internet, so the app also works offline.

**Removed from the old frontend:** React, React DOM, React Router, JSX,
Vite, `@vitejs/plugin-react`, Tailwind CSS, PostCSS, Autoprefixer,
`lucide-react` (icons), Google Fonts (Inter, Source Serif 4, JetBrains Mono),
`package.json`, `package-lock.json`, `vite.config.js`, `tailwind.config.js`,
`postcss.config.js`, and the `npm install` / `npm run dev` steps.

## Using the app

1. **Home** — an example proof and links to every section.
2. **Logic** — build an expression with P, Q, ¬ ∧ ∨ → ↔, generate its truth
   table, check tautology/contradiction, compare two expressions for
   logical equivalence, evaluate one row, or see the converse, inverse and
   contrapositive of an implication.
3. **Propositions** — enter a statement's P, Q and connecting operator to see
   its logical form and classification (conditional, biconditional, etc.).
4. **Proof Explorer** — the central module. Enter a statement (or pick one
   from the verified library), see which proof methods are mathematically
   suitable, and step through the chosen proof one step at a time — each
   step explains *what happened* and *why it's valid*. Compare methods
   side by side, then save the result to History.
5. **Induction** — type your own statement or pick an example, and watch the Base Case get computed
   exactly, the Inductive Hypothesis stated (clearly labeled as an
   assumption, not a proof), and the Inductive Step verified both
   symbolically and with numeric spot-checks (you can also test your own k).
6. **History** — everything you've saved from the Proof Explorer, stored in
   SQLite, with delete support.
7. **Help / About** — beginner-friendly explanations of every concept, and
   the project's purpose and architecture.

## Verified example library

| Method | Statement |
|---|---|
| Direct | If n is even, then n² is even |
| Direct | The sum of two even integers is even |
| Direct | The sum of two odd integers is even |
| Contrapositive | If n² is odd, then n is odd |
| Contradiction | √2 is irrational |
| Contradiction | There is no largest integer |
| Induction | 1 + 2 + ... + n = n(n+1)/2 |
| Induction | 1 + 3 + ... + (2n-1) = n² |
| Induction | 2ⁿ ≥ n+1 for all n ≥ 0 |
| Induction | n³ - n is divisible by 3 |

Every entry above was manually checked line-by-line before being added, and
is additionally covered by an automated correctness test (see below).

## Extending the library

To add a new fully-verified statement, add an entry to
`backend/proof_engine/library.py` (for direct/contrapositive/contradiction)
or `backend/induction/library.py` (for induction), following the existing
structure. **Verify the mathematics by hand before adding an entry** — this
library is the system's only source of truth for Tier 1 statements.

## Running the correctness tests

The core engines were validated during development with scripts like:

```bash
cd backend
python3 -c "
from logic.truth_table import classify, check_equivalence
assert classify('P | !P')['classification'] == 'Tautology'
assert check_equivalence('P -> Q', '!Q -> !P')['equivalent'] == True
assert check_equivalence('P -> Q', 'Q -> P')['equivalent'] == False
print('OK')
"
```

You can run similar checks against `induction/base_case.py`,
`induction/inductive_step.py`, and `proof_engine/*` to confirm every example
still verifies after any change to the library.

## Notes

- This is intentionally a curated library rather than a general theorem
  prover — see spec section 21's tiered design. Arbitrary user statements
  that don't match the library fall through to a structured Tier 2 flow or
  an honest Tier 3 "cannot verify" message. It is never allowed to display
  "PROVED" without genuine verification evidence.
- The backend has no external network dependency and runs entirely offline.
