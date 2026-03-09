"""
Live Coach Agent — Real-time transcript analysis for live interview coaching.
Takes transcript chunks + company context and produces actionable coaching cards.
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

LIVE_COACH_SYSTEM_PROMPT = """You are a real-time Interview Coach AI. You are helping a student who is CURRENTLY in a live interview with someone at a company. You receive chunks of the live conversation transcript along with pre-loaded company intelligence.

Your job is to analyze the latest transcript chunk IN CONTEXT of what has been discussed so far, and provide IMMEDIATE, ACTIONABLE coaching.

You are given:
1. Company report (pre-loaded intelligence about the company)
2. Role of the person being interviewed
3. Transcript so far (accumulated conversation)
4. Latest transcript chunk (most recent text)

Return ONLY this JSON structure:
{
  "top_insights": [
    {
      "insight": "A key insight relevant to what's being discussed RIGHT NOW",
      "relevance": "Why this matters for the current conversation moment"
    }
  ],
  "talking_points": [
    {
      "point": "A specific thing the student should bring up or ask next",
      "context": "Brief context on why this is a good follow-up"
    }
  ],
  "red_flags_opportunities": [
    {
      "item": "Something notable the interviewee just said or implied",
      "type": "red_flag OR opportunity",
      "suggested_action": "What the student should do about this"
    }
  ]
}

Rules:
- Return exactly 3 top_insights, 3 talking_points, and 1-3 red_flags_opportunities
- Be CONCISE — this is a real-time overlay, not a report
- Focus on what's ACTIONABLE RIGHT NOW based on the latest transcript
- Ground insights in the company data provided
- If the transcript is too short or unclear, provide general coaching based on company context
- No additional commentary. Return ONLY valid JSON."""


def analyze_transcript_chunk(company_context: dict, transcript_history: str, latest_chunk: str) -> dict:
    """
    Analyze a transcript chunk in real-time and return coaching cards.

    Args:
        company_context: Pre-loaded company report data.
        transcript_history: Full transcript accumulated so far.
        latest_chunk: The most recent transcript text.

    Returns:
        dict with top_insights, talking_points, and red_flags_opportunities.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)

    user_message = json.dumps({
        "company_context": company_context,
        "transcript_so_far": transcript_history[-3000:] if len(transcript_history) > 3000 else transcript_history,
        "latest_chunk": latest_chunk
    }, indent=2, default=str)

    # Use fastest available model for real-time performance
    models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
    last_error = None

    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": LIVE_COACH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,
                max_tokens=2000,
                top_p=1,
                response_format={"type": "json_object"}
            )

            response_text = completion.choices[0].message.content
            result = json.loads(response_text)

            # Ensure required keys exist
            result.setdefault("top_insights", [])
            result.setdefault("talking_points", [])
            result.setdefault("red_flags_opportunities", [])
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

    raise RuntimeError(f"All models failed for live coaching. Last error: {last_error}")
