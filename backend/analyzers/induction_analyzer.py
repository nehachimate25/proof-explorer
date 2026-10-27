"""
Induction Analyzer
---------------------
Recognizes common induction statement forms via flexible regex (so phrasing
variations like punctuation, "for all n \u2265 1" suffixes, etc. still match)
and reuses the hand-verified, Fraction-checked computation already in
induction/library.py + induction/pipeline.py. This is template *matching*,
not template *generation* -- every template here was manually verified
before being added, exactly like the static library. What's new is that a
statement no longer has to be a byte-for-byte match to trigger it.
"""

import re

from induction.library import get_example
from induction.pipeline import run_full_induction


def _matches_sum_first_n(t):
    if "odd" in t:
        return False
    return bool(re.search(r"n\s*\(\s*n\s*\+\s*1\s*\)\s*/\s*2", t)) or \
        bool(re.search(r"sum of (the )?first n (positive )?integers", t))


def _matches_sum_first_odd(t):
    return bool(re.search(r"first n odd", t)) or \
        bool(re.search(r"1\s*\+\s*3.*\(?\s*2n\s*-\s*1\s*\)?", t)) or \
        (bool(re.search(r"1\s*\+\s*3", t)) and bool(re.search(r"n\s*\u00b2", t)))


def _matches_power_ge(t):
    return bool(re.search(r"2\s*\^\s*n|2\u207f", t)) and \
        bool(re.search(r"n\s*\+\s*1", t)) and \
        bool(re.search(r"(\u2265|>=)", t))


def _matches_factorial_ge(t):
    return bool(re.search(r"\bn\s*!", t)) and \
        bool(re.search(r"2\s*\^\s*\(?\s*n\s*-\s*1\s*\)?|2\u207f\u207b\u00b9", t))


def _matches_divisible_by_3(t):
    return bool(re.search(r"n\s*\u00b3|n\s*\^\s*3|n\s+cubed", t)) and \
        bool(re.search(r"divisible by 3|3 divides", t))


TEMPLATE_MATCHERS = [
    ("sum-first-n", _matches_sum_first_n),
    ("sum-first-odd", _matches_sum_first_odd),
    ("power-ge-n-plus-1", _matches_power_ge),
    ("factorial-ge", _matches_factorial_ge),
    ("divisible-by-3", _matches_divisible_by_3),
]


def extract_start_value(t):
    m = re.search(r"for all n\s*(\u2265|>=)\s*(-?\d+)", t)
    if m:
        return int(m.group(2))
    m = re.search(r"for every (integer|natural number) n\s*(\u2265|>=)\s*(-?\d+)", t)
    if m:
        return int(m.group(3))
    return None


def analyze(text_norm: str):
    t = text_norm.lower()

    for example_id, matcher in TEMPLATE_MATCHERS:
        if not matcher(t):
            continue

        entry = get_example(example_id)
        start = extract_start_value(t)
        induction_result = run_full_induction(example_id, start_override=start)
        domain_start = induction_result["domain_start"]

        classification = {
            "type": "Induction Proposition",
            "variable": "n",
            "domain": f"n \u2208 \u2124, n \u2265 {domain_start}",
            "P": entry["statement"],
            "Q": None,
            "logical_form": f"P(n), \u2200n \u2265 {domain_start}",
        }

        methods = {
            "direct": {"suitable": False, "reason": "This statement is indexed over n and is best proved by induction rather than a single direct derivation."},
            "contrapositive": {"suitable": False, "reason": "Not applicable: this is not a single conditional statement."},
            "contradiction": {"suitable": False, "reason": "Induction is the standard and clearest method for this indexed statement."},
            "induction": {"suitable": True, "reason": "This statement has the form P(n) with a natural base case and inductive step."},
        }

        return {
            "classification": classification,
            "methods": methods,
            "support_level": "VERIFIED",
            "induction_result": induction_result,
        }

    return None
