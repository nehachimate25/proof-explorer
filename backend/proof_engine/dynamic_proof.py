"""
Dynamic Proof Generator
---------------------------
Given a raw statement and a chosen proof method, resolves the actual proof
to show. Checks library shortcuts first (byte-identical behavior to
before), then falls through to the dynamic analyzer's generated templates.
Never fabricates steps for a method the analyzer didn't mark suitable, and
never fabricates steps when a pattern was only SUPPORTED (structurally
recognized) rather than VERIFIED (fully templated).
"""

from proof_engine.library import find_by_statement
from proof_engine.direct import run_direct_proof
from proof_engine.contrapositive import run_contrapositive_proof
from proof_engine.contradiction import run_contradiction_proof
from proof_engine.validator import build_step_records
from induction.library import find_by_statement as find_induction_by_statement
from induction.pipeline import run_full_induction
from analyzers.statement_analyzer import analyze_statement


def generate_dynamic_proof(statement: str, method: str):
    if not statement or not statement.strip():
        return {"status": "unsupported", "message": "Please enter a mathematical statement."}

    if not method:
        return {"status": "unsupported", "message": "Please choose a proof method."}

    # 1. Library shortcuts (backward compatible, byte-identical results).
    entry = find_by_statement(statement)
    if entry:
        if method == "direct":
            return run_direct_proof(entry["id"])
        if method == "contrapositive":
            return run_contrapositive_proof(entry["id"])
        if method == "contradiction":
            return run_contradiction_proof(entry["id"])
        if method == "induction":
            return {"status": "unsuitable", "message": "Induction is not applicable to this conditional/standalone statement."}

    ind_entry = find_induction_by_statement(statement)
    if ind_entry:
        if method == "induction":
            result = run_full_induction(ind_entry["id"])
            return {"status": "verified_induction", **result}
        return {"status": "unsuitable", "message": "This statement is an indexed proposition P(n); induction is the natural method here."}

    # 2. Dynamic analysis.
    result = analyze_statement(statement)
    support = result.get("support_level")

    if support == "INVALID":
        return {"status": "invalid", "message": result.get("message", "Not recognized as a supported mathematical statement.")}

    if support == "NEEDS_REVIEW":
        return {"status": "needs_review", "message": result.get("message", "This proof could not be automatically verified. Please review the mathematical steps.")}

    if support == "DISPROVED":
        # A false statement has no valid proof under any method -- return
        # the disproof directly rather than routing through per-method
        # suitability logic. No proof method is ever offered here.
        return {
            "status": "disproved",
            "truth_value": False,
            "statement": result.get("statement", statement),
            "classification": result.get("classification"),
            "counterexample": result.get("counterexample"),
            "message": result.get("reason", "This statement is mathematically false."),
        }

    methods_info = result.get("methods", {})
    if method not in methods_info or not methods_info[method].get("suitable"):
        reason = methods_info.get(method, {}).get("reason", "This method is not suitable for this statement.")
        return {"status": "unsuitable", "message": reason}

    if method == "induction" and result.get("induction_result"):
        return {"status": "verified_induction", **result["induction_result"]}

    proofs = result.get("proofs", {})
    if method in proofs and proofs[method].get("steps"):
        p = proofs[method]
        classification = result.get("classification", {})
        return {
            "status": "verified",
            "method": method,
            "statement": result.get("statement", statement),
            "domain": classification.get("domain"),
            "P": classification.get("P"),
            "Q": classification.get("Q"),
            "logical_form": classification.get("logical_form"),
            "steps": build_step_records(p["steps"]),
            "conclusion": p["conclusion"],
            "verification_status": "VERIFIED",
        }

    # Recognized structurally (SUPPORTED) but no generated algebra for this method.
    return {
        "status": "supported_only",
        "message": result.get(
            "message",
            "This method is logically applicable, but the current deterministic engine does not have a "
            "safe algebraic template to auto-generate the full proof for this specific statement.",
        ),
    }
