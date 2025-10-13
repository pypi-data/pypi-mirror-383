"""
Rendering style configurations for Scriptum Simplex.

This module provides a flexible style system that allows different rendering
themes (e.g., default, Typora-like) to be applied to the canvas renderer.
This makes it easy to support different visual styles in the future.
"""

from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class FontStyle:
    """Configuration for a font style."""
    family: str
    size: int
    weight: str = 'normal'  # 'normal' or 'bold'
    slant: str = 'roman'    # 'roman' or 'italic'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for tkinter Font constructor."""
        return {
            'family': self.family,
            'size': self.size,
            'weight': self.weight,
            'slant': self.slant
        }


@dataclass
class ColorScheme:
    """Color scheme for rendering."""
    text: str = 'black'
    background: str = 'white'
    heading: str = 'black'  # Heading color (can be different from text)
    code_background: str = '#f8f9fa'
    code_text: str = '#2d3436'
    link: str = '#0066cc'
    blockquote_border: str = '#cccccc'  # Left border color for blockquotes
    blockquote_bg: str = '#f5f5f5'  # Background for blockquotes
    table_border: str = '#cccccc'
    table_header_bg: str = '#e8e8e8'
    table_alt_row_bg: str = '#f9f9f9'  # Alternating row background for zebra striping


@dataclass
class SpacingConfig:
    """Spacing configuration for layout."""
    text_margin: int = 20
    line_spacing: int = 5
    paragraph_spacing: int = 15
    list_indent: int = 30
    code_padding: int = 10


@dataclass
class RenderStyle:
    """
    Complete rendering style configuration.

    This class encapsulates all style-related settings, making it easy to
    create different themes (e.g., Default, Typora, GitHub) by simply
    instantiating with different parameters.
    """
    name: str
    fonts: Dict[str, FontStyle] = field(default_factory=dict)
    colors: ColorScheme = field(default_factory=ColorScheme)
    spacing: SpacingConfig = field(default_factory=SpacingConfig)

    def __post_init__(self) -> None:
        """Initialize default fonts if not provided."""
        if not self.fonts:
            self.fonts = self._create_default_fonts()

    def _create_default_fonts(self) -> Dict[str, FontStyle]:
        """Create default font configuration."""
        base_family = "Helvetica"
        base_size = 11

        return {
            'normal': FontStyle(base_family, base_size),
            'bold': FontStyle(base_family, base_size, weight='bold'),
            'italic': FontStyle(base_family, base_size, slant='italic'),
            'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                     slant='italic'),
            'h1': FontStyle(base_family, base_size + 8, weight='bold'),
            'h2': FontStyle(base_family, base_size + 4, weight='bold'),
            'h3': FontStyle(base_family, base_size + 2, weight='bold'),
            'code': FontStyle("Courier New", base_size),
        }


# Predefined style themes

def get_default_style() -> RenderStyle:
    """Get the default rendering style."""
    return RenderStyle(name="Default")


def get_typora_style() -> RenderStyle:
    """
    Get a Typora-inspired rendering style.

    This is a placeholder for future implementation. Typora uses:
    - Larger base font size
    - More generous spacing
    - Softer colors
    - Serif fonts for body text (optional)
    """
    # TODO: Implement Typora-specific styling
    # For now, return modified default with some Typora-like characteristics
    base_family = "Georgia"  # Typora often uses serif fonts
    base_size = 13  # Typora uses larger base font

    fonts = {
        'normal': FontStyle(base_family, base_size),
        'bold': FontStyle(base_family, base_size, weight='bold'),
        'italic': FontStyle(base_family, base_size, slant='italic'),
        'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                 slant='italic'),
        'h1': FontStyle(base_family, base_size + 12, weight='bold'),
        'h2': FontStyle(base_family, base_size + 8, weight='bold'),
        'h3': FontStyle(base_family, base_size + 4, weight='bold'),
        'code': FontStyle("Monaco", base_size - 1),
    }

    colors = ColorScheme(
        text='#333333',  # Softer black
        background='#fafafa',  # Off-white
        heading='#333333',
        code_background='#f5f5f5',
        code_text='#555555',
        link='#4078c0',
        blockquote_border='#4078c0',
        blockquote_bg='transparent',
    )

    spacing = SpacingConfig(
        text_margin=40,  # More generous margins
        line_spacing=8,
        paragraph_spacing=20,
        list_indent=32,
        code_padding=12,
    )

    return RenderStyle(
        name="Typora",
        fonts=fonts,
        colors=colors,
        spacing=spacing
    )


