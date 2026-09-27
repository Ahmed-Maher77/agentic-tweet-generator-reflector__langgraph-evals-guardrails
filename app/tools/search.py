"""Web search engine integrations: Tavily (Primary) and DuckDuckGo (Fallback)."""

from typing import Any

from duckduckgo_search import DDGS
from tavily import TavilyClient

from app.config import Settings, get_settings
from app.logging_config import get_logger
from app.tools.schemas import SearchResult

logger = get_logger(__name__)


# =========== Search Web using Tavily API =============
def search_tavily(
    query: str,
    api_key: str | None,
    max_results: int = 3,
) -> list[SearchResult]:
    """Execute search using Tavily API."""
    if not api_key:
        raise ValueError("Tavily API key not configured")

    logger.info("tavily_search_invoked", query=query, max_results=max_results)

    client = TavilyClient(api_key=api_key)
    response: dict[str, Any] = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
    )
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
        )
        for item in response.get("results", [])[:max_results]
    ]


# =========== Search Web using DuckDuckGo (Fallback) ===========
def search_duckduckgo(
    query: str,
    max_results: int = 3,
) -> list[SearchResult]:
    """Execute search using DuckDuckGo search."""
    logger.info("duckduckgo_search_invoked", query=query, max_results=max_results)

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))
        return [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("href", item.get("link", "")),
                snippet=item.get("body", item.get("snippet", "")),
            )
            for item in results[:max_results]
        ]


# ============= Execute Web Search (route search_tools logic) =============
def execute_web_search(
    query: str,
    settings: Settings | None = None,
) -> tuple[list[SearchResult], str]:
    """Execute web search with Tavily primary and DuckDuckGo fallback strategy."""
    cfg = settings or get_settings()
    max_res = cfg.max_search_results

    # 1. Try Tavily if key is available
    raw_key = cfg.tavily_api_key
    api_key_str: str | None = (
        raw_key.get_secret_value()
        if hasattr(raw_key, "get_secret_value")
        else (str(raw_key) if raw_key is not None else None)
    )

    if api_key_str:
        try:
            results = search_tavily(query=query, api_key=api_key_str, max_results=max_res)
            if results:
                logger.info("web_search_succeeded", engine="tavily", count=len(results))
                return results, "tavily"
        except Exception as exc:
            logger.warning("tavily_search_failed_falling_back", error=str(exc))

    # 2. Fallback to DuckDuckGo
    try:
        results = search_duckduckgo(query=query, max_results=max_res)
        if results:
            logger.info("web_search_succeeded", engine="duckduckgo", count=len(results))
            return results, "duckduckgo"
    except Exception as exc:
        logger.error("duckduckgo_fallback_failed", error=str(exc))

    logger.info("web_search_no_results", query=query)
    return [], "none"


def format_search_results_for_prompt(results: list[SearchResult], engine: str) -> str:
    """Format SearchResult list into clean text for prompt observation."""
    if not results:
        return "No relevant web search results found for the query. Proceed with internal knowledge."

    formatted_items = [
        f"[{i}] {item.title}\n    Snippet: {item.snippet.strip().replace(chr(10), ' ')}\n    Source: {item.url}"
        for i, item in enumerate(results, 1)
    ]
    return f"Web Search Results (Source: {engine.upper()}):\n" + "\n\n".join(formatted_items)
