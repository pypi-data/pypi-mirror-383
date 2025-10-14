"""Configuration management for KITECH Repository."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Config(BaseModel):
    """Configuration settings for KITECH Repository."""

    api_base_url: str = Field(
        default="http://localhost:6300/v1",
        description="Base URL for KITECH API"
    )
    api_token: Optional[str] = Field(
        default=None,
        description="API authentication token"
    )
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".kitech",
        description="Directory for storing configuration files"
    )
    download_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "downloads",
        description="Default directory for downloads"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    chunk_size: int = Field(
        default=8192,
        description="Chunk size for file downloads in bytes"
    )

    class Config:
        env_prefix = "KITECH_"

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