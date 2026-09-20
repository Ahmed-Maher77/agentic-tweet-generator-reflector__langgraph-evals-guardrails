"""Tests for app.config — Settings loading, validation, and defaults."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.config import Settings, get_settings


class TestSettingsDefaults:
    """Test that Settings loads with correct defaults when env vars are set."""

    def test_default_writer_model(self, test_settings: Settings) -> None:
        assert test_settings.writer_model == "gpt-4o-mini"

    def test_default_reviewer_model(self, test_settings: Settings) -> None:
        assert test_settings.reviewer_model == "gpt-4o-mini"

    def test_default_safety_model(self, test_settings: Settings) -> None:
        assert test_settings.safety_model == "gpt-4o-mini"

    def test_default_writer_temperature(self, test_settings: Settings) -> None:
        assert test_settings.writer_temperature == 0.7

    def test_default_reviewer_temperature(self, test_settings: Settings) -> None:
        assert test_settings.reviewer_temperature == 0.3

    def test_default_max_attempts(self, test_settings: Settings) -> None:
        assert test_settings.max_attempts == 3

    def test_default_max_tweet_length(self, test_settings: Settings) -> None:
        assert test_settings.max_tweet_length == 280

    def test_default_reflection_enabled(self, test_settings: Settings) -> None:
        assert test_settings.reflection_enabled is True

    def test_default_thresholds(self, test_settings: Settings) -> None:
        assert test_settings.relevance_threshold == 0.80
        assert test_settings.clarity_threshold == 0.80
        assert test_settings.professionalism_threshold == 0.80
        assert test_settings.engagement_threshold == 0.70
        assert test_settings.requirement_threshold == 0.85

    def test_default_max_input_length(self, test_settings: Settings) -> None:
        assert test_settings.max_input_length == 2000

    def test_default_log_level(self) -> None:
        """Default log level should be INFO when not overridden."""
        settings = Settings(
            openai_api_key="sk-test-key",  # type: ignore[arg-type]
        )
        assert settings.log_level == "INFO"


class TestSettingsValidation:
    """Test Settings validation constraints."""

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings must require OPENAI_API_KEY."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValidationError):
            Settings()  # type: ignore[call-arg]

    def test_temperature_below_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                writer_temperature=-0.1,
            )

    def test_temperature_above_max_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                writer_temperature=2.1,
            )

    def test_max_attempts_below_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                max_attempts=0,
            )

    def test_max_attempts_above_ten_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                max_attempts=11,
            )

    def test_threshold_below_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                relevance_threshold=-0.1,
            )

    def test_threshold_above_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                relevance_threshold=1.1,
            )

    def test_max_tweet_length_below_one_raises(self) -> None:
        with pytest.raises(ValidationError):
            Settings(
                openai_api_key="sk-test",  # type: ignore[arg-type]
                max_tweet_length=0,
            )


class TestSettingsApiKeySecurity:
    """Test that the API key is protected via SecretStr."""

    def test_api_key_is_secret(self, test_settings: Settings) -> None:
        """SecretStr should not reveal the key in string representation."""
        key_repr = repr(test_settings.openai_api_key)
        assert "sk-test-fake-key" not in key_repr
        assert "**" in key_repr

    def test_api_key_get_secret_value(self, test_settings: Settings) -> None:
        """SecretStr.get_secret_value() should return the actual key."""
        actual = test_settings.openai_api_key.get_secret_value()
        assert actual == "sk-test-fake-key-for-testing-only"


class TestSettingsFromEnv:
    """Test that Settings correctly reads from environment variables."""

    def test_override_model_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WRITER_MODEL", "gpt-4o")
        settings = Settings(openai_api_key="sk-test")  # type: ignore[arg-type]
        assert settings.writer_model == "gpt-4o"

    def test_override_max_attempts_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MAX_ATTEMPTS", "5")
        settings = Settings(openai_api_key="sk-test")  # type: ignore[arg-type]
        assert settings.max_attempts == 5

    def test_override_reflection_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("REFLECTION_ENABLED", "false")
        settings = Settings(openai_api_key="sk-test")  # type: ignore[arg-type]
        assert settings.reflection_enabled is False


class TestGetSettings:
    """Test the get_settings() factory function."""

    def test_get_settings_returns_settings(self) -> None:
        settings = get_settings()
        assert isinstance(settings, Settings)
