"""
Contradiction Proof Engine
----------------------------
Structure:  Assume ¬S -> derive consequences -> reach a contradiction
            -> therefore ¬S is false -> therefore S is true

Like the direct and contrapositive engines, this returns hand-verified
step sequences from the library rather than freelancing new mathematics.
"""

from .library import get_example
from .validator import build_step_records


def run_contradiction_proof(example_id: str):
    entry = get_example(example_id)
    if entry is None:
        return {"status": "not_found", "message": "This statement is not in the verified example library."}

    if "contradiction" not in entry["valid_methods"]:
        return {
            "status": "unsuitable",
            "message": (
                "Proof by contradiction is not the recommended method for this statement. "
                + entry["method_notes"].get("contradiction", "")
            ),
        }

    raw_steps = entry.get("contradiction_steps")
    if not raw_steps:
        return {
            "status": "unsupported",
            "message": "This proof could not be automatically verified. Please review the mathematical steps.",
        }

    steps = build_step_records(raw_steps)

    return {
        "status": "verified",
        "method": "contradiction",
        "statement": entry["statement"],
        "domain": entry["domain"],
        "logical_form": entry["logical_form"],
        "steps": steps,
        "conclusion": f"Therefore, {entry['statement'][0].lower()}{entry['statement'][1:]}",
        "verification_status": "VERIFIED",
    }
