"""
Conditional Analyzer
-----------------------
Recognizes common conditional / declarative Discrete Mathematics patterns
(parity, divisibility, sums) from normalized statement text and routes to
the appropriate generator. Every branch here corresponds to a genuine,
hand-verifiable algebraic template -- if nothing matches, this returns
None and the caller falls through to the generic logic analyzer or
NEEDS_REVIEW, rather than guessing.
"""

import re

from . import parity_analyzer, divisibility_analyzer, parity_rule_engine


def try_match(text_norm: str):
    t = text_norm.lower()

    # Pure parity conditionals (n / n\u00b2 / n+1 / n-1) go through the
    # deterministic truth engine FIRST -- it correctly returns VERIFIED for
    # true statements (with a real proof) and DISPROVED for false ones
    # (with a real counterexample), rather than the old hand-written
    # templates below which only recognized the TRUE cases.
    engine_result = parity_rule_engine.try_match(t)
    if engine_result:
        return engine_result

    # Declarative variant: "an even number has an even square"
    if re.search(r"an?\s+even\s+number\s+has\s+an?\s+even\s+square", t) or \
       re.search(r"even numbers have even squares", t):
        return parity_rule_engine.evaluate("n", "even", "n^2", "even")

    if re.search(r"an?\s+odd\s+number\s+has\s+an?\s+odd\s+square", t) or \
       re.search(r"odd numbers have odd squares", t):
        return parity_rule_engine.evaluate("n", "odd", "n^2", "odd")

    # "if X is divisible by K ... then X\u00b2 is divisible by K"
    m = re.search(r"if\s+([a-zA-Z])\s+is\s+divisible\s+by\s+(\d+).*?then\s+\1\s*\u00b2\s+is\s+divisible\s+by\s+\2", t)
    if m:
        return divisibility_analyzer.divisible_implies_square_divisible(m.group(1), int(m.group(2)))

    # Declarative: "the sum of two even integers/numbers is even"
    if re.search(r"sum of two even (integers|numbers) is even", t):
        return parity_analyzer.sum_two_evens("a", "b")

    # Declarative: "the sum of two odd integers/numbers is even"
    if re.search(r"sum of two odd (integers|numbers) is even", t):
        return parity_analyzer.sum_two_odds("a", "b")

    # "if X and Y are even ... then X+Y is even"
    m = re.search(r"if\s+([a-zA-Z])\s+and\s+([a-zA-Z])\s+are\s+even.*?then\s+\1\s*\+\s*\2\s+is\s+even", t)
    if m:
        return parity_analyzer.sum_two_evens(m.group(1), m.group(2))

    # "if X and Y are odd ... then X+Y is even"
    m = re.search(r"if\s+([a-zA-Z])\s+and\s+([a-zA-Z])\s+are\s+odd.*?then\s+\1\s*\+\s*\2\s+is\s+even", t)
    if m:
        return parity_analyzer.sum_two_odds(m.group(1), m.group(2))

    return None
