"""
CSS Utilities

Helper functions for converting CSS values to Tkinter-compatible values.
"""

import re
from typing import Union, Tuple, Optional


def css_to_pixels(value: str, base_size: int = 16, parent_size: Optional[int] = None) -> int:
    """
    Convert CSS size value to pixels.
    
    Args:
        value: CSS size value (e.g., "16px", "1.5em", "120%")
        base_size: Base font size in pixels (default 16)
        parent_size: Parent element size for percentage calculations
        
    Returns:
        Size in pixels
    """
    if not value or value in ['auto', 'inherit', 'initial']:
        return 0
    
    value = str(value).strip().lower()
    
    # Already pixels
    if value.endswith('px'):
        try:
            return int(float(value[:-2]))
        except:
            return 0
    
    # Rem units (relative to root font size) - CHECK BEFORE 'em' since 'rem' ends with 'em'!
    if value.endswith('rem'):
        try:
            rem_value = float(value[:-3])
            return int(rem_value * base_size)
        except:
            return 0
    
    # Em units (relative to base font size)
    if value.endswith('em'):
        try:
            em_value = float(value[:-2])
            return int(em_value * base_size)
        except:
            return 0
    
    # Percentage
    if value.endswith('%'):
        try:
            percent = float(value[:-1])
            if parent_size:
                return int((percent / 100) * parent_size)
            return int((percent / 100) * base_size)
        except:
            return 0
    
    # Point units
    if value.endswith('pt'):
        try:
            pt_value = float(value[:-2])
            return int(pt_value * 1.333)  # 1pt = 1.333px
        except:
            return 0
    
    # Try to parse as number
    try:
        return int(float(value))
    except:
        return 0

