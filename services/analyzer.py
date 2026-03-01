"""
Groq LLM-based company analyzer.
Sends structured company data to the LLM with the master prompt and returns a structured JSON report.
"""

import json
import os
from groq import Groq

SYSTEM_PROMPT = """You are an AI-powered Business Intelligence Analyst.

Your task is to generate structured, factual, and analytical company intelligence reports using:
1. Provided structured company data
2. Google search snippets
3. Publicly available information

You must:
- Avoid hallucinations
- Only use provided data + widely known public facts
- Clearly mark uncertainty
- Maintain professional tone
- Return strictly structured JSON
- Do not return markdown
- Do not add explanations outside JSON

If information is missing or contradictory, explicitly state "Insufficient Public Data" instead of inferring.

Given a company name and its knowledge base, generate:
1. Executive Summary (120-150 words covering business positioning, industry relevance, scale and maturity)
2. Financial Snapshot (revenue, revenue trend, employees, funding status, profitability status - mark unknown as "Not Public")
3. Business Model Analysis (core revenue streams, target customers, pricing model, distribution channels, monetization strategy)
4. Competitive Positioning (market category, key differentiators, competitive advantage, market maturity: Emerging/Growth/Established/Saturated)
5. SWOT Analysis (3-5 bullets each for strengths, weaknesses, opportunities, threats)
6. Market & Growth Outlook (industry growth trend, expansion potential, geographic opportunity, product diversification - classify as Low/Moderate/High/Aggressive)
7. Risk Assessment (regulatory/competitive/market/operational/financial risk as Low/Medium/High, overall_risk_score 1-10 where 1=Very Stable, 10=Extremely Risky)
8. AI / Technology Opportunities (where AI can improve operations, automation opportunities, predictive analytics use cases, cost reduction potential, innovation scope)
9. Key Structured Insights (5 crisp bullet strategic insights)
10. Confidence Score (Low/Medium/High based on completeness of input data)

Return ONLY this JSON structure:
{
  "company_name": "",
  "executive_summary": "",
  "financial_snapshot": {
    "revenue": "",
    "revenue_trend": "",
    "employees": "",
    "funding_status": "",
    "profitability_status": ""
  },
  "business_model_analysis": "",
  "competitive_positioning": {
    "market_category": "",
    "differentiation": "",
    "market_maturity": ""
  },
  "swot_analysis": {
    "strengths": [],
    "weaknesses": [],
    "opportunities": [],
    "threats": []
  },
  "market_growth_outlook": {
    "industry_trend": "",
    "growth_potential": "",
    "expansion_opportunities": ""
  },
  "risk_assessment": {
    "regulatory_risk": "",
    "competitive_risk": "",
    "market_risk": "",
    "operational_risk": "",
    "financial_risk": "",
    "overall_risk_score": 0
  },
  "ai_opportunities": [],
  "key_insights": [],
  "analysis_confidence": ""
}

No additional commentary. Return ONLY valid JSON."""


def analyze_company(company_data: dict) -> dict:
    """
    Send company data to Groq LLM and return structured analysis.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    client = Groq(api_key=api_key)

    user_message = json.dumps(company_data, indent=2, default=str)

    # Try primary model, fall back if needed
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
                temperature=0.2,
                max_tokens=6000,
                top_p=0.9,
                response_format={"type": "json_object"}
            )

            response_text = completion.choices[0].message.content
            result = json.loads(response_text)

            # Validate required keys
            required_keys = ["company_name", "executive_summary", "financial_snapshot",
                             "swot_analysis", "risk_assessment", "key_insights"]
            for key in required_keys:
                if key not in result:
                    result[key] = "Analysis unavailable"

            result["_model_used"] = model
            return result

        except json.JSONDecodeError:
            # Try to extract JSON from the response
            try:
                import re
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
