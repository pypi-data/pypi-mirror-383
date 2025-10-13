"""
Full Typora Theme Loader

Comprehensive CSS parser that extracts all properties for all elements.
"""

import re
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from .css_properties import (
    CSSProperties, ElementStyles, 
    parse_border_shorthand, parse_margin_padding_shorthand
)


class FullTyporaThemeLoader:
    """
    Comprehensive Typora theme loader that extracts all CSS properties.
    """
    
    # Mapping of CSS selectors to ElementStyles attributes
    SELECTOR_MAP = {
        'body': 'body',
        'html': 'body',
        '#write': 'write',
        'h1': 'h1',
        '#write h1': 'h1',
        'h2': 'h2',
        '#write h2': 'h2',
        'h3': 'h3',
        '#write h3': 'h3',
        'h4': 'h4',
        '#write h4': 'h4',
        'h5': 'h5',
        '#write h5': 'h5',
        'h6': 'h6',
        '#write h6': 'h6',
        'p': 'paragraph',
        '#write p': 'paragraph',
        'a': 'link',
        '#write a': 'link',
        'a:hover': 'link_hover',
        'ul': 'ul',
        '#write ul': 'ul',
        'ol': 'ol',
        '#write ol': 'ol',
        'li': 'li',
        '#write li': 'li',
        'code': 'code',
        'pre': 'code_block',
        '.md-fences': 'code_block',
        'blockquote': 'blockquote',
        '#write blockquote': 'blockquote',
        'blockquote::before': 'blockquote_before',
        'table': 'table',
        'thead': 'thead',
        'tbody': 'tbody',
        'tr': 'tr',
        'th': 'th',
        'td': 'td',
        'hr': 'hr',
        'img': 'img',
    }
    
    def __init__(self):
        """Initialize the theme loader."""
        self.css_variables: Dict[str, str] = {}
        self.theme_folder: Optional[Path] = None
        self.theme_name: str = "Unknown"
    
    def load_theme_from_folder(self, folder_path: str) -> Optional[ElementStyles]:
        """
        Load a Typora theme from a folder.
        
        Args:
            folder_path: Path to theme folder
            
        Returns:
            ElementStyles object with all CSS properties
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            logging.error(f"Theme folder does not exist: {folder_path}")
            return None
        
        self.theme_folder = folder
        
        # Find CSS file
        css_files = list(folder.glob('*.css'))
        if not css_files:
            logging.error(f"No CSS file found in: {folder_path}")
            return None
        
        css_file = css_files[0]
        self.theme_name = css_file.stem.replace('-', ' ').title()
        
        logging.info(f"Loading Typora theme: {self.theme_name} from {css_file.name}")
        
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Step 1: Extract CSS variables
            self._extract_css_variables(css_content)
            logging.info(f"Extracted {len(self.css_variables)} CSS variables")
            
            # Step 2: Parse all CSS rules
            styles = self._parse_css(css_content)
            
            logging.info(f"Successfully loaded theme: {self.theme_name}")
            return styles
            
        except Exception as e:
            logging.error(f"Error loading theme: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_css_variables(self, css_content: str) -> None:
        """Extract CSS custom properties from :root."""
        self.css_variables.clear()
        
        root_pattern = r':root\s*\{([^}]+)\}'
        root_match = re.search(root_pattern, css_content, re.DOTALL)
        
        if root_match:
            root_block = root_match.group(1)
            var_pattern = r'--([a-zA-Z0-9-]+)\s*:\s*([^;]+);'
            for match in re.finditer(var_pattern, root_block):
                var_name = f"--{match.group(1)}"
                var_value = match.group(2).strip()
                self.css_variables[var_name] = var_value
    
    def _resolve_css_value(self, value: str) -> str:
        """Resolve CSS var() references."""
        var_pattern = r'var\((--[a-zA-Z0-9-]+)\)'
        
        def replace_var(match):
            var_name = match.group(1)
            return self.css_variables.get(var_name, match.group(0))
        
        return re.sub(var_pattern, replace_var, value)
    
    def _parse_css(self, css_content: str) -> ElementStyles:
        """
        Parse CSS content and extract properties for each element.
        
        Args:
            css_content: CSS file content
            
        Returns:
            ElementStyles object with properties for each element
        """
        styles = ElementStyles()
        
        # Match CSS rules: selector { properties }
        rule_pattern = r'([^{}]+)\{([^{}]+)\}'
        
        for match in re.finditer(rule_pattern, css_content, re.DOTALL):
            selector = match.group(1).strip()
            properties_block = match.group(2)
            
            # Handle comma-separated selectors (e.g., "h1, h2, h3")
            if ',' in selector:
                selectors = [s.strip() for s in selector.split(',')]
            else:
                selectors = [selector]
            
            # Apply properties to all matching selectors
            for sel in selectors:
                # Map selector to element
                element_name = self._map_selector_to_element(sel)
                
                if element_name:
                    # Parse properties
                    props = self._parse_properties_block(properties_block)
                    
                    # Merge with existing properties
                    existing_props = getattr(styles, element_name, CSSProperties())
                    merged_props = existing_props.merge(props)
                    setattr(styles, element_name, merged_props)
        
        return styles
    
    def _parse_properties_block(self, block: str) -> CSSProperties:
        """
{{ ... }}
        
        Args:
            block: CSS properties block (inside {})
            
        Returns:
            CSSProperties object
        """
        props = CSSProperties()
        
        # Extract property: value pairs in order (important for override handling)
        prop_pattern = r'([a-zA-Z-]+)\s*:\s*([^;]+);'
        
        for match in re.finditer(prop_pattern, block):
            prop_name = match.group(1).strip()
            prop_value = match.group(2).strip()
            
            # Resolve CSS variables
            prop_value = self._resolve_css_value(prop_value)
            
            # Handle shorthand properties FIRST (so specific properties can override)
            if prop_name in ['margin', 'padding']:
                # Expand shorthand to individual sides
                parts = parse_margin_padding_shorthand(prop_value)
                for side, value in parts.items():
                    props.set(f'{prop_name}-{side}', value)
            elif prop_name == 'border' and prop_value not in ['none', '0']:
                border_parts = parse_border_shorthand(prop_value)
                if 'width' in border_parts:
                    props.set('border-width', border_parts['width'])
                if 'style' in border_parts:
                    props.set('border-style', border_parts['style'])
                if 'color' in border_parts:
                    props.set('border-color', border_parts['color'])
            elif prop_name == 'background' and not prop_value.startswith('url'):
                # Extract color from background shorthand
                color = self._extract_color_from_background(prop_value)
                props.set('background-color', color)
            
            # Always set the property itself (this allows specific properties to override shorthand)
            props.set(prop_name, prop_value)
        
        return props
    
    def _map_selector_to_element(self, selector: str) -> Optional[str]:
        """
        Map a CSS selector to an element name in ElementStyles.
        
        Args:
            selector: CSS selector (single selector, not comma-separated)
            
        Returns:
            Element name or None
        """
        # Clean up selector
        selector = selector.strip()
        
        # Direct match first (most specific)
        if selector in self.SELECTOR_MAP:
            return self.SELECTOR_MAP[selector]
        
        # Don't match complex selectors like "#write>p:first-child" to "#write"
        # Only match if it's an exact match or a simple descendant selector
        # Skip selectors with >, :, [, etc. unless they're in our map
        if any(char in selector for char in ['>', ':', '[', '~', '+']):
            # Check if it's a pseudo-element we care about
            if '::before' in selector:
                base = selector.split('::')[0].strip()
                if base == 'blockquote':
                    return 'blockquote_before'
            return None
        
        # Try to match simple selectors
        for key, value in self.SELECTOR_MAP.items():
            # Exact match
            if selector == key:
                return value
            # Simple descendant selector (e.g., "#write h1" matches "h1")
            if ' ' in key and selector in key.split():
                return value
        
        return None
    
    def _extract_color_from_background(self, background_value: str) -> str:
        """Extract color from background shorthand."""
        parts = background_value.split()
        for part in parts:
            if part.startswith('#') or part.startswith('rgb'):
                return part
            if part.lower() in ['white', 'black', 'red', 'green', 'blue', 'gray', 'grey', 'transparent']:
                return part
        return background_value
