"""
Business Intelligence Assist — Flask + SocketIO Application
Agentic AI Orchestration for company intelligence, interview coaching, and live coaching.
"""

import os
import json
import logging
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

from agents.orchestrator import Orchestrator
from agents.live_coach_agent import analyze_transcript_chunk
from agents.transcript_processor import process_full_transcript
from agents.knowledge_base import KnowledgeBase

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Initialize orchestrator and knowledge base
orchestrator = Orchestrator()
kb = KnowledgeBase()

# In-memory live session store (keyed by socket session id)
live_sessions = {}


# ── Static Routes ─────────────────────────────────────

@app.route("/")
def index():
    """Serve the main frontend page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/live")
def live_page():
    """Serve the live coaching overlay page."""
    return send_from_directory(app.static_folder, "live.html")


# ── REST API ──────────────────────────────────────────

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


@app.route("/api/process-transcript", methods=["POST"])
def process_transcript():
    """
    Process a full interview transcript and optionally save to KB.
    Expects JSON: { "transcript": "...", "company_name": "...", "role": "...", "save_to_kb": true }
    """
    try:
        data = request.get_json(force=True)
        transcript = data.get("transcript", "").strip()
        company_name = data.get("company_name", "").strip()
        role = data.get("role", "").strip()
        save_to_kb = data.get("save_to_kb", False)

        if not transcript:
            return jsonify({"error": "Transcript text is required"}), 400
        if not company_name:
            return jsonify({"error": "Company name is required"}), 400
        if not role:
            return jsonify({"error": "Role is required"}), 400

        # Process the transcript
        result = process_full_transcript(transcript, company_name, role)

        # Optionally save to knowledge base
        if save_to_kb:
            kb.save_transcript_insights(company_name, role, result)
            result["saved_to_kb"] = True

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 502
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Business Intelligence Assist",
        "version": "3.0.0",
        "agents": ["CompanyIntelAgent", "InterviewAgent", "LiveCoachAgent", "TranscriptProcessor"],
        "features": ["live_coaching", "post_interview_processing"]
    }), 200


# ── Socket.IO Events ─────────────────────────────────

@socketio.on("connect")
def handle_connect():
    """Client connected."""
    logging.info(f"[SocketIO] Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    """Client disconnected — clean up session."""
    sid = request.sid
    if sid in live_sessions:
        del live_sessions[sid]
    logging.info(f"[SocketIO] Client disconnected: {sid}")


@socketio.on("start_live_session")
def handle_start_session(data):
    """
    Start a live coaching session.
    Expects: { company_name, role, company_report (optional) }
    Immediately generates initial coaching insights if company data is available.
    """
    sid = request.sid
    company_name = data.get("company_name", "")
    role = data.get("role", "")
    company_report = data.get("company_report", {})

    live_sessions[sid] = {
        "company_name": company_name,
        "role": role,
        "company_report": company_report,
        "transcript": "",
        "chunk_count": 0
    }

    logging.info(f"[SocketIO] Live session started for '{company_name}' / '{role}' (sid={sid})")
    logging.info(f"[SocketIO] Company report keys: {list(company_report.keys()) if company_report else 'empty'}")
    emit("session_started", {
        "status": "active",
        "company_name": company_name,
        "role": role
    })

    # Generate initial coaching insights from company data
    if company_report:
        try:
            logging.info(f"[SocketIO] Generating initial coaching insights for '{company_name}'")
            initial_prompt = f"The interview with {role} at {company_name} is about to begin. Based on the company intelligence, provide initial coaching guidance — key things to watch for and discuss."
            result = analyze_transcript_chunk(
                company_context=company_report,
                transcript_history="",
                latest_chunk=initial_prompt
            )
            emit("coaching_update", {
                "top_insights": result.get("top_insights", []),
                "talking_points": result.get("talking_points", []),
                "red_flags_opportunities": result.get("red_flags_opportunities", []),
                "chunk_number": 0
            })
            logging.info(f"[SocketIO] Initial coaching insights sent for '{company_name}'")
        except Exception as e:
            logging.error(f"[SocketIO] Failed to generate initial insights: {str(e)}")
            traceback.print_exc()
            emit("coaching_error", {"message": f"Could not generate initial insights: {str(e)}"})


@socketio.on("transcript_chunk")
def handle_transcript_chunk(data):
    """
    Receive a transcript chunk and return coaching updates.
    Expects: { text: "..." }
    """
    sid = request.sid
    session = live_sessions.get(sid)

    if not session:
        emit("error", {"message": "No active session. Please start a session first."})
        return

    chunk_text = data.get("text", "").strip()
    if not chunk_text:
        return

    # Accumulate transcript
    session["transcript"] += f"\n{chunk_text}"
    session["chunk_count"] += 1

    try:
        # Run live coach analysis
        result = analyze_transcript_chunk(
            company_context=session["company_report"],
            transcript_history=session["transcript"],
            latest_chunk=chunk_text
        )

        emit("coaching_update", {
            "top_insights": result.get("top_insights", []),
            "talking_points": result.get("talking_points", []),
            "red_flags_opportunities": result.get("red_flags_opportunities", []),
            "chunk_number": session["chunk_count"]
        })

    except Exception as e:
        logging.error(f"[SocketIO] Live coaching error: {str(e)}")
        traceback.print_exc()
        emit("coaching_error", {"message": f"Could not process transcript chunk: {str(e)}"})


@socketio.on("end_session")
def handle_end_session():
    """End the live coaching session and return summary."""
    sid = request.sid
    session = live_sessions.get(sid)

    if not session:
        emit("error", {"message": "No active session."})
        return

    summary = {
        "company_name": session["company_name"],
        "role": session["role"],
        "total_chunks": session["chunk_count"],
        "full_transcript": session["transcript"].strip(),
        "status": "ended"
    }

    # Clean up
    del live_sessions[sid]

    logging.info(f"[SocketIO] Session ended — {session['chunk_count']} chunks processed")
    emit("session_ended", summary)


# ── Zoom CC API Template (placeholder for future integration) ─────

# TODO: Zoom RTMS Webhook integration
# When the Zoom RTMS SDK or webhook events are available:
# 1. Add a webhook endpoint: POST /api/zoom/webhook
# 2. Verify the Zoom webhook signature
# 3. Handle 'meeting.transcript' events
# 4. Forward transcript data to the appropriate live session via SocketIO
#
# @app.route("/api/zoom/webhook", methods=["POST"])
# def zoom_webhook():
#     """Handle Zoom RTMS webhook events for live transcript."""
#     # Verify webhook signature
#     # Parse transcript event
#     # Forward to SocketIO session
#     pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"\n🔷 Business Intelligence Assist v3.0 running at http://localhost:{port}\n")
    print(f"   Agents: CompanyIntelAgent → InterviewAgent → LiveCoachAgent")
    print(f"   Features: Pre-Interview Prep | Live Coaching | Post-Interview Processing")
    print(f"   Knowledge Bases: Company Directory, Search Service, Interview History\n")
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
