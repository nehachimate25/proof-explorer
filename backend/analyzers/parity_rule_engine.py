"""
Parity Rule Engine
---------------------
A genuine mathematical TRUTH engine for conditional statements about the
parity of n, n\u00b2, n+1, and n-1. This is the fix for the core bug: earlier
code only had hand-written templates for the TRUE cases (even -> even
square, odd -> odd square), so a FALSE statement like "if n is odd, then
n\u00b2 is even" fell through to the generic fallback and was mislabeled
SUPPORTED instead of DISPROVED.

The key mathematical fact this engine encodes:

    parity(n\u00b2)     = parity(n)              (squares preserve parity)
    parity(n + 1) = flip(parity(n))        (adding 1 flips parity)
    parity(n - 1) = flip(parity(n))        (subtracting 1 flips parity)

Given a hypothesis "{expr1} is {parity1}", this pins down n's own parity
(the map above is self-inverse for all four expression kinds, so solving
"what is n's parity given expr1's parity" uses the exact same table).
From n's parity we can then compute the ACTUAL parity of the conclusion's
expression and compare it to what the statement claims. If they match,
the statement is TRUE and we generate a real algebraic proof. If they
don't, the statement is FALSE and we construct a genuine, checked
counterexample -- never a random guess.

This determinism is what lets the system tell TRUE, FALSE, and UNKNOWN
apart, instead of inferring truth merely from having the syntactic shape
P -> Q.
"""

import re

KIND_LABELS = {
    "n": "n",
    "n^2": "n\u00b2",
    "n+1": "n + 1",
    "n-1": "n - 1",
}


def _kind_label(kind: str, var: str = "n") -> str:
    if var == "n":
        return KIND_LABELS[kind]
    return KIND_LABELS[kind].replace("n", var)


def _opposite(parity: str) -> str:
    return "even" if parity == "odd" else "odd"


def _flips(kind: str) -> bool:
    return kind in ("n+1", "n-1")


def _resolve_base_parity(kind: str, parity: str) -> str:
    """Given that expression `kind` has the given `parity`, determine n's
    own parity. The map is self-inverse (identity for n/n\u00b2, flip for
    n\u00b11), so applying it once more recovers n's parity from the
    expression's parity."""
    return _opposite(parity) if _flips(kind) else parity


def _apply_parity(kind: str, base_parity: str) -> str:
    """Given n's parity, determine the actual parity of expression `kind`."""
    return _opposite(base_parity) if _flips(kind) else base_parity


# Hand-verified algebra for deriving each expression kind from n = 2k or
# n = 2k + 1. Every entry here is a manually checked algebraic fact, not a
# per-statement template -- there are only 8 cells (4 kinds x 2 parities)
# and they are exhaustive and correct.
_ALGEBRA = {
    ("n", "even"): {"steps": [], "closing": None},
    ("n", "odd"): {"steps": [], "closing": None},
    ("n^2", "even"): {
        "steps": ["n\u00b2 = (2k)\u00b2", "n\u00b2 = 4k\u00b2", "n\u00b2 = 2(2k\u00b2)"],
        "closing": "Since 2k\u00b2 is an integer, n\u00b2 is even.",
    },
    ("n^2", "odd"): {
        "steps": ["n\u00b2 = (2k + 1)\u00b2", "n\u00b2 = 4k\u00b2 + 4k + 1", "n\u00b2 = 2(2k\u00b2 + 2k) + 1"],
        "closing": "Since 2k\u00b2 + 2k is an integer, n\u00b2 is odd.",
    },
    ("n+1", "even"): {
        "steps": ["n + 1 = 2k + 1"],
        "closing": "Since k is an integer, n + 1 is odd.",
    },
    ("n+1", "odd"): {
        "steps": ["n + 1 = (2k + 1) + 1", "n + 1 = 2k + 2", "n + 1 = 2(k + 1)"],
        "closing": "Since k + 1 is an integer, n + 1 is even.",
    },
    ("n-1", "even"): {
        "steps": ["n - 1 = 2k - 1", "n - 1 = 2(k - 1) + 1"],
        "closing": "Since k - 1 is an integer, n - 1 is odd.",
    },
    ("n-1", "odd"): {
        "steps": ["n - 1 = (2k + 1) - 1", "n - 1 = 2k"],
        "closing": "Since k is an integer, n - 1 is even.",
    },
}


def _value_of(kind: str, n: int) -> int:
    if kind == "n":
        return n
    if kind == "n^2":
        return n * n
    if kind == "n+1":
        return n + 1
    if kind == "n-1":
        return n - 1
    raise ValueError(kind)


def _parity_of_value(v: int) -> str:
    return "even" if v % 2 == 0 else "odd"


