"""
Proof Example Library
-----------------------
This is the single source of truth for every statement the system can
FULLY, DETERMINISTICALLY verify (Tier 1). Every entry below has been
manually checked line-by-line for mathematical correctness before being
added here -- see spec section 20/37.

Each entry declares which proof method(s) are mathematically valid for it.
The Proof Explorer UI uses `valid_methods` to decide which method cards are
selectable, and explains why the others are unsuitable (spec section 9).

Statements NOT in this library fall through to Tier 2 (structured manual
input) or Tier 3 (unsupported) -- see routes/proof_routes.py.
"""

# Each step: step_number, statement, reason, verification_status
# reason is drawn from a controlled vocabulary (spec section 23).

LIBRARY = {

    "even-square-even": {
        "id": "even-square-even",
        "statement": "If n is even, then n\u00b2 is even.",
        "domain": "n \u2208 \u2124",
        "P": "n is even",
        "Q": "n\u00b2 is even",
        "logical_form": "P \u2192 Q",
        "valid_methods": ["direct", "contrapositive", "contradiction"],
        "method_notes": {
            "direct": "Direct proof works cleanly: assume P, algebraically derive Q.",
            "contrapositive": "Equivalent to proving 'if n\u00b2 is odd then n is odd' -- also valid, shown in the contrapositive module for the related statement.",
            "contradiction": "Possible (assume n even and n\u00b2 odd, derive a contradiction) but less direct than the other two methods here.",
            "induction": "Not applicable: this is a single-instance conditional about an arbitrary integer n, not a statement indexed over all n \u2265 some base case."
        },
        "direct_steps": [
            {"statement": "Assume n is even.", "reason": "Assumption"},
            {"statement": "By definition of an even integer, n = 2k for some integer k.", "reason": "Definition"},
            {"statement": "n\u00b2 = (2k)\u00b2", "reason": "Substitution"},
            {"statement": "n\u00b2 = 4k\u00b2", "reason": "Algebraic simplification"},
            {"statement": "n\u00b2 = 2(2k\u00b2)", "reason": "Algebraic simplification"},
            {"statement": "Since 2k\u00b2 is an integer, n\u00b2 is of the form 2m (m = 2k\u00b2), so n\u00b2 is even.", "reason": "Definition"},
            {"statement": "Therefore, if n is even, then n\u00b2 is even.", "reason": "Logical equivalence"},
        ],
        "contrapositive_steps": [
            {"statement": "Original statement: P \u2192 Q, where P = 'n is even', Q = 'n\u00b2 is even'.", "reason": "Definition"},
            {"statement": "Contrapositive: \u00acQ \u2192 \u00acP, i.e. 'if n\u00b2 is odd, then n is odd'.", "reason": "Logical equivalence"},
            {"statement": "Assume n\u00b2 is odd (\u00acQ). Suppose, for the sake of this direction, that n were even instead.", "reason": "Assumption"},
            {"statement": "If n were even, n = 2k for some integer k, so n\u00b2 = 4k\u00b2 = 2(2k\u00b2), which is even.", "reason": "Algebraic simplification"},
            {"statement": "This contradicts our assumption that n\u00b2 is odd, so n cannot be even; n must be odd (\u00acP).", "reason": "Logical equivalence"},
            {"statement": "We have shown \u00acQ \u2192 \u00acP. Since a conditional and its contrapositive are logically equivalent, P \u2192 Q holds.", "reason": "Logical equivalence"},
            {"statement": "Therefore, if n is even, then n\u00b2 is even.", "reason": "Logical equivalence"},
        ],
        "contradiction_steps": [
            {"statement": "Assume, for contradiction, that n is even but n\u00b2 is odd.", "reason": "Assumption"},
            {"statement": "Since n is even, n = 2k for some integer k.", "reason": "Definition"},
            {"statement": "Then n\u00b2 = (2k)\u00b2 = 4k\u00b2 = 2(2k\u00b2).", "reason": "Algebraic simplification"},
            {"statement": "Since 2k\u00b2 is an integer, n\u00b2 = 2(2k\u00b2) is even.", "reason": "Definition"},
            {"statement": "This contradicts our assumption that n\u00b2 is odd.", "reason": "Contradiction"},
            {"statement": "Therefore the assumption was false: if n is even, then n\u00b2 must be even.", "reason": "Contradiction"},
        ],
    },

    "sum-two-evens": {
        "id": "sum-two-evens",
        "statement": "The sum of two even integers is even.",
        "domain": "a, b \u2208 \u2124",
        "P": "a and b are even",
        "Q": "a + b is even",
        "logical_form": "P \u2192 Q",
        "valid_methods": ["direct", "contradiction"],
        "method_notes": {
            "direct": "Direct algebraic proof is the natural approach.",
            "contradiction": "Possible but adds no clarity over the direct proof.",
            "contrapositive": "Awkward here since the contrapositive ('if a+b is odd then a or b is odd') requires a disjunction, making the direct route cleaner.",
            "induction": "Not applicable: no induction variable is being incremented."
        },
        "direct_steps": [
            {"statement": "Assume a and b are even integers.", "reason": "Assumption"},
            {"statement": "By definition, a = 2j and b = 2k for some integers j, k.", "reason": "Definition"},
            {"statement": "a + b = 2j + 2k", "reason": "Substitution"},
            {"statement": "a + b = 2(j + k)", "reason": "Algebraic simplification"},
            {"statement": "Since j + k is an integer, a + b is of the form 2m, so a + b is even.", "reason": "Definition"},
            {"statement": "Therefore, the sum of two even integers is even.", "reason": "Logical equivalence"},
        ],
    },

    "sum-two-odds": {
        "id": "sum-two-odds",
        "statement": "The sum of two odd integers is even.",
        "domain": "a, b \u2208 \u2124",
        "P": "a and b are odd",
        "Q": "a + b is even",
        "logical_form": "P \u2192 Q",
        "valid_methods": ["direct"],
        "method_notes": {
            "direct": "Direct algebraic proof is the natural approach.",
            "contrapositive": "Not offered: the contrapositive again involves a disjunction and is harder to state cleanly than the direct route.",
            "contradiction": "Possible but unnecessary complexity for this statement.",
            "induction": "Not applicable here."
        },
        "direct_steps": [
            {"statement": "Assume a and b are odd integers.", "reason": "Assumption"},
            {"statement": "By definition, a = 2j + 1 and b = 2k + 1 for some integers j, k.", "reason": "Definition"},
            {"statement": "a + b = (2j + 1) + (2k + 1)", "reason": "Substitution"},
            {"statement": "a + b = 2j + 2k + 2", "reason": "Algebraic simplification"},
            {"statement": "a + b = 2(j + k + 1)", "reason": "Algebraic simplification"},
            {"statement": "Since j + k + 1 is an integer, a + b is of the form 2m, so a + b is even.", "reason": "Definition"},
            {"statement": "Therefore, the sum of two odd integers is even.", "reason": "Logical equivalence"},
        ],
    },

    "square-odd-then-odd": {
        "id": "square-odd-then-odd",
        "statement": "If n\u00b2 is odd, then n is odd.",
        "domain": "n \u2208 \u2124",
        "P": "n\u00b2 is odd",
        "Q": "n is odd",
        "logical_form": "P \u2192 Q",
        "valid_methods": ["contrapositive"],
        "method_notes": {
            "contrapositive": "The direct route (assume n\u00b2 odd, i.e. n\u00b2 = 2k+1, and solve for n) is algebraically awkward because it requires a square root. Proving the contrapositive instead -- 'if n is even then n\u00b2 is even' -- is far cleaner, and since P \u2192 Q is logically equivalent to \u00acQ \u2192 \u00acP, this proves the original statement.",
            "direct": "Technically possible but requires solving n\u00b2 = 2k+1 for n, which is not a clean algebraic step. Contrapositive is strongly preferred.",
            "contradiction": "Possible (assume n\u00b2 odd and n even, derive a contradiction) -- essentially reuses the same algebra as the contrapositive proof.",
            "induction": "Not applicable: this is a conditional about an arbitrary integer, not indexed over n \u2265 base case."
        },
        "contrapositive_steps": [
            {"statement": "Original statement: P \u2192 Q, where P = 'n\u00b2 is odd', Q = 'n is odd'.", "reason": "Definition"},
            {"statement": "Contrapositive: \u00acQ \u2192 \u00acP, i.e. 'if n is even, then n\u00b2 is even'.", "reason": "Logical equivalence"},
            {"statement": "Assume n is even (\u00acQ).", "reason": "Assumption"},
            {"statement": "By definition of an even integer, n = 2k for some integer k.", "reason": "Definition"},
            {"statement": "n\u00b2 = (2k)\u00b2 = 4k\u00b2 = 2(2k\u00b2)", "reason": "Algebraic simplification"},
            {"statement": "Since 2k\u00b2 is an integer, n\u00b2 is even (\u00acP).", "reason": "Definition"},
            {"statement": "We have shown \u00acQ \u2192 \u00acP. Since a conditional and its contrapositive are logically equivalent, P \u2192 Q holds.", "reason": "Logical equivalence"},
            {"statement": "Therefore, if n\u00b2 is odd, then n is odd.", "reason": "Logical equivalence"},
        ],
    },

    "sqrt2-irrational": {
        "id": "sqrt2-irrational",
        "statement": "\u221a2 is irrational.",
        "domain": "N/A (a single real number)",
        "P": None,
        "Q": None,
        "logical_form": "S (a standalone proposition, not a conditional)",
        "valid_methods": ["contradiction"],
        "method_notes": {
            "contradiction": "The classical, essentially unique elementary proof of this fact. Assuming the negation lets us reach a contradiction via the well-ordering / lowest-terms argument.",
            "direct": "Not applicable: there is no direct algebraic chain from an assumption to 'irrational' -- irrationality is a non-existence claim, which contradiction handles naturally.",
            "contrapositive": "Not applicable: the statement is not a conditional P \u2192 Q, so there is no contrapositive to form.",
            "induction": "Not applicable: no natural number index is being incremented."
        },
        "contradiction_steps": [
            {"statement": "Assume, for contradiction, that \u221a2 is rational.", "reason": "Assumption"},
            {"statement": "Then \u221a2 = p/q for integers p, q with q \u2260 0, where p/q is in lowest terms (gcd(p, q) = 1).", "reason": "Definition"},
            {"statement": "Squaring both sides: 2 = p\u00b2/q\u00b2, so p\u00b2 = 2q\u00b2.", "reason": "Algebraic simplification"},
            {"statement": "So p\u00b2 is even. Since n\u00b2 even implies n even, p is even: p = 2k for some integer k.", "reason": "Substitution"},
            {"statement": "Substituting: (2k)\u00b2 = 2q\u00b2, so 4k\u00b2 = 2q\u00b2, so q\u00b2 = 2k\u00b2.", "reason": "Algebraic simplification"},
            {"statement": "So q\u00b2 is even, and therefore q is even.", "reason": "Substitution"},
            {"statement": "But then both p and q are even, so gcd(p, q) \u2265 2 -- contradicting that p/q was in lowest terms.", "reason": "Contradiction"},
            {"statement": "This contradiction shows our assumption was false. Therefore \u221a2 is irrational.", "reason": "Contradiction"},
        ],
    },

    "no-largest-integer": {
        "id": "no-largest-integer",
        "statement": "There is no largest integer.",
        "domain": "\u2124",
        "P": None,
        "Q": None,
        "logical_form": "\u00ac\u2203n \u2208 \u2124, \u2200m \u2208 \u2124, m \u2264 n",
        "valid_methods": ["contradiction"],
        "method_notes": {
            "contradiction": "A non-existence claim -- the standard approach is to assume a largest integer exists and exhibit a larger one.",
            "direct": "Not applicable: there is nothing to derive directly toward a non-existence statement.",
            "contrapositive": "Not applicable: not a conditional P \u2192 Q.",
            "induction": "Not applicable: this is a single existential claim about \u2124, not a property indexed by n."
        },
        "contradiction_steps": [
            {"statement": "Assume, for contradiction, that there is a largest integer N.", "reason": "Assumption"},
            {"statement": "By assumption, N \u2265 m for every integer m.", "reason": "Assumption"},
            {"statement": "Consider N + 1. Since N is an integer, N + 1 is also an integer.", "reason": "Definition"},
            {"statement": "N + 1 > N, so N + 1 is an integer greater than the supposed largest integer N.", "reason": "Algebraic simplification"},
            {"statement": "This contradicts the assumption that N is the largest integer.", "reason": "Contradiction"},
            {"statement": "Therefore, no largest integer exists.", "reason": "Contradiction"},
        ],
    },
}


def get_example(example_id: str):
    return LIBRARY.get(example_id)


def list_examples():
    return [
        {
            "id": e["id"],
            "statement": e["statement"],
            "logical_form": e["logical_form"],
            "valid_methods": e["valid_methods"],
        }
        for e in LIBRARY.values()
    ]


def find_by_statement(statement: str):
    """Loose case-insensitive match against the library so the free-text
    Proof Explorer box can find a Tier-1 example. Returns None (falls
    through to Tier 2/3) if nothing matches closely."""
    normalized = statement.strip().lower().rstrip(".")
    for entry in LIBRARY.values():
        if entry["statement"].strip().lower().rstrip(".") == normalized:
            return entry
    return None
