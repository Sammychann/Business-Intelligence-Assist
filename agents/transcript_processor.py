"""
Transcript Processor — Post-interview full transcript analysis.
Processes a complete interview transcript into structured insights for KB storage.
"""

import json
import os
import re
import logging
from groq import Groq

logger = logging.getLogger(__name__)

TRANSCRIPT_PROCESSOR_PROMPT = """You are a Post-Interview Analyst AI. You are given the full transcript of an interview that a student conducted with a professional at a company. Your job is to extract structured insights from the conversation.

You are given:
1. The full interview transcript
2. Company name and role of the person interviewed

Analyze the transcript and return ONLY this JSON structure:
{
  "summary": "A 2-3 sentence executive summary of the interview",
  "key_insights": [
    {
      "insight": "An important piece of information or perspective shared",
      "source_quote": "Brief quote or paraphrase from the transcript",
      "category": "industry_insight | company_culture | role_specific | career_advice | technical | strategic"
    }
  ],
  "notable_quotes": [
    {
      "quote": "A memorable or significant quote from the interviewee",
      "context": "Brief context for why this quote matters"
    }
  ],
  "follow_up_items": [
    "Specific follow-up actions, questions to research, or people to reach out to"
  ],
  "topics_discussed": ["List of main topics covered in the interview"],
  "interview_quality_score": "1-10 rating based on depth and quality of information gathered",
  "improvement_suggestions": [
    "Suggestions for how the student could improve their interviewing technique"
  ]
}

Rules:
- Extract 5-8 key insights
- Include 3-5 notable quotes
- List 3-5 follow-up items
- Be factual — only include what was actually discussed
- If the transcript is very short or unclear, note that in the summary
- No additional commentary. Return ONLY valid JSON."""


def process_full_transcript(transcript: str, company_name: str, role: str) -> dict:
    """
    Process a full interview transcript into structured insights.

    Args:
        transcript: The complete interview transcript text.
        company_name: Name of the company discussed.
        role: Role of the person who was interviewed.

    Returns:
        dict with structured insights ready for KB storage.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)

    user_message = json.dumps({
        "company": company_name,
        "role": role,
        "transcript": transcript
    }, indent=2, default=str)

    models = ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"]
    last_error = None

    for model in models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": TRANSCRIPT_PROCESSOR_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=4000,
                top_p=0.9,
                response_format={"type": "json_object"}
            )

            response_text = completion.choices[0].message.content
            result = json.loads(response_text)

            # Ensure required keys
            result.setdefault("summary", "")
            result.setdefault("key_insights", [])
            result.setdefault("notable_quotes", [])
            result.setdefault("follow_up_items", [])
            result.setdefault("topics_discussed", [])
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

    raise RuntimeError(f"All models failed for transcript processing. Last error: {last_error}")
