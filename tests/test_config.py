"""Tests for configuration settings."""

import os
from unittest.mock import patch

import pytest

from access_log_analyzer.config import Settings, settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_default_settings(self) -> None:
        """Test default configuration values."""
        config = Settings()

        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False
        assert config.logs_dir == "logs"
        assert config.max_log_entries == 85000
        assert config.default_ip_limit == 20

    def test_settings_from_env(self) -> None:
        """Test loading settings from environment variables."""
        with patch.dict(
            os.environ,
            {
                "HOST": "127.0.0.1",
                "PORT": "9000",
                "DEBUG": "true",
                "LOGS_DIR": "custom_logs",
                "MAX_LOG_ENTRIES": "10000",
                "DEFAULT_IP_LIMIT": "50",
            },
        ):
            config = Settings()

            assert config.host == "127.0.0.1"
            assert config.port == 9000
            assert config.debug is True
            assert config.logs_dir == "custom_logs"
            assert config.max_log_entries == 10000
            assert config.default_ip_limit == 50

    def test_settings_with_invalid_env_values(self) -> None:
        """Test that invalid environment values raise validation errors."""
        with patch.dict(
            os.environ,
            {
                "PORT": "not_a_number",
                "DEBUG": "not_a_bool",
                "MAX_LOG_ENTRIES": "invalid",
            },
        ):
            # Should raise validation errors for invalid values
            from pydantic import ValidationError

            with pytest.raises(ValidationError):
                Settings()

    def test_global_settings_instance(self) -> None:
        """Test that the global settings instance is properly configured."""
        assert isinstance(settings, Settings)
        assert settings.host == "0.0.0.0"  # Should use default
        assert settings.port == 8000  # Should use default
