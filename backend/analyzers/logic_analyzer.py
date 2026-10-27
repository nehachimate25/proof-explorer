"""
Logic Analyzer (generic fallback)
-------------------------------------
For "if P then Q" statements that don't match any specific mathematical
template (parity, divisibility, etc). We can still say something true and
useful WITHOUT fabricating algebra:

  - The statement genuinely has the structure P \u2192 Q.
  - A conditional and its contrapositive are ALWAYS logically equivalent
    -- that's a fact about logic itself, true regardless of what P and Q
    mean, so it's safe to state.
  - We do NOT claim to have proved P \u2192 Q itself, since we don't know
    what P and Q mean mathematically. support_level is SUPPORTED, not
    VERIFIED, and no algebraic steps are generated.
"""

import re


def analyze(text_norm: str):
    stripped = text_norm.rstrip(".")
    m = re.search(r"^if\s+(.*?),?\s+then\s+(.*)$", stripped, re.IGNORECASE)
    if not m:
        return None

    p_text = m.group(1).strip()
    q_text = m.group(2).strip()
    if not p_text or not q_text:
        return None

    classification = {
        "type": "Conditional Proposition (general)",
        "variable": None,
        "domain": None,
        "P": p_text,
        "Q": q_text,
        "logical_form": "P \u2192 Q",
    }

    methods = {
        "direct": {
            "suitable": True,
            "reason": "Direct proof is structurally applicable to any P \u2192 Q, but no algebraic template is available for this specific P and Q.",
        },
        "contrapositive": {
            "suitable": True,
            "reason": "A conditional and its contrapositive (\u00acQ \u2192 \u00acP) are always logically equivalent, regardless of content.",
        },
        "contradiction": {
            "suitable": True,
            "reason": "Proof by contradiction is structurally applicable, but no template is available for this specific content.",
        },
        "induction": {
            "suitable": False,
            "reason": "No natural-number index variable was detected in this statement.",
        },
    }

    return {
        "classification": classification,
        "methods": methods,
        "support_level": "SUPPORTED",
        "proofs": {},
        "message": (
            "This statement's logical structure (P \u2192 Q) is recognized, but the current deterministic "
            "engine does not have a mathematical content template for this specific P and Q, so it cannot "
            "safely generate algebraic proof steps. You can still study its logical structure in the Logic module."
        ),
    }
