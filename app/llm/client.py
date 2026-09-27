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
) -> BaseChatModel:
    """Factory function to build a ChatOpenAI client.

    Args:
        model_name: Target model identifier (defaults to writer_model from settings).
        temperature: Sampling temperature (defaults to writer_temperature from settings).
        settings: Settings instance (defaults to get_settings()).

    Returns:
        Configured BaseChatModel instance.
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
        "max_retries": 3,
        "timeout": 30.0,
    }
    if base_url_val:
        kwargs["base_url"] = base_url_val

    return ChatOpenAI(**kwargs)


# ============= Structured Model =============
def get_structured_model(
    schema: type[T],
    model_name: str | None = None,
    temperature: float | None = None,
    settings: Settings | None = None,
) -> Any:
    """Create an LLM client configured for structured output matching a Pydantic schema.

    Args:
        schema: Target Pydantic model class.
        model_name: Model identifier.
        temperature: Temperature setting.
        settings: Application settings.

    Returns:
        A Runnable that outputs instances of the provided schema.
    """
    base_llm = get_chat_model(
        model_name=model_name,
        temperature=temperature,
        settings=settings,
    )
    return base_llm.with_structured_output(schema)
