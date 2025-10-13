"""
Theme Manager

Handles loading, saving, and managing Typora themes.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging
import shutil
from datetime import datetime

from ..full_typora_theme_support import FullTyporaThemeLoader
from ..full_typora_theme_support.css_properties import ElementStyles


class ThemeManager:
    """Manages theme loading, saving, and modifications."""

    def __init__(self) -> None:
        """Initialize theme manager."""
        self.loader = FullTyporaThemeLoader()
        self.current_theme_path: Optional[Path] = None
        self.current_styles: Optional[ElementStyles] = None
        self.original_styles: Optional[ElementStyles] = None
        self.is_modified = False

    def load_theme(self, theme_path: Path) -> Optional[ElementStyles]:
        """
        Load a theme from a folder.

        Args:
            theme_path: Path to theme folder

        Returns:
            ElementStyles object if successful, None otherwise
        """
        try:
            logging.info(f"Loading theme from: {theme_path}")
            styles = self.loader.load_theme_from_folder(str(theme_path))

            if styles:
                self.current_theme_path = theme_path
                self.current_styles = styles
                # Store a copy of original styles for comparison
                self.original_styles = self._deep_copy_styles(styles)
                self.is_modified = False
                logging.info(f"Successfully loaded theme: {self.loader.theme_name}")
                return styles
            else:
                logging.error("Failed to load theme")
                return None

        except Exception as e:
            logging.error(f"Error loading theme: {e}", exc_info=True)
            return None

    def get_theme_name(self) -> str:
        """
        Get the name of the currently loaded theme.

        Returns:
            Theme name or empty string
        """
        return self.loader.theme_name if self.loader.theme_name else ""

    def get_css_variables(self) -> Dict[str, str]:
        """
        Get CSS variables from the current theme.

        Returns:
            Dictionary of CSS variable names to values
        """
        return self.loader.css_variables if self.loader.css_variables else {}

    def mark_modified(self) -> None:
        """Mark the current theme as modified."""
        self.is_modified = True

    def is_theme_modified(self) -> bool:
        """
        Check if current theme has been modified.

        Returns:
            True if modified, False otherwise
        """
        return self.is_modified

    def update_property(self, element: str, property_name: str, value: str) -> bool:
        """
        Update a CSS property value in the current theme.

        Args:
            element: Element name (e.g., 'h1', 'paragraph')
            property_name: CSS property name (e.g., 'color', 'font-size')
            value: New property value

        Returns:
            True if successful, False otherwise
        """
        if not self.current_styles:
            logging.error("No theme loaded")
            return False

        try:
            # Get the element's properties
            element_props = self.current_styles.get_element(element)
            if not element_props:
                logging.error(f"Element '{element}' not found")
                return False

            # Convert CSS property name to Python attribute name
            attr_name = property_name.replace('-', '_')

            # Set the property
            if hasattr(element_props, attr_name):
                setattr(element_props, attr_name, value)
                logging.info(f"Updated {element}.{property_name} = {value}")
                self.mark_modified()
                return True
            else:
                logging.warning(f"Property '{property_name}' not found on element '{element}'")
                return False

        except Exception as e:
            logging.error(f"Error updating property: {e}", exc_info=True)
            return False

    def update_css_variable(self, var_name: str, value: str) -> bool:
        """
        Update a CSS variable value.

        Args:
            var_name: CSS variable name (with or without --)
            value: New variable value

        Returns:
            True if successful, False otherwise
        """
        if not self.loader.css_variables:
            logging.error("No CSS variables loaded")
            return False

        try:
            # Ensure var_name starts with --
            if not var_name.startswith('--'):
                var_name = f'--{var_name}'

            # Update the variable
            self.loader.css_variables[var_name] = value
            logging.info(f"Updated CSS variable {var_name} = {value}")
            self.mark_modified()
            return True

        except Exception as e:
            logging.error(f"Error updating CSS variable: {e}", exc_info=True)
            return False

    def save_theme(self, backup: bool = True) -> bool:
        """
        Save the current theme back to its original location.

        Args:
            backup: Whether to create a backup before saving

        Returns:
            True if successful, False otherwise
        """
        if not self.current_theme_path or not self.current_styles:
            logging.error("No theme loaded to save")
            return False

        try:
            # Create backup if requested
            if backup:
                self._create_backup(self.current_theme_path)

            # Save the theme
            success = self._write_theme_files(self.current_theme_path, self.current_styles)

            if success:
                self.is_modified = False
                self.original_styles = self._deep_copy_styles(self.current_styles)
                logging.info(f"Theme saved successfully to {self.current_theme_path}")

            return success

        except Exception as e:
            logging.error(f"Error saving theme: {e}", exc_info=True)
            return False

    def save_theme_as(self, new_path: Path, new_name: str, backup: bool = False) -> bool:
        """
        Save the current theme to a new location with a new name.

        Args:
            new_path: Path to save the theme
            new_name: New theme name
            backup: Whether to create a backup (usually False for new themes)

        Returns:
            True if successful, False otherwise
        """
        if not self.current_styles:
            logging.error("No theme loaded to save")
            return False

        try:
            # Create the new theme directory
            new_path.mkdir(parents=True, exist_ok=True)

            # Update theme name
            self.loader.theme_name = new_name

            # Save the theme
            success = self._write_theme_files(new_path, self.current_styles)

            if success:
                self.current_theme_path = new_path
                self.is_modified = False
                self.original_styles = self._deep_copy_styles(self.current_styles)
                logging.info(f"Theme saved as '{new_name}' to {new_path}")

            return success

        except Exception as e:
            logging.error(f"Error saving theme as: {e}", exc_info=True)
            return False

    def _create_backup(self, theme_path: Path) -> Optional[Path]:
        """
        Create a backup of the theme.

        Args:
            theme_path: Path to theme folder

        Returns:
            Path to backup folder if successful, None otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{theme_path.name}_backup_{timestamp}"
            backup_path = theme_path.parent / backup_name

            shutil.copytree(theme_path, backup_path)
            logging.info(f"Created backup at {backup_path}")
            return backup_path

        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return None

    def _write_theme_files(self, theme_path: Path, styles: ElementStyles) -> bool:
        """
        Write theme files to disk.

        Args:
            theme_path: Path to theme folder
            styles: ElementStyles object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the CSS file
            css_files = list(theme_path.glob("*.css"))
            if not css_files:
                logging.error("No CSS file found in theme folder")
                return False

            css_file = css_files[0]

            # Generate CSS from styles
            css_content = self._generate_css(styles)

            # Write CSS file
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(css_content)

            logging.info(f"Wrote CSS to {css_file}")
            return True

        except Exception as e:
            logging.error(f"Error writing theme files: {e}", exc_info=True)
            return False

    def _generate_css(self, styles: ElementStyles) -> str:
        """
        Generate CSS content from ElementStyles.

        Args:
            styles: ElementStyles object

        Returns:
            CSS content as string
        """
        # TODO: Implement proper CSS generation
        # For now, return a placeholder
        css_lines = []
        css_lines.append("/* Generated by Scriptum Simplex Theme Editor */")
        css_lines.append("")

        # Add CSS for each element
        elements = [
            'body', 'write', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'paragraph', 'link', 'ul', 'ol', 'li', 'code', 'code_block',
            'blockquote', 'table', 'th', 'td', 'hr'
        ]

        for element_name in elements:
            props = styles.get_element(element_name)
            if props:
                css_lines.append(f"/* {element_name} */")
                # TODO: Convert props to CSS
                css_lines.append("")

        return "\n".join(css_lines)

    def _deep_copy_styles(self, styles: ElementStyles) -> ElementStyles:
        """
        Create a deep copy of ElementStyles.

        Args:
            styles: ElementStyles to copy

        Returns:
            Copy of ElementStyles
        """
        # TODO: Implement proper deep copy
        # For now, return the same object (will fix later)
        return styles

    def get_modified_properties(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a dictionary of modified properties.

        Returns:
            Dictionary mapping element names to modified properties
        """
        if not self.current_styles or not self.original_styles:
            return {}

        # TODO: Implement comparison logic
        return {}

    def revert_changes(self) -> bool:
        """
        Revert all changes to the original theme.

        Returns:
            True if successful, False otherwise
        """
        if not self.original_styles:
            return False

        self.current_styles = self._deep_copy_styles(self.original_styles)
        self.is_modified = False
        return True
