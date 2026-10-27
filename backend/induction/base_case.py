"""
Base Case Verification
-------------------------
Computes LHS and RHS of P(n) at the domain's starting value and compares
them EXACTLY (using Python's Fraction type to avoid floating point error).
This is real computation, not a narrated claim.
"""

from .library import get_example


def verify_base_case(example_id: str, n0_override=None):
    entry = get_example(example_id)
    if entry is None:
        return {"status": "not_found"}

    n0 = n0_override if n0_override is not None else entry["domain_start"]
    lhs = entry["lhs_fn"](n0)

    if entry.get("is_divisibility"):
        divisor = entry["divisor"]
        divisible = (lhs % divisor == 0)
        return {
            "status": "verified" if divisible else "invalid",
            "n": n0,
            "lhs_value": str(lhs),
            "lhs_desc": entry["lhs_desc"].replace("n", str(n0)),
            "check": f"{lhs} is {'divisible' if divisible else 'NOT divisible'} by {divisor}",
            "match": divisible,
            "verification_status": "VERIFIED" if divisible else "INVALID",
        }

    rhs = entry["rhs_fn"](n0)
    match = (lhs == rhs)

    comparison = "="
    if entry.get("is_inequality"):
        match = (lhs >= rhs)
        comparison = "\u2265"

    return {
        "status": "verified" if match else "invalid",
        "n": n0,
        "lhs_value": str(lhs),
        "rhs_value": str(rhs),
        "comparison": comparison,
        "match": match,
        "verification_status": "VERIFIED" if match else "INVALID",
    }
