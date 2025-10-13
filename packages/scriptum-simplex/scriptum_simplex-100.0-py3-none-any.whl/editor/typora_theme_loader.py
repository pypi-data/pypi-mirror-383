"""
Typora theme loader for importing Typora CSS themes.

Typora themes are CSS files that define styling for markdown elements.
This module parses Typora CSS themes and converts them to RenderStyle objects.

Supports:
- CSS custom properties (:root variables)
- @font-face declarations and custom font loading
- Folder-based themes with fonts and images
- Background shorthand properties
- Relative path resolution
"""

import os
import re
import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from .render_styles import RenderStyle, FontStyle, ColorScheme, SpacingConfig


class TyporaThemeLoader:
    """Loader for Typora CSS themes."""
    
    def __init__(self):
        """Initialize the Typora theme loader."""
        self.loaded_themes: Dict[str, RenderStyle] = {}
        self.css_variables: Dict[str, str] = {}
        self.theme_folder: Optional[Path] = None
        self.font_faces: Dict[str, Dict[str, Any]] = {}
    
    def load_theme_from_folder(self, folder_path: str) -> Optional[RenderStyle]:
        """
        Load a Typora theme from a folder containing CSS, fonts, and images.
        
        Args:
            folder_path: Path to the theme folder
            
        Returns:
            RenderStyle object if successful, None otherwise
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            logging.error(f"Theme folder does not exist: {folder_path}")
            return None
        
        # Store folder path for relative path resolution
        self.theme_folder = folder
        
        # Look for CSS file (typically named same as folder or theme.css)
        css_files = list(folder.glob('*.css'))
        if not css_files:
            logging.error(f"No CSS file found in theme folder: {folder_path}")
            return None
        
        # Use the first CSS file found
        css_file = css_files[0]
        logging.info(f"Found CSS file: {css_file.name}")
        
        return self.load_theme_from_css(str(css_file))
    
    def load_theme_from_css(self, css_path: str) -> Optional[RenderStyle]:
        """
        Load a Typora theme from a CSS file.
        
        Args:
            css_path: Path to the Typora CSS theme file
            
        Returns:
            RenderStyle object if successful, None otherwise
        """
        css_file = Path(css_path)
        if not css_file.exists() or not css_file.is_file():
            logging.error(f"CSS file does not exist: {css_path}")
            return None
        
        if css_file.suffix.lower() != '.css':
            logging.error(f"File is not a CSS file: {css_path}")
            return None
        
        # Set theme folder if not already set
        if not self.theme_folder:
            self.theme_folder = css_file.parent
        
        try:
            # Read CSS content
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Extract theme name from filename
            theme_name = css_file.stem.replace('-', ' ').title()
            
            # Step 1: Extract CSS variables from :root
            self._extract_css_variables(css_content)
            
            # Step 2: Extract @font-face declarations
            self._extract_font_faces(css_content)
            
            # Step 3: Parse CSS and extract styling
            fonts = self._extract_fonts(css_content)
            colors = self._extract_colors(css_content)
            spacing = self._extract_spacing(css_content)
            
            # Create RenderStyle
            style = RenderStyle(
                name=theme_name,
                fonts=fonts,
                colors=colors,
                spacing=spacing
            )
            
            # Cache the loaded theme
            self.loaded_themes[theme_name.lower()] = style
            
            logging.info(f"Successfully loaded Typora theme: {theme_name}")
            logging.info(f"  - Fonts: {list(fonts.keys())}")
            logging.info(f"  - Colors: bg={colors.background}, text={colors.text}")
            logging.info(f"  - CSS Variables: {len(self.css_variables)} found")
            logging.info(f"  - Font Faces: {len(self.font_faces)} found")
            
            return style
            
        except Exception as e:
            logging.error(f"Error loading Typora theme from {css_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_css_variables(self, css_content: str) -> None:
        """
        Extract CSS custom properties from :root declarations.
        
        Args:
            css_content: CSS file content
        """
        self.css_variables.clear()
        
        # Find :root block
        root_pattern = r':root\s*\{([^}]+)\}'
        root_match = re.search(root_pattern, css_content, re.DOTALL)
        
        if root_match:
            root_block = root_match.group(1)
            # Extract all --variable: value pairs
            var_pattern = r'--([a-zA-Z0-9-]+)\s*:\s*([^;]+);'
            for match in re.finditer(var_pattern, root_block):
                var_name = match.group(1)
                var_value = match.group(2).strip()
                self.css_variables[f'--{var_name}'] = var_value
                logging.debug(f"CSS Variable: --{var_name} = {var_value}")
    
    def _resolve_css_value(self, value: str) -> str:
        """
        Resolve CSS value, replacing var() references with actual values.
        
        Args:
            value: CSS value that might contain var() references
            
        Returns:
            Resolved value
        """
        # Check for var() references
        var_pattern = r'var\((--[a-zA-Z0-9-]+)\)'
        
        def replace_var(match):
            var_name = match.group(1)
            return self.css_variables.get(var_name, match.group(0))
        
        return re.sub(var_pattern, replace_var, value)
    
    def _extract_font_faces(self, css_content: str) -> None:
        """
        Extract @font-face declarations.
        
        Args:
            css_content: CSS file content
        """
        self.font_faces.clear()
        
        # Find all @font-face blocks
        font_face_pattern = r'@font-face\s*\{([^}]+)\}'
        
        for match in re.finditer(font_face_pattern, css_content, re.DOTALL):
            block = match.group(1)
            
            # Extract font-family
            family_match = re.search(r'font-family\s*:\s*["\']([^"\']+)["\']', block)
            if not family_match:
                continue
            
            family = family_match.group(1)
            
            # Extract font-weight (normal, bold, etc.)
            weight_match = re.search(r'font-weight\s*:\s*([^;]+);', block)
            weight = weight_match.group(1).strip() if weight_match else 'normal'
            
            # Extract font-style (normal, italic, etc.)
            style_match = re.search(r'font-style\s*:\s*([^;]+);', block)
            style = style_match.group(1).strip() if style_match else 'normal'
            
            # Extract src URL
            src_match = re.search(r'url\(["\']([^"\']+)["\']\)', block)
            if src_match:
                font_url = src_match.group(1)
                
                # Store font face info
                key = f"{family}_{weight}_{style}"
                self.font_faces[key] = {
                    'family': family,
                    'weight': weight,
                    'style': style,
                    'url': font_url
                }
                logging.debug(f"Font Face: {family} ({weight}, {style}) -> {font_url}")
    
    def _extract_fonts(self, css_content: str) -> Dict[str, FontStyle]:
        """
        Extract font information from CSS.
        
        Args:
            css_content: CSS file content
            
        Returns:
            Dictionary of FontStyle objects
        """
        fonts = {}
        
        # Extract base font family and size from body or #write
        font_family = self._extract_css_property(css_content, ['body', '#write'], 'font-family')
        font_size = self._extract_css_property(css_content, ['body', '#write'], 'font-size')
        
        # Clean up font family (remove quotes, fallbacks)
        if font_family:
            font_family = font_family.split(',')[0].strip().strip('"').strip("'")
        else:
            font_family = "Georgia"
        
        # Parse font size
        if font_size:
            base_size = self._parse_size(font_size, default=12)
        else:
            base_size = 12
        
        # Create font styles
        fonts['normal'] = FontStyle(font_family, base_size)
        fonts['bold'] = FontStyle(font_family, base_size, weight='bold')
        fonts['italic'] = FontStyle(font_family, base_size, slant='italic')
        fonts['bold_italic'] = FontStyle(font_family, base_size, weight='bold', slant='italic')
        
        # Extract heading sizes
        for i in range(1, 4):
            h_size = self._extract_css_property(css_content, [f'h{i}', f'#write h{i}'], 'font-size')
            if h_size:
                size = self._parse_size(h_size, default=base_size + (4 - i) * 3)
            else:
                size = base_size + (4 - i) * 3
            fonts[f'h{i}'] = FontStyle(font_family, size, weight='bold')
        
        # Code font
        code_family = self._extract_css_property(css_content, ['code', 'pre', '.md-fences'], 'font-family')
        if code_family:
            code_family = code_family.split(',')[0].strip().strip('"').strip("'")
        else:
            code_family = "Courier New"
        
        fonts['code'] = FontStyle(code_family, base_size - 1)
        
        return fonts
    
    def _extract_colors(self, css_content: str) -> ColorScheme:
        """
        Extract color information from CSS.
        
        Args:
            css_content: CSS file content
            
        Returns:
            ColorScheme object
        """
        # Extract colors - try both 'color' and 'background-color' and 'background'
        text_color = (self._extract_css_property(css_content, ['body', '#write'], 'color') or 
                     self._resolve_css_value('#000000'))
        
        # Heading color (often different from body text)
        heading_color = (self._extract_css_property(css_content, ['h1', 'h2', 'h3', '#write h1', '#write h2', '#write h3'], 'color') or 
                        text_color)
        
        # Try background-color first, then background shorthand
        bg_color = (self._extract_css_property(css_content, ['body', 'html', '#write'], 'background-color') or
                   self._extract_css_property(css_content, ['body', 'html', '#write'], 'background') or
                   self._resolve_css_value('#FFFFFF'))
        
        # Code colors - try multiple selectors and properties
        code_bg = (self._extract_css_property(css_content, ['code', 'pre', '.md-fences'], 'background-color') or
                  self._extract_css_property(css_content, ['code', 'pre', '.md-fences'], 'background') or
                  self._resolve_css_value('#F5F5F5'))
        code_text = (self._extract_css_property(css_content, ['code', 'pre', '.md-fences'], 'color') or 
                    text_color)
        
        # Link color
        link_color = (self._extract_css_property(css_content, ['a', '#write a'], 'color') or 
                     self._resolve_css_value('#0066CC'))
        
        # Blockquote colors
        blockquote_border = (self._extract_css_property(css_content, ['blockquote::before', 'blockquote'], 'background') or
                            self._extract_css_property(css_content, ['blockquote'], 'border-left-color') or
                            self._resolve_css_value('#CCCCCC'))
        blockquote_bg = (self._extract_css_property(css_content, ['blockquote'], 'background-color') or
                        self._extract_css_property(css_content, ['blockquote'], 'background') or
                        'transparent')
        
        # Table colors
        table_border = (self._extract_css_property(css_content, ['table', 'th', 'td'], 'border-color') or 
                       self._resolve_css_value('#CCCCCC'))
        table_header_bg = (self._extract_css_property(css_content, ['th', 'thead'], 'background-color') or 
                          self._extract_css_property(css_content, ['th', 'thead'], 'background') or
                          self._resolve_css_value('#E8E8E8'))
        
        # Table alternating row - try to infer from theme (darker for dark themes)
        table_alt_row_bg = self._infer_alt_row_color(bg_color)
        
        # Resolve any CSS variables in the extracted colors
        text_color = self._resolve_css_value(text_color)
        bg_color = self._resolve_css_value(bg_color)
        code_bg = self._resolve_css_value(code_bg)
        code_text = self._resolve_css_value(code_text)
        link_color = self._resolve_css_value(link_color)
        table_border = self._resolve_css_value(table_border)
        table_header_bg = self._resolve_css_value(table_header_bg)
        
        # Extract color from background shorthand if needed
        bg_color = self._extract_color_from_background(bg_color)
        code_bg = self._extract_color_from_background(code_bg)
        table_header_bg = self._extract_color_from_background(table_header_bg)
        blockquote_border = self._extract_color_from_background(blockquote_border)
        blockquote_bg = self._extract_color_from_background(blockquote_bg)
        
        return ColorScheme(
            text=self._normalize_color(text_color),
            background=self._normalize_color(bg_color),
            heading=self._normalize_color(heading_color),
            code_background=self._normalize_color(code_bg),
            code_text=self._normalize_color(code_text),
            link=self._normalize_color(link_color),
            blockquote_border=self._normalize_color(blockquote_border),
            blockquote_bg=self._normalize_color(blockquote_bg) if blockquote_bg != 'transparent' else 'transparent',
            table_border=self._normalize_color(table_border),
            table_header_bg=self._normalize_color(table_header_bg),
            table_alt_row_bg=table_alt_row_bg
        )
    
    def _infer_alt_row_color(self, bg_color: str) -> str:
        """
        Infer alternating row color based on background.
        For dark themes, make it slightly lighter. For light themes, slightly darker.
        
        Args:
            bg_color: Background color
            
        Returns:
            Alternating row color
        """
        # Simple heuristic: if background is dark, lighten it; if light, darken it
        try:
            # Normalize and check if it's a hex color
            bg_norm = self._normalize_color(bg_color)
            if bg_norm.startswith('#') and len(bg_norm) == 7:
                # Extract RGB
                r = int(bg_norm[1:3], 16)
                g = int(bg_norm[3:5], 16)
                b = int(bg_norm[5:7], 16)
                
                # Calculate brightness (0-255)
                brightness = (r + g + b) / 3
                
                # If dark (< 128), lighten by 10%; if light, darken by 5%
                if brightness < 128:
                    # Dark theme - lighten
                    r = min(255, int(r * 1.1))
                    g = min(255, int(g * 1.1))
                    b = min(255, int(b * 1.1))
                else:
                    # Light theme - darken
                    r = max(0, int(r * 0.95))
                    g = max(0, int(g * 0.95))
                    b = max(0, int(b * 0.95))
                
                return f'#{r:02X}{g:02X}{b:02X}'
        except:
            pass
        
        # Fallback
        return '#F9F9F9'
    
    def _extract_color_from_background(self, background_value: str) -> str:
        """
        Extract color from background shorthand property.
        
        Args:
            background_value: Value of background property
            
        Returns:
            Extracted color or original value
        """
        # If it's already a simple color, return it
        if background_value.startswith('#') or background_value.startswith('rgb'):
            return background_value
        
        # Try to extract color from background shorthand
        # Format: background: color image repeat position / size
        parts = background_value.split()
        for part in parts:
            if part.startswith('#') or part.startswith('rgb'):
                return part
            # Check for named colors
            if part.lower() in ['white', 'black', 'red', 'green', 'blue', 'gray', 'grey']:
                return part
        
        return background_value
    
    def _extract_spacing(self, css_content: str) -> SpacingConfig:
        """
        Extract spacing information from CSS.
        
        Args:
            css_content: CSS file content
            
        Returns:
            SpacingConfig object
        """
        # Extract margins and padding
        margin = self._extract_css_property(css_content, ['#write'], 'padding') or '20px'
        line_height = self._extract_css_property(css_content, ['body', '#write'], 'line-height') or '1.6'
        
        # Parse margin
        text_margin = self._parse_size(margin.split()[0] if margin else '20px', default=20)
        
        # Parse line height (convert to spacing)
        if line_height:
            try:
                lh = float(line_height.replace('em', '').replace('rem', ''))
                line_spacing = int((lh - 1) * 10)
            except:
                line_spacing = 5
        else:
            line_spacing = 5
        
        return SpacingConfig(
            text_margin=text_margin,
            line_spacing=line_spacing,
            paragraph_spacing=15,
            list_indent=30,
            code_padding=10
        )
    
    def _extract_css_property(self, css_content: str, selectors: list, property_name: str) -> Optional[str]:
        """
        Extract a CSS property value from content.
        
        Args:
            css_content: CSS file content
            selectors: List of CSS selectors to search
            property_name: CSS property name
            
        Returns:
            Property value if found, None otherwise
        """
        for selector in selectors:
            # Build regex pattern to find selector block
            pattern = rf'{re.escape(selector)}\s*\{{([^}}]+)\}}'
            matches = re.finditer(pattern, css_content, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                block = match.group(1)
                # Extract property value
                prop_pattern = rf'{re.escape(property_name)}\s*:\s*([^;]+);'
                prop_match = re.search(prop_pattern, block, re.IGNORECASE)
                if prop_match:
                    return prop_match.group(1).strip()
        
        return None
    
    def _parse_size(self, size_str: str, default: int = 12) -> int:
        """
        Parse a CSS size string to integer pixels.
        
        Args:
            size_str: CSS size string (e.g., "16px", "1.2em")
            default: Default value if parsing fails
            
        Returns:
            Size in pixels
        """
        try:
            # Remove units and convert
            size_str = size_str.lower().strip()
            if 'px' in size_str:
                return int(float(size_str.replace('px', '')))
            elif 'em' in size_str or 'rem' in size_str:
                em_value = float(size_str.replace('em', '').replace('rem', ''))
                return int(em_value * 16)  # Assume 16px base
            elif 'pt' in size_str:
                pt_value = float(size_str.replace('pt', ''))
                return int(pt_value * 1.333)  # Convert pt to px
            else:
                return int(float(size_str))
        except:
            return default
    
    def _normalize_color(self, color_str: str) -> str:
        """
        Normalize a CSS color to hex format.
        
        Args:
            color_str: CSS color string
            
        Returns:
            Normalized hex color
        """
        color_str = color_str.strip().lower()
        
        # Already hex
        if color_str.startswith('#'):
            return color_str.upper()
        
        # RGB/RGBA
        if color_str.startswith('rgb'):
            rgb_match = re.search(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_str)
            if rgb_match:
                r, g, b = rgb_match.groups()
                return f'#{int(r):02X}{int(g):02X}{int(b):02X}'
        
        # Named colors (basic support)
        color_map = {
            'white': '#FFFFFF',
            'black': '#000000',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'gray': '#808080',
            'grey': '#808080',
        }
        
        return color_map.get(color_str, color_str.upper())


# Global instance
_typora_loader = TyporaThemeLoader()


def load_typora_theme_from_folder(folder_path: str) -> Optional[RenderStyle]:
    """
    Load a Typora theme from a folder.
    
    Args:
        folder_path: Path to the theme folder
        
    Returns:
        RenderStyle object if successful, None otherwise
    """
    return _typora_loader.load_theme_from_folder(folder_path)


def load_typora_theme(css_path: str) -> Optional[RenderStyle]:
    """
    Load a Typora theme from a CSS file.
    
    Args:
        css_path: Path to the Typora CSS theme file
        
    Returns:
        RenderStyle object if successful, None otherwise
    """
    return _typora_loader.load_theme_from_css(css_path)
