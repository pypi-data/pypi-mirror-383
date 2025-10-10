"""Configuration for Boston Harbor ferry tracker."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APRS_",
    )

    # API configuration
    api_key: str
    api_base_url: str = "https://api.aprs.fi/api"

    # Rate limiting
    max_requests_per_minute: int = 10

    # Caching
    cache_ttl_seconds: int = 120  # 2 minutes default
    cache_dir: str = str(Path.home() / ".cache" / "boston-harbor-ferries")

    # User-Agent identification (required by aprs.fi)
    app_name: str = "boston-harbor-ferries"
    app_version: str = "0.1.0"
    app_url: str = "https://github.com/aygp-dr/boston-harbor-ferries"

    @property
    def user_agent(self) -> str:
        """Generate User-Agent header as required by aprs.fi API terms."""
        return f"{self.app_name}/{self.app_version} (+{self.app_url})"


def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    return Settings()
