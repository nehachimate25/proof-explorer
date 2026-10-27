from flask import Blueprint, request, jsonify
from logic.parser import parse_expression, LogicSyntaxError, ImplyNode, IffNode, AndNode, OrNode, NotNode, VarNode

proposition_bp = Blueprint("proposition", __name__, url_prefix="/api/proposition")


def classify_proposition(node):
    if isinstance(node, ImplyNode):
        return "Conditional"
    if isinstance(node, IffNode):
        return "Biconditional"
    if isinstance(node, AndNode):
        return "Conjunction"
    if isinstance(node, OrNode):
        return "Disjunction"
    if isinstance(node, NotNode):
        return "Negation"
    if isinstance(node, VarNode):
        return "Atomic proposition"
    return "Compound proposition"


@proposition_bp.route("/analyze", methods=["POST"])
def analyze_route():
    """
    Structured input, per spec section 8: the user supplies P, Q and the
    connecting operator (or a raw logic expression) -- we do NOT attempt to
    freelance-parse arbitrary natural language, which would risk
    misclassifying the statement.
    """
    data = request.get_json(force=True) or {}
    p_text = data.get("P", "").strip()
    q_text = data.get("Q", "").strip()
    operator = data.get("operator", "").strip()  # one of -> <-> & | !
    raw_expression = data.get("expression", "").strip()

    if raw_expression:
        expr = raw_expression
    elif p_text and operator and q_text:
        expr = f"P {operator} Q"
    elif p_text and operator and not q_text:
        expr = f"{operator}P"
    elif p_text:
        expr = "P"
    else:
        return jsonify({"success": False, "error": "Please provide at least a P statement or a raw expression."}), 400

    try:
        node = parse_expression(expr)
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400

    prop_type = classify_proposition(node)

    return jsonify({
        "success": True,
        "data": {
            "statement": data.get("statement", ""),
            "P": p_text or None,
            "Q": q_text or None,
            "logical_form": node.to_string(),
            "proposition_type": prop_type,
            "variables": sorted(node.variables()),
        }
    })
