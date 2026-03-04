"""
Base Agent — Abstract base class for all agents in the orchestration pipeline.
Provides structured logging, execution timing, and error handling.
"""

import time
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base agent with timing, logging, and error wrapping."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, context: dict) -> dict:
        """
        Execute the agent's task.

        Args:
            context: Shared context dict with inputs and accumulated data.

        Returns:
            dict with the agent's output, merged into the pipeline context.
        """
        raise NotImplementedError

    def run(self, context: dict) -> dict:
        """
        Run the agent with timing and error handling.
        Wraps execute() with structured logging and exception capture.
        """
        logger.info(f"[{self.name}] Starting — {self.description}")
        start = time.time()

        try:
            result = self.execute(context)
            elapsed = round(time.time() - start, 2)
            logger.info(f"[{self.name}] Completed in {elapsed}s")
            result["_agent_meta"] = {
                "agent": self.name,
                "status": "success",
                "elapsed_seconds": elapsed
            }
            return result

        except Exception as e:
            elapsed = round(time.time() - start, 2)
            logger.error(f"[{self.name}] Failed after {elapsed}s — {str(e)}")
            return {
                "_agent_meta": {
                    "agent": self.name,
                    "status": "error",
                    "elapsed_seconds": elapsed,
                    "error": str(e)
                }
            }
