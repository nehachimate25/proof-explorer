"""
Parity Analyzer
------------------
Generates fully-verified proofs for even/odd conditional patterns, for any
variable name detected in the statement. Every proof template here was
hand-verified before being wired in (same standard as the static example
library) -- the variable name is the only thing substituted.
"""


def even_implies_even_square(var="n"):
    classification = {
        "type": "Conditional Proposition",
        "variable": var,
        "domain": f"{var} \u2208 \u2124",
        "P": f"{var} is even",
        "Q": f"{var}\u00b2 is even",
        "logical_form": "P \u2192 Q",
    }

    direct_steps = [
        {"statement": f"Assume {var} is even.", "reason": "Assumption"},
        {"statement": f"By definition of an even integer, {var} = 2k for some integer k.", "reason": "Definition"},
        {"statement": f"{var}\u00b2 = (2k)\u00b2", "reason": "Substitution"},
        {"statement": f"{var}\u00b2 = 4k\u00b2", "reason": "Algebraic simplification"},
        {"statement": f"{var}\u00b2 = 2(2k\u00b2)", "reason": "Algebraic simplification"},
        {"statement": f"Since 2k\u00b2 is an integer, {var}\u00b2 is even.", "reason": "Definition"},
        {"statement": f"Therefore, if {var} is even, then {var}\u00b2 is even.", "reason": "Logical equivalence"},
    ]

    contrapositive_steps = [
        {"statement": f"Original: P \u2192 Q, where P = '{var} is even', Q = '{var}\u00b2 is even'.", "reason": "Definition"},
        {"statement": f"Contrapositive: \u00acQ \u2192 \u00acP, i.e. 'if {var}\u00b2 is odd, then {var} is odd'.", "reason": "Logical equivalence"},
        {"statement": f"Assume {var}\u00b2 is odd. Suppose, toward showing \u00acP, that {var} were even instead.", "reason": "Assumption"},
        {"statement": f"If {var} were even, {var} = 2k for some integer k, so {var}\u00b2 = 4k\u00b2 = 2(2k\u00b2), which is even.", "reason": "Algebraic simplification"},
        {"statement": f"This contradicts {var}\u00b2 being odd, so {var} cannot be even; {var} must be odd.", "reason": "Logical equivalence"},
        {"statement": "We have shown \u00acQ \u2192 \u00acP. Since a conditional and its contrapositive are logically equivalent, P \u2192 Q holds.", "reason": "Logical equivalence"},
        {"statement": f"Therefore, if {var} is even, then {var}\u00b2 is even.", "reason": "Logical equivalence"},
    ]

    contradiction_steps = [
        {"statement": f"Assume, for contradiction, that {var} is even but {var}\u00b2 is odd.", "reason": "Assumption"},
        {"statement": f"Since {var} is even, {var} = 2k for some integer k.", "reason": "Definition"},
        {"statement": f"Then {var}\u00b2 = (2k)\u00b2 = 4k\u00b2 = 2(2k\u00b2).", "reason": "Algebraic simplification"},
        {"statement": f"Since 2k\u00b2 is an integer, {var}\u00b2 = 2(2k\u00b2) is even.", "reason": "Definition"},
        {"statement": f"This contradicts our assumption that {var}\u00b2 is odd.", "reason": "Contradiction"},
        {"statement": f"Therefore the assumption was false: if {var} is even, then {var}\u00b2 must be even.", "reason": "Contradiction"},
    ]

    return {
        "classification": classification,
        "methods": {
            "direct": {"suitable": True, "reason": "Direct proof works cleanly: assume P, algebraically derive Q."},
            "contrapositive": {"suitable": True, "reason": "Equally valid: proves the logically equivalent contrapositive instead."},
            "contradiction": {"suitable": True, "reason": "Also valid, though slightly less direct than the direct proof."},
            "induction": {"suitable": False, "reason": "This is a conditional statement about an arbitrary integer, not a recursively indexed proposition P(n)."},
        },
        "support_level": "VERIFIED",
        "proofs": {
            "direct": {"steps": direct_steps, "conclusion": f"Therefore, if {var} is even, then {var}\u00b2 is even."},
            "contrapositive": {"steps": contrapositive_steps, "conclusion": f"Therefore, if {var} is even, then {var}\u00b2 is even."},
            "contradiction": {"steps": contradiction_steps, "conclusion": f"Therefore, if {var} is even, then {var}\u00b2 is even."},
        },
    }


