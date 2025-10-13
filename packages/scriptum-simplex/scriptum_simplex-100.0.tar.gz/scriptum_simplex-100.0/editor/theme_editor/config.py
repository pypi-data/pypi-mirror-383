"""
Theme Editor Configuration

Manages user preferences and settings for the theme editor.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging


class ThemeEditorConfig:
    """Configuration manager for theme editor."""

    DEFAULT_CONFIG = {
        "recent_themes": [],
        "max_recent_themes": 10,
        "auto_save": True,
        "auto_save_interval": 300,  # seconds
        "preview_debounce_ms": 300,
        "default_sample": "comprehensive.md",
        "show_computed_styles": True,
        "syntax_highlighting": True,
        "theme": "cosmo",
        "window_geometry": "1400x900",
        "window_position": None,
        "property_editor_width": 400,
        "preview_width": 600,
        "sample_library_width": 300,
        "create_backups": True,
        "backup_count": 5,
        "show_line_numbers": True,
        "auto_format_css": True,
    }

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """
        Initialize configuration.

        Args:
            config_file: Path to config file. If None, uses default location.
        """
        if config_file is None:
            config_dir = Path.home() / ".scriptum_simplex"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "theme_editor_config.json"
        else:
            self.config_file = config_file

        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logging.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                logging.error(f"Error loading config: {e}")
                # Use defaults on error

    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logging.info(f"Saved config to {self.config_file}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value

    def add_recent_theme(self, theme_path: Path) -> None:
        """
        Add theme to recent themes list.

        Args:
            theme_path: Path to theme folder
        """
        theme_str = str(theme_path)
        recent = self.config.get("recent_themes", [])

        # Remove if already exists
        if theme_str in recent:
            recent.remove(theme_str)

        # Add to front
        recent.insert(0, theme_str)

        # Limit size
        max_recent = self.config.get("max_recent_themes", 10)
        recent = recent[:max_recent]

        self.config["recent_themes"] = recent
        self.save()

    def get_recent_themes(self) -> List[Path]:
        """
        Get list of recent theme paths.

        Returns:
            List of Path objects for recent themes
        """
        recent = self.config.get("recent_themes", [])
        return [Path(p) for p in recent if Path(p).exists()]

    def clear_recent_themes(self) -> None:
        """Clear recent themes list."""
        self.config["recent_themes"] = []
        self.save()

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
