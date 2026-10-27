"""
check_app.py - quick self-test for Proof Explorer.

    python check_app.py

It does NOT need the server to be running. It loads the same Flask app that
run.py uses and sends it test requests: the health endpoint, every page of the
frontend, and every API route the frontend calls. Each line prints PASS or FAIL.
"""

import os
import sys

ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_FOLDER, "backend"))

import run  # noqa: E402  (this builds the app exactly like "python run.py")

client = run.app.test_client()
failures = 0


def check(name, condition):
    global failures
    print(("PASS  " if condition else "FAIL  ") + name)
    if not condition:
        failures += 1


def post(path, data):
    response = client.post(path, json=data)
    return response.status_code, response.get_json()


# ---------- health ----------
response = client.get("/api/health")
check("GET /api/health -> status ok", response.status_code == 200 and response.get_json()["status"] == "ok")

# ---------- every frontend file is served ----------
pages = ["", "index.html", "logic.html", "propositions.html", "proof-explorer.html",
         "induction.html", "history.html", "help.html", "about.html",
         "css/style.css", "js/api.js", "js/common.js", "js/views.js", "js/logic.js",
         "js/propositions.js", "js/proof-explorer.js", "js/induction.js", "js/history.js"]
for page in pages:
    check("GET /" + page, client.get("/" + page).status_code == 200)

check("unknown /api/ address still gives the backend's JSON 404",
      client.get("/api/nope").status_code == 404 and client.get("/api/nope").get_json()["success"] is False)

# ---------- logic ----------
code, body = post("/api/logic/truth-table", {"expression": "P -> Q"})
check("POST /api/logic/truth-table", code == 200 and len(body["data"]["rows"]) == 4)
code, body = post("/api/logic/analyze", {"expression": "P | !P"})
check("POST /api/logic/analyze -> Tautology", code == 200 and body["data"]["classification"] == "Tautology")
code, body = post("/api/logic/equivalence", {"expression1": "P -> Q", "expression2": "!Q -> !P"})
check("POST /api/logic/equivalence", code == 200 and body["data"]["equivalent"] is True)
code, body = post("/api/logic/evaluate", {"expression": "P -> Q", "assignment": {"P": True, "Q": False}})
check("POST /api/logic/evaluate", code == 200 and body["data"]["result"] is False)
code, body = post("/api/logic/truth-table", {"expression": "P ->"})
check("bad formula -> 400 with an error message", code == 400 and body["success"] is False and body["error"])

# ---------- propositions ----------
code, body = post("/api/proposition/analyze", {"P": "n is even", "Q": "n^2 is even", "operator": "→"})
check("POST /api/proposition/analyze", code == 200 and body["data"]["proposition_type"] == "Conditional")

# ---------- proofs ----------
response = client.get("/api/proof/examples")
examples = response.get_json()["data"]
check("GET /api/proof/examples", response.status_code == 200 and len(examples) > 0)
example_id = examples[0]["id"]
code, body = post("/api/proof/analyze", {"statement": examples[0]["statement"]})
check("POST /api/proof/analyze", code == 200 and body["data"]["status"] == "VERIFIED")
for method in ["direct", "contrapositive", "contradiction"]:
    code, body = post("/api/proof/" + method, {"example_id": example_id})
    check("POST /api/proof/" + method, code == 200 and body["data"]["status"] == "verified")
code, body = post("/api/proof/dynamic", {"statement": "If n is odd, then n² is odd.", "method": "direct"})
check("POST /api/proof/dynamic", code == 200 and body["data"]["status"] == "verified")
code, body = post("/api/proof/contrapositive/transform", {"expression": "P -> Q"})
check("POST /api/proof/contrapositive/transform", code == 200 and body["data"]["equivalence_verified"] is True)
code, body = post("/api/proof/compare", {"example_id": example_id})
check("POST /api/proof/compare", code == 200 and len(body["data"]["comparisons"]) == 3)

# ---------- induction ----------
response = client.get("/api/induction/examples")
induction_examples = response.get_json()["data"]
check("GET /api/induction/examples", response.status_code == 200 and len(induction_examples) > 0)
induction_id = induction_examples[0]["id"]
code, body = post("/api/induction/analyze", {"example_id": induction_id})
check("POST /api/induction/analyze -> PROVED", code == 200 and body["data"]["final_status"] == "PROVED")
code, body = post("/api/induction/base-case", {"example_id": induction_id})
check("POST /api/induction/base-case", code == 200 and body["data"]["verification_status"] == "VERIFIED")
code, body = post("/api/induction/step", {"example_id": induction_id, "sample_k": 7})
check("POST /api/induction/step (sample_k)", code == 200 and len(body["data"]["numeric_spot_checks"]) == 1)
code, body = post("/api/induction/analyze-statement", {"statement": "1 + 2 + ... + n = n(n+1)/2 for all n ≥ 1"})
check("POST /api/induction/analyze-statement", code == 200 and body["data"]["applicable"] is True)

# ---------- history (saves one entry, then deletes it again) ----------
code, body = post("/api/history", {"statement": "check_app test", "proof_method": "direct", "result": "VERIFIED", "num_steps": 3})
check("POST /api/history", code == 200 and "id" in body["data"])
new_id = body["data"]["id"]
entries = client.get("/api/history").get_json()["data"]
check("GET /api/history contains the new entry", any(entry["id"] == new_id for entry in entries))
response = client.delete("/api/history/" + str(new_id))
check("DELETE /api/history/<id>", response.status_code == 200)
entries = client.get("/api/history").get_json()["data"]
check("entry is gone after delete", not any(entry["id"] == new_id for entry in entries))

print()
if failures:
    print(str(failures) + " check(s) FAILED.")
    sys.exit(1)
print("All checks passed.")
