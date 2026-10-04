"""Centralized LLM client factory and helper utilities."""

from typing import Any, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


# ============= Chat Model =============
def get_chat_model(
    model_name: str | None = None,
    temperature: float | None = None,
    settings: Settings | None = None,
    with_cohere_fallback: bool = True,
) -> Any:
    """Factory function to build a ChatOpenAI client with optional automatic Cohere fallback.

    Args:
        model_name: Target model identifier (defaults to writer_model from settings).
        temperature: Sampling temperature (defaults to writer_temperature from settings).
        settings: Settings instance (defaults to get_settings()).
        with_cohere_fallback: Whether to attach Cohere as an automatic fallback if available.

    Returns:
        Configured BaseChatModel instance (or RunnableWithFallbacks).
    """
    cfg = settings or get_settings()
    model = model_name or cfg.writer_model
    temp = temperature if temperature is not None else cfg.writer_temperature

    api_key_val = cfg.effective_api_key.get_secret_value()
    base_url_val = cfg.effective_base_url

    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temp,
        "api_key": api_key_val,
        "max_retries": 2,
        "timeout": 30.0,
    }
    if base_url_val:
        kwargs["base_url"] = base_url_val

    primary_model = ChatOpenAI(**kwargs)

    # Attach Cohere as an automatic fallback when Groq/OpenAI encounters errors (e.g. 403, 429, 500)
    if with_cohere_fallback and cfg.cohere_api_key and cfg.llm_provider != "cohere":
        fallback_model = ChatOpenAI(
            model="command-r-08-2024",
            temperature=temp,
            api_key=cfg.cohere_api_key,
            base_url="https://api.cohere.com/compatibility/v1",
            max_retries=2,
            timeout=30.0,
        )
        return primary_model.with_fallbacks([fallback_model])

    return primary_model


# ============= Structured Model =============
def get_structured_model(
    schema: type[T],
    model_name: str | None = None,
    temperature: float | None = None,
    settings: Settings | None = None,
    with_cohere_fallback: bool = True,
) -> Any:
    """Create an LLM client configured for structured output matching a Pydantic schema.

    Args:
        schema: Target Pydantic model class.
        model_name: Model identifier.
        temperature: Temperature setting.
        settings: Application settings.
        with_cohere_fallback: Whether to attach Cohere structured output as fallback.

    Returns:
        A Runnable that outputs instances of the provided schema.
    """
    cfg = settings or get_settings()
    model = model_name or cfg.reviewer_model
    temp = temperature if temperature is not None else cfg.reviewer_temperature

    api_key_val = cfg.effective_api_key.get_secret_value()
    base_url_val = cfg.effective_base_url

    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temp,
        "api_key": api_key_val,
        "max_retries": 2,
        "timeout": 30.0,
    }
    if base_url_val:
        kwargs["base_url"] = base_url_val

    base_llm = ChatOpenAI(**kwargs)
    primary_structured = base_llm.with_structured_output(schema)

    # Attach Cohere structured fallback if available
    if with_cohere_fallback and cfg.cohere_api_key and cfg.llm_provider != "cohere":
        fallback_llm = ChatOpenAI(
            model="command-r-08-2024",
            temperature=temp,
            api_key=cfg.cohere_api_key,
            base_url="https://api.cohere.com/compatibility/v1",
            max_retries=2,
            timeout=30.0,
        )
        fallback_structured = fallback_llm.with_structured_output(schema)
        return primary_structured.with_fallbacks([fallback_structured])

    return primary_structured
