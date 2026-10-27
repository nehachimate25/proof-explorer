"""
Contrapositive Proof Engine
-----------------------------
For P -> Q, the contrapositive is ¬Q -> ¬P. A conditional and its
contrapositive are logically equivalent (verifiable exhaustively by truth
table -- see logic/truth_table.check_equivalence, which the route calls to
back this claim with real evidence rather than an assertion).

This module is careful to NEVER conflate:
    Contrapositive:  ¬Q -> ¬P   (equivalent to the original)
    Converse:        Q -> P    (NOT generally equivalent)
    Inverse:         ¬P -> ¬Q  (NOT generally equivalent)
"""

from .library import get_example
from .validator import build_step_records
from logic.evaluator import derive_conditional_forms
from logic.truth_table import check_equivalence


def run_contrapositive_proof(example_id: str):
    entry = get_example(example_id)
    if entry is None:
        return {"status": "not_found", "message": "This statement is not in the verified example library."}

    if "contrapositive" not in entry["valid_methods"]:
        return {
            "status": "unsuitable",
            "message": (
                "Contrapositive proof is not the recommended method for this statement. "
                + entry["method_notes"].get("contrapositive", "")
            ),
        }

    raw_steps = entry.get("contrapositive_steps")
    if not raw_steps:
        return {
            "status": "unsupported",
            "message": "This proof could not be automatically verified. Please review the mathematical steps.",
        }

    steps = build_step_records(raw_steps)

    # Independently confirm P<->Q equivalence with ¬Q -> ¬P using an abstract
    # truth table on generic symbols A, B, so the "equivalent" claim shown to
    # the user is backed by exhaustive evaluation, not just prose.
    equivalence = check_equivalence("A -> B", "!B -> !A")

    return {
        "status": "verified",
        "method": "contrapositive",
        "statement": entry["statement"],
        "domain": entry["domain"],
        "P": entry["P"],
        "Q": entry["Q"],
        "logical_form": entry["logical_form"],
        "transform": {
            "original": f"{entry['P']} \u2192 {entry['Q']}" if entry["P"] else entry["logical_form"],
            "contrapositive": f"\u00ac({entry['Q']}) \u2192 \u00ac({entry['P']})" if entry["P"] else None,
        },
        "abstract_equivalence_check": equivalence,
        "steps": steps,
        "conclusion": f"Therefore, {entry['statement'][0].lower()}{entry['statement'][1:]}",
        "verification_status": "VERIFIED",
    }


def transform_conditional(expr: str):
    """General-purpose endpoint: given any P -> Q expression (using logic
    syntax, e.g. 'P -> Q' or 'A -> B'), symbolically derive converse,
    inverse, and contrapositive, and confirm contrapositive equivalence."""
    forms = derive_conditional_forms(expr)
    equivalence = check_equivalence(expr, forms["contrapositive"])
    forms["equivalence_verified"] = equivalence["equivalent"]
    forms["equivalence_table"] = equivalence
    return forms