def odd_implies_odd_square(var="n"):
    classification = {
        "type": "Conditional Proposition",
        "variable": var,
        "domain": f"{var} \u2208 \u2124",
        "P": f"{var} is odd",
        "Q": f"{var}\u00b2 is odd",
        "logical_form": "P \u2192 Q",
    }

    direct_steps = [
        {"statement": f"Assume {var} is odd.", "reason": "Assumption"},
        {"statement": f"By definition of an odd integer, {var} = 2k + 1 for some integer k.", "reason": "Definition"},
        {"statement": f"{var}\u00b2 = (2k + 1)\u00b2", "reason": "Substitution"},
        {"statement": f"{var}\u00b2 = 4k\u00b2 + 4k + 1", "reason": "Algebraic simplification"},
        {"statement": f"{var}\u00b2 = 2(2k\u00b2 + 2k) + 1", "reason": "Algebraic simplification"},
        {"statement": f"Since 2k\u00b2 + 2k is an integer, {var}\u00b2 is of the form 2m + 1, so {var}\u00b2 is odd.", "reason": "Definition"},
        {"statement": f"Therefore, if {var} is odd, then {var}\u00b2 is odd.", "reason": "Logical equivalence"},
    ]

    contrapositive_steps = [
        {"statement": f"Original: P \u2192 Q, where P = '{var} is odd', Q = '{var}\u00b2 is odd'.", "reason": "Definition"},
        {"statement": f"Contrapositive: \u00acQ \u2192 \u00acP, i.e. 'if {var}\u00b2 is even, then {var} is even'.", "reason": "Logical equivalence"},
        {"statement": f"Assume {var}\u00b2 is even. Suppose, toward showing \u00acP, that {var} were odd instead.", "reason": "Assumption"},
        {"statement": f"If {var} were odd, {var} = 2k+1, so {var}\u00b2 = 4k\u00b2+4k+1 = 2(2k\u00b2+2k)+1, which is odd.", "reason": "Algebraic simplification"},
        {"statement": f"This contradicts {var}\u00b2 being even, so {var} cannot be odd; {var} must be even.", "reason": "Logical equivalence"},
        {"statement": "We have shown \u00acQ \u2192 \u00acP. Since a conditional and its contrapositive are logically equivalent, P \u2192 Q holds.", "reason": "Logical equivalence"},
        {"statement": f"Therefore, if {var} is odd, then {var}\u00b2 is odd.", "reason": "Logical equivalence"},
    ]

    contradiction_steps = [
        {"statement": f"Assume, for contradiction, that {var} is odd but {var}\u00b2 is even.", "reason": "Assumption"},
        {"statement": f"Since {var} is odd, {var} = 2k + 1 for some integer k.", "reason": "Definition"},
        {"statement": f"Then {var}\u00b2 = (2k+1)\u00b2 = 4k\u00b2 + 4k + 1 = 2(2k\u00b2+2k) + 1.", "reason": "Algebraic simplification"},
        {"statement": f"This means {var}\u00b2 is of the form 2m + 1, i.e. odd.", "reason": "Definition"},
        {"statement": f"This contradicts our assumption that {var}\u00b2 is even.", "reason": "Contradiction"},
        {"statement": f"Therefore the assumption was false: if {var} is odd, then {var}\u00b2 must be odd.", "reason": "Contradiction"},
    ]

    return {
        "classification": classification,
        "methods": {
            "direct": {"suitable": True, "reason": "Direct proof works cleanly: assume P, algebraically derive Q."},
            "contrapositive": {"suitable": True, "reason": "Equally valid: proves the logically equivalent contrapositive instead."},
            "contradiction": {"suitable": True, "reason": "Also valid, though slightly less direct than the direct proof."},
            "induction": {"suitable": False, "reason": "This is a conditional statement about an arbitrary integer, not a recursively indexed proposition P(n)."},
        },
        "support_level": "VERIFIED",
        "proofs": {
            "direct": {"steps": direct_steps, "conclusion": f"Therefore, if {var} is odd, then {var}\u00b2 is odd."},
            "contrapositive": {"steps": contrapositive_steps, "conclusion": f"Therefore, if {var} is odd, then {var}\u00b2 is odd."},
            "contradiction": {"steps": contradiction_steps, "conclusion": f"Therefore, if {var} is odd, then {var}\u00b2 is odd."},
        },
    }


