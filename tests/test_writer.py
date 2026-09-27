"""Unit tests for app.agents.writer — Tweet Writer Agent (the ONLY agent)."""

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage

from app.agents.writer import clean_tweet_output, run_writer_agent
from app.config import Settings
from app.tools.schemas import SearchResult


class TestCleanTweetOutput:
    """Test text post-processing and whitespace normalization with Markdown preservation."""

    def test_clean_plain_text(self) -> None:
        raw = "  Building AI workflows with LangGraph is a game changer.  "
        assert clean_tweet_output(raw) == "Building AI workflows with LangGraph is a game changer."

    def test_preserve_markdown_bold_and_code(self) -> None:
        raw = "**AI agents** are changing how we build software.\n\n```python\nprint('hello')\n```"
        assert clean_tweet_output(raw) == raw

    def test_preserve_quotes_in_markdown(self) -> None:
        raw = '"Excited to announce our new AI project! 🚀"'
        assert clean_tweet_output(raw) == '"Excited to announce our new AI project! 🚀"'



class TestWriterAgentExecution:
    """Test Writer Agent generation, tool invocation, and revision paths."""

    def test_initial_generation_without_tool_call(self, test_settings: Settings) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="🚀 Announcing Antigravity: The next-gen AI agent framework. Fast, typed, and robust."
        )

        tweet, search_used = run_writer_agent(
            user_query="Announce our new AI agent framework called Antigravity",
            attempt=1,
            max_attempts=3,
            search_enabled=False,
            settings=test_settings,
            llm=mock_llm,
        )

        assert "Antigravity" in tweet
        assert search_used is False
        mock_llm.invoke.assert_called_once()

    def test_initial_generation_with_tool_call(self, test_settings: Settings) -> None:
        # First call returns a tool call request
        mock_tool_ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "search_web",
                "args": {"query": "LangGraph releases 2026"},
                "id": "call_123",
            }],
        )
        # Second call returns final tweet grounded with search
        mock_final_ai_msg = AIMessage(
            content="LangGraph just dropped major updates in 2026! 🚀 Multi-agent workflows are faster than ever."
        )

        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.side_effect = [mock_tool_ai_msg, mock_final_ai_msg]

        fake_results = [
            SearchResult(
                title="LangGraph 2026",
                url="https://example.com/langgraph",
                snippet="LangGraph adds enterprise agent features.",
            )
        ]

        with patch("app.agents.writer.execute_web_search", return_value=(fake_results, "tavily")):
            tweet, search_used = run_writer_agent(
                user_query="Latest updates on LangGraph",
                attempt=1,
                max_attempts=3,
                search_enabled=True,
                settings=test_settings,
                llm=mock_llm,
            )

        assert "LangGraph" in tweet
        assert search_used is True
        mock_llm.bind_tools.assert_called_once()
        assert mock_llm_with_tools.invoke.call_count == 2

    def test_writer_agent_hits_max_tool_iterations_cutoff(self, test_settings: Settings) -> None:
        """Test that agent loops up to max_agent_tool_iterations (5) and disables tools on last iteration."""
        # Consecutive tool calls for iterations 1..4
        continuous_tool_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "search_web",
                "args": {"query": "AI research"},
                "id": "call_continuous",
            }],
        )
        # 5th call (final notice) returns final output
        final_notice_response = AIMessage(
            content="🚀 Final tweet based on available info (Note: Search tool limit reached)."
        )

        mock_llm = MagicMock()
        mock_llm_with_tools = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm_with_tools
        mock_llm_with_tools.invoke.return_value = continuous_tool_msg
        mock_llm.invoke.return_value = final_notice_response

        fake_results = [
            SearchResult(
                title="AI Research",
                url="https://example.com",
                snippet="AI is advancing rapidly.",
            )
        ]

        with patch("app.agents.writer.execute_web_search", return_value=(fake_results, "tavily")):
            tweet, search_used = run_writer_agent(
                user_query="AI research",
                attempt=1,
                max_attempts=3,
                search_enabled=True,
                settings=test_settings,
                llm=mock_llm,
            )

        assert "Final tweet" in tweet
        assert search_used is True
        # Iterations 1..4 called model_with_tools
        assert mock_llm_with_tools.invoke.call_count == 4
        # 5th iteration called base model without tools and with system cutoff notice
        assert mock_llm.invoke.call_count == 1
        last_call_messages = mock_llm.invoke.call_args[0][0]
        assert "[SYSTEM NOTICE]" in str(last_call_messages[-1].content)

    def test_revision_generation(self, test_settings: Settings) -> None:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="⚡ We built an AI Tweet Generator with LangGraph and DeepEval reflection loops. Check it out!"
        )

        tweet, search_used = run_writer_agent(
            user_query="AI Tweet Generator project announcement",
            attempt=2,
            max_attempts=3,
            previous_tweet="Check out my tweet generator.",
            feedback="Make the hook much stronger and mention LangGraph and DeepEval.",
            issues=["Hook is too generic.", "Missing tech stack details."],
            search_enabled=False,
            settings=test_settings,
            llm=mock_llm,
        )

        assert "LangGraph" in tweet
        assert search_used is False
        mock_llm.invoke.assert_called_once()
