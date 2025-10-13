"""
Configuration management for Markdown Critic.

Handles loading and saving user preferences from a TOML configuration file.
"""

import tomli
import tomli_w
from pathlib import Path
from typing import Dict, Any, List
import logging


class Config:
    """
    Configuration manager for user preferences.
    
    Loads settings from config.toml and provides access to configuration values.
    """
    
    DEFAULT_CONFIG = {
        "themes": {
            "folders": [
                "c:/RH/Working Code/Markdown Critic/Data/Themes/typora-cobalt-theme-master-v1.4",
                "c:/RH/Working Code/Markdown Critic/Data/Themes/Typora-GitHub-Themes-main/Typora-GitHub-Themes-main",
            ],
            "default_theme": None  # Path to default theme folder
        },
        "rendering": {
            "min_margin_top": 20,
            "min_margin_left": 50,
            "min_margin_right": 50,
            "min_margin_bottom": 20
        },
        "editor": {
            "font_family": "Consolas",
            "font_size": 11,
            "tab_size": 4
        }
    }
    
    def __init__(self, config_path: str = "config.toml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file, or create default if not exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'rb') as f:
                    self.config = tomli.load(f)
                logging.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logging.error(f"Error loading config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            logging.info("No config file found, using defaults")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()  # Create default config file
    
    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'wb') as f:
                tomli_w.dump(self.config, f)
            logging.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'themes.folders')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'themes.folders')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    # Convenience methods for common settings
    
    def get_theme_folders(self) -> List[str]:
        """Get list of theme folder paths."""
        folders = self.get('themes.folders', [])
        # Filter to only existing folders
        return [f for f in folders if Path(f).exists()]
    
    def add_theme_folder(self, folder_path: str) -> None:
        """Add a theme folder to the list."""
        folders = self.get('themes.folders', [])
        if folder_path not in folders:
            folders.append(folder_path)
            self.set('themes.folders', folders)
            self.save()
    
    def get_default_theme(self) -> str:
        """Get default theme path."""
        return self.get('themes.default_theme', None)
    
    def set_default_theme(self, theme_path: str) -> None:
        """Set default theme path."""
        self.set('themes.default_theme', theme_path)
        self.save()
    
    def get_min_margins(self) -> Dict[str, int]:
        """Get minimum margin settings."""
        return {
            'top': self.get('rendering.min_margin_top', 20),
            'left': self.get('rendering.min_margin_left', 50),
            'right': self.get('rendering.min_margin_right', 50),
            'bottom': self.get('rendering.min_margin_bottom', 20)
        }
