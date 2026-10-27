from flask import Blueprint, request, jsonify
from models import history as history_model

history_bp = Blueprint("history", __name__, url_prefix="/api/history")


@history_bp.route("", methods=["GET"])
def list_history():
    return jsonify({"success": True, "data": history_model.list_entries()})


@history_bp.route("", methods=["POST"])
def add_history():
    data = request.get_json(force=True) or {}
    entry_id = history_model.add_entry(
        statement=data.get("statement", ""),
        proof_method=data.get("proof_method", ""),
        result=data.get("result", ""),
        num_steps=data.get("num_steps", 0),
    )
    return jsonify({"success": True, "data": {"id": entry_id}})


@history_bp.route("/<int:entry_id>", methods=["DELETE"])
def delete_history(entry_id):
    history_model.delete_entry(entry_id)
    return jsonify({"success": True})
