"""
Interview Coach Agent — Generates questions a STUDENT should ASK during an interview.

Use case: The student needs to interview a person at company X with role Y.
This agent generates smart, research-backed questions the student can ask,
along with what the interviewee is likely to answer.
"""

import json
import os
import re
import logging
from agents.base_agent import BaseAgent
from agents.knowledge_base import KnowledgeBase
from services.search import search_role_context
from groq import Groq

logger = logging.getLogger(__name__)

INTERVIEW_SYSTEM_PROMPT = """You are an expert Interview Coach helping a STUDENT prepare to interview someone.

IMPORTANT CONTEXT:
- The student is NOT the interviewee — the student IS the interviewer
- The student needs to interview a professional at a specific company in a specific role
- Your job is to generate smart, insightful questions the student should ASK the interviewee
- Questions should make the student sound well-researched, thoughtful, and impressive
- Expected answers are what the interviewee is LIKELY to respond with

You are given:
1. Company intelligence data (overview, products, culture, challenges, insights)
2. The role of the PERSON BEING INTERVIEWED (not the student)
3. Role-specific context from web research
4. Previously asked questions (to avoid repetition)

Generate 10-12 questions the student should ASK, following these rules:
- Questions should be smart, probing, and show the student did deep research
- Questions should extract valuable information and insights from the interviewee
- Cover three categories:
  1. "role_specific" — Questions about their day-to-day work, responsibilities, challenges in this role
  2. "strategic" — Questions about company direction, industry trends, strategic decisions
  3. "culture_insight" — Questions that reveal what it's really like to work there (culture, team dynamics, growth)
- Each question should have a difficulty: "easy" (safe opener), "medium" (shows research), "hard" (deeply insightful, might surprise them)
- Expected answers should be 2-4 sentences of what the interviewee would likely say
- Include a "why_ask_this" field explaining what intel or value the student gains from asking this
- Do NOT repeat any questions from the "previously_asked" list
- Questions should feel like they come from a well-prepared journalism/business student who deeply understands the company

Return ONLY this JSON structure:
{
  "interview_questions": [
    {
      "question": "Question the student ASKS the interviewee",
      "expected_answer": "What the interviewee would likely respond with",
      "category": "role_specific|strategic|culture_insight",
      "difficulty": "easy|medium|hard",
      "why_ask_this": "What the student gains from asking this question"
    }
  ],
  "coaching_tips": [
    "5-7 tips for the student on HOW to conduct the interview well (body language, follow-ups, active listening, etc.)"
  ]
}

No additional commentary. Return ONLY valid JSON."""


class InterviewAgent(BaseAgent):
    """
    Agent responsible for generating questions a student should ASK during an interview.

    Knowledge bases used:
        1. Company Intelligence — from CompanyIntelAgent output
        2. Search Service — role-specific web search
        3. Previous Interview Questions — from KnowledgeBase
    """

    def __init__(self):
        super().__init__(
            name="InterviewAgent",
            description="Generates smart interview questions for a student to ASK a professional"
        )
        self.knowledge_base = KnowledgeBase()

    def execute(self, context: dict) -> dict:
        """
        Generate interview questions the student should ask.

        Args:
            context: Must contain 'company_name', 'role', and 'company_report'.

        Returns:
            dict with 'interview_questions' and 'coaching_tips'.
        """
        company_name = context.get("company_name", "")
        role = context.get("role", "")
        company_report = context.get("company_report", {})
        search_data = context.get("search_data", {})

        if not company_name or not role:
            raise ValueError("company_name and role are required in context")

        # Knowledge Base 1: Previous interview questions
        previous_questions = self.knowledge_base.get_previous_questions(
            company_name, role
        )

        # Knowledge Base 2: Role-specific search context
        logger.info(f"[InterviewAgent] Searching role context: {role} at {company_name}")
        role_context = search_role_context(company_name, role)

        # Build the LLM prompt payload
        prompt_data = {
            "company_name": company_name,
            "role_being_interviewed": role,
            "context": "A student is preparing to interview a professional in this role at this company. Generate questions the STUDENT should ASK.",
            "company_intelligence": {
                "snapshot": company_report.get("company_snapshot", {}),
                "hidden_insights": company_report.get("hidden_insights", []),
                "talking_points": company_report.get("talking_points", []),
                "red_flags_opportunities": company_report.get("red_flags_opportunities", [])
            },
            "role_search_context": role_context,
            "company_search_snippets": search_data.get("google_results", [])[:10],
            "previously_asked": [
                q.get("question", "") for q in previous_questions
            ][:20]
        }

        # Call LLM
        result = self._generate_questions(prompt_data)

        # Persist new questions to knowledge base
        questions = result.get("interview_questions", [])
        self.knowledge_base.save_questions(company_name, role, questions)

        return result

    def _generate_questions(self, prompt_data: dict) -> dict:
        """Call Groq LLM with the interview prompt."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        client = Groq(api_key=api_key)
        user_message = json.dumps(prompt_data, indent=2, default=str)

        models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
        last_error = None

        for model in models:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": INTERVIEW_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=6000,
                    top_p=0.9,
                    response_format={"type": "json_object"}
                )

                response_text = completion.choices[0].message.content
                result = json.loads(response_text)

                if "interview_questions" not in result:
                    result["interview_questions"] = []
                if "coaching_tips" not in result:
                    result["coaching_tips"] = []

                result["_model_used"] = model
                return result

            except json.JSONDecodeError:
                try:
                    json_match = re.search(r'\{[\s\S]*\}', response_text)
                    if json_match:
                        result = json.loads(json_match.group())
                        result["_model_used"] = model
                        return result
                except Exception:
                    pass
                last_error = f"Invalid JSON from model {model}"
                continue

            except Exception as e:
                last_error = str(e)
                continue

        raise RuntimeError(f"Interview question generation failed. Last error: {last_error}")
