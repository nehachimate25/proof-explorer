"""
Induction Pipeline
---------------------
Shared helper that runs the full base case / hypothesis / inductive step /
conclusion sequence for a library entry, optionally overriding the domain
start value (e.g. when a user-typed statement says "for all n \u2265 2"
instead of the library's default). Used by both routes/induction_routes.py
and analyzers/induction_analyzer.py so there's exactly one implementation
of "what counts as PROVED".
"""

from .library import get_example
from .base_case import verify_base_case
from .hypothesis import get_hypothesis
from .inductive_step import verify_inductive_step


def run_full_induction(example_id: str, start_override=None):
    entry = get_example(example_id)
    if entry is None:
        return None

    base = verify_base_case(example_id, start_override)
    hyp = get_hypothesis(example_id)
    step = verify_inductive_step(example_id)

    fully_proved = (
        base.get("verification_status") == "VERIFIED"
        and step.get("verification_status") == "VERIFIED"
    )

    return {
        "statement": entry["statement"],
        "domain_start": start_override if start_override is not None else entry["domain_start"],
        "base_case": base,
        "inductive_hypothesis": hyp,
        "inductive_step": step,
        "final_status": "PROVED" if fully_proved else "NEEDS REVIEW",
    }