def css_color_to_hex(color: str) -> str:
    """
    Convert CSS color to hex format.
    
    Args:
        color: CSS color value (hex, rgb, rgba, or named color)
        
    Returns:
        Hex color string (e.g., '#FF0000')
    """
    if not color:
        return '#000000'
    
    color = color.strip()
    
    # Remove !important flag if present
    if '!important' in color.lower():
        color = color.lower().replace('!important', '').strip()
    
    # Already hex
    if color.startswith('#'):
        return color.upper()
    
    # RGB/RGBA
    if color.startswith('rgb'):
        rgb_match = re.search(r'(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color)
        if rgb_match:
            r, g, b = rgb_match.groups()
            return f'#{int(r):02X}{int(g):02X}{int(b):02X}'
    
    # Named colors
    color_map = {
        'white': '#FFFFFF',
        'black': '#000000',
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'gray': '#808080',
        'grey': '#808080',
        'silver': '#C0C0C0',
        'maroon': '#800000',
        'olive': '#808000',
        'lime': '#00FF00',
        'aqua': '#00FFFF',
        'teal': '#008080',
        'navy': '#000080',
        'fuchsia': '#FF00FF',
        'purple': '#800080',
        'transparent': '#FFFFFF',  # Fallback
    }
    
    return color_map.get(color, '#000000')


def parse_border_width(border_value: str) -> int:
    """
    Extract border width from border shorthand or border-width value.
    
    Args:
        border_value: Border value (e.g., "1px solid #000" or "2px")
        
    Returns:
        Border width in pixels
    """
    if not border_value or border_value == 'none':
        return 0
    
    # Try to find pixel value
    match = re.search(r'(\d+(?:\.\d+)?)\s*px', border_value)
    if match:
        return int(float(match.group(1)))
    
    # Named widths
    width_map = {
        'thin': 1,
        'medium': 2,
        'thick': 3,
    }
    
    for name, width in width_map.items():
        if name in border_value.lower():
            return width
    
    return 0


def parse_border_color(border_value: str) -> str:
    """
    Extract border color from border shorthand.
    
    Args:
        border_value: Border value (e.g., "1px solid #f79f2a")
        
    Returns:
        Hex color string
    """
    if not border_value or border_value == 'none':
        return '#000000'
    
    # Look for hex color
    hex_match = re.search(r'#[0-9a-fA-F]{3,6}', border_value)
    if hex_match:
        return hex_match.group(0).upper()
    
    # Look for rgb color
    rgb_match = re.search(r'rgb\([^)]+\)', border_value)
    if rgb_match:
        return css_color_to_hex(rgb_match.group(0))
    
    return '#000000'


def get_font_weight_name(weight: Union[str, int]) -> str:
    """
    Convert CSS font-weight to Tkinter font weight name.
    
    Args:
        weight: CSS font-weight (normal, bold, 100-900)
        
    Returns:
        'normal' or 'bold'
    """
    if not weight:
        return 'normal'
    
    weight = str(weight).strip().lower()
    
    # Named weights
    if weight in ['bold', 'bolder']:
        return 'bold'
    if weight in ['normal', 'lighter']:
        return 'normal'
    
    # Numeric weights
    try:
        weight_num = int(weight)
        return 'bold' if weight_num >= 600 else 'normal'
    except:
        return 'normal'


def get_font_slant_name(style: str) -> str:
    """
    Convert CSS font-style to Tkinter font slant name.
    
    Args:
        style: CSS font-style (normal, italic, oblique)
        
    Returns:
        'roman' or 'italic'
    """
    if not style:
        return 'roman'
    
    style = style.strip().lower()
    return 'italic' if style in ['italic', 'oblique'] else 'roman'


def extract_font_family(font_family: str) -> str:
    """
    Extract the first font family from a CSS font-family value.
    
    Args:
        font_family: CSS font-family value
        
    Returns:
        First font family name
    """
    if not font_family:
        return 'Helvetica'
    
    # Split by comma
    families = font_family.split(',')
    
    # Get first family and clean it
    first_family = families[0].strip().strip('"').strip("'")
    
    # Remove generic family names if they're the only option
    if first_family.lower() in ['serif', 'sans-serif', 'monospace', 'cursive', 'fantasy']:
        if len(families) > 1:
            return families[1].strip().strip('"').strip("'")
    
    return first_family if first_family else 'Helvetica'


def calculate_line_height(line_height: str, font_size: int) -> int:
    """
    Calculate line height in pixels.
    
    Args:
        line_height: CSS line-height value
        font_size: Font size in pixels
        
    Returns:
        Line height in pixels
    """
    if not line_height or line_height == 'normal':
        return int(font_size * 1.2)  # Default line height
    
    line_height = str(line_height).strip().lower()
    
    # Pixel value
    if line_height.endswith('px'):
        return css_to_pixels(line_height)
    
    # Em/rem value
    if line_height.endswith('em') or line_height.endswith('rem'):
        return css_to_pixels(line_height, font_size)
    
    # Percentage
    if line_height.endswith('%'):
        try:
            percent = float(line_height[:-1])
            return int((percent / 100) * font_size)
        except:
            return int(font_size * 1.2)
    
    # Unitless number (multiplier)
    try:
        multiplier = float(line_height)
        return int(multiplier * font_size)
    except:
        return int(font_size * 1.2)


def parse_margin_padding(value: str, base_size: int = 16) -> Tuple[int, int, int, int]:
    """
    Parse CSS margin or padding shorthand into (top, right, bottom, left).
    
    Args:
        value: CSS margin/padding value
        base_size: Base size for em/rem calculations
        
    Returns:
        Tuple of (top, right, bottom, left) in pixels
    """
    if not value or value == '0':
        return (0, 0, 0, 0)
    
    parts = value.split()
    
    if len(parts) == 1:
        v = css_to_pixels(parts[0], base_size)
        return (v, v, v, v)
    elif len(parts) == 2:
        v = css_to_pixels(parts[0], base_size)
        h = css_to_pixels(parts[1], base_size)
        return (v, h, v, h)
    elif len(parts) == 3:
        t = css_to_pixels(parts[0], base_size)
        h = css_to_pixels(parts[1], base_size)
        b = css_to_pixels(parts[2], base_size)
        return (t, h, b, h)
    elif len(parts) == 4:
        t = css_to_pixels(parts[0], base_size)
        r = css_to_pixels(parts[1], base_size)
        b = css_to_pixels(parts[2], base_size)
        l = css_to_pixels(parts[3], base_size)
        return (t, r, b, l)
    
    return (0, 0, 0, 0)


def should_render_border(border_value: str) -> bool:
    """
    Check if a border should be rendered.
    
    Args:
        border_value: Border CSS value
        
    Returns:
        True if border should be rendered
    """
    if not border_value:
        return False
    
    border_value = border_value.strip().lower()
    
    if border_value in ['none', '0', '0px', 'hidden']:
        return False
    
    return True
