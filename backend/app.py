"""
Mathematical Proof Verification and Proof Method Explorer -- Backend
-----------------------------------------------------------------------
Flask application entrypoint. Registers all API blueprints and initializes
the local SQLite database. No paid API dependency -- everything here runs
fully offline.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from database.db import init_db
from routes.logic_routes import logic_bp
from routes.proposition_routes import proposition_bp
from routes.proof_routes import proof_bp
from routes.induction_routes import induction_bp
from routes.history_routes import history_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(logic_bp)
    app.register_blueprint(proposition_bp)
    app.register_blueprint(proof_bp)
    app.register_blueprint(induction_bp)
    app.register_blueprint(history_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "proof-explorer-backend"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


app = create_app()
init_db()  # always initialize, regardless of how the app is launched
           # (python app.py, flask run, gunicorn, etc.)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
