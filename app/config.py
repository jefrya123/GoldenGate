"""
Configuration management for PII scanner.
"""

import json
from pathlib import Path
from typing import Any


class Config:
    """Configuration manager for PII scanner."""

    def __init__(self, config_file: Path = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to config file (default: ~/.pii_scanner_config.json)
        """
        if config_file is None:
            config_file = Path.home() / ".pii_scanner_config.json"

        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "default_output_dir": "./pii_results",
            "default_extensions": [".txt", ".csv", ".log", ".md", ".html", ".pdf"],
            "default_chunk_size": 2000,
            "default_overlap": 100,
            "default_poll_seconds": 10,
            "recent_output_dirs": [],
            "max_recent_dirs": 10,
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        return default_config

    def _save_config(self):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self._save_config()

    def add_recent_output_dir(self, output_dir: str):
        """Add output directory to recent list."""
        recent_dirs = self.config.get("recent_output_dirs", [])

        # Remove if already exists
        if output_dir in recent_dirs:
            recent_dirs.remove(output_dir)

        # Add to front
        recent_dirs.insert(0, output_dir)

        # Limit size
        max_dirs = self.config.get("max_recent_dirs", 10)
        recent_dirs = recent_dirs[:max_dirs]

        self.config["recent_output_dirs"] = recent_dirs
        self._save_config()

    def get_recent_output_dirs(self) -> list:
        """Get list of recent output directories."""
        return self.config.get("recent_output_dirs", [])

    def get_default_output_dir(self) -> str:
        """Get default output directory."""
        return self.config.get("default_output_dir", "./pii_results")

    def set_default_output_dir(self, output_dir: str):
        """Set default output directory."""
        self.set("default_output_dir", output_dir)

    def get_default_extensions(self) -> list:
        """Get default file extensions."""
        return self.config.get(
            "default_extensions", [".txt", ".csv", ".log", ".md", ".html", ".pdf"]
        )

    def set_default_extensions(self, extensions: list):
        """Set default file extensions."""
        self.set("default_extensions", extensions)

    def get_default_chunk_settings(self) -> dict[str, int]:
        """Get default chunk settings."""
        return {
            "chunk_size": self.config.get("default_chunk_size", 2000),
            "overlap": self.config.get("default_overlap", 100),
        }

    def set_default_chunk_settings(self, chunk_size: int, overlap: int):
        """Set default chunk settings."""
        self.set("default_chunk_size", chunk_size)
        self.set("default_overlap", overlap)

    def get_default_poll_seconds(self) -> int:
        """Get default polling interval."""
        return self.config.get("default_poll_seconds", 10)

    def set_default_poll_seconds(self, poll_seconds: int):
        """Set default polling interval."""
        self.set("default_poll_seconds", poll_seconds)


# Global config instance
_config = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config():
    """Reset configuration to defaults."""
    global _config
    if _config and _config.config_file.exists():
        _config.config_file.unlink()
    _config = None
