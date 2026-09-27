"""Tool Action Guardrails for safe tool execution and output sanitization."""

import re
from typing import Any

from pydantic import ValidationError

from app.logging_config import get_logger
from app.tools.schemas import SearchResult, WebSearchInput

logger = get_logger(__name__)

ALLOWED_TOOLS: set[str] = {"search_web", "web_search"}

# Regex patterns commonly used in prompt injection attacks via web snippets
INJECTION_SNIPPET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?system\s+prompt", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in\s+)?(DAN|developer)\s+mode", re.IGNORECASE),
    re.compile(r"<\s*system\s*>", re.IGNORECASE),
    re.compile(r"<\s*/\s*system\s*>", re.IGNORECASE),
]


class ToolGuardrailError(Exception):
    """Exception raised when a tool call violates guardrail policies."""


# ================== Tool Action Guardrails ====================
# ====== Validate tool name exists in the whitelist ======
def validate_tool_name(tool_name: str) -> str:
    """Validate that the requested tool is explicitly whitelisted.

    Args:
        tool_name: Name of the tool requested by LLM.

    Returns:
        Standardized tool name.

    Raises:
        ToolGuardrailError: If tool is not allowed.
    """
    normalized = tool_name.strip().lower()
    if normalized not in ALLOWED_TOOLS:
        logger.warning("unauthorized_tool_call_blocked", requested_tool=tool_name)
        raise ToolGuardrailError(
            f"Unauthorized tool execution attempted: '{tool_name}'. Allowed tools: {list(ALLOWED_TOOLS)}"
        )
    return normalized


# ====== Validate tool arguments (validate type, content, and length) ======
def validate_search_arguments(raw_args: dict[str, Any] | str) -> WebSearchInput:
    """Validate and sanitize search arguments against WebSearchInput schema.

    Args:
        raw_args: Raw arguments dictionary or query string from LLM tool call.

    Returns:
        Validated WebSearchInput instance.

    Raises:
        ToolGuardrailError: If arguments fail schema or safety checks.
    """
    query_val: Any
    if isinstance(raw_args, str):
        query_val = raw_args
    elif isinstance(raw_args, dict):
        if not raw_args:
            raise ToolGuardrailError("Search query argument is required")
        query_val = raw_args.get("query") or raw_args.get("q") or raw_args.get("search_query")
        if query_val is None:
            raise ToolGuardrailError("Search query argument is required")
    else:
        raise ToolGuardrailError(f"Invalid tool arguments format: {type(raw_args)}")

    cleaned_query = str(query_val).strip()
    if not cleaned_query:
        raise ToolGuardrailError("Search query cannot be empty")

    if len(cleaned_query) > 500:
        raise ToolGuardrailError(
            f"Search query exceeds maximum allowed length of 500 characters (got {len(cleaned_query)})"
        )

    # Check for prompt injection patterns inside tool arguments
    for pattern in INJECTION_SNIPPET_PATTERNS:
        if pattern.search(cleaned_query):
            logger.warning("adversarial_tool_arg_detected", pattern=pattern.pattern)
            raise ToolGuardrailError(f"Prohibited adversarial pattern in query: {pattern.pattern}")

    # Remove null bytes or dangerous control chars
    cleaned_query = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned_query)

    try:
        return WebSearchInput(query=cleaned_query)
    except ValidationError as exc:
        logger.warning("search_argument_validation_failed", error=str(exc))
        raise ToolGuardrailError(f"Search argument validation failed: {exc}") from exc


# ====== Sanitize search results (remove injection patterns, truncate overly long snippets) ======
def sanitize_search_results(results: list[SearchResult]) -> list[SearchResult]:
    """Sanitize retrieved search result snippets to neutralize prompt injection attacks.

    Args:
        results: Raw list of SearchResult objects from search engine.

    Returns:
        Sanitized list of SearchResult objects.
    """
    sanitized: list[SearchResult] = []
    for item in results:
        clean_text = item.snippet
        # Check and neutralize injection patterns
        for pattern in INJECTION_SNIPPET_PATTERNS:
            if pattern.search(clean_text):
                logger.warning(
                    "potential_injection_in_search_snippet_neutralized",
                    pattern=pattern.pattern,
                    url=item.url,
                )
                clean_text = pattern.sub("[REDACTED_INJECTION_PATTERN]", clean_text)

        # Truncate overly long snippets so total length <= 1500
        if len(clean_text) > 1500:
            clean_text = clean_text[:1497] + "..."

        sanitized.append(
            SearchResult(
                title=item.title.strip(),
                url=item.url.strip(),
                snippet=clean_text.strip(),
            )
        )
    return sanitized
