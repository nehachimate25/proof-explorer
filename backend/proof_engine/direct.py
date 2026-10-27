"""
Direct Proof Engine
---------------------
Direct proof structure:  Assume P -> transform -> derive Q -> therefore P -> Q

This module does NOT invent proofs on the fly for arbitrary statements
(that would require an AI to freelance mathematics, which spec section 2
explicitly forbids as the final authority). Instead it returns the
hand-verified step sequence from the library for statements the system
recognizes, and clearly reports "cannot verify" otherwise.
"""

from .library import get_example
from .validator import build_step_records


def run_direct_proof(example_id: str):
    entry = get_example(example_id)
    if entry is None:
        return {
            "status": "not_found",
            "message": "This statement is not in the verified example library.",
        }

    if "direct" not in entry["valid_methods"]:
        return {
            "status": "unsuitable",
            "message": (
                "Direct proof is not the recommended method for this statement. "
                + entry["method_notes"].get("direct", "")
            ),
        }

    raw_steps = entry.get("direct_steps")
    if not raw_steps:
        return {
            "status": "unsupported",
            "message": "This proof could not be automatically verified. Please review the mathematical steps.",
        }

    steps = build_step_records(raw_steps)

    return {
        "status": "verified",
        "method": "direct",
        "statement": entry["statement"],
        "domain": entry["domain"],
        "P": entry["P"],
        "Q": entry["Q"],
        "logical_form": entry["logical_form"],
        "steps": steps,
        "conclusion": f"Therefore, {entry['statement'][0].lower()}{entry['statement'][1:]}",
        "verification_status": "VERIFIED",
    }
