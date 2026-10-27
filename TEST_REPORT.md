# Test report

Frontend rebuilt in HTML, CSS and vanilla JavaScript, tested against the
**unchanged** Flask backend started with `python run.py`.

Backend integrity: SHA-256 checksums of all 43 files in `backend/` were taken
before the work and compared afterwards. All match.

## How it was tested

1. `python check_app.py` (included): 42 checks of the health endpoint, every
   page and asset, and every API route. **42/42 passed.**
2. A scripted browser run (headless Chromium, 161 checks) that opened every
   page, clicked buttons, typed input and read the results from the screen,
   while recording JavaScript errors and failed requests.
   **161/161 passed, 0 JavaScript errors.** The only HTTP 4xx responses were
   the 400s deliberately triggered by invalid formulas.

The browser script is not shipped because it needs Playwright; run
`check_app.py` for the repeatable check.

## Features tested

| Area | What was checked |
|---|---|
| Health | `GET /api/health` returns `{"status":"ok"}`; the page shows a banner telling the user to run `python run.py` when it cannot be reached |
| Serving | All 8 pages, the stylesheet and 8 scripts return 200; `/` opens Home; unknown `/api/...` URLs still return the backend's JSON 404 (GET and POST); path traversal is blocked |
| Navigation | 8 nav links on every page, current page marked; every internal link resolves |
| Logic | Truth table (unicode and `->`/`!`/`&` input, 2 and 3 letters); evaluate one row; tautology / contradiction / contingency; converse, inverse, contrapositive; equivalence (equal and not equal); symbol buttons insert at the cursor; example buttons; Enter key |
| Logic errors | Empty input, unfinished formula, unclosed bracket, missing operator, unknown symbol, more than 6 letters, non-conditional for the contrapositive tool |
| Propositions | Conditional, biconditional, conjunction, disjunction, negation; direct formula; empty P / empty Q validation |
| Proof Explorer | 6 library examples; analyze typed text; library proofs by direct, contrapositive and contradiction; dynamic (non-library) proof; step-by-step reveal, show all, start over; compare methods; save to History (once only); disproved statement with counterexample; invalid text; unrecognised pattern ("needs review"); statement with no proof template; only-contradiction case (√2); induction statement handled inside the explorer; `?statement=` link from Home |
| Induction | All 5 library examples (base case, hypothesis, step, spot checks, conclusion); own statement; statement where induction does not fit; empty and nonsense input; "try your own k" (valid values and 5 invalid ones) |
| History | List, entry details and local date, delete with confirm (cancel keeps, OK removes), empty state with link |
| Help / About | 9 collapsible questions, symbol table, no outdated React text |
| Errors | Backend unreachable (page banner, action error, history, example list); unreadable server response; buttons re-enabled after every failure |
| Safety | HTML typed by the user is displayed as text, never run |
| Responsive | All 8 pages at 375px wide: no sideways page scroll |

## Problems found and fixed during testing

- **Double save:** the "Saved" button was switched back on by the loading
  helper, so the same proof could be saved twice. Fixed.
- **Old UI bug, not carried over:** the old Propositions page still sent the
  Q text when the operator was ¬, which made the backend build `P ¬ Q` and
  fail. The new page sends an empty Q for ¬.
- **Old UI gaps, now handled:** failed example loading and unknown proof
  statuses (e.g. `not_found`) were silently ignored; empty input did nothing.
  The new pages show a message in each case.
- **Hypothesis label:** repeated its own heading; trimmed.

## Known backend behaviour (not changed)

- `/api/induction/step` does not validate `sample_k`; a non-number gives a
  500. The page only sends whole numbers from the start value up to 100.
- Parser errors such as `Unexpected token: (None, None)` are technical; the
  pages translate the common ones into plain language and show the rest as is.
- The README lists induction examples under the proof library, but
  `/api/proof/examples` returns only the 6 non-induction ones; induction
  examples are on the Induction page.
