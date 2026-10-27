"""
Truth Table Engine
-------------------
Given a parsed propositional logic AST, deterministically enumerates every
possible truth assignment for its variables (2^n rows) and evaluates the
expression for each row. This is pure boolean arithmetic -- no AI, no
guessing -- so the result is always mathematically correct for the given
expression.
"""

import itertools
from .parser import parse_expression, ordered_variables, LogicSyntaxError


def generate_truth_table(expr: str):
    node = parse_expression(expr)
    variables = ordered_variables(node)

    if len(variables) > 6:
        raise LogicSyntaxError(
            "Too many distinct variables (max 6 supported for a readable truth table)."
        )

    rows = []
    for combo in itertools.product([True, False], repeat=len(variables)):
        env = dict(zip(variables, combo))
        result = node.evaluate(env)
        rows.append({"assignment": env, "result": result})

    return {
        "expression": expr,
        "normalized": node.to_string(),
        "variables": variables,
        "rows": rows,
    }


def classify(expr: str):
    """Classify an expression as a Tautology, Contradiction, or
    Contingency, based on exhaustively checking every row of its truth
    table -- the only mathematically sound way to make this claim."""
    table = generate_truth_table(expr)
    results = [r["result"] for r in table["rows"]]
    if all(results):
        classification = "Tautology"
    elif not any(results):
        classification = "Contradiction"
    else:
        classification = "Contingency"
    return {**table, "classification": classification}


def check_equivalence(expr1: str, expr2: str):
    """Two expressions are logically equivalent iff they share the exact
    same truth value on every possible assignment of shared variables.
    We build a combined variable set and evaluate both expressions across
    every joint assignment."""
    node1 = parse_expression(expr1)
    node2 = parse_expression(expr2)

    vars1 = ordered_variables(node1)
    vars2 = ordered_variables(node2)
    all_vars = list(dict.fromkeys(vars1 + vars2))

    if len(all_vars) > 6:
        raise LogicSyntaxError("Too many distinct variables (max 6 supported).")

    rows = []
    equivalent = True
    for combo in itertools.product([True, False], repeat=len(all_vars)):
        env = dict(zip(all_vars, combo))
        r1 = node1.evaluate(env)
        r2 = node2.evaluate(env)
        if r1 != r2:
            equivalent = False
        rows.append({"assignment": env, "left": r1, "right": r2, "match": r1 == r2})

    return {
        "expr1": expr1,
        "expr2": expr2,
        "normalized1": node1.to_string(),
        "normalized2": node2.to_string(),
        "variables": all_vars,
        "rows": rows,
        "equivalent": equivalent,
    }
