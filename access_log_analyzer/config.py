"""Configuration settings for the access log analyzer."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Log settings
    logs_dir: str = Field(default="logs", description="Directory containing log files")
    max_log_entries: int = Field(default=85000, description="Maximum log entries to process")

    # Display settings
    default_ip_limit: int = Field(default=20, description="Default number of top IPs to show")


settings = Settings()
