"""Shared pytest fixtures for the evals test runners using configured LLM (Groq / OpenAI)."""

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph

from app.config import Settings, get_settings
from app.graph.workflow import create_tweet_graph
from app.llm.client import get_chat_model
from app.logging_config import get_logger

logger = get_logger(__name__)


# =========== Application Settings Fixture =============
@pytest.fixture(scope="session")
def settings() -> Settings:
    """Session-scoped application settings."""
    return get_settings()


# =========== ChatModel Fixtures =============
@pytest.fixture(scope="session")
def chat_model(settings: Settings) -> BaseChatModel:
    """Session-scoped BaseChatModel using configured LLM provider (Groq / OpenAI)."""
    try:
        return get_chat_model(settings=settings)
    except Exception as e:
        logger.error("failed_to_create_chat_model", error=str(e))
        raise


@pytest.fixture(scope="session")
def ollama_llm(chat_model: BaseChatModel) -> BaseChatModel:
    """Alias for backwards compatibility with test runner signatures."""
    return chat_model


# =========== Compiled Graph Fixture ===========
@pytest.fixture(scope="session")
def graph(settings: Settings) -> CompiledStateGraph:
    """Session-scoped compiled tweet workflow graph using configured settings."""
    return create_tweet_graph(settings=settings)

