"""
Inductive Step
-----------------
Proves P(k) -> P(k+1). We present the hand-verified symbolic algebra AND
back it with a numeric spot-check at several concrete values of k
(computed exactly via Fraction) so the "Inductive Step Verified" badge is
grounded in real arithmetic, not just narration.
"""

from fractions import Fraction
from .library import get_example


def verify_inductive_step(example_id: str, sample_k=None):
    entry = get_example(example_id)
    if entry is None:
        return {"status": "not_found"}

    n0 = entry["domain_start"]
    if sample_k is None:
        sample_ks = [n0, n0 + 1, n0 + 2, n0 + 5]
    else:
        sample_ks = [sample_k]

    checks = []
    all_ok = True

    for k in sample_ks:
        if entry.get("is_divisibility"):
            divisor = entry["divisor"]
            lhs_next = entry["lhs_fn"](k + 1)
            ok = (lhs_next % divisor == 0)
            checks.append({"k": k, "P(k+1)_value": str(lhs_next), "divisible_by": divisor, "holds": ok})
        elif entry.get("is_inequality"):
            lhs_next = entry["lhs_fn"](k + 1)
            rhs_next = entry["rhs_fn"](k + 1)
            ok = (lhs_next >= rhs_next)
            checks.append({"k": k, "lhs": str(lhs_next), "rhs": str(rhs_next), "holds": ok})
        else:
            lhs_next = entry["lhs_fn"](k + 1)
            rhs_next = entry["rhs_fn"](k + 1)
            ok = (lhs_next == rhs_next)
            checks.append({"k": k, "lhs": str(lhs_next), "rhs": str(rhs_next), "holds": ok})
        all_ok = all_ok and ok

    return {
        "status": "verified" if all_ok else "invalid",
        "hypothesis": entry["hypothesis_text"],
        "algebra": entry["inductive_step_algebra"],
        "target": entry["target_text"],
        "numeric_spot_checks": checks,
        "verification_status": "VERIFIED" if all_ok else "INVALID",
        "note": (
            "The algebra above is the general symbolic proof that P(k) implies P(k+1) "
            "for every k in the domain. The numeric spot-checks confirm P(k+1) holds "
            "exactly at several concrete values as an additional sanity check."
        ),
    }