def _build_direct_steps(p_kind, p_parity, q_kind, q_parity, base_parity, var="n"):
    p_label = _kind_label(p_kind, var)
    q_label = _kind_label(q_kind, var)

    steps = [{"statement": f"Assume {p_label} is {p_parity}.", "reason": "Assumption"}]

    if p_kind == "n^2":
        steps.append({
            "statement": f"Since {p_label} is {p_parity} if and only if {var} is {p_parity} (squares preserve parity), {var} is {p_parity}.",
            "reason": "Logical equivalence",
        })
    elif _flips(p_kind):
        op = "adding" if p_kind == "n+1" else "subtracting"
        steps.append({
            "statement": f"Since {p_label} is {p_parity}, and {op} 1 flips parity, {var} is {base_parity}.",
            "reason": "Logical equivalence",
        })

    steps.append({
        "statement": f"By definition, {var} = {'2k' if base_parity == 'even' else '2k + 1'} for some integer k.",
        "reason": "Definition",
    })

    algebra = _ALGEBRA[(q_kind, base_parity)]
    for s in algebra["steps"]:
        steps.append({"statement": s.replace("n", var) if var != "n" else s, "reason": "Algebraic simplification"})
    if algebra["closing"]:
        steps.append({"statement": algebra["closing"].replace("n", var) if var != "n" else algebra["closing"], "reason": "Definition"})

    steps.append({
        "statement": f"Therefore, if {p_label} is {p_parity}, then {q_label} is {q_parity}.",
        "reason": "Logical equivalence",
    })
    return steps


def _build_contrapositive_steps(p_kind, p_parity, q_kind, q_parity, var="n"):
    p_label = _kind_label(p_kind, var)
    q_label = _kind_label(q_kind, var)

    cp_p_kind, cp_p_parity = q_kind, _opposite(q_parity)
    cp_q_kind, cp_q_parity = p_kind, _opposite(p_parity)
    cp_base_parity = _resolve_base_parity(cp_p_kind, cp_p_parity)

    inner = _build_direct_steps(cp_p_kind, cp_p_parity, cp_q_kind, cp_q_parity, cp_base_parity, var)

    steps = [
        {"statement": f"Original: P \u2192 Q, where P = '{p_label} is {p_parity}', Q = '{q_label} is {q_parity}'.", "reason": "Definition"},
        {"statement": f"Contrapositive: \u00acQ \u2192 \u00acP, i.e. 'if {q_label} is {cp_p_parity}, then {p_label} is {cp_q_parity}'.", "reason": "Logical equivalence"},
    ]
    steps.extend(inner[:-1])  # drop inner's own "Therefore" line
    steps.append({"statement": "We have shown \u00acQ \u2192 \u00acP. Since a conditional and its contrapositive are logically equivalent, P \u2192 Q holds.", "reason": "Logical equivalence"})
    steps.append({"statement": f"Therefore, if {p_label} is {p_parity}, then {q_label} is {q_parity}.", "reason": "Logical equivalence"})
    return steps


def _build_contradiction_steps(p_kind, p_parity, q_kind, q_parity, base_parity, var="n"):
    p_label = _kind_label(p_kind, var)
    q_label = _kind_label(q_kind, var)

    direct = _build_direct_steps(p_kind, p_parity, q_kind, q_parity, base_parity, var)
    middle = direct[1:-1]  # drop "Assume P" and "Therefore" framing, keep the derivation

    steps = [{"statement": f"Assume, for contradiction, that {p_label} is {p_parity} but {q_label} is {_opposite(q_parity)}.", "reason": "Assumption"}]
    steps.extend(middle)
    steps.append({"statement": f"This contradicts our assumption that {q_label} is {_opposite(q_parity)}.", "reason": "Contradiction"})
    steps.append({"statement": f"Therefore the assumption was false: if {p_label} is {p_parity}, then {q_label} must be {q_parity}.", "reason": "Contradiction"})
    return steps


def _build_counterexample(p_kind, p_parity, q_kind, q_parity, base_parity, var="n"):
    """Construct a genuine, checked counterexample -- an actual integer n
    that satisfies P and violates Q, never a random guess. We pick the
    smallest n whose parity is base_parity (1 for odd, 2 for even); by
    construction of base_parity this n is GUARANTEED to satisfy P, and we
    verify that fact numerically below rather than assuming it."""
    n = 1 if base_parity == "odd" else 2

    p_val = _value_of(p_kind, n)
    q_val = _value_of(q_kind, n)
    p_actual = _parity_of_value(p_val)
    q_actual = _parity_of_value(q_val)

    # Defensive check: the counterexample must actually satisfy P.
    assert p_actual == p_parity, "internal error: counterexample does not satisfy P"

    p_label = _kind_label(p_kind, var)
    q_label = _kind_label(q_kind, var)

    explanation = (
        f"{var} = {n}. "
        f"{p_label} = {p_val}, which is {p_actual} (satisfies P: '{p_label} is {p_parity}'). "
        f"{q_label} = {q_val}, which is {q_actual}, not {q_parity} (violates Q: '{q_label} is {q_parity}')."
    )

    return {"value": n, "explanation": explanation}


