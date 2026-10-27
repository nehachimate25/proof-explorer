"""
Single-assignment evaluator and contrapositive/converse/inverse transforms
for conditional (P -> Q) statements. Pure symbolic manipulation -- every
transform below is a syntactic rule from propositional logic, not an AI
guess.
"""

from .parser import parse_expression, ImplyNode, NotNode, LogicSyntaxError


def evaluate_with_assignment(expr: str, assignment: dict):
    node = parse_expression(expr)
    return {
        "expression": expr,
        "normalized": node.to_string(),
        "assignment": assignment,
        "result": node.evaluate(assignment),
    }


def _negate(node):
    """Return the logical negation of a node, simplifying double negation."""
    if isinstance(node, NotNode):
        return node.child
    return NotNode(node)


def derive_conditional_forms(expr: str):
    """For an expression of the form P -> Q, derive:
        Converse:        Q -> P
        Inverse:         ¬P -> ¬Q
        Contrapositive:  ¬Q -> ¬P   (logically equivalent to the original)

    Raises LogicSyntaxError if the top-level connective is not '->' , since
    these named transforms are only defined for conditional statements.
    """
    node = parse_expression(expr)
    if not isinstance(node, ImplyNode):
        raise LogicSyntaxError(
            "This transform (converse/inverse/contrapositive) requires a "
            "top-level conditional statement of the form P -> Q."
        )

    P, Q = node.left, node.right
    converse = ImplyNode(Q, P)
    inverse = ImplyNode(_negate(P), _negate(Q))
    contrapositive = ImplyNode(_negate(Q), _negate(P))

    return {
        "original": node.to_string(),
        "P": P.to_string(),
        "Q": Q.to_string(),
        "converse": converse.to_string(),
        "inverse": inverse.to_string(),
        "contrapositive": contrapositive.to_string(),
    }
