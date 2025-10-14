"""Configuration management for KITECH Repository."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, model_validator

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration settings for KITECH Repository.

    Environment variables can be used with KITECH_ prefix:
    - KITECH_API_BASE_URL: API base URL (default: http://localhost:6300, /v1 is auto-appended)
    - KITECH_API_TOKEN: API authentication token
    - KITECH_TIMEOUT: Request timeout in seconds (default: 30)
    - KITECH_MAX_RETRIES: Maximum retry attempts (default: 3)
    - KITECH_CHUNK_SIZE: Download chunk size in bytes (default: 8192)
    """

    model_config = ConfigDict(env_prefix="KITECH_")

    api_base_url: str = Field(
        default=os.getenv("KITECH_API_BASE_URL", "http://localhost:6300"), description="Base URL for KITECH API (without /v1)"
    )
    api_token: str | None = Field(default=os.getenv("KITECH_API_TOKEN"), description="API authentication token")

    @model_validator(mode='after')
    def normalize_api_url(self) -> 'Config':
        """Normalize API URL by removing trailing slashes and ensuring /v1 suffix."""
        # Remove trailing slashes
        url = self.api_base_url.rstrip("/")

        # If URL doesn't end with /v1, append it
        if not url.endswith("/v1"):
            url = f"{url}/v1"

        self.api_base_url = url
        return self

    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".kitech", description="Directory for storing configuration files"
    )
    download_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "downloads", description="Default directory for downloads"
    )
    timeout: int = Field(default=int(os.getenv("KITECH_TIMEOUT", "30")), description="Request timeout in seconds")
    max_retries: int = Field(
        default=int(os.getenv("KITECH_MAX_RETRIES", "3")), description="Maximum number of retry attempts"
    )
    chunk_size: int = Field(
        default=int(os.getenv("KITECH_CHUNK_SIZE", "8192")), description="Chunk size for file downloads in bytes"
    )

    def save(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "config.json"
        config_file.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file or environment."""
        config_dir = Path.home() / ".kitech"
        config_file = config_dir / "config.json"

        if config_file.exists():
            import json

            data = json.loads(config_file.read_text())
            return cls(**data)

        return cls()


def get_config() -> Config:
    """Get the current configuration."""
    return Config.load()
