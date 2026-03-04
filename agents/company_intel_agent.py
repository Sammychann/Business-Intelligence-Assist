"""
Company Intelligence Agent — Gathers company data and generates insight-focused intelligence.
Uses business directory as primary knowledge base, supplemented by web search.
"""

import json
import logging
import os
from agents.base_agent import BaseAgent
from services.search import search_company
from services.analyzer import analyze_company

logger = logging.getLogger(__name__)

BUSINESS_DIRECTORY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "business_directory.json"
)


class CompanyIntelAgent(BaseAgent):
    """
    Agent responsible for gathering and analyzing company intelligence.

    Knowledge bases used:
        1. Business Directory — curated local company data (primary)
        2. Company Directory — DuckDuckGo search (supplementary)
        3. Search Service — financial, news, and competitor queries
    """

    def __init__(self):
        super().__init__(
            name="CompanyIntelAgent",
            description="Gathers company intelligence from business directory and web search"
        )
        self._directory = None

    def _load_directory(self):
        """Load the business directory JSON file."""
        if self._directory is not None:
            return self._directory

        try:
            with open(BUSINESS_DIRECTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._directory = data.get("companies", [])
                logger.info(f"[CompanyIntelAgent] Loaded business directory with {len(self._directory)} companies")
        except FileNotFoundError:
            logger.warning("[CompanyIntelAgent] Business directory not found, using web search only")
            self._directory = []
        except Exception as e:
            logger.error(f"[CompanyIntelAgent] Error loading directory: {e}")
            self._directory = []

        return self._directory

    def _lookup_company(self, company_name: str) -> dict:
        """Look up a company in the business directory (case-insensitive, fuzzy match)."""
        directory = self._load_directory()
        name_lower = company_name.lower().strip()

        for company in directory:
            # Exact match on name
            if company.get("name", "").lower() == name_lower:
                return company

            # Match on also_known_as
            aliases = [a.lower() for a in company.get("also_known_as", [])]
            if name_lower in aliases:
                return company

            # Partial match (company name contained in search)
            if name_lower in company.get("name", "").lower():
                return company

        return {}

    def execute(self, context: dict) -> dict:
        """
        Gather company data and produce insight-focused intelligence.

        Args:
            context: Must contain 'company_name' and optionally 'role'.

        Returns:
            dict with company intelligence report.
        """
        company_name = context.get("company_name", "")
        role = context.get("role", "")

        if not company_name:
            raise ValueError("company_name is required in context")

        # Knowledge Base 1: Business Directory (local)
        directory_data = self._lookup_company(company_name)
        if directory_data:
            logger.info(f"[CompanyIntelAgent] Found '{company_name}' in business directory")
        else:
            logger.info(f"[CompanyIntelAgent] '{company_name}' not in directory, using web search only")

        # Knowledge Base 2: Web search (always supplement with fresh data)
        logger.info(f"[CompanyIntelAgent] Running web search for '{company_name}'")
        search_data = search_company(company_name)

        # Merge directory data and search data for analysis
        combined_data = {
            "company_name": company_name,
            "role_being_interviewed": role,
            "business_directory_entry": directory_data,
            "web_search_results": search_data
        }

        # Run LLM analysis
        logger.info(f"[CompanyIntelAgent] Running AI analysis for '{company_name}'")
        report = analyze_company(combined_data)

        # Return both report and search data for downstream agents
        return {
            "report": report,
            "search_data": search_data,
            "from_directory": bool(directory_data)
        }
