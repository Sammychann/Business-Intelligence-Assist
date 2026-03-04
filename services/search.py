"""
DuckDuckGo-based company search service.
Gathers public snippets and structured data about a company.
"""

import re
import json
from duckduckgo_search import DDGS


def search_company(company_name: str) -> dict:
    """
    Search for company information using DuckDuckGo.
    Returns structured data and raw snippets.
    """
    structured_data = {
        "industry": "",
        "headquarters": "",
        "founded": "",
        "ceo": "",
        "revenue": "",
        "employees": "",
        "funding": "",
        "website": "",
        "description": "",
        "products_services": [],
        "competitors": [],
        "recent_news": []
    }
    google_results = []

    try:
        with DDGS() as ddgs:
            # Main company search
            results = list(ddgs.text(f"{company_name} company overview", max_results=8))
            for r in results:
                snippet = r.get("body", "")
                if snippet:
                    google_results.append(snippet)
                # Try to extract website
                href = r.get("href", "")
                if not structured_data["website"] and href and company_name.lower().replace(" ", "") in href.lower():
                    structured_data["website"] = href

            # Search for financial / employee info
            fin_results = list(ddgs.text(f"{company_name} revenue employees funding", max_results=5))
            for r in fin_results:
                snippet = r.get("body", "")
                if snippet:
                    google_results.append(snippet)

            # Search for recent news
            try:
                news_results = list(ddgs.news(f"{company_name}", max_results=5))
                for n in news_results:
                    title = n.get("title", "")
                    body = n.get("body", "")
                    if title:
                        structured_data["recent_news"].append(title)
                        if body:
                            google_results.append(f"[News] {title}: {body}")
            except Exception:
                pass

            # Search for competitors
            comp_results = list(ddgs.text(f"{company_name} competitors alternatives", max_results=3))
            for r in comp_results:
                snippet = r.get("body", "")
                if snippet:
                    google_results.append(snippet)

        # Try to extract structured fields from snippets
        all_text = " ".join(google_results)
        structured_data["description"] = _extract_description(all_text, company_name)
        structured_data["industry"] = _extract_field(all_text, ["industry", "sector", "market"])
        structured_data["headquarters"] = _extract_field(all_text, ["headquartered", "headquarters", "based in", "located in"])
        structured_data["founded"] = _extract_founded(all_text)
        structured_data["ceo"] = _extract_field(all_text, ["CEO", "chief executive"])
        structured_data["revenue"] = _extract_field(all_text, ["revenue", "sales", "annual revenue"])
        structured_data["employees"] = _extract_field(all_text, ["employees", "workforce", "team of"])

    except Exception as e:
        google_results.append(f"Search encountered an error: {str(e)}")

    # Deduplicate snippets
    seen = set()
    unique_results = []
    for s in google_results:
        normalized = s.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_results.append(s)

    return {
        "company_name": company_name,
        "structured_data": structured_data,
        "google_results": unique_results[:20]  # Cap at 20 snippets
    }


def _extract_description(text: str, company_name: str) -> str:
    """Extract a short description from the search results."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        if company_name.lower() in s.lower() and 20 < len(s) < 300:
            return s.strip()
    return ""


def _extract_field(text: str, keywords: list) -> str:
    """Try to extract a field value near a keyword."""
    for keyword in keywords:
        pattern = rf'{keyword}[:\s]+([^.;,\n]{{3,80}})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def _extract_founded(text: str) -> str:
    """Extract founding year."""
    patterns = [
        r'founded\s+(?:in\s+)?(\d{4})',
        r'established\s+(?:in\s+)?(\d{4})',
        r'since\s+(\d{4})'
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def search_role_context(company_name: str, role: str) -> list[str]:
    """
    Search for role-specific context at a company.
    Returns a list of relevant snippets about the role, interview culture, etc.
    """
    snippets = []

    queries = [
        f"{company_name} {role} interview questions",
        f"{company_name} {role} responsibilities",
        f"{company_name} engineering culture work environment",
    ]

    try:
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = list(ddgs.text(query, max_results=4))
                    for r in results:
                        snippet = r.get("body", "")
                        if snippet:
                            snippets.append(snippet)
                except Exception:
                    continue
    except Exception as e:
        snippets.append(f"Role context search error: {str(e)}")

    # Deduplicate
    seen = set()
    unique = []
    for s in snippets:
        normalized = s.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(s)

    return unique[:15]
