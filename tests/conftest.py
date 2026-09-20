"""Shared pytest fixtures for the AI Tweet Generator test suite.

All LLM calls are mocked by default. Tests requiring real LLM calls
must be marked with @pytest.mark.llm and are excluded from default runs.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests never use real API keys by setting a dummy key."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key-for-testing-only")


@pytest.fixture()
def test_settings() -> Settings:
    """Create a Settings instance with test-safe defaults.

    Uses the dummy API key set by _set_test_env.
    """
    return Settings(
        openai_api_key="sk-test-fake-key-for-testing-only",  # type: ignore[arg-type]
        writer_model="gpt-4o-mini",
        reviewer_model="gpt-4o-mini",
        safety_model="gpt-4o-mini",
        writer_temperature=0.7,
        reviewer_temperature=0.3,
        max_attempts=3,
        max_tweet_length=280,
        reflection_enabled=True,
        relevance_threshold=0.80,
        clarity_threshold=0.80,
        professionalism_threshold=0.80,
        engagement_threshold=0.70,
        requirement_threshold=0.85,
        max_input_length=2000,
        log_level="DEBUG",
    )
