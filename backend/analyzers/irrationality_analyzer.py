"""
Irrationality Analyzer
--------------------------
Recognizes standalone irrationality claims ("\u221ak is irrational"). Only
\u221a2 has a fully generated contradiction proof (reusing the hand-verified
library entry). For other k, the system honestly reports SUPPORTED
(pattern recognized, full auto-proof not yet templated) rather than
fabricating the general lowest-terms argument, and it actively catches the
mathematically FALSE case (k a perfect square) instead of pretending to
prove a false statement.
"""

import re
import math


def _is_perfect_square(k: int) -> bool:
    root = int(math.isqrt(k))
    return root * root == k


def analyze(text_norm: str):
    t = text_norm.lower()

    # \u221a2 specifically -- fully supported
    if re.search(r"(\u221a2|sqrt\(2\)|sqrt 2|root 2)\s+is\s+irrational", t):
        return {
            "classification": {
                "type": "Standalone Proposition",
                "variable": None,
                "domain": "N/A (a single real number)",
                "P": None,
                "Q": None,
                "logical_form": "S (not a conditional)",
            },
            "methods": {
                "direct": {"suitable": False, "reason": "Not applicable: irrationality is a non-existence claim, which contradiction handles naturally."},
                "contrapositive": {"suitable": False, "reason": "Not applicable: the statement is not a conditional P \u2192 Q."},
                "contradiction": {"suitable": True, "reason": "The classical elementary proof of this fact, via the lowest-terms argument."},
                "induction": {"suitable": False, "reason": "No natural number index is being incremented."},
            },
            "support_level": "VERIFIED",
            "proofs": {
                "contradiction": {
                    "steps": [
                        {"statement": "Assume, for contradiction, that \u221a2 is rational.", "reason": "Assumption"},
                        {"statement": "Then \u221a2 = p/q for integers p, q with q \u2260 0, where p/q is in lowest terms (gcd(p, q) = 1).", "reason": "Definition"},
                        {"statement": "Squaring both sides: 2 = p\u00b2/q\u00b2, so p\u00b2 = 2q\u00b2.", "reason": "Algebraic simplification"},
                        {"statement": "So p\u00b2 is even. Since n\u00b2 even implies n even, p is even: p = 2k for some integer k.", "reason": "Substitution"},
                        {"statement": "Substituting: (2k)\u00b2 = 2q\u00b2, so 4k\u00b2 = 2q\u00b2, so q\u00b2 = 2k\u00b2.", "reason": "Algebraic simplification"},
                        {"statement": "So q\u00b2 is even, and therefore q is even.", "reason": "Substitution"},
                        {"statement": "But then both p and q are even, so gcd(p, q) \u2265 2 -- contradicting that p/q was in lowest terms.", "reason": "Contradiction"},
                        {"statement": "This contradiction shows our assumption was false. Therefore \u221a2 is irrational.", "reason": "Contradiction"},
                    ],
                    "conclusion": "Therefore \u221a2 is irrational.",
                },
            },
        }

    # \u221ak for other k -- recognize but be careful
    m = re.search(r"(\u221a(\d+)|sqrt\((\d+)\)|sqrt (\d+)|root (\d+))\s+is\s+irrational", t)
    if m:
        k_str = next(g for g in m.groups()[1:] if g)
        k = int(k_str)

        if _is_perfect_square(k):
            root_val = int(math.isqrt(k))
            return {
                "classification": {
                    "type": "Standalone Proposition",
                    "variable": None,
                    "domain": "N/A (a single real number)",
                    "P": None,
                    "Q": None,
                    "logical_form": "S (not a conditional)",
                },
                "methods": {m2: {"suitable": False, "reason": "This statement is mathematically false."} for m2 in ["direct", "contrapositive", "contradiction", "induction"]},
                "support_level": "NEEDS_REVIEW",
                "proofs": {},
                "message": f"This statement appears to be mathematically FALSE: \u221a{k} = {root_val}, which is rational, since {k} is a perfect square.",
            }

        return {
            "classification": {
                "type": "Standalone Proposition",
                "variable": None,
                "domain": "N/A (a single real number)",
                "P": None,
                "Q": None,
                "logical_form": "S (not a conditional)",
            },
            "methods": {
                "direct": {"suitable": False, "reason": "Not applicable: irrationality is a non-existence claim."},
                "contrapositive": {"suitable": False, "reason": "Not applicable: not a conditional statement."},
                "contradiction": {"suitable": True, "reason": "The standard approach for irrationality claims, following the same lowest-terms argument as for \u221a2."},
                "induction": {"suitable": False, "reason": "No natural number index is being incremented."},
            },
            "support_level": "SUPPORTED",
            "proofs": {},
            "message": (
                f"Recognized as an irrationality claim about \u221a{k}. A fully automatic step-by-step proof is "
                f"currently only generated for \u221a2 in this version; general \u221a{k} proofs follow the same "
                f"lowest-terms contradiction argument but are not auto-generated yet."
            ),
        }

    if re.search(r"is irrational", t):
        return {
            "classification": {
                "type": "Standalone Proposition",
                "variable": None,
                "domain": None,
                "P": None,
                "Q": None,
                "logical_form": "S (not a conditional)",
            },
            "methods": {
                "direct": {"suitable": False, "reason": "Not applicable: irrationality is a non-existence claim."},
                "contrapositive": {"suitable": False, "reason": "Not applicable: not a conditional statement."},
                "contradiction": {"suitable": True, "reason": "The standard approach for irrationality claims."},
                "induction": {"suitable": False, "reason": "No natural number index is being incremented."},
            },
            "support_level": "SUPPORTED",
            "proofs": {},
            "message": "Recognized as an irrationality claim. Proof by contradiction is the standard approach, but this specific statement is not in the automatic template library yet.",
        }

    return None
