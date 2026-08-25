"""
BevHub AI — BaseAgent v2
Production-grade abstract base for all AI specialists.

Every agent now:
- Receives the full reasoning context from ReasoningEngine
- Logs execution with structured metadata
- Has automatic retry with exponential backoff
- Returns a typed AgentOutput instead of raw dict
- Reads its system prompt from the markdown spec files
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from core.services.ai_router import AIRouterService

logger = logging.getLogger(__name__)

_PROMPT_CACHE: dict[int, str] = {}


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT MODEL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentOutput:
    """Typed output from any specialist agent."""
    agent_id:    str
    success:     bool
    data:        dict = field(default_factory=dict)
    reasoning:   str  = ""          # what the agent decided and why
    warnings:    list = field(default_factory=list)
    error:       Optional[str] = None
    provider:    str  = ""
    duration_ms: int  = 0


# ─────────────────────────────────────────────────────────────────────────────
# BASE AGENT
# ─────────────────────────────────────────────────────────────────────────────

class BaseAgent(ABC):
    """
    Abstract base class for all BevHub AI specialist agents.

    Subclasses must implement:
        agent_id  (property) – unique slug, e.g. "cto_agent"
        system_prompt_part   – which SYSTEM_PROMPT_PART_xx.md to load
        task_type            – routing key for AIRouterService
        run()                – core logic, returns AgentOutput
    """

    MAX_RETRIES   = 2
    RETRY_DELAY_S = 1.0

    def __init__(self):
        self.router = AIRouterService()
        self._log_entries: list[str] = []

    # ── identity ──────────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique identifier, e.g. 'cto_agent'."""

    @property
    def system_prompt_part(self) -> int:
        """Override in subclass to load the correct SYSTEM_PROMPT_PART_xx.md."""
        return 1

    @property
    def task_type(self) -> str:
        """Override to select the correct provider routing key."""
        return "copywriting_text"

    # ── core contract ─────────────────────────────────────────────────────────

    @abstractmethod
    def run(self, context: dict, prompt: str) -> AgentOutput:
        """Execute the agent's primary capability. Must return AgentOutput."""

    # ── execution with retry ──────────────────────────────────────────────────

    def execute(self, context: dict, prompt: str) -> AgentOutput:
        """
        Public entry point. Wraps run() with retry logic and timing.
        Orchestrator calls this instead of run() directly.
        """
        start = time.monotonic()
        last_error: Optional[str] = None

        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                output = self.run(context, prompt)
                output.duration_ms = int((time.monotonic() - start) * 1000)
                logger.info(
                    "[%s] Completed in %dms (attempt %d)",
                    self.agent_id, output.duration_ms, attempt
                )
                return output
            except Exception as exc:
                last_error = str(exc)
                logger.warning(
                    "[%s] Attempt %d/%d failed: %s",
                    self.agent_id, attempt, self.MAX_RETRIES + 1, exc
                )
                if attempt <= self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY_S * attempt)

        # All retries exhausted — return graceful fallback
        return AgentOutput(
            agent_id=self.agent_id,
            success=False,
            error=last_error,
            duration_ms=int((time.monotonic() - start) * 1000),
            warnings=[f"All {self.MAX_RETRIES + 1} attempts failed."],
        )

    # ── system prompt loader ──────────────────────────────────────────────────

    def get_system_instruction(self, part_number: int | None = None) -> str:
        """
        Load SYSTEM_PROMPT_PART_xx.md from the project root.
        Results are cached in-process to avoid repeated disk reads.
        """
        if part_number is not None:
            part = part_number
        elif hasattr(self, 'active_part_number') and self.active_part_number is not None:
            part = self.active_part_number
        else:
            part = self.system_prompt_part

        if part in _PROMPT_CACHE:
            return _PROMPT_CACHE[part]

        try:
            from django.conf import settings
            root = settings.BASE_DIR.parent
            filepath = os.path.join(root, f"SYSTEM_PROMPT_PART_{part:02d}.md")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                _PROMPT_CACHE[part] = content
                return content
        except Exception as exc:
            logger.warning("[BaseAgent] Could not load Part %d: %s", part, exc)

        fallback = f"You are a world-class AI specialist (Part {part})."
        _PROMPT_CACHE[part] = fallback
        return fallback

    # ── reasoning context helper ──────────────────────────────────────────────

    def get_reasoning_context(self, context: dict) -> str:
        """
        Extract a formatted string of the ReasoningEngine's decision so the
        agent can incorporate it into its system prompt / user message.
        """
        r = context.get("reasoning", {})
        if not r:
            return ""
        return (
            f"\n\n=== REASONING ENGINE CONTEXT ===\n"
            f"Request class : {r.get('request_class', 'unknown')}\n"
            f"Thinking mode : {r.get('thinking_mode', 'analytical')}\n"
            f"Complexity    : {r.get('complexity', 'medium')}\n"
            f"Best approach : {r.get('chosen_approach', 'production-grade standard')}\n"
            f"Confidence    : {r.get('confidence', 0):.1f}/10\n"
            f"Risks         : {'; '.join(r.get('risks', []))}\n"
            f"================================\n"
        )

    # ── provider helper ───────────────────────────────────────────────────────

    def call_llm(
        self,
        prompt: str,
        system_instruction: str | None = None,
        task_type: str | None = None,
    ) -> str:
        """
        Single-call helper: selects provider, calls generate_text, returns text.
        Falls back to empty string on any error (subclass should handle).
        """
        chosen_task = task_type or self.task_type
        provider_name = self.router.select_best_provider_for_task(chosen_task)
        provider = self.router.get_provider(provider_name)
        result = provider.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
        )
        return result.text, provider_name
