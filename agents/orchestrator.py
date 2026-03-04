"""
Orchestrator — Central coordinator for the agentic AI pipeline.
Dispatches to specialized agents and merges results into a unified response.
"""

import time
import logging
from agents.company_intel_agent import CompanyIntelAgent
from agents.interview_agent import InterviewAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Agentic AI Orchestrator.

    Pipeline:
        1. CompanyIntelAgent — Gather company intelligence (company directory + search)
        2. InterviewAgent — Generate role-tailored interview questions (uses company data + KB)
        3. Merge — Combine results into unified response
    """

    def __init__(self):
        self.company_intel_agent = CompanyIntelAgent()
        self.interview_agent = InterviewAgent()

    def run(self, company_name: str, role: str) -> dict:
        """
        Execute the full agentic pipeline.

        Args:
            company_name: Name of the company to analyze.
            role: Role of the person being interviewed.

        Returns:
            Unified dict with company dashboard + interview questions.
        """
        pipeline_start = time.time()
        agent_trace = []

        logger.info(f"[Orchestrator] Starting pipeline: {company_name} / {role}")

        # ── Agent 1: Company Intelligence ─────────────────
        context = {"company_name": company_name, "role": role}

        intel_result = self.company_intel_agent.run(context)
        agent_trace.append(intel_result.get("_agent_meta", {}))

        # Extract company report into context for next agent
        company_report = intel_result.get("report", {})
        search_data = intel_result.get("search_data", {})
        context["company_report"] = company_report
        context["search_data"] = search_data

        # ── Agent 2: Interview Coach ──────────────────────
        interview_result = self.interview_agent.run(context)
        agent_trace.append(interview_result.get("_agent_meta", {}))

        # ── Merge Results ─────────────────────────────────
        pipeline_elapsed = round(time.time() - pipeline_start, 2)
        logger.info(f"[Orchestrator] Pipeline completed in {pipeline_elapsed}s")

        response = {
            # Company Intelligence Dashboard
            **company_report,

            # Interview Coach Section
            "interview_questions": interview_result.get("interview_questions", []),
            "coaching_tips": interview_result.get("coaching_tips", []),

            # Pipeline metadata
            "role_analyzed": role,
            "_pipeline": {
                "total_elapsed_seconds": pipeline_elapsed,
                "agent_trace": agent_trace
            }
        }

        return response
