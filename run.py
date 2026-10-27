"""
run.py - start Proof Explorer (backend + frontend) with one command.

    python run.py

Then open http://localhost:5000 in your browser.

How it works
------------
The Flask app lives in backend/app.py and is NOT changed. This file imports
that app and adds two small things on top of it:

  1. "/"            -> frontend/index.html
  2. "/<some file>" -> any file inside the frontend/ folder
                       (html pages, css/style.css, js/*.js)

Every URL that starts with /api/ still goes to the original backend routes,
exactly as before. Because the pages and the API now come from the same
address (localhost:5000), no proxy and no build tool is needed.
"""

import os
import sys

from flask import abort, request, send_from_directory

# Folders, worked out from where this file lives, so it runs from anywhere.
ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
BACKEND_FOLDER = os.path.join(ROOT_FOLDER, "backend")
FRONTEND_FOLDER = os.path.join(ROOT_FOLDER, "frontend")

# The backend files import each other ("from routes... import ..."), so the
# backend folder has to be on Python's search path before we import it.
sys.path.insert(0, BACKEND_FOLDER)

# Importing backend/app.py builds the Flask app, registers every API route,
# and creates the SQLite database file if it does not exist yet.
from app import app  # noqa: E402  (import is intentionally after sys.path)


@app.route("/")
def home_page():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


# This route also accepts POST/PUT/DELETE on purpose: if someone calls an
# /api/ address that does not exist, the backend's own JSON "Not found"
# answer should come back (not a confusing "405 Method Not Allowed" page).
@app.route("/<path:filename>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def frontend_files(filename):
    if request.method not in ("GET", "HEAD") or filename.startswith("api/"):
        abort(404)  # handled by the backend's JSON 404 handler
    return send_from_directory(FRONTEND_FOLDER, filename)


if __name__ == "__main__":
    print("Proof Explorer is starting...")
    print("Open http://localhost:5000 in your browser. Press Ctrl+C to stop.")
    app.run(debug=True, port=5000)
