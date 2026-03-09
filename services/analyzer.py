"""
Groq LLM-based company analyzer.
Generates insight-focused intelligence reports — prioritizing non-obvious, AI-synthesized insights
that a student interviewer wouldn't find by just Googling.
"""

import json
import os
import re
from groq import Groq

SYSTEM_PROMPT = """You are an AI-powered Company Intelligence Analyst helping a student prepare to INTERVIEW someone at a company.

The student is NOT applying for a job — they are CONDUCTING an interview with a person who works at this company in a specific role. Your job is to give the student deep, non-obvious intelligence about the company so they can ask smart, informed questions during the interview.

You are given:
1. Company data from a business directory (may include financials, culture, challenges, products)
2. Web search results with recent news and context
3. The role of the person the student will interview

CRITICAL RULES:
- For factual company details (name, industry, size, founded, headquarters, what they do), you MUST use ONLY the data provided in the business directory entry or web search results. DO NOT make up or guess any factual details.
- If a factual field is not available in the provided data, return "Not available" for that field.
- NEVER fabricate founding years, employee counts, headquarters locations, or product descriptions.
- AVOID stating things anyone can find with a quick Google search (e.g., "Google is a search engine")
- FOCUS on hidden patterns, strategic implications, and cross-referenced insights
- Surface non-obvious connections between company developments, market dynamics, and the specific role
- Provide actionable talking points the student can use to sound well-informed
- Identify red flags and opportunities worth probing during the interview
- Be concise — quality over quantity

Return ONLY this JSON structure:
{
  "company_name": "",
  "company_snapshot": {
    "what_they_do": "One-line description focusing on what matters, not obvious facts — use ONLY provided data",
    "industry": "From provided data only",
    "size": "e.g. 180K employees — from provided data only, or 'Not available'",
    "founded": "From provided data only, or 'Not available'",
    "headquarters": "From provided data only, or 'Not available'"
  },
  "hidden_insights": [
    {
      "insight": "Non-obvious AI-synthesized insight the student couldn't easily find",
      "significance": "Why this matters and how to use it in the interview"
    }
  ],
  "talking_points": [
    "Specific things the student can mention to sound impressively well-prepared (not generic)"
  ],
  "red_flags_opportunities": [
    {
      "item": "Something worth probing deeper during the interview",
      "type": "red_flag OR opportunity",
      "probe_question": "A specific follow-up question to ask about this"
    }
  ],
  "analysis_confidence": "Low/Medium/High"
}

Generate 5-7 hidden insights, 4-6 talking points, and 3-5 red flags/opportunities.
No additional commentary. Return ONLY valid JSON."""


def analyze_company(company_data: dict) -> dict:
    """
    Send company data to Groq LLM and return insight-focused analysis.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)

    user_message = json.dumps(company_data, indent=2, default=str)

    models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
    last_error = None

    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=5000,
                top_p=1,
                response_format={"type": "json_object"}
            )

            response_text = completion.choices[0].message.content
            result = json.loads(response_text)

            required_keys = ["company_name", "company_snapshot", "hidden_insights",
                             "talking_points", "red_flags_opportunities"]
            for key in required_keys:
                if key not in result:
                    result[key] = "Analysis unavailable"

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

    raise RuntimeError(f"All models failed. Last error: {last_error}")
