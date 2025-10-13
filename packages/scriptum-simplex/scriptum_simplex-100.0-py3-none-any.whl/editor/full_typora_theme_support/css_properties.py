"""
CSS Properties Model

Comprehensive CSS property storage for all markdown elements.
Supports all CSS properties that Typora themes use.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class CSSProperties:
    """
    Complete CSS properties for a single element.
    Stores all CSS properties that can be extracted from Typora themes.
    """
    # Colors
    color: Optional[str] = None
    background: Optional[str] = None
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_top_color: Optional[str] = None
    border_bottom_color: Optional[str] = None
    border_left_color: Optional[str] = None
    border_right_color: Optional[str] = None
    
    # Borders
    border: Optional[str] = None
    border_top: Optional[str] = None
    border_bottom: Optional[str] = None
    border_left: Optional[str] = None
    border_right: Optional[str] = None
    border_width: Optional[str] = None
    border_style: Optional[str] = None
    border_radius: Optional[str] = None
    
    # Fonts
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    font_style: Optional[str] = None
    line_height: Optional[str] = None
    text_decoration: Optional[str] = None
    text_align: Optional[str] = None
    
    # Spacing
    margin: Optional[str] = None
    margin_top: Optional[str] = None
    margin_bottom: Optional[str] = None
    margin_left: Optional[str] = None
    margin_right: Optional[str] = None
    padding: Optional[str] = None
    padding_top: Optional[str] = None
    padding_bottom: Optional[str] = None
    padding_left: Optional[str] = None
    padding_right: Optional[str] = None
    
    # Dimensions
    width: Optional[str] = None
    max_width: Optional[str] = None
    min_width: Optional[str] = None
    height: Optional[str] = None
    max_height: Optional[str] = None
    min_height: Optional[str] = None
    
    # Other
    opacity: Optional[str] = None
    display: Optional[str] = None
    position: Optional[str] = None
    
    def get(self, property_name: str, default: Any = None) -> Any:
        """Get a CSS property value."""
        # Convert CSS property name to Python attribute name
        attr_name = property_name.replace('-', '_')
        return getattr(self, attr_name, default)
    
    def set(self, property_name: str, value: Any) -> None:
        """Set a CSS property value."""
        # Convert CSS property name to Python attribute name
        attr_name = property_name.replace('-', '_')
        if hasattr(self, attr_name):
            setattr(self, attr_name, value)
    
    def merge(self, other: 'CSSProperties') -> 'CSSProperties':
        """
        Merge another CSSProperties into this one.
        Non-None values from other override values in self.
        """
        result = CSSProperties()
        for attr in dir(self):
            if not attr.startswith('_') and not callable(getattr(self, attr)):
                self_val = getattr(self, attr)
                other_val = getattr(other, attr, None)
                setattr(result, attr, other_val if other_val is not None else self_val)
        return result


@dataclass
class ElementStyles:
    """
    Complete styling information for all markdown elements.
    Each element type has its own CSSProperties.
    """
    # Global
    body: CSSProperties = field(default_factory=CSSProperties)
    write: CSSProperties = field(default_factory=CSSProperties)  # #write container
    
    # Typography
    h1: CSSProperties = field(default_factory=CSSProperties)
    h2: CSSProperties = field(default_factory=CSSProperties)
    h3: CSSProperties = field(default_factory=CSSProperties)
    h4: CSSProperties = field(default_factory=CSSProperties)
    h5: CSSProperties = field(default_factory=CSSProperties)
    h6: CSSProperties = field(default_factory=CSSProperties)
    paragraph: CSSProperties = field(default_factory=CSSProperties)
    
    # Links
    link: CSSProperties = field(default_factory=CSSProperties)
    link_hover: CSSProperties = field(default_factory=CSSProperties)
    
    # Lists
    ul: CSSProperties = field(default_factory=CSSProperties)
    ol: CSSProperties = field(default_factory=CSSProperties)
    li: CSSProperties = field(default_factory=CSSProperties)
    
    # Code
    code: CSSProperties = field(default_factory=CSSProperties)
    code_block: CSSProperties = field(default_factory=CSSProperties)  # pre, .md-fences
    
    # Blockquote
    blockquote: CSSProperties = field(default_factory=CSSProperties)
    blockquote_before: CSSProperties = field(default_factory=CSSProperties)  # ::before pseudo-element
    
    # Tables
    table: CSSProperties = field(default_factory=CSSProperties)
    thead: CSSProperties = field(default_factory=CSSProperties)
    tbody: CSSProperties = field(default_factory=CSSProperties)
    tr: CSSProperties = field(default_factory=CSSProperties)
    th: CSSProperties = field(default_factory=CSSProperties)
    td: CSSProperties = field(default_factory=CSSProperties)
    
    # Horizontal rule
    hr: CSSProperties = field(default_factory=CSSProperties)
    
    # Images
    img: CSSProperties = field(default_factory=CSSProperties)
    
    def get_element(self, element_name: str) -> CSSProperties:
        """Get CSS properties for an element."""
        return getattr(self, element_name, CSSProperties())
    
    def set_element(self, element_name: str, props: CSSProperties) -> None:
        """Set CSS properties for an element."""
        if hasattr(self, element_name):
            setattr(self, element_name, props)


def parse_css_value(value: str, property_name: str) -> Any:
    """
    Parse a CSS value into appropriate Python type.
    
    Args:
        value: CSS value string
        property_name: Name of the CSS property
        
    Returns:
        Parsed value (int, float, str, tuple, etc.)
    """
    value = value.strip()
    
    # Handle 'none', 'inherit', 'initial'
    if value.lower() in ['none', 'inherit', 'initial', 'auto']:
        return value.lower()
    
    # Handle pixel values
    if value.endswith('px'):
        try:
            return int(float(value[:-2]))
        except:
            return value
    
    # Handle em/rem values
    if value.endswith('em') or value.endswith('rem'):
        try:
            return float(value[:-2 if value.endswith('em') else -3])
        except:
            return value
    
    # Handle percentage
    if value.endswith('%'):
        try:
            return float(value[:-1])
        except:
            return value
    
    # Handle numbers
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except:
        pass
    
    # Return as string
    return value


def parse_border_shorthand(border_value: str) -> Dict[str, str]:
    """
    Parse CSS border shorthand into components.
    
    Example: "1px solid #f79f2a" -> {width: "1px", style: "solid", color: "#f79f2a"}
    
    Args:
        border_value: Border shorthand value
        
    Returns:
        Dictionary with width, style, color
    """
    parts = border_value.split()
    result = {}
    
    for part in parts:
        # Check if it's a width (ends with px, em, etc.)
        if any(part.endswith(unit) for unit in ['px', 'em', 'rem', 'pt']):
            result['width'] = part
        # Check if it's a color (starts with # or is a color name)
        elif part.startswith('#') or part.startswith('rgb'):
            result['color'] = part
        # Otherwise it's likely a style
        elif part in ['solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'none', 'hidden']:
            result['style'] = part
    
    return result


def parse_margin_padding_shorthand(value: str) -> Dict[str, str]:
    """
    Parse CSS margin/padding shorthand into components.
    
    Examples:
        "10px" -> {top: "10px", right: "10px", bottom: "10px", left: "10px"}
        "10px 20px" -> {top: "10px", right: "20px", bottom: "10px", left: "20px"}
        "10px 20px 30px" -> {top: "10px", right: "20px", bottom: "30px", left: "20px"}
        "10px 20px 30px 40px" -> {top: "10px", right: "20px", bottom: "30px", left: "40px"}
    
    Args:
        value: Margin/padding shorthand value
        
    Returns:
        Dictionary with top, right, bottom, left
    """
    parts = value.split()
    
    if len(parts) == 1:
        return {'top': parts[0], 'right': parts[0], 'bottom': parts[0], 'left': parts[0]}
    elif len(parts) == 2:
        return {'top': parts[0], 'right': parts[1], 'bottom': parts[0], 'left': parts[1]}
    elif len(parts) == 3:
        return {'top': parts[0], 'right': parts[1], 'bottom': parts[2], 'left': parts[1]}
    elif len(parts) == 4:
        return {'top': parts[0], 'right': parts[1], 'bottom': parts[2], 'left': parts[3]}
    
    return {}