def evaluate(p_kind: str, p_parity: str, q_kind: str, q_parity: str, var: str = "n"):
    """Core entry point: given a parsed P and Q (each an (expression kind,
    parity) pair), determine whether the conditional is TRUE or FALSE and
    return a fully-formed analyzer result -- VERIFIED with real proofs, or
    DISPROVED with a real counterexample. Never SUPPORTED: for pure parity
    conditionals of this form, the engine always has enough information to
    decide TRUE or FALSE outright."""
    base_parity = _resolve_base_parity(p_kind, p_parity)
    actual_q_parity = _apply_parity(q_kind, base_parity)
    truth = actual_q_parity == q_parity

    p_label = _kind_label(p_kind, var)
    q_label = _kind_label(q_kind, var)

    classification = {
        "type": "Conditional Proposition",
        "variable": var,
        "domain": f"{var} \u2208 \u2124",
        "P": f"{p_label} is {p_parity}",
        "Q": f"{q_label} is {q_parity}",
        "logical_form": "P \u2192 Q",
    }

    if truth:
        direct_steps = _build_direct_steps(p_kind, p_parity, q_kind, q_parity, base_parity, var)
        contrapositive_steps = _build_contrapositive_steps(p_kind, p_parity, q_kind, q_parity, var)
        contradiction_steps = _build_contradiction_steps(p_kind, p_parity, q_kind, q_parity, base_parity, var)
        conclusion = f"Therefore, if {p_label} is {p_parity}, then {q_label} is {q_parity}."

        return {
            "classification": classification,
            "methods": {
                "direct": {"suitable": True, "reason": "Direct algebraic proof: substitute n = 2k or 2k + 1 and simplify."},
                "contrapositive": {"suitable": True, "reason": "Equally valid: proves the logically equivalent contrapositive instead."},
                "contradiction": {"suitable": True, "reason": "Also valid: assumes the negation and derives a contradiction."},
                "induction": {"suitable": False, "reason": "This is a conditional statement about an arbitrary integer, not a recursively indexed proposition P(n)."},
            },
            "support_level": "VERIFIED",
            "status": "VERIFIED",
            "truth_value": True,
            "proofs": {
                "direct": {"steps": direct_steps, "conclusion": conclusion},
                "contrapositive": {"steps": contrapositive_steps, "conclusion": conclusion},
                "contradiction": {"steps": contradiction_steps, "conclusion": conclusion},
            },
        }

    counterexample = _build_counterexample(p_kind, p_parity, q_kind, q_parity, base_parity, var)
    return {
        "classification": classification,
        "methods": {
            m: {"suitable": False, "reason": "This statement is false, so no valid proof exists."}
            for m in ["direct", "contrapositive", "contradiction", "induction"]
        },
        "support_level": "DISPROVED",
        "status": "DISPROVED",
        "truth_value": False,
        "counterexample": counterexample,
        "reason": "A counterexample satisfies P but does not satisfy Q.",
        "proofs": {},
    }


# ---------------------------------------------------------------------------
# Clause parsing -- extracts (kind, parity) from normalized clause text.
# Order matters: check n\u00b2 / n+1 / n-1 before the bare-variable pattern.
# ---------------------------------------------------------------------------

def _extract_clause(text: str):
    t = text.strip()

    m = re.search(r"([a-zA-Z])\s*\u00b2\s+is\s+(even|odd)", t)
    if m:
        return m.group(1), "n^2", m.group(2)

    m = re.search(r"([a-zA-Z])\s*\+\s*1\s+is\s+(even|odd)", t)
    if m:
        return m.group(1), "n+1", m.group(2)

    m = re.search(r"([a-zA-Z])\s*-\s*1\s+is\s+(even|odd)", t)
    if m:
        return m.group(1), "n-1", m.group(2)

    m = re.search(r"\b([a-zA-Z])\s+is\s+(even|odd)\b", t)
    if m:
        return m.group(1), "n", m.group(2)

    return None


def try_match(text_norm: str):
    """Entry point for conditional_analyzer.py. Returns an evaluate()
    result if the text is recognized as a parity conditional, else None."""
    t = text_norm.rstrip(".")

    m = re.search(r"^if\s+(.*?),?\s+then\s+(.*)$", t, re.IGNORECASE)
    if not m:
        return None

    p_raw, q_raw = m.group(1), m.group(2)
    p_clause = _extract_clause(p_raw)
    q_clause = _extract_clause(q_raw)
    if not p_clause or not q_clause:
        return None

    p_var, p_kind, p_parity = p_clause
    q_var, q_kind, q_parity = q_clause
    if p_var.lower() != q_var.lower():
        return None  # different variables -- not a pattern we can safely resolve

    return evaluate(p_kind, p_parity, q_kind, q_parity, var=p_var)
