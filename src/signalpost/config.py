"""Configuration module for Signalpost."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Storage
    database_path: str = "data/signalpost.db"

    # HTTP & Networking
    user_agent: str = (
        "Signalpost-Research-Agent/1.0 (+https://github.com/build-signalpost; "
        "research@signalpost.internal)"
    )
    request_timeout_seconds: float = 15.0
    max_retries: int = 3
    backoff_factor: float = 1.5

    # Operational limits & challenge budgets
    max_outbound_requests: int = 2000
    max_external_api_cost_usd: float = 10.0
    execution_timeout_minutes: int = 45

    # Source enablement (default free official public sources)
    enable_brreg_registry: bool = True
    enable_brreg_financial: bool = True
    enable_website_discovery: bool = True

    # Optional AI enhancement (strictly opt-in, default disabled / $0 cost)
    enable_optional_llm: bool = False
    optional_llm_provider: str = "none"
    optional_llm_api_key: str = ""
    optional_llm_model: str = ""

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_db_path(self) -> Path:
        """Resolve and ensure parent directory for the database path."""
        p = Path(self.database_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        p.parent.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