def get_github_style() -> RenderStyle:
    """
    Get a GitHub-inspired rendering style.

    GitHub uses:
    - System fonts
    - Moderate spacing
    - GitHub's signature colors
    """
    base_family = "-apple-system, BlinkMacSystemFont, Segoe UI"
    base_size = 11

    fonts = {
        'normal': FontStyle(base_family, base_size),
        'bold': FontStyle(base_family, base_size, weight='bold'),
        'italic': FontStyle(base_family, base_size, slant='italic'),
        'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                 slant='italic'),
        'h1': FontStyle(base_family, base_size + 10, weight='bold'),
        'h2': FontStyle(base_family, base_size + 6, weight='bold'),
        'h3': FontStyle(base_family, base_size + 3, weight='bold'),
        'code': FontStyle("Consolas", base_size),
    }

    colors = ColorScheme(
        text='#24292e',
        background='#ffffff',
        heading='#24292e',
        code_background='#f6f8fa',
        code_text='#24292e',
        link='#0366d6',
        blockquote_border='#dfe2e5',
        blockquote_bg='transparent',
    )

    spacing = SpacingConfig(
        text_margin=20,
        line_spacing=6,
        paragraph_spacing=16,
        list_indent=30,
        code_padding=10,
    )

    return RenderStyle(
        name="GitHub",
        fonts=fonts,
        colors=colors,
        spacing=spacing
    )


def get_typora_night_style() -> RenderStyle:
    """
    Get Typora Night theme - a dark theme with warm colors.
    
    Features:
    - Dark background (#363B40)
    - Light text (#F8F8F2)
    - Warm accent colors
    - Comfortable for night reading
    """
    base_family = "Georgia"
    base_size = 13

    fonts = {
        'normal': FontStyle(base_family, base_size),
        'bold': FontStyle(base_family, base_size, weight='bold'),
        'italic': FontStyle(base_family, base_size, slant='italic'),
        'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                 slant='italic'),
        'h1': FontStyle(base_family, base_size + 12, weight='bold'),
        'h2': FontStyle(base_family, base_size + 8, weight='bold'),
        'h3': FontStyle(base_family, base_size + 4, weight='bold'),
        'code': FontStyle("Monaco", base_size - 1),
    }

    colors = ColorScheme(
        text='#F8F8F2',  # Light text
        background='#363B40',  # Dark gray background
        heading='#F8F8F2',
        code_background='#2D3136',  # Darker gray for code
        code_text='#A6E22E',  # Green code text
        link='#66D9EF',  # Cyan links
        blockquote_border='#66D9EF',
        blockquote_bg='transparent',
        table_border='#555555',
        table_header_bg='#2D3136',
        table_alt_row_bg='#3A3F44',
    )

    spacing = SpacingConfig(
        text_margin=40,
        line_spacing=8,
        paragraph_spacing=20,
        list_indent=32,
        code_padding=12,
    )

    return RenderStyle(
        name="Typora Night",
        fonts=fonts,
        colors=colors,
        spacing=spacing
    )


