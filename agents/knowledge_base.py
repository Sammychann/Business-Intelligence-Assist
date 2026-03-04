"""
Knowledge Base Manager — Manages persistent storage of interview Q&A history.
Acts as the 'Previous Interview Questions' knowledge source for the agentic pipeline.
"""

import os
import json
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Persistent storage path
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "interview_history.json"


class KnowledgeBase:
    """
    Manages interview question history indexed by (company, role).
    Provides retrieval of previous questions and persistence of new ones.
    """

    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        """Create data directory and history file if they don't exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not HISTORY_FILE.exists():
            HISTORY_FILE.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        """Load the full history from disk."""
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save(self, data: dict):
        """Persist history to disk."""
        HISTORY_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    @staticmethod
    def _key(company: str, role: str) -> str:
        """Generate a normalized key from company + role."""
        return f"{company.strip().lower()}|{role.strip().lower()}"

    def get_previous_questions(self, company: str, role: str) -> list[dict]:
        """
        Retrieve previously generated questions for a company + role pair.

        Returns:
            List of question dicts from past sessions (may be empty).
        """
        history = self._load()
        key = self._key(company, role)
        entries = history.get(key, [])

        # Flatten all questions from all sessions
        all_questions = []
        for entry in entries:
            all_questions.extend(entry.get("questions", []))

        logger.info(
            f"[KnowledgeBase] Found {len(all_questions)} previous questions "
            f"for '{company}' / '{role}'"
        )
        return all_questions

    def save_questions(self, company: str, role: str, questions: list[dict]):
        """
        Persist newly generated questions for future reference.
        Appends to the session list for the company+role key.
        """
        if not questions:
            return

        history = self._load()
        key = self._key(company, role)

        if key not in history:
            history[key] = []

        # Deduplicate — don't save questions whose text already exists
        existing_texts = set()
        for entry in history[key]:
            for q in entry.get("questions", []):
                existing_texts.add(q.get("question", "").strip().lower())

        new_questions = [
            q for q in questions
            if q.get("question", "").strip().lower() not in existing_texts
        ]

        if new_questions:
            from datetime import datetime
            history[key].append({
                "timestamp": datetime.now().isoformat(),
                "questions": new_questions
            })
            self._save(history)
            logger.info(
                f"[KnowledgeBase] Saved {len(new_questions)} new questions "
                f"for '{company}' / '{role}'"
            )

    def get_all_company_data(self, company: str) -> list[dict]:
        """
        Retrieve all questions ever generated for a company (any role).
        Useful for building broader company context.
        """
        history = self._load()
        prefix = f"{company.strip().lower()}|"
        all_questions = []

        for key, entries in history.items():
            if key.startswith(prefix):
                for entry in entries:
                    all_questions.extend(entry.get("questions", []))

        return all_questions
