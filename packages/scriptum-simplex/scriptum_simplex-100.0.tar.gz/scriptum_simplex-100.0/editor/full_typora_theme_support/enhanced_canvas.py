"""
Enhanced Markdown Canvas

Canvas widget that renders markdown with full CSS property support.
"""

import tkinter as tk
from tkinter import font
import logging
from typing import Optional, Dict

from .css_properties import ElementStyles, CSSProperties
from .css_utils import (
    css_to_pixels, css_color_to_hex, get_font_weight_name,
    get_font_slant_name, extract_font_family, calculate_line_height,
    parse_border_width, parse_border_color, should_render_border,
    parse_margin_padding
)
from .syntax_highlighter import highlight_code


class EnhancedMarkdownCanvas(tk.Canvas):
    """
    Enhanced canvas that renders markdown using full CSS properties.
    """
    
    def __init__(self, parent, config=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.config = config  # Configuration object
        self.styles = None
        self.fonts = {}
        self.base_font_size = 16
        self.envelope_left = 30
        self.envelope_right = 580
        self.envelope_width = 550
        self.current_y = 20
        self.markdown_text = ""
        
        # Bind resize event
        self.bind('<Configure>', self._on_configure)
    
    def set_theme(self, styles: ElementStyles) -> None:
        """
        Set the theme styles.
        
        Args:
            styles: ElementStyles with all CSS properties
        """
        self.styles = styles
        
        # Extract base font size from body
        if styles.body.font_size:
            self.base_font_size = css_to_pixels(styles.body.font_size, 16)
        
        # Set canvas background
        if styles.body.background_color:
            bg_color = css_color_to_hex(styles.body.background_color)
            self.configure(bg=bg_color)
        elif styles.body.background:
            bg_color = css_color_to_hex(styles.body.background)
            self.configure(bg=bg_color)
        elif styles.write.background_color:
            bg_color = css_color_to_hex(styles.write.background_color)
            self.configure(bg=bg_color)
        
        # Ensure body has a color (fallback to paragraph or heading color)
        if not styles.body.color:
            if styles.paragraph.color:
                styles.body.color = styles.paragraph.color
                logging.info(f"Body color fallback from paragraph: {styles.body.color}")
            elif styles.h1.color:
                styles.body.color = styles.h1.color
                logging.info(f"Body color fallback from h1: {styles.body.color}")
        
        # Calculate envelope (content area) from #write padding
        # Check specific padding-left first, then fall back to shorthand
        write_props = styles.write
        if write_props.padding_left:
            self.envelope_left = css_to_pixels(write_props.padding_left, self.base_font_size)
            logging.info(f"Applied padding-left from #write: {self.envelope_left}px")
        elif write_props.padding:
            padding = parse_margin_padding(write_props.padding, self.base_font_size)
            self.envelope_left = padding[3]  # left padding
            logging.info(f"Applied padding from #write: {self.envelope_left}px")
        else:
            self.envelope_left = 30  # Default
            logging.info(f"Using default padding: {self.envelope_left}px")
        
        # Apply minimum margins from config
        if self.config:
            min_margins = self.config.get_min_margins()
            logging.info(f"set_theme: Checking minimum margins - current envelope_left={self.envelope_left}, min={min_margins['left']}")
            if self.envelope_left < min_margins['left']:
                logging.info(f"Applying minimum left margin: {min_margins['left']}px (was {self.envelope_left}px)")
                self.envelope_left = min_margins['left']
            if self.current_y < min_margins['top']:
                logging.info(f"Applying minimum top margin: {min_margins['top']}px (was {self.current_y}px)")
                self.current_y = min_margins['top']
        else:
            logging.warning("set_theme: No config available, cannot apply minimum margins!")
        
        # Setup fonts
        self._setup_fonts()
        
        logging.info(f"Theme applied: base_font_size={self.base_font_size}, envelope_left={self.envelope_left}")
    
    def _setup_fonts(self) -> None:
        """Create Tkinter fonts from CSS properties."""
        if not self.styles:
            return
        
        self.fonts.clear()
        
        # Helper to create font from CSS properties
        def create_font(props: CSSProperties, default_size: int = None) -> font.Font:
            family = extract_font_family(props.font_family) if props.font_family else 'Helvetica'
            size = css_to_pixels(props.font_size, self.base_font_size) if props.font_size else (default_size or self.base_font_size)
            weight = get_font_weight_name(props.font_weight) if props.font_weight else 'normal'
            slant = get_font_slant_name(props.font_style) if props.font_style else 'roman'
            
            return font.Font(family=family, size=size, weight=weight, slant=slant)
        
        # Body font
        self.fonts['body'] = create_font(self.styles.body, self.base_font_size)
        
        # Heading fonts
        for i in range(1, 7):
            h_props = getattr(self.styles, f'h{i}')
            self.fonts[f'h{i}'] = create_font(h_props, self.base_font_size + (7-i) * 3)
        
        # Other fonts
        # Code should use monospace if no font-family specified
        code_props = self.styles.code
        if not code_props.font_family:
            code_props.font_family = 'Courier New'
        self.fonts['code'] = create_font(code_props, self.base_font_size - 1)
        
        code_block_props = self.styles.code_block
        if not code_block_props.font_family:
            code_block_props.font_family = 'Courier New'
        self.fonts['code_block'] = create_font(code_block_props, self.base_font_size - 1)
        
        # Blockquote inherits from body if no font specified
        bq_props = self.styles.blockquote
        if not bq_props.font_family:
            bq_props.font_family = self.styles.body.font_family
        self.fonts['blockquote'] = create_font(bq_props, self.base_font_size)
        
        # Paragraph uses body font
        self.fonts['paragraph'] = self.fonts['body']
    
    def _on_configure(self, event):
        """Handle canvas resize."""
        # Update envelope width
        actual_width = self.winfo_width()
        logging.info(f"_on_configure: actual_width={actual_width}, current envelope_left={self.envelope_left}")
        if actual_width > 1:
            # Account for right padding
            right_padding = self.envelope_left  # Symmetric padding
            if self.styles and self.styles.write.padding_right:
                right_padding = css_to_pixels(self.styles.write.padding_right, self.base_font_size)
            
            old_width = self.envelope_width
            self.envelope_right = actual_width - right_padding
            self.envelope_width = max(200, self.envelope_right - self.envelope_left)
            
            # Check for max-width constraint
            if self.styles and self.styles.write.max_width:
                max_width = css_to_pixels(self.styles.write.max_width, self.base_font_size, actual_width)
                if max_width > 0 and self.envelope_width > max_width:
                    # Center the content, but respect minimum margins
                    self.envelope_width = max_width
                    centered_left = (actual_width - max_width) // 2
                    
                    # Apply minimum margin if configured
                    if self.config:
                        min_margins = self.config.get_min_margins()
                        self.envelope_left = max(centered_left, min_margins['left'])
                        logging.info(f"_on_configure: Applied max-width centering with min margin: envelope_left={self.envelope_left} (centered={centered_left}, min={min_margins['left']})")
                    else:
                        self.envelope_left = centered_left
                        logging.info(f"_on_configure: Applied max-width centering: envelope_left={self.envelope_left}")
                    
                    self.envelope_right = self.envelope_left + max_width
            
            # Redraw if width changed significantly
            if abs(old_width - self.envelope_width) > 10 and self.markdown_text:
                logging.info(f"Canvas resized: {old_width} -> {self.envelope_width}, redrawing")
                self.render_markdown(self.markdown_text)
    
    def render_markdown(self, markdown_text: str) -> None:
        """
        Render markdown text with CSS styling.
        
        Args:
            markdown_text: Markdown text to render
        """
        logging.info(f"=== render_markdown START ===")
        logging.info(f"  self.envelope_left at START = {self.envelope_left}")
        logging.info(f"  self.config = {self.config}")
        
        self.markdown_text = markdown_text
        
        # Clear canvas
        self.delete('all')
        logging.info(f"  self.envelope_left after delete('all') = {self.envelope_left}")
        
        # Reset to minimum margins (from config or default)
        if self.config:
            min_margins = self.config.get_min_margins()
            logging.info(f"  min_margins = {min_margins}")
            logging.info(f"  self.envelope_left BEFORE margin check = {self.envelope_left}")
            self.current_y = min_margins['top']
            # CRITICAL: Also ensure envelope_left respects minimum margin
            if self.envelope_left < min_margins['left']:
                logging.info(f"  APPLYING minimum left margin: {min_margins['left']}px (was {self.envelope_left}px)")
                self.envelope_left = min_margins['left']
            else:
                logging.info(f"  envelope_left {self.envelope_left} >= min {min_margins['left']}, no change needed")
            logging.info(f"  self.envelope_left AFTER margin check = {self.envelope_left}")
        else:
            logging.warning("  No config in render_markdown!")
            self.current_y = 20
        
        # If no text, render test content
        if not markdown_text or markdown_text.strip() == '':
            self._render_test_content()
            return
        
        # Parse and render real markdown
        from ..markdown_parser import MarkdownParser
        from .enhanced_canvas_renderer import EnhancedCanvasRenderer
        
        parser = MarkdownParser()
        ast = parser.parse(markdown_text)
        
        # Draw margin guides (for debugging) - comment out to disable
        # self._draw_margin_guides()
        logging.info(f"  self.envelope_left BEFORE renderer = {self.envelope_left}")
        
        # Create enhanced renderer and render
        renderer = EnhancedCanvasRenderer(self)
        renderer.render(ast)
        
        # Update scroll region - ensure it starts at (0,0) not at first item
        bbox = self.bbox('all')
        if bbox:
            # Expand bbox to include (0,0) origin
            x1, y1, x2, y2 = bbox
            scroll_region = (0, 0, max(x2, self.winfo_width()), max(y2, self.winfo_height()))
            self.configure(scrollregion=scroll_region)
            logging.info(f"  Scroll region set to: {scroll_region} (bbox was {bbox})")
        else:
            self.configure(scrollregion=(0, 0, self.winfo_width(), self.winfo_height()))
    
    def _draw_margin_guides(self) -> None:
        """Draw visual guides for margins (debugging)."""
        logging.info(f"=== _draw_margin_guides START ===")
        logging.info(f"  self.config = {self.config}")
        logging.info(f"  self.envelope_left BEFORE = {self.envelope_left}")
        
        if not self.config:
            logging.warning("  No config, returning")
            return
        
        min_margins = self.config.get_min_margins()
        logging.info(f"  min_margins from config = {min_margins}")
        logging.info(f"  self.envelope_left AFTER get_min_margins = {self.envelope_left}")
        
        # Draw left margin line
        self.create_line(
            min_margins['left'], 0,
            min_margins['left'], 2000,
            fill='#FF0000',
            width=1,
            dash=(4, 4),
            tags='margin_guide'
        )
        
        # Draw top margin line
        self.create_line(
            0, min_margins['top'],
            2000, min_margins['top'],
            fill='#FF0000',
            width=1,
            dash=(4, 4),
            tags='margin_guide'
        )
        
        # Add label
        self.create_text(
            min_margins['left'] + 5, 5,
            text=f"Left margin: {min_margins['left']}px",
            font=('Arial', 8),
            anchor='nw',
            fill='#FF0000',
            tags='margin_guide'
        )
        
        logging.info(f"  self.envelope_left at END = {self.envelope_left}")
        logging.info(f"=== _draw_margin_guides END ===")
    
    def _render_test_content(self) -> None:
        """Render test content to verify CSS styling."""
        if not self.styles:
            return
        
        # Render headings
        for i in range(1, 4):  # Just H1-H3 to save space
            self._render_heading(f"Heading {i}", i)
        
        # Render paragraph
        self._render_paragraph("This is a paragraph of text. It should use the body font and color from the theme.")
        
        # Render bullet list
        self._render_list(["First bullet item", "Second bullet item", "Third bullet item"], ordered=False)
        
        # Render numbered list
        self._render_list(["First numbered item", "Second numbered item", "Third numbered item"], ordered=True)
        
        # Render code
        self._render_inline_code("inline code")
        
        # Render code block
        self._render_code_block("def hello():\n    print('Hello, World!')\n    return 42")
        
        # Render blockquote
        self._render_blockquote("This is a blockquote. It should have a left border and proper styling.")
        
        # Render horizontal rule
        self._render_hr()
        
        # Render link
        self._render_link("This is a link", "https://example.com")
        
        # Update scroll region
        self.configure(scrollregion=self.bbox('all'))
    
    def _render_heading(self, text: str, level: int) -> None:
        """Render a heading with CSS styling."""
        h_props = getattr(self.styles, f'h{level}')
        
        # Get margin
        margin_top = 0
        margin_bottom = 0
        if h_props.margin:
            margins = parse_margin_padding(h_props.margin, self.base_font_size)
            margin_top, margin_bottom = margins[0], margins[2]
        elif h_props.margin_top:
            margin_top = css_to_pixels(h_props.margin_top, self.base_font_size)
        if h_props.margin_bottom:
            margin_bottom = css_to_pixels(h_props.margin_bottom, self.base_font_size)
        
        self.current_y += margin_top
        
        # Get color
        color = css_color_to_hex(h_props.color) if h_props.color else css_color_to_hex(self.styles.body.color)
        
        # Render text
        heading_font = self.fonts[f'h{level}']
        logging.info(f"_render_heading: level={level}, x={self.envelope_left}, y={self.current_y}, text='{text}'")
        self.create_text(
            self.envelope_left, self.current_y,
            text=text,
            font=heading_font,
            anchor='nw',
            fill=color
        )
        
        line_height = heading_font.metrics('linespace')
        self.current_y += line_height
        
        # Render border-bottom if specified
        if h_props.border_bottom and should_render_border(h_props.border_bottom):
            border_width = parse_border_width(h_props.border_bottom)
            border_color = parse_border_color(h_props.border_bottom)
            
            # Get padding-bottom
            padding_bottom = 0
            if h_props.padding_bottom:
                padding_bottom = css_to_pixels(h_props.padding_bottom, self.base_font_size)
            
            self.current_y += padding_bottom
            
            # Measure text width for border
            text_width = heading_font.measure(text)
            
            # Draw border under the text, not full width
            self.create_line(
                self.envelope_left, self.current_y,
                self.envelope_left + text_width, self.current_y,
                fill=border_color,
                width=border_width
            )
            
            self.current_y += border_width
        
        self.current_y += margin_bottom
    
    def _render_list(self, items: list, ordered: bool = False) -> None:
        """Render a list (bullet or numbered)."""
        # Use ul properties for both types (they typically have same indentation)
        list_props = self.styles.ul
        
        # Get margin
        margin_top = margin_bottom = 10
        if list_props.margin:
            margins = parse_margin_padding(list_props.margin, self.base_font_size)
            margin_top, margin_bottom = margins[0], margins[2]
        
        # Get padding-left (indentation) - same for both list types
        indent = 30
        if list_props.padding_left:
            indent = css_to_pixels(list_props.padding_left, self.base_font_size)
        
        self.current_y += margin_top
        
        # Get color
        text_color = css_color_to_hex(self.styles.body.color) if self.styles.body.color else '#000000'
        
        # Render each item
        for i, item in enumerate(items):
            # Render marker - position it consistently for both types
            marker_x = self.envelope_left + indent - 25
            if ordered:
                marker = f"{i+1}."
            else:
                marker = "•"
            
            self.create_text(
                marker_x, self.current_y,
                text=marker,
                font=self.fonts['body'],
                anchor='nw',
                fill=text_color
            )
            
            # Render item text - same position for both types
            self.create_text(
                self.envelope_left + indent, self.current_y,
                text=item,
                font=self.fonts['body'],
                anchor='nw',
                fill=text_color,
                width=self.envelope_width - indent
            )
            
            line_height = self.fonts['body'].metrics('linespace')
            self.current_y += line_height + 5
        
        self.current_y += margin_bottom
    
    def _render_paragraph(self, text: str) -> None:
        """Render a paragraph."""
        p_props = self.styles.paragraph
        
        # Get margin
        margin_top = margin_bottom = 0
        if p_props.margin:
            margins = parse_margin_padding(p_props.margin, self.base_font_size)
            margin_top, margin_bottom = margins[0], margins[2]
        
        self.current_y += margin_top
        
        # Get color
        color = css_color_to_hex(self.styles.body.color) if self.styles.body.color else '#000000'
        
        # Render text
        x_pos = self.envelope_left
        logging.info(f"_render_paragraph: x={x_pos}, y={self.current_y}, text='{text[:30]}...', self.envelope_left={self.envelope_left}")
        self.create_text(
            x_pos, self.current_y,
            text=text,
            font=self.fonts['paragraph'],
            anchor='nw',
            fill=color,
            width=self.envelope_width
        )
        
        line_height = self.fonts['paragraph'].metrics('linespace')
        # Estimate lines
        char_width = self.fonts['paragraph'].measure('M')
        chars_per_line = max(1, self.envelope_width // char_width)
        lines = max(1, len(text) // chars_per_line + 1)
        
        self.current_y += line_height * lines + margin_bottom
    
    def _render_inline_code(self, text: str) -> None:
        """Render inline code."""
        code_props = self.styles.code
        
        self.current_y += 10
        
        # Get colors
        bg_color = css_color_to_hex(code_props.background_color) if code_props.background_color else '#F5F5F5'
        text_color = css_color_to_hex(code_props.color) if code_props.color else '#000000'
        
        # Get padding
        padding = 5
        if code_props.padding:
            paddings = parse_margin_padding(code_props.padding, self.base_font_size)
            padding = paddings[0]
        
        # Measure text
        code_font = self.fonts['code']
        text_width = code_font.measure(text)
        text_height = code_font.metrics('linespace')
        
        # Draw background
        self.create_rectangle(
            self.envelope_left, self.current_y,
            self.envelope_left + text_width + padding * 2, self.current_y + text_height + padding * 2,
            fill=bg_color,
            outline=''
        )
        
        # Draw text
        self.create_text(
            self.envelope_left + padding, self.current_y + padding,
            text=text,
            font=code_font,
            anchor='nw',
            fill=text_color
        )
        
        self.current_y += text_height + padding * 2 + 10
    
    def _render_code_block(self, code: str) -> None:
        """Render a code block."""
        block_props = self.styles.code_block
        
        # Get margin
        margin_top = margin_bottom = 15
        if block_props.margin:
            margins = parse_margin_padding(block_props.margin, self.base_font_size)
            margin_top, margin_bottom = margins[0], margins[2]
        elif block_props.margin_top:
            margin_top = css_to_pixels(block_props.margin_top, self.base_font_size)
        if block_props.margin_bottom:
            margin_bottom = css_to_pixels(block_props.margin_bottom, self.base_font_size)
        
        self.current_y += margin_top
        
        # Get colors
        bg_color = css_color_to_hex(block_props.background_color) if block_props.background_color else '#F5F5F5'
        text_color = css_color_to_hex(block_props.color) if block_props.color else '#000000'
        
        # Get padding - respect CSS values, including 0
        # Only use defaults if NO padding is specified at all
        has_any_padding = (block_props.padding or block_props.padding_top or 
                          block_props.padding_bottom or block_props.padding_left or 
                          block_props.padding_right)
        
        logging.info(f"=== CODE BLOCK PADDING DEBUG ===")
        logging.info(f"  CSS padding: {block_props.padding}")
        logging.info(f"  CSS padding-top: {block_props.padding_top}")
        logging.info(f"  CSS padding-right: {block_props.padding_right}")
        logging.info(f"  CSS padding-bottom: {block_props.padding_bottom}")
        logging.info(f"  CSS padding-left: {block_props.padding_left}")
        logging.info(f"  has_any_padding: {has_any_padding}")
        
        if has_any_padding:
            # Start with 0 if any padding is specified
            padding_top = padding_bottom = padding_left = padding_right = 0
            
            # Apply shorthand if it exists
            if block_props.padding:
                paddings = parse_margin_padding(block_props.padding, self.base_font_size)
                padding_top, padding_right, padding_bottom, padding_left = paddings
                logging.info(f"  After shorthand: top={padding_top}, right={padding_right}, bottom={padding_bottom}, left={padding_left}")
            
            # Override with specific sides if they exist (these take priority)
            if block_props.padding_top:
                padding_top = css_to_pixels(block_props.padding_top, self.base_font_size)
                logging.info(f"  Override padding-top: {padding_top}px from '{block_props.padding_top}'")
            if block_props.padding_bottom:
                padding_bottom = css_to_pixels(block_props.padding_bottom, self.base_font_size)
                logging.info(f"  Override padding-bottom: {padding_bottom}px from '{block_props.padding_bottom}'")
            if block_props.padding_left:
                padding_left = css_to_pixels(block_props.padding_left, self.base_font_size)
                logging.info(f"  Override padding-left: {padding_left}px from '{block_props.padding_left}'")
            if block_props.padding_right:
                padding_right = css_to_pixels(block_props.padding_right, self.base_font_size)
                logging.info(f"  Override padding-right: {padding_right}px from '{block_props.padding_right}'")
        else:
            # No padding specified in CSS, use reasonable defaults
            padding_top = padding_bottom = padding_left = padding_right = 10
            logging.info(f"  Using defaults: 10px all sides")
        
        logging.info(f"  FINAL padding: top={padding_top}, right={padding_right}, bottom={padding_bottom}, left={padding_left}")
        logging.info(f"  base_font_size: {self.base_font_size}px")
        logging.info(f"=== END PADDING DEBUG ===")
        
        # Calculate dimensions
        lines = code.split('\n')
        code_font = self.fonts['code_block']
        line_height = code_font.metrics('linespace')
        
        # Find max line width
        max_line_width = 0
        for line in lines:
            line_width = code_font.measure(line)
            max_line_width = max(max_line_width, line_width)
        
        # Calculate block dimensions
        block_width = max_line_width + padding_left + padding_right
        block_height = len(lines) * line_height + padding_top + padding_bottom
        
        logging.info(f"  Block dimensions:")
        logging.info(f"    max_line_width: {max_line_width}px")
        logging.info(f"    block_width: {block_width}px (max_line_width + {padding_left} + {padding_right})")
        logging.info(f"    block_height: {block_height}px ({len(lines)} lines * {line_height} + {padding_top} + {padding_bottom})")
        
        # Draw background - sized to fit content
        rect_x1 = self.envelope_left
        rect_y1 = self.current_y
        rect_x2 = self.envelope_left + block_width
        rect_y2 = self.current_y + block_height
        
        logging.info(f"  Rectangle: ({rect_x1}, {rect_y1}) to ({rect_x2}, {rect_y2})")
        
        self.create_rectangle(
            rect_x1, rect_y1, rect_x2, rect_y2,
            fill=bg_color,
            outline=''
        )
        
        # Draw code lines with syntax highlighting
        code_y = self.current_y + padding_top
        text_x = self.envelope_left + padding_left
        
        logging.info(f"  Text starts at: ({text_x}, {code_y})")
        
        # Try to highlight the code
        try:
            highlighted = highlight_code(code, language='python')  # Default to Python
            
            # Group tokens by line
            current_line_tokens = []
            for token_text, token_color in highlighted:
                if '\n' in token_text:
                    # Token spans multiple lines
                    parts = token_text.split('\n')
                    for i, part in enumerate(parts):
                        if part:  # Skip empty parts
                            current_line_tokens.append((part, token_color))
                        if i < len(parts) - 1:  # Not the last part
                            # Render current line
                            x_pos = text_x
                            for text, color in current_line_tokens:
                                self.create_text(
                                    x_pos, code_y,
                                    text=text,
                                    font=code_font,
                                    anchor='nw',
                                    fill=color
                                )
                                x_pos += code_font.measure(text)
                            code_y += line_height
                            current_line_tokens = []
                else:
                    current_line_tokens.append((token_text, token_color))
            
            # Render last line if any tokens remain
            if current_line_tokens:
                x_pos = text_x
                for text, color in current_line_tokens:
                    self.create_text(
                        x_pos, code_y,
                        text=text,
                        font=code_font,
                        anchor='nw',
                        fill=color
                    )
                    x_pos += code_font.measure(text)
                    
        except Exception as e:
            # Fallback to non-highlighted rendering
            logging.warning(f"Syntax highlighting failed: {e}, falling back to plain text")
            for line in lines:
                self.create_text(
                    text_x, code_y,
                    text=line,
                    font=code_font,
                    anchor='nw',
                    fill=text_color
                )
                code_y += line_height
        
        self.current_y += block_height + margin_bottom
    
    def _render_blockquote(self, text: str) -> None:
        """Render a blockquote with left border."""
        bq_props = self.styles.blockquote
        bq_before = self.styles.blockquote_before
        
        # Get margin
        margin_top = margin_bottom = 10
        margin_left = 20
        if bq_props.margin:
            margins = parse_margin_padding(bq_props.margin, self.base_font_size)
            margin_top, margin_left, margin_bottom = margins[0], margins[3], margins[2]
        
        self.current_y += margin_top
        
        # Get border color and width from ::before pseudo-element
        border_color = '#CCCCCC'
        border_width = 5  # default
        
        # Check if we have blockquote::before properties
        if bq_before.background:
            border_color = css_color_to_hex(bq_before.background)
            logging.info(f"Blockquote border color from ::before: {border_color}")
        elif bq_props.border_left_color:
            border_color = css_color_to_hex(bq_props.border_left_color)
            logging.info(f"Blockquote border color from border-left-color: {border_color}")
        
        # Get border width from ::before
        if bq_before.width:
            border_width = css_to_pixels(bq_before.width, self.base_font_size)
            logging.info(f"Blockquote border width from ::before: {border_width}px")
        
        logging.info(f"Rendering blockquote with border: width={border_width}px, color={border_color}")
        
        # Calculate dimensions
        bq_font = self.fonts['blockquote']
        char_width = bq_font.measure('M')
        chars_per_line = max(1, (self.envelope_width - margin_left - 30) // char_width)
        lines = max(1, len(text) // chars_per_line + 1)
        line_height = bq_font.metrics('linespace')
        bq_height = lines * line_height + 10  # Reduced padding
        
        # Draw left border (thick bar) - height matches content
        self.create_rectangle(
            self.envelope_left + margin_left, self.current_y,
            self.envelope_left + margin_left + border_width, self.current_y + bq_height,
            fill=border_color,
            outline=''
        )
        
        # Draw text
        text_color = css_color_to_hex(self.styles.body.color) if self.styles.body.color else '#000000'
        self.create_text(
            self.envelope_left + margin_left + border_width + 15, self.current_y + 5,
            text=text,
            font=bq_font,
            anchor='nw',
            fill=text_color,
            width=self.envelope_width - margin_left - border_width - 20
        )
        
        self.current_y += bq_height + margin_bottom
    
    def _render_hr(self) -> None:
        """Render a horizontal rule."""
        hr_props = self.styles.hr
        
        # Get margin
        margin_top = margin_bottom = 16
        if hr_props.margin:
            margins = parse_margin_padding(hr_props.margin, self.base_font_size)
            margin_top, margin_bottom = margins[0], margins[2]
        
        self.current_y += margin_top
        
        # Get height and color
        height = 2
        if hr_props.height:
            height = css_to_pixels(hr_props.height, self.base_font_size)
        
        color = '#CCCCCC'
        if hr_props.background_color:
            color = css_color_to_hex(hr_props.background_color)
        elif hr_props.background:
            color = css_color_to_hex(hr_props.background)
        
        # Draw line
        self.create_rectangle(
            self.envelope_left, self.current_y,
            self.envelope_right, self.current_y + height,
            fill=color,
            outline=''
        )
        
        self.current_y += height + margin_bottom
    
    def _render_table_from_ast(self, rows: list[list[str]], alignments: list[str]) -> None:
        """
        Render a table with full theme support.
        
        Args:
            rows: List of rows, where each row is a list of cell texts
            alignments: List of alignment strings ('left', 'center', 'right') for each column
        """
        if not rows:
            return
        
        # Add spacing before table
        self.current_y += 10
        
        # Calculate column widths based on content
        num_cols = len(rows[0]) if rows else 0
        col_widths = [0] * num_cols
        
        # Measure all cells (simple text measurement for now)
        for row in rows:
            for col_idx, cell_text in enumerate(row):
                if col_idx < num_cols:
                    # Use paragraph font for measurement
                    cell_width = self.fonts['paragraph'].measure(cell_text)
                    col_widths[col_idx] = max(col_widths[col_idx], cell_width)
        
        # Add padding to column widths
        cell_padding = 12
        col_widths = [w + cell_padding * 2 for w in col_widths]
        
        # Ensure table fits within envelope
        total_width = sum(col_widths)
        available_width = self.envelope_width
        if total_width > available_width:
            scale_factor = available_width / total_width
            col_widths = [int(w * scale_factor) for w in col_widths]
        
        # Calculate column positions
        col_positions = [self.envelope_left]
        for width in col_widths:
            col_positions.append(col_positions[-1] + width)
        
        # Get theme colors and properties
        table_props = self.styles.table
        td_props = self.styles.td
        th_props = self.styles.th
        tr_props = self.styles.tr
        
        # Border color
        border_color = '#DDDDDD'  # default
        if td_props.border_color:
            border_color = css_color_to_hex(td_props.border_color)
        elif table_props.border_color:
            border_color = css_color_to_hex(table_props.border_color)
        
        # Border width
        border_width = 1  # default
        if table_props.border_width:
            bw = css_to_pixels(table_props.border_width, self.base_font_size)
            if bw:
                border_width = max(1, bw)  # Minimum 1px
        
        # Header background
        header_bg = '#F0F0F0'  # default
        if th_props.background_color:
            header_bg = css_color_to_hex(th_props.background_color)
        elif th_props.background:
            header_bg = css_color_to_hex(th_props.background)
        
        # Alternating row background
        alt_row_bg = '#F9F9F9'  # default
        if tr_props.background_color:
            alt_row_bg = css_color_to_hex(tr_props.background_color)
        
        # Cell padding - check td and th padding
        cell_padding_left = cell_padding_right = 12  # default
        cell_padding_top = cell_padding_bottom = 8  # default
        
        # Try td padding first
        if td_props.padding:
            paddings = parse_margin_padding(td_props.padding, self.base_font_size)
            cell_padding_top, cell_padding_right, cell_padding_bottom, cell_padding_left = paddings
        else:
            # Check individual padding properties
            if td_props.padding_left:
                cell_padding_left = css_to_pixels(td_props.padding_left, self.base_font_size) or cell_padding_left
            if td_props.padding_right:
                cell_padding_right = css_to_pixels(td_props.padding_right, self.base_font_size) or cell_padding_right
            if td_props.padding_top:
                cell_padding_top = css_to_pixels(td_props.padding_top, self.base_font_size) or cell_padding_top
            if td_props.padding_bottom:
                cell_padding_bottom = css_to_pixels(td_props.padding_bottom, self.base_font_size) or cell_padding_bottom
        
        # Cell height based on font + padding
        cell_height = self.fonts['paragraph'].metrics('linespace') + cell_padding_top + cell_padding_bottom
        
        logging.info(f"Table rendering: border={border_color} width={border_width}px, header_bg={header_bg}, alt_bg={alt_row_bg}")
        logging.info(f"  num_cols={num_cols}, cell_height={cell_height}px")
        logging.info(f"  padding: top={cell_padding_top}, right={cell_padding_right}, bottom={cell_padding_bottom}, left={cell_padding_left}")
        
        # Render table border (top)
        table_top = self.current_y
        self.create_line(
            col_positions[0], table_top,
            col_positions[-1], table_top,
            fill=border_color, width=border_width
        )
        
        # Render each row
        for row_idx, row in enumerate(rows):
            row_top = self.current_y
            row_bottom = row_top + cell_height
            
            # Draw background for row
            if row_idx == 0:
                # Header row
                self.create_rectangle(
                    col_positions[0], row_top,
                    col_positions[-1], row_bottom,
                    fill=header_bg, outline=''
                )
            elif row_idx % 2 == 0:
                # Even rows (zebra striping)
                self.create_rectangle(
                    col_positions[0], row_top,
                    col_positions[-1], row_bottom,
                    fill=alt_row_bg, outline=''
                )
            
            # Render cells in this row
            for col_idx, cell_text in enumerate(row):
                if col_idx >= num_cols:
                    break
                
                # Draw cell borders (left and right)
                self.create_line(
                    col_positions[col_idx], row_top,
                    col_positions[col_idx], row_bottom,
                    fill=border_color, width=border_width
                )
                if col_idx == num_cols - 1:
                    self.create_line(
                        col_positions[col_idx + 1], row_top,
                        col_positions[col_idx + 1], row_bottom,
                        fill=border_color, width=border_width
                    )
                
                # Calculate text position based on alignment
                # Check for cell-specific text-align from CSS
                align = alignments[col_idx] if col_idx < len(alignments) else 'left'
                
                # Override with CSS text-align if specified
                if row_idx == 0 and th_props.text_align:
                    align = th_props.text_align
                elif td_props.text_align:
                    align = td_props.text_align
                
                cell_left = col_positions[col_idx]
                cell_right = col_positions[col_idx + 1]
                cell_center_y = row_top + (cell_height // 2)
                
                # Get text color from theme
                if row_idx == 0 and th_props.color:
                    # Header row - use th color
                    text_color = css_color_to_hex(th_props.color)
                elif td_props.color:
                    # Regular cells - use td color
                    text_color = css_color_to_hex(td_props.color)
                elif self.styles.body.color:
                    # Fallback to body color
                    text_color = css_color_to_hex(self.styles.body.color)
                else:
                    # Final fallback
                    text_color = '#000000'
                
                # Get font - use th font for header row, otherwise paragraph font
                if row_idx == 0:
                    # Header row - check for th font properties
                    base_family = self.fonts['paragraph'].actual('family')
                    base_size = self.fonts['paragraph'].actual('size')
                    
                    # Check for th font-family
                    if th_props.font_family:
                        th_family = extract_font_family(th_props.font_family)
                        if th_family:
                            base_family = th_family
                    
                    # Check for th font-size
                    if th_props.font_size:
                        th_size = css_to_pixels(th_props.font_size, self.base_font_size)
                        if th_size:
                            base_size = th_size
                    
                    # Check for th font-weight (bold)
                    is_bold = False
                    if th_props.font_weight:
                        if 'bold' in th_props.font_weight.lower():
                            is_bold = True
                        elif th_props.font_weight.isdigit() and int(th_props.font_weight) >= 600:
                            is_bold = True
                    
                    # Create header font
                    if is_bold:
                        cell_font = font.Font(family=base_family, size=base_size, weight='bold')
                    else:
                        cell_font = font.Font(family=base_family, size=base_size)
                else:
                    cell_font = self.fonts['paragraph']
                
                # Debug logging for first cell
                if row_idx == 0 and col_idx == 0:
                    logging.info(f"Table header cell: text='{cell_text}', color={text_color}, align={align}")
                    logging.info(f"  th.color={th_props.color}, th.text_align={th_props.text_align}")
                    logging.info(f"  Font: family={base_family}, size={base_size}, bold={is_bold if row_idx == 0 else 'N/A'}")
                
                # Render text based on alignment
                if align == 'center':
                    cell_center_x = (cell_left + cell_right) // 2
                    self.create_text(
                        cell_center_x, cell_center_y,
                        text=cell_text,
                        font=cell_font,
                        anchor='center',
                        fill=text_color
                    )
                elif align == 'right':
                    cell_x = cell_right - cell_padding_right
                    self.create_text(
                        cell_x, cell_center_y,
                        text=cell_text,
                        font=cell_font,
                        anchor='e',
                        fill=text_color
                    )
                else:  # left
                    cell_x = cell_left + cell_padding_left
                    self.create_text(
                        cell_x, cell_center_y,
                        text=cell_text,
                        font=cell_font,
                        anchor='w',
                        fill=text_color
                    )
            
            # Draw row bottom border
            self.create_line(
                col_positions[0], row_bottom,
                col_positions[-1], row_bottom,
                fill=border_color, width=border_width
            )
            
            self.current_y = row_bottom
        
        # Add spacing after table
        self.current_y += 10
    
    def _render_link(self, text: str, url: str) -> None:
        """Render a link."""
        link_props = self.styles.link
        
        self.current_y += 10
        
        # Get color
        color = css_color_to_hex(link_props.color) if link_props.color else '#0066CC'
        
        # Render heading text
        logging.info(f"_render_heading: level={level}, x={self.envelope_left}, y={self.current_y}, text='{text}'")
        self.create_text(
            self.envelope_left, self.current_y,
            text=text,
            font=self.fonts[font_key],
            anchor='nw',
            fill=color
        )
        
        # Add underline if text-decoration is underline
        if link_props.text_decoration and 'underline' in link_props.text_decoration.lower():
            text_width = self.fonts[font_key].measure(text)
            line_height = self.fonts[font_key].metrics('linespace')
            text_width = self.fonts['body'].measure(text)
            line_height = self.fonts['body'].metrics('linespace')
            self.create_line(
                self.envelope_left, self.current_y + line_height - 2,
                self.envelope_left + text_width, self.current_y + line_height - 2,
                fill=color,
                width=1
            )
        
        self.current_y += self.fonts['body'].metrics('linespace') + 10
