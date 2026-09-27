"""Unit tests for app.tools.search — Web search tool with Tavily and DuckDuckGo fallback."""

from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings
from app.tools.schemas import SearchResult, WebSearchInput
from app.tools.search import (
    execute_web_search,
    format_search_results_for_prompt,
    search_duckduckgo,
    search_tavily,
)


class TestSearchSchemas:
    """Test search input and result schemas."""

    def test_valid_search_input(self) -> None:
        valid = WebSearchInput(query="Python 3.14 release date")
        assert valid.query == "Python 3.14 release date"

    def test_search_result_model(self) -> None:
        res = SearchResult(title="Test", url="https://example.com", snippet="Example text")
        assert res.title == "Test"
        assert res.url == "https://example.com"
        assert res.snippet == "Example text"


class TestTavilySearch:
    """Test Tavily search client integration and fallback handling."""

    def test_search_tavily_success(self, test_settings: Settings) -> None:
        mock_tavily_client = MagicMock()
        mock_tavily_client.search.return_value = {
            "results": [
                {
                    "title": "Agentic AI News",
                    "url": "https://example.com/agents",
                    "content": "Agents are transforming software development.",
                }
            ]
        }

        with patch("app.tools.search.TavilyClient", return_value=mock_tavily_client):
            results = search_tavily("Agentic AI", "fake_key")

        assert len(results) == 1
        assert results[0].title == "Agentic AI News"
        assert results[0].url == "https://example.com/agents"
        assert "transforming" in results[0].snippet

    def test_search_tavily_without_key_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Tavily API key not configured"):
            search_tavily("test", None)


class TestDuckDuckGoSearch:
    """Test DuckDuckGo fallback search integration."""

    def test_search_duckduckgo_success(self) -> None:
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {
                "title": "DuckDuckGo Python News",
                "href": "https://duckduckgo.com/news",
                "body": "Python 3.14 brings speed enhancements.",
            }
        ]

        with patch("app.tools.search.DDGS", return_value=mock_ddgs):
            results = search_duckduckgo("Python news")

        assert len(results) == 1
        assert results[0].title == "DuckDuckGo Python News"
        assert results[0].url == "https://duckduckgo.com/news"


class TestExecuteWebSearchFallback:
    """Test automatic fallback from Tavily to DuckDuckGo."""

    def test_tavily_primary_success(self, test_settings: Settings) -> None:
        test_settings.tavily_api_key = "fake_key"
        fake_results = [
            SearchResult(title="Tavily Result", url="https://tavily.com", snippet="From Tavily")
        ]

        with patch("app.tools.search.search_tavily", return_value=fake_results):
            results, engine = execute_web_search("AI models", test_settings)

        assert engine == "tavily"
        assert len(results) == 1
        assert results[0].title == "Tavily Result"

    def test_tavily_failure_falls_back_to_duckduckgo(self, test_settings: Settings) -> None:
        test_settings.tavily_api_key = "fake_key"
        ddg_results = [
            SearchResult(title="DDG Result", url="https://duckduckgo.com", snippet="From DDG")
        ]

        with (
            patch("app.tools.search.search_tavily", side_effect=RuntimeError("Rate limit")),
            patch("app.tools.search.search_duckduckgo", return_value=ddg_results),
        ):
            results, engine = execute_web_search("AI models", test_settings)

        assert engine == "duckduckgo"
        assert len(results) == 1
        assert results[0].title == "DDG Result"


class TestFormatSearchResults:
    """Test formatted prompt observation string generation."""

    def test_format_empty_results(self) -> None:
        formatted = format_search_results_for_prompt([], "tavily")
        assert "No relevant web search results found" in formatted

    def test_format_valid_results(self) -> None:
        results = [
            SearchResult(
                title="LangGraph Overview",
                url="https://langchain.com/langgraph",
                snippet="Cyclic state graphs for agents.",
            )
        ]
        formatted = format_search_results_for_prompt(results, "tavily")
        assert "Source: TAVILY" in formatted
        assert "LangGraph Overview" in formatted
        assert "https://langchain.com/langgraph" in formatted
