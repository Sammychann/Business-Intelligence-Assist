"""
Business Intelligence Assist — Flask Application
Serves the frontend and provides the /api/analyze endpoint.
"""

import os
import json
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from services.search import search_company
from services.analyzer import analyze_company

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


@app.route("/")
def index():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze a company.
    Expects JSON: { "company_name": "..." }
    Returns structured intelligence report JSON.
    """
    try:
        data = request.get_json(force=True)
        company_name = data.get("company_name", "").strip()

        if not company_name:
            return jsonify({"error": "Company name is required"}), 400

        if len(company_name) > 200:
            return jsonify({"error": "Company name too long"}), 400

        # Step 1: Search for company data
        search_data = search_company(company_name)

        # Step 2: Analyze with LLM
        report = analyze_company(search_data)

        return jsonify(report), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 502
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "Business Intelligence Assist"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🔷 Business Intelligence Assist running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
