"""Clarification evaluation — detects underspecified prompts to prevent ungrounded assumptions."""

import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.config import Settings, get_settings
from app.llm.client import get_structured_model
from app.logging_config import get_logger
from app.models.schemas import ClarificationItem

logger = get_logger(__name__)


class ClarificationAnalysisResult(BaseModel):
    """Structured assessment of whether a prompt requires missing details."""

    needs_clarification: bool = Field(
        description=(
            "True ONLY if the prompt is underspecified, vague, or missing essential details "
            "(e.g., what an announced product/package does, the core problem it solves, "
            "or target tech stack) such that generating a tweet would force inventing ungrounded assumptions."
        )
    )
    reason: str = Field(
        default="",
        description="Short, polite explanation of what missing details would make the tweet authentic.",
    )
    questions: list[ClarificationItem] = Field(
        default_factory=list,
        description="1 to 3 focused, quick-fill questions with helpful placeholder examples for the user.",
    )


CLARIFICATION_SYSTEM_PROMPT = """You are the Prompt Detail Analyzer for AI Tweet Studio.
Your role is to ensure tweets are authentic, high-impact, and grounded without inventing unrequested facts or hallucinating third-party details.

CRITICAL RULES:
1. If the user's prompt provides enough concrete detail to write a complete, truthful tweet (even a short one), set needs_clarification = False and questions = [].
2. Set needs_clarification = True ONLY if the prompt is open-ended or missing key core information:
   - For product/package/feature announcements where the name, purpose, or problem solved is completely unstated.
   - For vague requests like "tell others we will publish an open-source package" where the package's functionality is unknown.
3. When needs_clarification is True, generate 2 to 3 targeted, actionable questions:
   - Keep questions conversational and quick to answer.
   - Always include realistic, helpful placeholder examples.
   - Each question MUST have a distinct, unique snake_case 'key' (e.g., 'company_name', 'role', 'company_focus') and a unique 'id'.
   - Mark non-vital details (like GitHub URL, launch date) with optional = True.
"""

CLARIFICATION_USER_PROMPT = """Analyze the following user tweet prompt:

<user_prompt>
{user_query}
</user_prompt>

Determine if this prompt is underspecified and requires missing details, or if it has enough context to generate directly.
"""


def analyze_prompt_clarifications(
    user_query: str,
    settings: Settings | None = None,
    structured_model: Any | None = None,
) -> ClarificationAnalysisResult:
    """Analyze if a prompt needs user clarifications before drafting."""
    cfg = settings or get_settings()

    # Short-circuit if prompt is extremely detailed (e.g. contains code, urls, specs)
    if len(user_query.strip()) > 300 and ("http" in user_query or "\n" in user_query):
        return ClarificationAnalysisResult(needs_clarification=False, questions=[])

    try:
        model: Any = structured_model or get_structured_model(
            schema=ClarificationAnalysisResult,
            model_name=cfg.safety_model,
            temperature=0.0,
            settings=cfg,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", CLARIFICATION_SYSTEM_PROMPT),
            ("user", CLARIFICATION_USER_PROMPT),
        ])
        messages = prompt.format_messages(user_query=user_query)
        result: ClarificationAnalysisResult = model.invoke(messages)  # type: ignore[assignment]

        # Post-process: Guarantee each question has a distinct, sanitized non-empty key and id
        if result and result.questions:
            seen_keys: set[str] = set()
            for idx, q in enumerate(result.questions):
                raw_key = (q.key or q.id or f"detail_{idx + 1}").strip().lower().replace(" ", "_")
                clean_key = re.sub(r"[^a-z0-9_]", "", raw_key) or f"detail_{idx + 1}"
                unique_key = clean_key
                counter = 1
                while unique_key in seen_keys:
                    unique_key = f"{clean_key}_{counter}"
                    counter += 1
                seen_keys.add(unique_key)
                q.key = unique_key
                if not q.id:
                    q.id = f"q_{unique_key}"

        return result
    except Exception as exc:
        logger.warning("clarification_analysis_failed_open", error=str(exc))
        # Fail-open to allow direct generation if analyzer is unavailable
        return ClarificationAnalysisResult(needs_clarification=False, questions=[])
