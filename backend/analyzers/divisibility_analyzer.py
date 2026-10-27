"""
Divisibility Analyzer
-------------------------
Generates a fully-verified direct proof for the general pattern:
    "If {var} is divisible by {k}, then {var}\u00b2 is divisible by {k}"
for ANY positive integer k -- this is a genuine algebraic generalization
(var = km => var\u00b2 = k(km\u00b2)), not a lookup, so it is safe to mark VERIFIED
for any k.

Contrapositive and contradiction are logically applicable to any
conditional, but we do not fabricate their specific algebra here -- they
are marked suitable with an honest note, and the dynamic proof endpoint
returns a "supported_only" explanation rather than invented steps if
requested.
"""


def divisible_implies_square_divisible(var="n", k=3):
    classification = {
        "type": "Conditional Proposition",
        "variable": var,
        "domain": f"{var} \u2208 \u2124",
        "P": f"{var} is divisible by {k}",
        "Q": f"{var}\u00b2 is divisible by {k}",
        "logical_form": "P \u2192 Q",
    }

    direct_steps = [
        {"statement": f"Assume {var} is divisible by {k}.", "reason": "Assumption"},
        {"statement": f"By definition, {var} = {k}m for some integer m.", "reason": "Definition"},
        {"statement": f"{var}\u00b2 = ({k}m)\u00b2", "reason": "Substitution"},
        {"statement": f"{var}\u00b2 = {k * k}m\u00b2", "reason": "Algebraic simplification"},
        {"statement": f"{var}\u00b2 = {k}({k}m\u00b2)", "reason": "Algebraic simplification"},
        {"statement": f"Since {k}m\u00b2 is an integer, {var}\u00b2 is divisible by {k}.", "reason": "Definition"},
        {"statement": f"Therefore, if {var} is divisible by {k}, then {var}\u00b2 is divisible by {k}.", "reason": "Logical equivalence"},
    ]

    return {
        "classification": classification,
        "methods": {
            "direct": {"suitable": True, "reason": f"Direct algebraic proof works cleanly using {var} = {k}m."},
            "contrapositive": {"suitable": True, "reason": "Logically equivalent by contraposition, though the direct proof above is the clearest route."},
            "contradiction": {"suitable": True, "reason": "Possible via contradiction, but adds unnecessary complexity here."},
            "induction": {"suitable": False, "reason": "This is a conditional statement about an arbitrary integer, not a recursively indexed proposition P(n)."},
        },
        "support_level": "VERIFIED",
        "proofs": {
            "direct": {"steps": direct_steps, "conclusion": f"Therefore, if {var} is divisible by {k}, then {var}\u00b2 is divisible by {k}."},
        },
    }
