"""Shared pytest fixtures for the evals test runners using local Ollama (gpt-oss) with langchain_ollama."""

import os

import httpx
import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph

from app.graph.workflow import create_tweet_graph
from app.logging_config import get_logger
from app.reflection.schemas import ReviewResult

logger = get_logger(__name__)


def ensure_ollama_running(base_url: str, model_name: str) -> None:
    """Check whether local Ollama server is running and the specified model is pulled."""
    tags_url = f"{base_url.rstrip('/')}/api/tags"
    try:
        response = httpx.get(tags_url, timeout=3.0)
        if response.status_code != 200:
            pytest.fail(f"Ollama server at '{base_url}' returned HTTP {response.status_code}. Please ensure Ollama is healthy.")
    except Exception as exc:
        pytest.fail(
            f"❌ Ollama server is not running at '{base_url}' ({exc}).\n"
            "Please start Ollama (e.g. run `ollama serve`) before running evaluation tests."
        )

    # Verify model is available
    try:
        models = [m.get("name", "") for m in response.json().get("models", [])]
        # Match exact name or base prefix
        if not any(model_name in m or m in model_name for m in models):
            available = ", ".join(models) if models else "none"
            pytest.fail(
                f"❌ Model '{model_name}' is not found in local Ollama.\n"
                f"Available local models: [{available}].\n"
                f"Run `ollama pull {model_name}` to download it or set OLLAMA_MODEL environment variable."
            )
    except Exception as e:
        logger.warning("ollama_model_check_failed", error=str(e))


# =========== Ollama ChatModel instance (for testing) =============
@pytest.fixture(scope="session")
def ollama_llm() -> BaseChatModel:
    """Session-scoped BaseChatModel using ChatOllama from langchain_ollama with health check."""
    model_name = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").replace("/v1", "").rstrip("/")

    # Pre-flight check: ensure Ollama is online and model exists
    ensure_ollama_running(base_url=base_url, model_name=model_name)

    try:
        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.7,
        )
    except Exception as e:
        logger.error("failed_to_create_ollama_llm", error=str(e))
        raise


# =========== Compiled Graph (for testing) ===========
@pytest.fixture(scope="session")
def graph(ollama_llm: BaseChatModel) -> CompiledStateGraph:
    """Session-scoped compiled tweet workflow graph using ChatOllama from langchain_ollama."""
    return create_tweet_graph(
        writer_llm=ollama_llm,
        reviewer_model=ollama_llm.with_structured_output(ReviewResult),
    )
