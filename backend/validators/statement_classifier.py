"""
Statement Classifier -- merged library + dynamic analysis
--------------------------------------------------------------
THIS IS THE KEY FIX: the verified example libraries are now an
optimization / verified-reference shortcut, NOT the only source of
supported statements.

Flow:
    find_by_statement() in proof_engine library
        -> exact match? use the verified library proof (fast path, VERIFIED)
    find_by_statement() in induction library
        -> exact match? use the verified induction pipeline (VERIFIED)
    else:
        dynamic analyzer (analyzers/statement_analyzer.py)
            -> recognizes a supported pattern -> VERIFIED or SUPPORTED
            -> partially understood -> NEEDS_REVIEW
            -> not mathematical / empty -> INVALID

A statement is NEVER rejected just because it isn't byte-for-byte in a
library anymore.
"""

from proof_engine.library import find_by_statement as find_proof_by_statement
from proof_engine.validator import suitable_methods_for
from induction.library import find_by_statement as find_induction_by_statement
from induction.pipeline import run_full_induction
from analyzers.statement_analyzer import analyze_statement


def _normalize_truth_fields(result: dict) -> dict:
    """Guarantee every response carries the canonical status/truth_value
    pair, regardless of which analyzer (static library or dynamic) built
    it. This is the single place that maps the legacy support_level values
    onto the required user-facing status vocabulary: VERIFIED, DISPROVED,
    NEEDS_REVIEW, INVALID. A statement is never inferred TRUE just because
    it has the shape P -> Q -- truth_value is only True when support_level
    is genuinely VERIFIED (a checked proof exists), and only False when
    support_level is DISPROVED (a checked counterexample exists)."""
    support_level = result.get("support_level")
    if "status" not in result:
        result["status"] = support_level
    if "truth_value" not in result:
        if support_level == "VERIFIED":
            result["truth_value"] = True
        elif support_level == "DISPROVED":
            result["truth_value"] = False
        else:
            result["truth_value"] = None
    return result


def classify_statement(statement: str):
    if not statement or not statement.strip():
        return _normalize_truth_fields({"support_level": "INVALID", "message": "Please enter a mathematical statement."})

    # 1. Exact match in the verified proof-method library (fast path).
    entry = find_proof_by_statement(statement)
    if entry:
        return _normalize_truth_fields({
            "statement": entry["statement"],
            "support_level": "VERIFIED",
            "source": "library",
            "kind": "proof",
            "example_id": entry["id"],
            "classification": {
                "type": "Conditional Proposition" if entry.get("P") else "Standalone Proposition",
                "variable": None,
                "domain": entry["domain"],
                "P": entry.get("P"),
                "Q": entry.get("Q"),
                "logical_form": entry["logical_form"],
            },
            "methods": suitable_methods_for(entry),
        })

    # 2. Exact match in the verified induction library (fast path).
    ind_entry = find_induction_by_statement(statement)
    if ind_entry:
        induction_result = run_full_induction(ind_entry["id"])
        return _normalize_truth_fields({
            "statement": ind_entry["statement"],
            "support_level": "VERIFIED",
            "source": "library",
            "kind": "induction",
            "example_id": ind_entry["id"],
            "classification": {
                "type": "Induction Proposition",
                "variable": "n",
                "domain": f"n \u2208 \u2124, n \u2265 {ind_entry['domain_start']}",
                "P": ind_entry["statement"],
                "Q": None,
                "logical_form": f"P(n), \u2200n \u2265 {ind_entry['domain_start']}",
            },
            "methods": {
                "direct": {"suitable": False, "reason": "Indexed over n; induction is the natural method."},
                "contrapositive": {"suitable": False, "reason": "Not a single conditional statement."},
                "contradiction": {"suitable": False, "reason": "Induction is the standard method here."},
                "induction": {"suitable": True, "reason": "Has the form P(n) with a natural base case and inductive step."},
            },
            "induction_result": induction_result,
        })

    # 3. No exact match -- dynamic rule-based analysis (never a hard reject).
    result = analyze_statement(statement)
    result["source"] = "dynamic"
    return _normalize_truth_fields(result)
