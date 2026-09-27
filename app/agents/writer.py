"""Tweet Writer Agent — The ONLY autonomous agent in the system.

Responsible for:
1. Initial tweet generation from user request.
2. Optional web search grounding (Tavily + DuckDuckGo fallback) protected by Tool Action Guardrails.
3. Iterative refinement using reflection reviewer feedback and issues.
4. Capped multi-turn tool calling loop with final cutoff notice.
"""

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.config import Settings, get_settings
from app.guardrails.tools import (
    sanitize_search_results,
    validate_search_arguments,
    validate_tool_name,
)
from app.llm.client import get_chat_model
from app.logging_config import get_logger
from app.prompts.writer import (
    WRITER_INITIAL_USER_PROMPT,
    WRITER_REVISION_USER_PROMPT,
    WRITER_SYSTEM_PROMPT,
)
from app.tools.schemas import WebSearchInput
from app.tools.search import execute_web_search, format_search_results_for_prompt

logger = get_logger(__name__)


# =========== Web Search Tool =============
@tool(args_schema=WebSearchInput)
def search_web(query: str) -> str:
    """Search the live web for real-time facts, recent news, benchmark statistics, or data."""
    validate_tool_name("search_web")
    validated_input = validate_search_arguments({"query": query})
    raw_results, engine = execute_web_search(validated_input.query)
    sanitized_results = sanitize_search_results(raw_results)
    return format_search_results_for_prompt(sanitized_results, engine)


def clean_tweet_output(raw_text: str) -> str:
    """Clean the raw LLM output preserving valid Markdown formatting.

    Only performs necessary whitespace normalization. Presentation and Markdown
    rendering are handled by the frontend.
    """
    return raw_text.strip()



# =========== Run the writer agent ===========
def run_writer_agent(
    user_query: str,
    attempt: int = 1,
    max_attempts: int = 3,
    previous_tweet: str | None = None,
    feedback: str | None = None,
    issues: list[str] | None = None,
    search_enabled: bool = True,
    settings: Settings | None = None,
    llm: BaseChatModel | None = None,
) -> tuple[str, bool]:
    """Execute the Tweet Writer Agent with iterative tool calling.

    Args:
        user_query: The original prompt or topic.
        attempt: The current attempt number (1 for initial, >1 for revisions).
        max_attempts: Maximum allowed iterations.
        previous_tweet: The draft generated in the preceding attempt (if revising).
        feedback: Actionable feedback from the reflection evaluator (if revising).
        issues: Specific issues identified by the evaluator (if revising).
        search_enabled: Whether real-time web search tool binding is active.
        settings: Application settings.
        llm: Optional injected LLM client (for testing).

    Returns:
        Tuple of (generated tweet text, boolean indicating if search was utilized).
    """
    cfg = settings or get_settings()
    model = llm or get_chat_model(
        model_name=cfg.writer_model,
        temperature=cfg.writer_temperature,
        settings=cfg,
    )

    is_revision = attempt > 1 and previous_tweet is not None
    is_search_active = search_enabled and cfg.search_enabled
    search_used = False

    if is_revision:
        logger.info(
            "writer_agent_refining_tweet",
            attempt=attempt,
            max_attempts=max_attempts,
            issues_count=len(issues or []),
        )
        formatted_issues = (
            "\n".join(f"- {issue}" for issue in issues)
            if issues
            else "None specified. Improve overall impact and clarity."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", WRITER_SYSTEM_PROMPT),
            ("user", WRITER_REVISION_USER_PROMPT),
        ])
        messages = prompt.format_messages(
            user_query=user_query,
            previous_tweet=previous_tweet,
            feedback=feedback or "Refine the tweet for better clarity and impact.",
            issues=formatted_issues,
            attempt=attempt,
            max_attempts=max_attempts,
            max_tweet_length=cfg.max_tweet_length,
        )
    else:
        logger.info(
            "writer_agent_generating_initial_tweet",
            attempt=1,
            max_attempts=max_attempts,
            search_enabled=is_search_active,
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", WRITER_SYSTEM_PROMPT),
            ("user", WRITER_INITIAL_USER_PROMPT),
        ])
        messages = prompt.format_messages(
            user_query=user_query,
            max_tweet_length=cfg.max_tweet_length,
        )

    # Bind tools if search is active
    model_with_tools: Any = None
    if is_search_active and hasattr(model, "bind_tools"):
        try:
            model_with_tools = model.bind_tools([search_web])
        except Exception as exc:
            logger.warning("tool_binding_failed_falling_back_to_direct_generation", error=str(exc))
            model_with_tools = None

    max_requests = cfg.max_agent_tool_iterations
    conversation_history: list[Any] = list(messages)
    raw_output = ""

    # Iterative agent tool-calling loop (capped at max_requests)
    for iteration in range(1, max_requests + 1):
        is_last_iteration = iteration == max_requests

        if is_last_iteration:
            logger.warning(
                "writer_agent_last_request_tool_cutoff",
                iteration=iteration,
                max_requests=max_requests,
            )
            # Final request: tool calling is disabled. Notify LLM to finalize output.
            final_notice = HumanMessage(
                content=(
                    "[SYSTEM NOTICE]: You have reached the maximum tool call limit and no more tool calls can be made. "
                    "Generate your final tweet response immediately using all available information. "
                    "If the lack of additional tool access negatively impacts the completeness, accuracy, or confidence of the response, "
                    "explicitly notify the user of this limitation in your final response."
                )
            )
            conversation_history.append(final_notice)
            response = model.invoke(conversation_history)
            raw_output = (
                response.content
                if hasattr(response, "content") and isinstance(response.content, str)
                else str(response)
            )
            break

        # Standard iterations (1 .. max_requests - 1): invoke with tool support
        active_model = model_with_tools if model_with_tools is not None else model
        response = active_model.invoke(conversation_history)
        tool_calls = getattr(response, "tool_calls", None)

        if isinstance(tool_calls, list) and len(tool_calls) > 0:
            logger.info(
                "writer_agent_invoked_tools",
                iteration=iteration,
                tool_calls_count=len(tool_calls),
            )
            conversation_history.append(response)

            for call in tool_calls:
                call_name = call.get("name", "search_web") if isinstance(call, dict) else "search_web"
                call_args = call.get("args", {}) if isinstance(call, dict) else {}
                call_id = call.get("id", f"call_{iteration}") if isinstance(call, dict) else f"call_{iteration}"

                try:
                    # 1. Whitelist tool check
                    validate_tool_name(call_name)
                    # 2. Argument schema validation
                    validated_input = validate_search_arguments(call_args)
                    # 3. Execute search with Tavily -> DuckDuckGo fallback
                    results, engine = execute_web_search(validated_input.query, settings=cfg)
                    # 4. Sanitize results against prompt injections
                    sanitized_results = sanitize_search_results(results)
                    observation = format_search_results_for_prompt(sanitized_results, engine)
                    search_used = True
                except Exception as exc:
                    logger.warning("tool_action_guardrail_caught_error", error=str(exc))
                    observation = f"Search tool unavailable: {exc}. Proceed with internal knowledge."

                conversation_history.append(ToolMessage(content=observation, tool_call_id=call_id))
        else:
            raw_output = (
                response.content
                if hasattr(response, "content") and isinstance(response.content, str)
                else str(response)
            )
            break

    cleaned = clean_tweet_output(raw_output)

    logger.info(
        "writer_agent_completed",
        attempt=attempt,
        tweet_length=len(cleaned),
        search_used=search_used,
    )
    return cleaned, search_used
