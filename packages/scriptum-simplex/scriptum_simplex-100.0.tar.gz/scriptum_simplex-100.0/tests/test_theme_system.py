"""
Tests for the theme system.
"""

import pytest
from editor.render_styles import (
    get_default_style,
    get_typora_style,
    get_github_style,
    get_style,
    RenderStyle,
    FontStyle,
    ColorScheme,
    SpacingConfig
)


class TestRenderStyles:
    """Test render style configurations."""

    def test_get_default_style(self):
        """Test default style creation."""
        style = get_default_style()
        assert style.name == "Default"
        assert 'normal' in style.fonts
        assert 'h1' in style.fonts
        assert style.colors.background == 'white'

    def test_get_typora_style(self):
        """Test Typora style creation."""
        style = get_typora_style()
        assert style.name == "Typora"
        assert style.fonts['normal'].family == "Georgia"
        assert style.fonts['normal'].size == 13
        assert style.colors.text == '#333333'
        assert style.spacing.text_margin == 40

    def test_get_github_style(self):
        """Test GitHub style creation."""
        style = get_github_style()
        assert style.name == "GitHub"
        assert style.fonts['normal'].family == "-apple-system, BlinkMacSystemFont, Segoe UI"
        assert style.fonts['normal'].size == 11
        assert style.colors.text == '#24292e'
        assert style.colors.link == '#0366d6'

    def test_get_style_by_name(self):
        """Test getting style by name."""
        default = get_style('default')
        assert default.name == "Default"
        
        typora = get_style('typora')
        assert typora.name == "Typora"
        
        github = get_style('github')
        assert github.name == "GitHub"

    def test_get_style_case_insensitive(self):
        """Test that style names are case-insensitive."""
        style1 = get_style('DEFAULT')
        style2 = get_style('Default')
        style3 = get_style('default')
        
        assert style1.name == style2.name == style3.name

    def test_get_style_invalid_name(self):
        """Test that invalid style name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_style('invalid_style')
        
        assert "Unknown style" in str(exc_info.value)

    def test_font_style_to_dict(self):
        """Test FontStyle conversion to dictionary."""
        font_style = FontStyle(
            family="Arial",
            size=12,
            weight='bold',
            slant='italic'
        )
        
        font_dict = font_style.to_dict()
        assert font_dict['family'] == "Arial"
        assert font_dict['size'] == 12
        assert font_dict['weight'] == 'bold'
        assert font_dict['slant'] == 'italic'

    def test_color_scheme_defaults(self):
        """Test ColorScheme default values."""
        colors = ColorScheme()
        assert colors.text == 'black'
        assert colors.background == 'white'
        assert colors.code_background == '#f8f9fa'

    def test_spacing_config_defaults(self):
        """Test SpacingConfig default values."""
        spacing = SpacingConfig()
        assert spacing.text_margin == 20
        assert spacing.line_spacing == 5
        assert spacing.paragraph_spacing == 15

    def test_render_style_custom(self):
        """Test creating a custom RenderStyle."""
        custom_fonts = {
            'normal': FontStyle('Courier', 10),
            'bold': FontStyle('Courier', 10, weight='bold'),
        }
        custom_colors = ColorScheme(text='#ff0000', background='#000000')
        custom_spacing = SpacingConfig(text_margin=50)
        
        style = RenderStyle(
            name="Custom",
            fonts=custom_fonts,
            colors=custom_colors,
            spacing=custom_spacing
        )
        
        assert style.name == "Custom"
        assert style.fonts['normal'].family == 'Courier'
        assert style.colors.text == '#ff0000'
        assert style.spacing.text_margin == 50

    def test_render_style_auto_fonts(self):
        """Test that RenderStyle creates default fonts if not provided."""
        style = RenderStyle(name="Test")
        
        # Should have auto-created fonts
        assert 'normal' in style.fonts
        assert 'bold' in style.fonts
        assert 'italic' in style.fonts
        assert 'h1' in style.fonts
        assert 'h2' in style.fonts
        assert 'h3' in style.fonts
        assert 'code' in style.fonts


class TestThemeProperties:
    """Test specific theme properties."""

    def test_typora_uses_serif_font(self):
        """Test that Typora theme uses serif font."""
        style = get_typora_style()
        assert style.fonts['normal'].family == "Georgia"

    def test_typora_larger_font_size(self):
        """Test that Typora theme uses larger font size."""
        default = get_default_style()
        typora = get_typora_style()
        
        assert typora.fonts['normal'].size > default.fonts['normal'].size

    def test_typora_generous_margins(self):
        """Test that Typora theme has generous margins."""
        default = get_default_style()
        typora = get_typora_style()
        
        assert typora.spacing.text_margin > default.spacing.text_margin

    def test_github_uses_system_font(self):
        """Test that GitHub theme uses system font."""
        style = get_github_style()
        assert style.fonts['normal'].family == "-apple-system, BlinkMacSystemFont, Segoe UI"

    def test_github_specific_colors(self):
        """Test GitHub theme uses GitHub-specific colors."""
        style = get_github_style()
        assert style.colors.text == '#24292e'
        assert style.colors.link == '#0366d6'
        assert style.colors.code_background == '#f6f8fa'

    def test_all_themes_have_required_fonts(self):
        """Test that all themes have required font keys."""
        required_fonts = ['normal', 'bold', 'italic', 'bold_italic', 
                         'h1', 'h2', 'h3', 'code']
        
        for theme_func in [get_default_style, get_typora_style, get_github_style]:
            style = theme_func()
            for font_key in required_fonts:
                assert font_key in style.fonts, \
                    f"{style.name} theme missing font: {font_key}"

    def test_all_themes_have_color_scheme(self):
        """Test that all themes have complete color schemes."""
        from editor.render_styles import get_typora_night_style, get_typora_academic_style, get_typora_newsprint_style
        for theme_func in [get_default_style, get_typora_style, get_github_style,
                           get_typora_night_style, get_typora_academic_style, get_typora_newsprint_style]:
            style = theme_func()
            assert hasattr(style.colors, 'text')
            assert hasattr(style.colors, 'background')
            assert hasattr(style.colors, 'link')
            assert hasattr(style.colors, 'table_border')
            assert hasattr(style.colors, 'table_header_bg')
            assert hasattr(style.colors, 'table_alt_row_bg')

    def test_all_themes_have_required_fonts(self):
        """Test that all themes have all required font styles."""
        from editor.render_styles import get_typora_night_style, get_typora_academic_style, get_typora_newsprint_style
        for theme_func in [get_default_style, get_typora_style, get_github_style, 
                           get_typora_night_style, get_typora_academic_style, get_typora_newsprint_style]:
            style = theme_func()
            required_fonts = ['normal', 'bold', 'italic', 'bold_italic', 'h1', 'h2', 'h3', 'code']
            for font_name in required_fonts:
                assert font_name in style.fonts, f"Missing font '{font_name}' in {style.name}"
