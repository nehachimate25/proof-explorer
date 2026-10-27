# Mathematical Proof Verification and Proof Method Explorer

An interactive Discrete Mathematics proof laboratory built for a B.Tech
Information Technology project. It covers four syllabus areas —
**Logic, Propositions, Proofs, and Mathematical Induction** — and, crucially,
explains *how* a statement is verified step by step rather than only
returning TRUE/FALSE.

# Why this is trustworthy

Mathematical correctness comes from a **deterministic verification engine**,
not from an AI model:

### 🧠 Logic
- Uses a recursive-descent parser to check all possible truth-value combinations and generate truth tables.
- Identifies whether a statement is a **tautology, contradiction, or logically equivalent** to another statement.

### 📘 Proofs
- Supports direct, contrapositive, and contradiction proofs.
- Uses a verified proof library and rule-based pattern analysis to generate algebraic proofs for recognized statements about parity, divisibility, sums, irrational numbers, and more.
- Checks whether a proof method is suitable for the given statement and explains when it is not.
- Does not rely only on predefined examples; it can recognize different ways of writing supported statements.

### 🔢 Mathematical Induction
- Checks base cases and inductive steps using Python's exact `Fraction` arithmetic.
- Recognizes supported induction statements written in different ways.
- Avoids floating-point calculation errors when checking exact fractions.

### ✅ Reliable Results
- If a statement is not recognized or cannot be verified, the system clearly marks it as `NEEDS_REVIEW` or `INVALID` instead of generating a fake proof.

No paid API is required anywhere in this project.

## Support levels

Every analysis returns one of four honest support levels:

| Level | Meaning |

|---|---|
| `VERIFIED` | The proof follows verified rules, and every step is checked. |
| `SUPPORTED` | The system recognizes the pattern and provides an explanation, but does not generate a complete formal proof. |
| `NEEDS_REVIEW` | The system understands part of the statement but cannot safely complete the analysis. |
| `INVALID` | The input is empty, incorrectly formatted, or not a valid mathematical statement. |

📚 Static Libraries and Dynamic Analysis

- Static libraries contain predefined examples and verified proofs that can be reused quickly.
- They help the system find known solutions faster.
- The dynamic analyzer in `backend/analyzers/` checks statements using recognized mathematical patterns.
- Statements do not need to exist in the static libraries to be analyzed.
- If the system cannot safely verify a statement, it reports the limitation instead of making up a proof.

## Project structure
## 📁 Project Structure

```text
proof-explorer/
├── run.py                  # Starts the backend and web pages
├── check_app.py            # Checks whether the app is working
├── frontend/               # Website built with HTML, CSS and JavaScript
│   ├── index.html          # Home page
│   ├── logic.html           # Logic and truth tables
│   ├── propositions.html    # Propositional logic
│   ├── proof-explorer.html  # Mathematical proofs
│   ├── induction.html       # Mathematical induction
│   ├── history.html         # Previous results
│   ├── help.html            # Help page
│   ├── about.html           # About the project
│   ├── css/
│   │   └── style.css        # Website design and styling
│   └── js/
│       ├── api.js           # Connects the frontend to the backend
│       ├── common.js        # Shared navigation and error handling
│       ├── views.js         # Displays tables and results
│       ├── logic.js         # Logic page functionality
│       ├── propositions.js  # Propositions page functionality
│       ├── proof-explorer.js # Proof page functionality
│       ├── induction.js     # Induction page functionality
│       └── history.js       # History page functionality
├── backend/                 # Flask backend and SQLite database
│   ├── app.py               # Creates the backend application
│   ├── routes/               # Handles API requests for each feature
│   ├── logic/                # Parses and evaluates logical expressions
│   ├── analyzers/            # Recognizes and analyzes mathematical patterns
│   ├── proof_engine/         # Generates and validates mathematical proofs
│   ├── induction/            # Handles induction proof steps
│   ├── validators/           # Checks and classifies input statements
│   ├── models/               # Defines data models
│   └── database/             # Manages SQLite database operations
└── README.md                 # Project documentation
```

### 🛠️ Technologies Used

- **Frontend:** HTML, CSS and JavaScript
- **Backend:** Python and Flask
- **Database:** SQLite
- **Communication:** Fetch API for sending requests between the frontend and backend

### 🔄 How It Works

1. The user enters a mathematical statement on the website.
2. JavaScript sends the input to the Flask backend using the Fetch API.
3. The backend analyzes the statement using logic parsers, mathematical analyzers, or proof engines.
4. The backend returns the result to the frontend.
5. JavaScript displays the truth table, proof, induction steps, or analysis status on the webpage.
6. SQLite stores relevant history for later viewing.

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


1. **Home** — Shows an example proof and links to all sections of the website.

2. **Logic** — Create logical expressions using symbols like `P`, `Q`, `¬`, `∧`, `∨`, `→`, and `↔`.
 Generate truth tables, check tautologies and contradictions, compare expressions, evaluate individual rows, 
 and find the converse, inverse, and contrapositive of an implication.

3. **Propositions** — Enter statements and logical operators to understand their logical structure and
 identify types such as conditional and biconditional statements.

4. **Proof Explorer** — Explore mathematical proofs using different methods, including direct proof,
 contrapositive, and contradiction. Follow each proof step by step, understand why each step is valid,
  compare suitable methods, and save results to History.

5. **Induction** — Enter a mathematical statement or choose an example. Check the base case, understand the inductive hypothesis, 
and verify the inductive step using symbolic calculations and numerical checks.

6. **History** — View and delete previously saved proof results stored in the SQLite database.

7. **Help & About** — Learn mathematical concepts through beginner-friendly explanations and 
understand the project's purpose and architecture.


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