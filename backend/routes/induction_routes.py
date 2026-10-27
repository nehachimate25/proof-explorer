from flask import Blueprint, request, jsonify

from induction.library import get_example, list_examples
from induction.base_case import verify_base_case
from induction.hypothesis import get_hypothesis
from induction.inductive_step import verify_inductive_step
from validators.statement_classifier import classify_statement

induction_bp = Blueprint("induction", __name__, url_prefix="/api/induction")


@induction_bp.route("/examples", methods=["GET"])
def examples_route():
    return jsonify({"success": True, "data": list_examples()})


@induction_bp.route("/analyze", methods=["POST"])
def analyze_route():
    """Run the full induction pipeline: base case, hypothesis, inductive
    step, and only report PROVED if every component verified."""
    data = request.get_json(force=True) or {}
    example_id = data.get("example_id", "")

    entry = get_example(example_id)
    if not entry:
        return jsonify({"success": False, "error": "Induction example not found."}), 404

    base = verify_base_case(example_id)
    hyp = get_hypothesis(example_id)
    step = verify_inductive_step(example_id)

    fully_proved = (
        base.get("verification_status") == "VERIFIED"
        and step.get("verification_status") == "VERIFIED"
    )

    return jsonify({
        "success": True,
        "data": {
            "statement": entry["statement"],
            "domain_start": entry["domain_start"],
            "base_case": base,
            "inductive_hypothesis": hyp,
            "inductive_step": step,
            "final_status": "PROVED" if fully_proved else "NEEDS REVIEW",
        }
    })


@induction_bp.route("/base-case", methods=["POST"])
def base_case_route():
    data = request.get_json(force=True) or {}
    result = verify_base_case(data.get("example_id", ""))
    return jsonify({"success": True, "data": result})


@induction_bp.route("/step", methods=["POST"])
def step_route():
    data = request.get_json(force=True) or {}
    result = verify_inductive_step(data.get("example_id", ""), data.get("sample_k"))
    return jsonify({"success": True, "data": result})


@induction_bp.route("/analyze-statement", methods=["POST"])
def analyze_statement_route():
    """Dynamic induction entry point: accepts ANY user-typed statement
    (not an example_id). Reuses the same merged classifier as the Proof
    Explorer, so a statement that matches an induction pattern -- whether
    via the exact-match library or the flexible dynamic matcher -- is
    handled identically here as it would be there."""
    data = request.get_json(force=True) or {}
    statement = data.get("statement", "")

    if not statement or not statement.strip():
        return jsonify({"success": True, "data": {
            "applicable": False,
            "statement": statement,
            "message": "Please enter a mathematical statement.",
        }})

    result = classify_statement(statement)

    is_induction = (
        result.get("kind") == "induction"
        or result.get("classification", {}).get("type") == "Induction Proposition"
    )

    if is_induction and result.get("induction_result"):
        return jsonify({"success": True, "data": {
            "applicable": True,
            "statement": result["statement"],
            "classification": result["classification"],
            **result["induction_result"],
        }})

    reason = None
    methods = result.get("methods")
    if methods and "induction" in methods:
        reason = methods["induction"].get("reason")

    return jsonify({"success": True, "data": {
        "applicable": False,
        "statement": statement,
        "support_level": result.get("support_level"),
        "message": reason or result.get("message") or "Induction is not the natural proof method for this statement.",
    }})
