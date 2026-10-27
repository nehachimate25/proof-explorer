from flask import Blueprint, request, jsonify
from logic.truth_table import generate_truth_table, classify, check_equivalence
from logic.evaluator import evaluate_with_assignment
from logic.parser import LogicSyntaxError

logic_bp = Blueprint("logic", __name__, url_prefix="/api/logic")


@logic_bp.route("/truth-table", methods=["POST"])
def truth_table_route():
    data = request.get_json(force=True) or {}
    expr = data.get("expression", "")
    try:
        result = generate_truth_table(expr)
        return jsonify({"success": True, "data": result})
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@logic_bp.route("/analyze", methods=["POST"])
def analyze_route():
    """Classify as Tautology / Contradiction / Contingency, using the full
    truth table as evidence."""
    data = request.get_json(force=True) or {}
    expr = data.get("expression", "")
    try:
        result = classify(expr)
        return jsonify({"success": True, "data": result})
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@logic_bp.route("/equivalence", methods=["POST"])
def equivalence_route():
    data = request.get_json(force=True) or {}
    expr1 = data.get("expression1", "")
    expr2 = data.get("expression2", "")
    try:
        result = check_equivalence(expr1, expr2)
        return jsonify({"success": True, "data": result})
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@logic_bp.route("/evaluate", methods=["POST"])
def evaluate_route():
    data = request.get_json(force=True) or {}
    expr = data.get("expression", "")
    assignment = data.get("assignment", {})
    try:
        result = evaluate_with_assignment(expr, assignment)
        return jsonify({"success": True, "data": result})
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400
