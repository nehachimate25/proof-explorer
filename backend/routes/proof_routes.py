from flask import Blueprint, request, jsonify

from proof_engine.library import get_example, list_examples, LIBRARY
from proof_engine.validator import suitable_methods_for
from proof_engine.direct import run_direct_proof
from proof_engine.contrapositive import run_contrapositive_proof, transform_conditional
from proof_engine.contradiction import run_contradiction_proof
from proof_engine.dynamic_proof import generate_dynamic_proof
from validators.statement_classifier import classify_statement
from logic.parser import LogicSyntaxError

proof_bp = Blueprint("proof", __name__, url_prefix="/api/proof")


@proof_bp.route("/examples", methods=["GET"])
def examples_route():
    return jsonify({"success": True, "data": list_examples()})


@proof_bp.route("/analyze", methods=["POST"])
def analyze_route():
    """Given a free-text statement, classify it: an exact match in a
    verified library is used as a fast VERIFIED shortcut, otherwise the
    dynamic rule-based analyzer (analyzers/statement_analyzer.py) takes
    over. A statement is never hard-rejected just for being absent from a
    library -- see validators/statement_classifier.py."""
    data = request.get_json(force=True) or {}
    statement = data.get("statement", "")
    result = classify_statement(statement)
    return jsonify({"success": True, "data": result})


@proof_bp.route("/dynamic", methods=["POST"])
def dynamic_route():
    """Generate the actual proof for a given statement + method. Works for
    ANY statement the analyzer recognizes, not just example_id lookups."""
    data = request.get_json(force=True) or {}
    statement = data.get("statement", "")
    method = data.get("method", "")
    result = generate_dynamic_proof(statement, method)
    return jsonify({"success": True, "data": result})


@proof_bp.route("/direct", methods=["POST"])
def direct_route():
    data = request.get_json(force=True) or {}
    example_id = data.get("example_id", "")
    result = run_direct_proof(example_id)
    return jsonify({"success": True, "data": result})


@proof_bp.route("/contrapositive", methods=["POST"])
def contrapositive_route():
    data = request.get_json(force=True) or {}
    example_id = data.get("example_id", "")
    result = run_contrapositive_proof(example_id)
    return jsonify({"success": True, "data": result})


@proof_bp.route("/contrapositive/transform", methods=["POST"])
def contrapositive_transform_route():
    """General P -> Q symbolic transform (converse / inverse / contrapositive)
    for any user-supplied conditional expression, backed by a truth-table
    equivalence check."""
    data = request.get_json(force=True) or {}
    expr = data.get("expression", "")
    try:
        result = transform_conditional(expr)
        return jsonify({"success": True, "data": result})
    except LogicSyntaxError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@proof_bp.route("/contradiction", methods=["POST"])
def contradiction_route():
    data = request.get_json(force=True) or {}
    example_id = data.get("example_id", "")
    result = run_contradiction_proof(example_id)
    return jsonify({"success": True, "data": result})


@proof_bp.route("/compare", methods=["POST"])
def compare_route():
    """Compare available proof methods for a given example_id (spec
    section 25)."""
    data = request.get_json(force=True) or {}
    example_id = data.get("example_id", "")
    entry = get_example(example_id)
    if not entry:
        return jsonify({"success": False, "error": "Example not found."}), 404

    comparisons = []
    method_runners = {
        "direct": run_direct_proof,
        "contrapositive": run_contrapositive_proof,
        "contradiction": run_contradiction_proof,
    }
    difficulty_map = {"direct": "Beginner", "contrapositive": "Intermediate", "contradiction": "Intermediate"}

    for method in entry["valid_methods"]:
        if method == "induction":
            continue
        runner = method_runners.get(method)
        if not runner:
            continue
        result = runner(example_id)
        comparisons.append({
            "method": method,
            "num_steps": len(result.get("steps", [])),
            "logical_approach": entry["method_notes"].get(method, ""),
            "difficulty": difficulty_map.get(method, "Intermediate"),
            "result": result.get("verification_status", "NEEDS REVIEW"),
        })

    return jsonify({"success": True, "data": {"statement": entry["statement"], "comparisons": comparisons}})
