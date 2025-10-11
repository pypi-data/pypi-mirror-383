"""Configuration management for shinkuro."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    folder: Optional[str]
    git_url: Optional[str]
    cache_dir: Path
    auto_pull: bool

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        cache_dir_str = os.getenv("CACHE_DIR")
        if cache_dir_str:
            cache_dir = Path(cache_dir_str)
        else:
            cache_dir = Path.home() / ".shinkuro" / "remote"

        return cls(
            folder=os.getenv("FOLDER"),
            git_url=os.getenv("GIT_URL"),
            cache_dir=cache_dir,
            auto_pull=os.getenv("AUTO_PULL", "false").lower() == "true",
        )