def sum_two_evens(var1="a", var2="b"):
    classification = {
        "type": "General Proposition",
        "variable": None,
        "domain": f"{var1}, {var2} \u2208 \u2124",
        "P": f"{var1} and {var2} are even",
        "Q": f"{var1} + {var2} is even",
        "logical_form": "P \u2192 Q",
    }

    direct_steps = [
        {"statement": f"Assume {var1} and {var2} are even integers.", "reason": "Assumption"},
        {"statement": f"By definition, {var1} = 2m and {var2} = 2n for some integers m, n.", "reason": "Definition"},
        {"statement": f"{var1} + {var2} = 2m + 2n", "reason": "Substitution"},
        {"statement": f"{var1} + {var2} = 2(m + n)", "reason": "Algebraic simplification"},
        {"statement": f"Since m + n is an integer, {var1} + {var2} is of the form 2p, so it is even.", "reason": "Definition"},
        {"statement": "Therefore, the sum of two even integers is even.", "reason": "Logical equivalence"},
    ]

    contradiction_steps = [
        {"statement": f"Assume, for contradiction, that {var1} and {var2} are even but {var1} + {var2} is odd.", "reason": "Assumption"},
        {"statement": f"Since {var1}, {var2} are even, {var1} = 2m, {var2} = 2n for integers m, n.", "reason": "Definition"},
        {"statement": f"{var1} + {var2} = 2m + 2n = 2(m + n).", "reason": "Algebraic simplification"},
        {"statement": f"Since m + n is an integer, {var1} + {var2} is even.", "reason": "Definition"},
        {"statement": "This contradicts the assumption that the sum was odd.", "reason": "Contradiction"},
        {"statement": "Therefore, the sum of two even integers must be even.", "reason": "Contradiction"},
    ]

    return {
        "classification": classification,
        "methods": {
            "direct": {"suitable": True, "reason": "Direct algebraic proof is the natural approach."},
            "contrapositive": {"suitable": False, "reason": "The contrapositive involves a disjunction ('a or b is odd'), which is more awkward to state than the direct route."},
            "contradiction": {"suitable": True, "reason": "Possible but adds no clarity over the direct proof."},
            "induction": {"suitable": False, "reason": "No natural-number index is being incremented here."},
        },
        "support_level": "VERIFIED",
        "proofs": {
            "direct": {"steps": direct_steps, "conclusion": "Therefore, the sum of two even integers is even."},
            "contradiction": {"steps": contradiction_steps, "conclusion": "Therefore, the sum of two even integers is even."},
        },
    }


def sum_two_odds(var1="a", var2="b"):
    classification = {
        "type": "General Proposition",
        "variable": None,
        "domain": f"{var1}, {var2} \u2208 \u2124",
        "P": f"{var1} and {var2} are odd",
        "Q": f"{var1} + {var2} is even",
        "logical_form": "P \u2192 Q",
    }

    direct_steps = [
        {"statement": f"Assume {var1} and {var2} are odd integers.", "reason": "Assumption"},
        {"statement": f"By definition, {var1} = 2m + 1 and {var2} = 2n + 1 for some integers m, n.", "reason": "Definition"},
        {"statement": f"{var1} + {var2} = (2m + 1) + (2n + 1)", "reason": "Substitution"},
        {"statement": f"{var1} + {var2} = 2m + 2n + 2", "reason": "Algebraic simplification"},
        {"statement": f"{var1} + {var2} = 2(m + n + 1)", "reason": "Algebraic simplification"},
        {"statement": f"Since m + n + 1 is an integer, {var1} + {var2} is of the form 2p, so it is even.", "reason": "Definition"},
        {"statement": "Therefore, the sum of two odd integers is even.", "reason": "Logical equivalence"},
    ]

    return {
        "classification": classification,
        "methods": {
            "direct": {"suitable": True, "reason": "Direct algebraic proof is the natural approach."},
            "contrapositive": {"suitable": False, "reason": "The contrapositive again involves a disjunction and is harder to state cleanly than the direct route."},
            "contradiction": {"suitable": False, "reason": "Possible but unnecessary complexity for this statement; the direct proof is already clean."},
            "induction": {"suitable": False, "reason": "No natural-number index is being incremented here."},
        },
        "support_level": "VERIFIED",
        "proofs": {
            "direct": {"steps": direct_steps, "conclusion": "Therefore, the sum of two odd integers is even."},
        },
    }
