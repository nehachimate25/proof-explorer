"""
Proof Step Validator
----------------------
Shared utilities for turning raw (statement, reason) pairs into fully
structured proof-step records (spec section 23), and for deciding which
proof methods are appropriate for a given statement (spec section 9).

VALID_REASONS is a controlled vocabulary -- every step in the library must
use one of these, which is enforced defensively here so a malformed
library entry fails loudly instead of silently displaying an unverifiable
step as "verified".
"""

VALID_REASONS = {
    "Definition",
    "Substitution",
    "Algebraic simplification",
    "Logical equivalence",
    "Assumption",
    "Contradiction",
    "Inductive hypothesis",
    "Inductive step",
}


def build_step_records(raw_steps):
    """raw_steps: list of {"statement": str, "reason": str}
    Returns fully structured step records with step_number, previous_steps,
    and verification_status, per spec section 23's JSON schema."""
    records = []
    for i, step in enumerate(raw_steps, start=1):
        reason = step["reason"]
        status = "verified" if reason in VALID_REASONS else "needs_review"
        records.append({
            "step_number": i,
            "statement": step["statement"],
            "reason": reason,
            "previous_steps": list(range(1, i)),
            "verification_status": status,
        })
    return records


def all_steps_verified(steps):
    return len(steps) > 0 and all(s["verification_status"] == "verified" for s in steps)


def suitable_methods_for(entry):
    """Given a library entry, return {method: {suitable: bool, reason: str}}
    for all four proof methods, so the UI can grey out / explain unsuitable
    methods rather than presenting them as if they always work (spec
    section 9). Uses the key "reason" to stay consistent with the dynamic
    analyzer's method-suitability output (analyzers/*.py)."""
    all_methods = ["direct", "contrapositive", "contradiction", "induction"]
    result = {}
    for m in all_methods:
        suitable = m in entry["valid_methods"]
        reason = entry.get("method_notes", {}).get(m, "")
        result[m] = {"suitable": suitable, "reason": reason}
    return result
