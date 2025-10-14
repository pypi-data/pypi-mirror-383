# SPDX-FileCopyrightText: 2025-present Yiannis Charalambous <yiannis128@hotmail.com>
#
# SPDX-License-Identifier: AGPL-3.0

from pathlib import Path
import toml
from pydantic import BaseModel, Field, field_validator


class AppConfig(BaseModel):
    """Application configuration."""

    base_game_directory: Path = Field(
        default=Path.home(), description="Base directory of the game"
    )

    relative_active_mods_dir: str = Field(
        default="UNION/Content/Paks",
        description="Relative path from game directory to active mods location",
    )

    @property
    def active_mods_directory(self) -> Path:
        """Return the full path to the active mods directory."""
        return self.base_game_directory / self.relative_active_mods_dir / "~mods"

    @property
    def inactive_mods_directory(self) -> Path:
        """Return the full path to the inactive mods directory."""
        return self.base_game_directory / "mods"

    def is_valid(self) -> tuple[bool, str]:
        """
        Validate the configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if base game directory exists
        if not self.base_game_directory.exists():
            return False, "Base game directory does not exist"

        # Check if it's a directory
        if not self.base_game_directory.is_dir():
            return False, "Base game directory is not a directory"

        # Check if it contains the game executable
        game_exe = self.base_game_directory / "SonicRacingCrossWorlds.exe"
        if not game_exe.exists():
            return False, "SonicRacingCrossWorlds.exe not found in base game directory"

        return True, ""

    @field_validator("base_game_directory", mode="before")
    @classmethod
    def validate_path(cls, v):
        """Convert string to Path if needed."""
        if isinstance(v, str):
            return Path(v)
        return v

    class Config:
        arbitrary_types_allowed = True


class ConfigManager:
    """Manages loading and saving application configuration."""

    CONFIG_DIR = Path.home() / ".config" / "crossworlds-modmanager"
    CONFIG_FILE = CONFIG_DIR / "config.toml"

    @classmethod
    def load(cls) -> AppConfig:
        """Load configuration from file or create default."""
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, "r") as f:
                    data = toml.load(f)
                return AppConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return AppConfig()
        return AppConfig()

    @classmethod
    def save(cls, config: AppConfig) -> None:
        """Save configuration to file."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Convert to dict and handle Path serialization
        data = config.model_dump(mode="json")
        data["base_game_directory"] = str(config.base_game_directory)

        with open(cls.CONFIG_FILE, "w") as f:
            toml.dump(data, f)
