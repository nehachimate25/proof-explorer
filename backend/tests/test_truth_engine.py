"""
Unit tests for the parity truth engine (analyzers/parity_rule_engine.py)
and its integration through validators/statement_classifier.py.

Run with:
    cd backend && python3 -m tests.test_truth_engine
or simply:
    cd backend && python3 tests/test_truth_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.statement_classifier import classify_statement
from proof_engine.dynamic_proof import generate_dynamic_proof
from analyzers import parity_rule_engine


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def run_all():
    results = []

    # --- Core 8 parity rules required by spec -------------------------------
    results.append(check(
        "odd -> odd square = TRUE",
        classify_statement("If n is odd, then n^2 is odd")["status"] == "VERIFIED"
        and classify_statement("If n is odd, then n^2 is odd")["truth_value"] is True,
    ))
    results.append(check(
        "even -> even square = TRUE",
        classify_statement("If n is even, then n^2 is even")["status"] == "VERIFIED"
        and classify_statement("If n is even, then n^2 is even")["truth_value"] is True,
    ))
    results.append(check(
        "odd -> even square = FALSE",
        classify_statement("If n is odd, then n^2 is even")["status"] == "DISPROVED"
        and classify_statement("If n is odd, then n^2 is even")["truth_value"] is False,
    ))
    results.append(check(
        "even -> odd square = FALSE",
        classify_statement("If n is even, then n^2 is odd")["status"] == "DISPROVED"
        and classify_statement("If n is even, then n^2 is odd")["truth_value"] is False,
    ))
    results.append(check(
        "odd -> even next number = TRUE",
        classify_statement("If n is odd, then n+1 is even")["status"] == "VERIFIED",
    ))
    results.append(check(
        "even -> odd next number = TRUE",
        classify_statement("If n is even, then n+1 is odd")["status"] == "VERIFIED",
    ))
    results.append(check(
        "odd -> odd next number = FALSE",
        classify_statement("If n is odd, then n+1 is odd")["status"] == "DISPROVED",
    ))
    results.append(check(
        "even -> even next number = FALSE",
        classify_statement("If n is even, then n+1 is even")["status"] == "DISPROVED",
    ))

    # --- n-1 rules ------------------------------------------------------------
    results.append(check(
        "even -> odd n-1 = TRUE",
        classify_statement("If n is even, then n-1 is odd")["status"] == "VERIFIED",
    ))
    results.append(check(
        "odd -> even n-1 = TRUE",
        classify_statement("If n is odd, then n-1 is even")["status"] == "VERIFIED",
    ))

    # --- reverse direction (n\u00b2 -> n) ---------------------------------------
    results.append(check(
        "n\u00b2 even -> n even = TRUE",
        classify_statement("If n\u00b2 is even, then n is even")["status"] == "VERIFIED",
    ))
    results.append(check(
        "n\u00b2 odd -> n odd = TRUE",
        classify_statement("If n\u00b2 is odd, then n is odd")["status"] == "VERIFIED",
    ))

    # --- counterexample correctness: must actually satisfy P, violate Q -----
    r = classify_statement("If n is odd, then n^2 is even")
    ce = r["counterexample"]
    n = ce["value"]
    results.append(check(
        "counterexample n=1 actually satisfies P (odd) and violates Q (even)",
        n % 2 == 1 and (n * n) % 2 == 1,  # n odd, n^2 NOT even (i.e. odd) -- violates Q
    ))

    r2 = classify_statement("If n is even, then n^2 is odd")
    ce2 = r2["counterexample"]
    n2 = ce2["value"]
    results.append(check(
        "counterexample n=2 actually satisfies P (even) and violates Q (odd)",
        n2 % 2 == 0 and (n2 * n2) % 2 == 0,
    ))

    # --- no proof methods offered for a false statement ------------------------
    r3 = classify_statement("If n is odd, then n^2 is even")
    all_unsuitable = all(not v["suitable"] for v in r3["methods"].values())
    results.append(check("DISPROVED statement offers no suitable proof methods", all_unsuitable))

    # --- dynamic_proof bypasses method logic entirely for DISPROVED ------------
    p = generate_dynamic_proof("If n is odd, then n^2 is even", "direct")
    results.append(check("dynamic_proof returns disproved status directly", p["status"] == "disproved"))

    # --- malformed / empty / unsupported input ----------------------------------
    results.append(check("empty input -> INVALID", classify_statement("")["status"] == "INVALID"))
    results.append(check("whitespace-only input -> INVALID", classify_statement("   ")["status"] == "INVALID"))
    results.append(check("non-mathematical input -> INVALID", classify_statement("hello world")["status"] == "INVALID"))
    results.append(check(
        "unsupported but math-flavored input -> NEEDS_REVIEW",
        classify_statement("n is prime and divisible by itself")["status"] == "NEEDS_REVIEW",
    ))

    # --- normalization robustness -----------------------------------------------
    results.append(check(
        "uppercase input normalizes correctly",
        classify_statement("IF N IS ODD, THEN N^2 IS ODD")["status"] == "VERIFIED",
    ))
    results.append(check(
        "n\u00b2 vs n^2 produce identical results",
        classify_statement("If n is odd, then n^2 is odd")["status"]
        == classify_statement("If n is odd, then n\u00b2 is odd")["status"],
    ))
    results.append(check(
        "extra spaces don't break parsing",
        classify_statement("if   n   is   odd,    then   n^2   is   odd")["status"] == "VERIFIED",
    ))

    # --- induction not hijacked by parity statements -----------------------------
    results.append(check(
        "parity statement stays a Conditional Proposition, not forced into induction",
        classify_statement("If n is odd, then n^2 is odd")["classification"]["type"] == "Conditional Proposition",
    ))
    results.append(check(
        "genuine induction statement still recognized",
        classify_statement("1 + 2 + ... + n = n(n+1)/2 for all n \u2265 1.")["classification"]["type"] == "Induction Proposition",
    ))

    print(f"\n{sum(results)}/{len(results)} passed")
    return all(results)


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