def get_typora_academic_style() -> RenderStyle:
    """
    Get Typora Academic theme - clean, professional academic style.
    
    Features:
    - Serif fonts (Times New Roman)
    - Generous margins for readability
    - Traditional academic appearance
    - High contrast
    """
    base_family = "Times New Roman"
    base_size = 12

    fonts = {
        'normal': FontStyle(base_family, base_size),
        'bold': FontStyle(base_family, base_size, weight='bold'),
        'italic': FontStyle(base_family, base_size, slant='italic'),
        'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                 slant='italic'),
        'h1': FontStyle(base_family, base_size + 10, weight='bold'),
        'h2': FontStyle(base_family, base_size + 6, weight='bold'),
        'h3': FontStyle(base_family, base_size + 3, weight='bold'),
        'code': FontStyle("Courier New", base_size - 1),
    }

    colors = ColorScheme(
        text='#000000',  # Pure black for academic clarity
        background='#FFFFFF',  # Pure white
        heading='#000000',
        code_background='#F5F5F5',
        code_text='#333333',
        link='#1A0DAB',  # Academic blue
        blockquote_border='#1A0DAB',
        blockquote_bg='transparent',
        table_border='#CCCCCC',
        table_header_bg='#E8E8E8',
        table_alt_row_bg='#F9F9F9',
    )

    spacing = SpacingConfig(
        text_margin=60,  # Wide margins like academic papers
        line_spacing=10,  # Double-spaced feel
        paragraph_spacing=24,
        list_indent=36,
        code_padding=14,
    )

    return RenderStyle(
        name="Typora Academic",
        fonts=fonts,
        colors=colors,
        spacing=spacing
    )


def get_typora_newsprint_style() -> RenderStyle:
    """
    Get Typora Newsprint theme - newspaper-inspired design.
    
    Features:
    - Serif fonts
    - Cream/sepia background
    - Dark brown text
    - Vintage newspaper feel
    """
    base_family = "Georgia"
    base_size = 12

    fonts = {
        'normal': FontStyle(base_family, base_size),
        'bold': FontStyle(base_family, base_size, weight='bold'),
        'italic': FontStyle(base_family, base_size, slant='italic'),
        'bold_italic': FontStyle(base_family, base_size, weight='bold',
                                 slant='italic'),
        'h1': FontStyle(base_family, base_size + 10, weight='bold'),
        'h2': FontStyle(base_family, base_size + 6, weight='bold'),
        'h3': FontStyle(base_family, base_size + 3, weight='bold'),
        'code': FontStyle("Courier New", base_size - 1),
    }

    colors = ColorScheme(
        text='#2B2B2B',  # Dark brown text
        background='#F4ECD8',  # Cream/sepia background
        heading='#2B2B2B',
        code_background='#E8DCC4',  # Darker cream
        code_text='#4A4A4A',
        link='#8B4513',  # Saddle brown
        blockquote_border='#8B4513',
        blockquote_bg='transparent',
        table_border='#D4C4A8',
        table_header_bg='#E0D4BC',
        table_alt_row_bg='#EBE2D0',
    )

    spacing = SpacingConfig(
        text_margin=50,
        line_spacing=7,
        paragraph_spacing=18,
        list_indent=32,
        code_padding=12,
    )

    return RenderStyle(
        name="Typora Newsprint",
        fonts=fonts,
        colors=colors,
        spacing=spacing
    )


def get_style(name: str) -> RenderStyle:
    """
    Get a rendering style by name.

    Args:
        name: Style name ('default', 'typora', 'github', 'typora_night', 'typora_academic', 'typora_newsprint')

    Returns:
        RenderStyle configuration

    Raises:
        ValueError: If style name is not recognized
    """
    styles = {
        'default': get_default_style,
        'typora': get_typora_style,
        'github': get_github_style,
        'typora_night': get_typora_night_style,
        'typora_academic': get_typora_academic_style,
        'typora_newsprint': get_typora_newsprint_style,
    }

    style_func = styles.get(name.lower())
    if style_func is None:
        raise ValueError(
            f"Unknown style: {name}. "
            f"Available styles: {', '.join(styles.keys())}"
        )

    return style_func()
