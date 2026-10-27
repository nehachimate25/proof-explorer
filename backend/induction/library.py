"""
Induction Example Library
---------------------------
Each entry defines a closed-form statement P(n), its base case value, and
symbolic algebra text for the inductive step. Base-case and a sample of
inductive-step arithmetic are checked COMPUTATIONALLY (not just narrated)
in base_case.py / inductive_step.py using Python's exact fractions module,
so "verified" claims are backed by real computation.
"""

from fractions import Fraction
from math import factorial


def _sum_n(n):
    return sum(range(1, n + 1))


def _sum_odd(n):
    return sum(2 * i - 1 for i in range(1, n + 1))


LIBRARY = {

    "sum-first-n": {
        "id": "sum-first-n",
        "statement": "1 + 2 + 3 + ... + n = n(n+1)/2",
        "domain_start": 1,
        "lhs_desc": "1 + 2 + ... + n",
        "rhs_desc": "n(n+1)/2",
        "lhs_fn": _sum_n,
        "rhs_fn": lambda n: Fraction(n * (n + 1), 2),
        "hypothesis_text": "1 + 2 + ... + k = k(k+1)/2",
        "inductive_step_algebra": [
            "1 + 2 + ... + k + (k+1) = [1 + 2 + ... + k] + (k+1)",
            "= k(k+1)/2 + (k+1)                     (by the inductive hypothesis)",
            "= k(k+1)/2 + 2(k+1)/2                   (common denominator)",
            "= [k(k+1) + 2(k+1)] / 2",
            "= (k+1)(k+2) / 2",
        ],
        "target_text": "1 + 2 + ... + (k+1) = (k+1)(k+2)/2, which is P(k+1).",
    },

    "sum-first-odd": {
        "id": "sum-first-odd",
        "statement": "1 + 3 + 5 + ... + (2n-1) = n\u00b2",
        "domain_start": 1,
        "lhs_desc": "1 + 3 + ... + (2n-1)",
        "rhs_desc": "n\u00b2",
        "lhs_fn": _sum_odd,
        "rhs_fn": lambda n: Fraction(n * n),
        "hypothesis_text": "1 + 3 + ... + (2k-1) = k\u00b2",
        "inductive_step_algebra": [
            "1 + 3 + ... + (2k-1) + (2(k+1)-1) = [1 + 3 + ... + (2k-1)] + (2k+1)",
            "= k\u00b2 + (2k+1)                          (by the inductive hypothesis)",
            "= k\u00b2 + 2k + 1",
            "= (k+1)\u00b2",
        ],
        "target_text": "1 + 3 + ... + (2(k+1)-1) = (k+1)\u00b2, which is P(k+1).",
    },

    "power-ge-n-plus-1": {
        "id": "power-ge-n-plus-1",
        "statement": "2\u207f \u2265 n + 1 for all n \u2265 0",
        "domain_start": 0,
        "lhs_desc": "2\u207f",
        "rhs_desc": "n + 1",
        "lhs_fn": lambda n: Fraction(2 ** n),
        "rhs_fn": lambda n: Fraction(n + 1),
        "hypothesis_text": "2\u1d4f \u2265 k + 1",
        "inductive_step_algebra": [
            "2\u1d4f\u207a\u00b9 = 2 \u00b7 2\u1d4f",
            "\u2265 2(k+1)                                  (by the inductive hypothesis, since 2\u1d4f \u2265 k+1)",
            "= 2k + 2",
            "= (k+1) + (k+1)",
            "\u2265 (k+1) + 1        (since k+1 \u2265 1 for k \u2265 0)",
        ],
        "target_text": "2\u1d4f\u207a\u00b9 \u2265 (k+1) + 1, which is P(k+1).",
        "is_inequality": True,
    },

    "divisible-by-3": {
        "id": "divisible-by-3",
        "statement": "n\u00b3 - n is divisible by 3, for all n \u2265 1",
        "domain_start": 1,
        "lhs_desc": "n\u00b3 - n",
        "rhs_desc": "a multiple of 3",
        "lhs_fn": lambda n: Fraction(n ** 3 - n),
        "rhs_fn": None,  # divisibility, handled specially
        "hypothesis_text": "k\u00b3 - k = 3m for some integer m",
        "inductive_step_algebra": [
            "(k+1)\u00b3 - (k+1) = k\u00b3 + 3k\u00b2 + 3k + 1 - k - 1",
            "= (k\u00b3 - k) + 3k\u00b2 + 3k",
            "= 3m + 3k\u00b2 + 3k                       (by the inductive hypothesis)",
            "= 3(m + k\u00b2 + k)",
        ],
        "target_text": "(k+1)\u00b3 - (k+1) = 3(m + k\u00b2 + k), a multiple of 3, which is P(k+1).",
        "is_divisibility": True,
        "divisor": 3,
    },

    "factorial-ge": {
        "id": "factorial-ge",
        "statement": "n! \u2265 2\u207f\u207b\u00b9 for all n \u2265 1",
        "domain_start": 1,
        "lhs_desc": "n!",
        "rhs_desc": "2\u207f\u207b\u00b9",
        "lhs_fn": lambda n: Fraction(factorial(n)),
        "rhs_fn": lambda n: Fraction(2 ** (n - 1)),
        "hypothesis_text": "k! \u2265 2\u1d4f\u207b\u00b9",
        "inductive_step_algebra": [
            "(k+1)! = (k+1) \u00b7 k!",
            "\u2265 (k+1) \u00b7 2\u1d4f\u207b\u00b9                       (by the inductive hypothesis)",
            "\u2265 2 \u00b7 2\u1d4f\u207b\u00b9                           (since k+1 \u2265 2 for k \u2265 1)",
            "= 2\u1d4f",
        ],
        "target_text": "(k+1)! \u2265 2\u1d4f = 2\u207d\u1d4f\u207a\u00b9\u207e\u207b\u00b9, which is P(k+1).",
        "is_inequality": True,
    },
}


def get_example(example_id):
    return LIBRARY.get(example_id)


def list_examples():
    return [
        {"id": e["id"], "statement": e["statement"], "domain_start": e["domain_start"]}
        for e in LIBRARY.values()
    ]


def find_by_statement(statement: str):
    """Loose case-insensitive exact match against the library, used as a
    fast VERIFIED shortcut before falling back to the dynamic pattern
    matcher in analyzers/induction_analyzer.py."""
    if not statement:
        return None
    normalized = statement.strip().lower().rstrip(".")
    for entry in LIBRARY.values():
        if entry["statement"].strip().lower().rstrip(".") == normalized:
            return entry
    return None
