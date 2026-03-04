"""
Business Intelligence Assist — Flask Application
Agentic AI Orchestration for company intelligence and interview coaching.
"""

import os
import json
import logging
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

from agents.orchestrator import Orchestrator

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# Initialize orchestrator once
orchestrator = Orchestrator()


@app.route("/")
def index():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze a company and generate interview coaching for a specific role.
    Expects JSON: { "company_name": "...", "role": "..." }
    Returns structured intelligence report + interview questions.
    """
    try:
        data = request.get_json(force=True)
        company_name = data.get("company_name", "").strip()
        role = data.get("role", "").strip()

        if not company_name:
            return jsonify({"error": "Company name is required"}), 400

        if not role:
            return jsonify({"error": "Role is required"}), 400

        if len(company_name) > 200:
            return jsonify({"error": "Company name too long"}), 400

        if len(role) > 100:
            return jsonify({"error": "Role description too long"}), 400

        # Run the agentic pipeline
        report = orchestrator.run(company_name, role)

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
    return jsonify({
        "status": "ok",
        "service": "Business Intelligence Assist",
        "version": "2.0.0",
        "agents": ["CompanyIntelAgent", "InterviewAgent"]
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🔷 Business Intelligence Assist v2.0 running at http://localhost:{port}\n")
    print(f"   Agents: CompanyIntelAgent → InterviewAgent")
    print(f"   Knowledge Bases: Company Directory, Search Service, Interview History\n")
    app.run(host="0.0.0.0", port=port, debug=True)
