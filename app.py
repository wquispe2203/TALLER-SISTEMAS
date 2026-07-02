from __future__ import annotations

import json
from flask import Flask, jsonify, request

from calculator import calculate_transfer
from validation import validate_payload

app = Flask(__name__)


@app.get("/")
def index():
    with open("public/index.html", "r", encoding="utf-8") as handle:
        return handle.read()


@app.post("/api/transfer-calculator")
def transfer_calculator():
    try:
        payload = request.get_json(silent=True) or {}
        validate_payload(payload)
        result = calculate_transfer(payload)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover
        return jsonify({"success": False, "error": "Error inesperado al calcular el traslado."}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
