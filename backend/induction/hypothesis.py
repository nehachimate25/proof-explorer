"""
Inductive Hypothesis
-----------------------
IMPORTANT (spec section 16): the inductive hypothesis is an ASSUMPTION used
inside the inductive step -- it is explicitly NOT a proof of the statement
by itself. This module only ever labels it as such and never marks it
"verified" on its own.
"""

from .library import get_example


def get_hypothesis(example_id: str):
    entry = get_example(example_id)
    if entry is None:
        return {"status": "not_found"}

    return {
        "status": "ok",
        "label": "INDUCTIVE HYPOTHESIS (an assumption, not a proven fact)",
        "text": f"Assume the statement is true for n = k:",
        "hypothesis": entry["hypothesis_text"],
        "note": (
            "This is an assumption used only within the inductive step below. "
            "It is not, by itself, evidence that the statement is true."
        ),
    }
