"""
MarkdownCanvas - A custom Tkinter Canvas widget for rendering Markdown text.

This module provides a lightweight alternative to web-based Markdown renderers
by implementing direct canvas-based rendering of basic Markdown elements.
"""

import tkinter as tk
from tkinter import font
import re
import logging
import os
from typing import List, Tuple, Optional, Dict
from .render_styles import RenderStyle, get_default_style

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available. Image rendering will be disabled.")


class MarkdownCanvas(tk.Canvas):
    """
    A custom Canvas widget that renders basic Markdown text directly onto the canvas.

    Supports:
    - Headings (# ## ###)
    - Bullet lists (* -)
    - Numbered lists (1. 2.)
    - Bold text (**text** or __text__)
    - Italic text (*text* or _text_)
    - Paragraphs with automatic text wrapping
    - Scrollable content
    """

    def __init__(self, parent, theme: Optional[RenderStyle] = None, **kwargs):
        """
        Initialize the MarkdownCanvas widget.
        
        Args:
            parent: Parent widget
            theme: Optional RenderStyle theme (defaults to Default theme)
            **kwargs: Additional canvas options
        """
        # Set default canvas options
        canvas_options = {
            'bg': 'white',
            'highlightthickness': 0,
            'scrollregion': (0, 0, 0, 0)
        }
        canvas_options.update(kwargs)

        super().__init__(parent, **canvas_options)

        # Initialize theme
        self.current_theme = theme if theme else get_default_style()
        
        # Initialize fonts from theme
        self._setup_fonts()

        # Canvas dimensions and layout settings from theme
        self.text_margin = self.current_theme.spacing.text_margin
        self.line_spacing = self.current_theme.spacing.line_spacing
        self.paragraph_spacing = self.current_theme.spacing.paragraph_spacing
        self.list_indent = self.current_theme.spacing.list_indent
        self.current_y = self.text_margin

        # Store last width to prevent redundant re-renders
        self.last_width = 0
        self.markdown_text = ""
        
        # Track links for click handling
        self.links = []  # List of (bbox, url) tuples
        
        # Image cache to prevent garbage collection
        self.image_cache: Dict[str, ImageTk.PhotoImage] = {}
        
        # Image resolver function (set by view/controller)
        self.image_path_resolver = None

        # Bind canvas resize to update text wrapping
        self.bind('<Configure>', self._on_canvas_configure)

        # Enable mouse wheel scrolling
        self.bind('<MouseWheel>', self._on_mousewheel)
        self.bind('<Button-4>', self._on_mousewheel)
        self.bind('<Button-5>', self._on_mousewheel)
        
        # Bind mouse events for link handling
        self.bind('<Button-1>', self._on_click)
        self.bind('<Motion>', self._on_motion)

        # Calculate drawable envelope (content area within margins)
        self._update_drawable_envelope()

    def _setup_fonts(self):
        """Initialize font configurations from theme."""
        self.fonts = {}
        for font_name, font_style in self.current_theme.fonts.items():
            self.fonts[font_name] = font.Font(**font_style.to_dict())
    
    def set_theme(self, theme: RenderStyle) -> None:
        """
        Change the rendering theme and re-render content.
        
        Args:
            theme: New RenderStyle theme to apply
        """
        self.current_theme = theme
        
        # Update spacing from theme
        self.text_margin = theme.spacing.text_margin
        self.line_spacing = theme.spacing.line_spacing
        self.paragraph_spacing = theme.spacing.paragraph_spacing
        self.list_indent = theme.spacing.list_indent
        
        # Update fonts from theme
        self._setup_fonts()
        
        # Update background color
        self.configure(bg=theme.colors.background)
        
        # Update drawable envelope with new margins
        self._update_drawable_envelope()
        
        # Re-render current content if any
        if self.markdown_text:
            self.render_markdown(self.markdown_text)

    def _update_drawable_envelope(self):
        """Calculate the drawable envelope (content area within margins)."""
        # Get the actual available width, accounting for widget hierarchy
        actual_width = self.winfo_width()
        if actual_width <= 1:  # Canvas not yet laid out
            actual_width = 600  # Default width for calculations

        # Calculate envelope WITHOUT hierarchy compensation - let margins be pure
        self.envelope_left = self.text_margin  # Left margin
        self.envelope_right = actual_width - self.text_margin  # Right margin
        self.envelope_width = max(200, self.envelope_right - self.envelope_left)

        # Ensure envelope doesn't go negative
        if self.envelope_right <= self.envelope_left:
            self.envelope_right = actual_width - 10
            self.envelope_width = max(100, self.envelope_right - self.envelope_left)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta:
            # Windows
            self.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            # Linux
            if event.num == 4:
                self.yview_scroll(-1, "units")
            elif event.num == 5:
                self.yview_scroll(1, "units")

    def update_scrollregion(self) -> None:
        """Update the canvas scroll region to fit all rendered content."""
        import logging
        bbox = self.bbox('all')
        logging.info(f"MarkdownCanvas.update_scrollregion: bbox = {bbox}")
        if bbox:
            scroll_region = (bbox[0], bbox[1], bbox[2] + 50, bbox[3] + 50)
            logging.info(f"Setting scrollregion to: {scroll_region}")
            self.configure(scrollregion=scroll_region)
        else:
            logging.warning("No bbox found - canvas has no items!")

    def render_markdown(self, markdown_text: str) -> None:
        """
        Clear the canvas and render the provided Markdown text.

        Args:
            markdown_text (str): The Markdown text to render
        """
        self.markdown_text = markdown_text

        # Clear the canvas, links, and image cache
        self.delete('all')
        self.links = []
        self.image_cache.clear()
        self.current_y = self.text_margin

        if not markdown_text.strip():
            return

        # Split text into lines and process each line
        lines = markdown_text.split('\n')

        # Track list numbering and blocks
        ordered_list_counter = 0
        in_ordered_list = False
        code_block_lines: List[str] = []
        table_lines: List[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Handle code blocks
            if line.strip().startswith('```'):
                code_block_lines = []
                i += 1  # Move past the opening fence
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_block_lines.append(lines[i])
                    i += 1
                self._render_code_block(code_block_lines)
                i += 1  # Move past the closing fence
                continue

            # Handle single-line elements
            line = line.rstrip()
            if not line.strip():
                self.current_y += self.line_spacing
                in_ordered_list = False
            elif line.startswith('### '):
                self._render_heading(line[4:], 'h3')
                in_ordered_list = False
            elif line.startswith('## '):
                self._render_heading(line[3:], 'h2')
                in_ordered_list = False
            elif line.startswith('# '):
                self._render_heading(line[2:], 'h1')
                in_ordered_list = False
            elif line.startswith('* ') or line.startswith('- '):
                self._render_bullet_list_item(line[2:])
                in_ordered_list = False
            # Handle tables
            elif '|' in line and self._is_table_line(line, lines, i):
                table_lines = []
                # Collect all lines of the table
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1

                self._render_table(table_lines)
                in_ordered_list = False
                continue  # Continue to next iteration, as i is already advanced

            elif re.match(r'^\d+\.\s', line):
                match = re.match(r'^(\d+)\.\s(.*)$', line)
                if match:
                    number = int(match.group(1))
                    text = match.group(2)
                    if not in_ordered_list or number == 1:
                        ordered_list_counter = number
                        in_ordered_list = True
                    else:
                        ordered_list_counter += 1
                    self._render_numbered_list_item(text, ordered_list_counter)
            else:
                self._render_paragraph(line)
                in_ordered_list = False

            i += 1  # Increment for all single-line elements

    def render_markdown_deferred(self, markdown_text: str, delay_ms: int = 100):
        """
        Render Markdown text with a delay to ensure proper canvas sizing.

        Args:
            markdown_text (str): The Markdown text to render
            delay_ms (int): Delay in milliseconds before rendering
        """
        def delayed_render():
            self.render_markdown(markdown_text)

        # Schedule the rendering with a delay
        self.after(delay_ms, delayed_render)

    def _on_canvas_configure(self, event):
        """Handle canvas resize events to update text wrapping."""
        # Only re-render if we have content and the width actually changed
        new_width = self.winfo_width()
        if new_width != self.last_width and new_width > 1:
            self.last_width = new_width
            logging.info(f"Canvas resized to width: {new_width}")
            # First, update the envelope with the new width
            self._update_drawable_envelope()
            # Then, defer the re-render to ensure layout updates are processed
            if self.markdown_text:
                self.after_idle(lambda: self.render_markdown(self.markdown_text))
                logging.info("Scheduled canvas re-render after resize")

    def _render_heading(self, text: str, level: str):
        """Render a heading with the specified level."""
        import logging
        logging.info(f"_render_heading called: '{text}' level={level}")
        
        self.current_y += self.paragraph_spacing

        # Parse inline formatting
        text_segments = self._parse_inline_formatting(text)
        logging.info(f"Heading text segments: {text_segments}")

        x = self.envelope_left
        heading_y_start = self.current_y

        for segment_text, is_bold, is_italic, critic_type in text_segments:
            # Override with heading font (always bold)
            heading_font = self.fonts[level].copy()
            if is_italic:
                heading_font.configure(slant='italic')

            # Use heading color from theme, unless it's CriticMarkup
            if critic_type:
                text_color = self._get_critic_color(critic_type)
            else:
                text_color = self.current_theme.colors.heading

            # Create text on canvas
            logging.info(f"Creating heading text at ({x}, {self.current_y}): '{segment_text}'")
            text_id = self.create_text(
                x, self.current_y,
                text=segment_text,
                font=heading_font,
                anchor='nw',
                fill=text_color
            )
            logging.info(f"Created text item with id: {text_id}")

            # Move x position for next segment
            x += heading_font.measure(segment_text)

        # Move to next line
        line_height = self.fonts[level].metrics('linespace')
        self.current_y += line_height
        
        # Add underline for H1 and H2 if theme is dark (common in dark themes)
        if level in ['h1', 'h2']:
            # Draw underline
            underline_y = self.current_y + 2
            self.create_line(
                self.envelope_left, underline_y,
                self.envelope_right, underline_y,
                fill=self.current_theme.colors.heading,
                width=2 if level == 'h1' else 1
            )
            self.current_y += 5  # Extra space after underline
        
        self.current_y += self.paragraph_spacing
        logging.info(f"Heading rendered, current_y now: {self.current_y}")

    def _render_bullet_list_item(self, text: str):
        """Render a bullet list item."""
        # Add bullet symbol
        bullet_x = self.envelope_left + self.list_indent
        bullet_y = self.current_y

        self.create_text(
            bullet_x - 15, bullet_y,
            text='•',
            font=self.fonts['normal'],
            anchor='nw',
            fill=self.current_theme.colors.text
        )

        # Render the text with inline formatting
        self._render_text_with_formatting(text, bullet_x, bullet_y)

    def _render_numbered_list_item(self, text: str, number: int):
        """Render a numbered list item."""
        # Add number
        number_x = self.envelope_left + self.list_indent
        number_y = self.current_y

        self.create_text(
            number_x - 20, number_y,
            text=f'{number}.',
            font=self.fonts['normal'],
            anchor='nw',
            fill=self.current_theme.colors.text
        )

        # Render the text with inline formatting
        self._render_text_with_formatting(text, number_x, number_y)

    def _render_paragraph(self, text: str):
        """Render a regular paragraph."""
        self.current_y += self.line_spacing
        self._render_text_with_formatting(text, self.envelope_left, self.current_y)
    
    def _render_link(self, link_text: str, url: str, x: int, y: int) -> int:
        """
        Render a clickable link and track its position.
        
        Args:
            link_text: The display text for the link
            url: The URL to open when clicked
            x: X position to render at
            y: Y position to render at
            
        Returns:
            Width of the rendered link
        """
        # Use theme link color
        link_color = self.current_theme.colors.link
        link_font = self.fonts['normal']
        
        # Create the link text with underline
        text_id = self.create_text(
            x, y,
            text=link_text,
            font=link_font,
            anchor='nw',
            fill=link_color
        )
        
        # Get the bounding box of the text
        bbox = self.bbox(text_id)
        if bbox:
            # Store the link for click detection
            self.links.append((bbox, url))
            logging.debug(f"Registered link: {link_text} -> {url} at {bbox}")
        
        # Return the width of the link
        return link_font.measure(link_text)
    
    def _render_image(self, image_path: str, alt_text: str) -> None:
        """
        Render an image at full width (respecting margins).
        
        Args:
            image_path: Path to the image file
            alt_text: Alternative text for the image
        """
        if not PIL_AVAILABLE:
            # Fallback: render alt text
            self._render_paragraph(f"[Image: {alt_text}]")
            return
        
        # Resolve image path
        if self.image_path_resolver:
            resolved_path = self.image_path_resolver(image_path)
        else:
            resolved_path = image_path
        
        # Check if image exists
        if not os.path.exists(resolved_path):
            logging.warning(f"Image not found: {resolved_path}")
            self._render_paragraph(f"[Image not found: {alt_text}]")
            return
        
        try:
            # Load image
            img = Image.open(resolved_path)
            
            # Calculate target width (full width minus margins)
            target_width = self.envelope_width
            
            # Calculate height maintaining aspect ratio
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            
            # Resize image
            img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and cache it
            photo = ImageTk.PhotoImage(img_resized)
            self.image_cache[resolved_path] = photo
            
            # Add spacing before image
            self.current_y += self.paragraph_spacing
            
            # Create image on canvas
            self.create_image(
                self.envelope_left,
                self.current_y,
                image=photo,
                anchor='nw'
            )
            
            # Update current_y to be below the image
            self.current_y += target_height + self.paragraph_spacing
            
            logging.info(f"Rendered image: {resolved_path} ({target_width}x{target_height})")
            
        except Exception as e:
            logging.error(f"Error rendering image {resolved_path}: {e}")
            self._render_paragraph(f"[Error loading image: {alt_text}]")

    def _render_text_with_formatting(self, text: str, start_x: int, start_y: int):
        """Render text with inline formatting (bold/italic) and handle wrapping."""
        # Parse inline formatting
        text_segments = self._parse_inline_formatting(text)

        current_x = start_x
        current_y = start_y
        line_height = self.fonts['normal'].metrics('linespace')
        space_width = self.fonts['normal'].measure(' ')

        for segment_text, is_bold, is_italic, critic_type in text_segments:
            font_key = 'normal'
            if is_bold and is_italic:
                font_key = 'bold_italic'
            elif is_bold:
                font_key = 'bold'
            elif is_italic:
                font_key = 'italic'

            segment_font = self.fonts[font_key]
            segment_width = segment_font.measure(segment_text)
            
            # Determine text color based on CriticMarkup
            text_color = self._get_critic_color(critic_type)
            words = segment_text.split(' ')
            for i, word in enumerate(words):
                if not word:
                    continue

                word_width = segment_font.measure(word)

                # Check if word fits on the current line
                if current_x + word_width > self.envelope_right and current_x > start_x:
                    current_x = start_x  # Reset to the initial start position for the line
                    current_y += line_height

                self.create_text(current_x, current_y, text=word,
                                 font=segment_font, anchor='nw', fill=text_color)
                current_x += word_width

                # Add space if it's not the last word
                if i < len(words) - 1:
                    current_x += space_width

        # Update current_y for the next element
        self.current_y = current_y + line_height + self.line_spacing

    def _render_code_block(self, lines: List[str]):
        """Render a multi-line code block with a background."""
        self.current_y += self.paragraph_spacing

        # Use drawable envelope for consistent margins
        max_text_width = 0
        line_height = self.fonts['code'].metrics('linespace')
        for line in lines:
            max_text_width = max(max_text_width, self.fonts['code'].measure(line))

        # Calculate height needed for block
        line_height = self.fonts['code'].metrics('linespace')
        block_height = line_height * len(lines) + 10  # 10px padding

        # Draw background rectangle within drawable envelope
        self.create_rectangle(
            self.envelope_left, self.current_y - 5,
            self.envelope_right, self.current_y + block_height,
            fill=self.current_theme.colors.code_background,
            outline=self.current_theme.colors.table_border
        )

        # Render each line of code within the envelope
        code_x = self.envelope_left + 10  # 10px internal padding
        code_y = self.current_y
        for line in lines:
            self.create_text(
                code_x, code_y,
                text=line,
                font=self.fonts['code'],
                anchor='nw',
                fill=self.current_theme.colors.code_text
            )
            code_y += line_height

        # Update current_y to be below the code block
        self.current_y += block_height + self.paragraph_spacing

    def _render_table(self, lines: List[str]) -> None:
        """Render a Markdown table (legacy line-based method)."""
        # Placeholder for backward compatibility
        # Tables are now rendered via _render_table_from_ast()
        self.current_y += self.paragraph_spacing
        self.create_text(
            self.envelope_left, self.current_y,
            text="[Table rendering requires AST - use CanvasRenderer]",
            font=self.fonts['italic'],
            anchor='nw',
            fill='gray'
        )
        self.current_y += self.fonts['normal'].metrics('linespace') + self.paragraph_spacing

    def _render_table_from_ast(
        self,
        rows: List[List[str]],
        alignments: List[str]
    ) -> None:
        """
        Render a table from parsed AST data.

        Args:
            rows: List of rows, where each row is a list of cell texts
            alignments: List of alignment strings ('left', 'center', 'right')
                       for each column
        """
        if not rows:
            return

        self.current_y += self.paragraph_spacing

        # Calculate column widths based on content
        num_cols = len(rows[0]) if rows else 0
        col_widths = [0] * num_cols

        # Parse inline formatting for all cells and measure
        cell_segments = []  # Store parsed segments for reuse
        for row in rows:
            row_segments = []
            for col_idx, cell_text in enumerate(row):
                segments = self._parse_inline_formatting(cell_text)
                row_segments.append(segments)

                # Calculate width needed for this cell
                cell_width = 0
                for seg_text, is_bold, is_italic, critic_type in segments:
                    font_key = 'normal'
                    if is_bold and is_italic:
                        font_key = 'bold_italic'
                    elif is_bold:
                        font_key = 'bold'
                    elif is_italic:
                        font_key = 'italic'
                    cell_width += self.fonts[font_key].measure(seg_text)

                if col_idx < num_cols:
                    col_widths[col_idx] = max(col_widths[col_idx], cell_width)

            cell_segments.append(row_segments)

        # Add padding to column widths - increased for better spacing
        cell_padding = 12  # Increased from 10 to 12
        col_widths = [w + cell_padding * 2 for w in col_widths]

        # Ensure table fits within envelope, scale down if needed
        total_width = sum(col_widths)
        available_width = self.envelope_width
        if total_width > available_width:
            scale_factor = available_width / total_width
            col_widths = [int(w * scale_factor) for w in col_widths]

        # Calculate column positions
        col_positions = [self.envelope_left]
        for width in col_widths:
            col_positions.append(col_positions[-1] + width)

        # Cell and row heights - increased for better padding
        cell_height = self.fonts['normal'].metrics('linespace') + 16  # Increased from 10 to 16
        border_color = self.current_theme.colors.table_border
        header_bg = self.current_theme.colors.table_header_bg

        # Render table border (top)
        table_top = self.current_y
        self.create_line(
            col_positions[0], table_top,
            col_positions[-1], table_top,
            fill=border_color, width=1
        )

        # Render each row
        for row_idx, (row, row_segments) in enumerate(zip(rows, cell_segments)):
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
                alt_row_bg = self.current_theme.colors.table_alt_row_bg
                self.create_rectangle(
                    col_positions[0], row_top,
                    col_positions[-1], row_bottom,
                    fill=alt_row_bg, outline=''
                )

            # Render cells in this row
            for col_idx, segments in enumerate(row_segments):
                if col_idx >= num_cols:
                    break

                # Draw cell borders (left and right)
                self.create_line(
                    col_positions[col_idx], row_top,
                    col_positions[col_idx], row_bottom,
                    fill=border_color, width=1
                )
                if col_idx == num_cols - 1:
                    self.create_line(
                        col_positions[col_idx + 1], row_top,
                        col_positions[col_idx + 1], row_bottom,
                        fill=border_color, width=1
                    )

                # Calculate text position based on alignment
                align = alignments[col_idx] if col_idx < len(alignments) else 'left'
                cell_left = col_positions[col_idx]
                cell_right = col_positions[col_idx + 1]
                # Position text slightly above center for better bottom padding
                cell_center_y = row_top + (cell_height // 2) - 2

                # Render text with inline formatting
                if align == 'center':
                    cell_center_x = (cell_left + cell_right) // 2
                    self._render_cell_text(
                        segments, cell_center_x, cell_center_y,
                        anchor='center', bold_header=(row_idx == 0)
                    )
                elif align == 'right':
                    cell_x = cell_right - cell_padding
                    self._render_cell_text(
                        segments, cell_x, cell_center_y,
                        anchor='e', bold_header=(row_idx == 0)
                    )
                else:  # left
                    cell_x = cell_left + cell_padding
                    self._render_cell_text(
                        segments, cell_x, cell_center_y,
                        anchor='w', bold_header=(row_idx == 0)
                    )

            # Draw row bottom border
            self.create_line(
                col_positions[0], row_bottom,
                col_positions[-1], row_bottom,
                fill=border_color, width=1
            )

            self.current_y = row_bottom

        self.current_y += self.paragraph_spacing

    def _render_cell_text(
        self,
        segments: List[Tuple[str, bool, bool, str]],
        x: int,
        y: int,
        anchor: str = 'w',
        bold_header: bool = False
    ) -> None:
        """
        Render text segments within a table cell.

        Args:
            segments: List of (text, is_bold, is_italic, critic_type) tuples
            x: X position
            y: Y position
            anchor: Text anchor ('w', 'center', 'e')
            bold_header: If True, make all text bold (for header row)
        """
        # For center and right alignment, we need to calculate total width first
        if anchor in ('center', 'e'):
            total_width = 0
            for seg_text, is_bold, is_italic, critic_type in segments:
                font_key = 'normal'
                if bold_header or (is_bold and is_italic):
                    font_key = 'bold_italic'
                elif bold_header or is_bold:
                    font_key = 'bold'
                elif is_italic:
                    font_key = 'italic'
                total_width += self.fonts[font_key].measure(seg_text)

            # Adjust starting position
            if anchor == 'center':
                current_x = x - total_width // 2
            else:  # anchor == 'e'
                current_x = x - total_width
        else:
            current_x = x

        # Render each segment
        for seg_text, is_bold, is_italic, critic_type in segments:
            font_key = 'normal'
            if bold_header or (is_bold and is_italic):
                font_key = 'bold_italic'
            elif bold_header or is_bold:
                font_key = 'bold'
            elif is_italic:
                font_key = 'italic'

            # Get CriticMarkup color
            text_color = self._get_critic_color(critic_type)

            self.create_text(
                current_x, y,
                text=seg_text,
                font=self.fonts[font_key],
                anchor='nw' if anchor in ('w', 'center', 'e') else anchor,
                fill=text_color
            )

            # Move to next segment position
            current_x += self.fonts[font_key].measure(seg_text)

    def _is_table_line(self, line: str, all_lines: List[str], current_index: int) -> bool:
        """Check if a line is part of a valid Markdown table."""
        if '|' not in line:
            return False

        # A table must have at least a header and a separator line
        if current_index + 1 >= len(all_lines):
            return False

        header = line.strip()
        separator = all_lines[current_index + 1].strip()

        # Basic validation for header and separator
        if not (header.startswith('|') and header.endswith('|')):
            return False
        if not (separator.startswith('|') and separator.endswith('|')):
            return False

        # Check if separator line has valid format, e.g., |---|---| or |:--|--:|
        separator_parts = [part.strip() for part in separator.split('|')][1:-1]
        if not all(re.match(r':?-+:?', part) for part in separator_parts):
            return False

        return True

    def _parse_inline_formatting(self, text: str) -> List[Tuple[str, bool, bool, str, bool]]:
        """
        Parse text for inline formatting (bold/italic/strikethrough) and CriticMarkup.

        Returns:
            List of tuples (text, is_bold, is_italic, critic_type, is_strikethrough)
            critic_type can be: '', 'addition', 'deletion', 'substitution', 'highlight', 'comment'
        """
        segments = []
        remaining_text = text
        
        # Combined pattern for CriticMarkup and formatting
        # Process CriticMarkup first, then regular formatting within each segment
        critic_patterns = [
            (r'\{\+\+([^}]+)\+\+\}', 'addition'),
            (r'\{--([^}]+)--\}', 'deletion'),
            (r'\{~~([^}]+)~>([^}]+)~~\}', 'substitution'),
            (r'\{==([^}]+)==\}', 'highlight'),
            (r'\{>>([^}]+)<<\}', 'comment'),
        ]
        
        pos = 0
        while pos < len(remaining_text):
            # Find the earliest CriticMarkup pattern
            earliest_match = None
            earliest_pos = len(remaining_text)
            earliest_type = ''
            
            for pattern, critic_type in critic_patterns:
                match = re.search(pattern, remaining_text[pos:])
                if match and match.start() + pos < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start() + pos
                    earliest_type = critic_type
            
            if earliest_match:
                # Add text before CriticMarkup
                if earliest_pos > pos:
                    before_text = remaining_text[pos:earliest_pos]
                    # Parse regular formatting in this segment
                    segments.extend(self._parse_regular_formatting(before_text))
                
                # Add CriticMarkup content
                if earliest_type == 'substitution':
                    old_text = earliest_match.group(1)
                    new_text = earliest_match.group(2)
                    segments.append((f"{old_text} → {new_text}", False, False, earliest_type))
                else:
                    content = earliest_match.group(1)
                    segments.append((content, False, False, earliest_type))
                
                pos = earliest_pos + len(earliest_match.group(0))
            else:
                # No more CriticMarkup, process remaining text for regular formatting
                remaining = remaining_text[pos:]
                if remaining:
                    segments.extend(self._parse_regular_formatting(remaining))
                break
        
        return segments
    
    def _parse_regular_formatting(self, text: str) -> List[Tuple[str, bool, bool, str]]:
        """Parse regular markdown formatting (bold/italic) in text."""
        segments = []
        current_pos = 0

        # Pattern to match bold and italic formatting
        pattern = r'(\*\*|__)(.*?)\1|(\*|_)(.*?)\3'

        for match in re.finditer(pattern, text):
            # Add text before the match
            if match.start() > current_pos:
                plain_text = text[current_pos:match.start()]
                if plain_text:
                    segments.append((plain_text, False, False, ''))

            # Determine formatting type
            if match.group(1):  # Bold (**text** or __text__)
                formatted_text = match.group(2)
                segments.append((formatted_text, True, False, ''))
            elif match.group(3):  # Italic (*text* or _text_)
                formatted_text = match.group(4)
                segments.append((formatted_text, False, True, ''))

            current_pos = match.end()

        # Add remaining text
        if current_pos < len(text):
            remaining_text = text[current_pos:]
            if remaining_text:
                segments.append((remaining_text, False, False, ''))

        # If no formatting found, return the whole text as plain
        if not segments:
            segments.append((text, False, False, ''))

        return segments
    
    def _get_critic_color(self, critic_type: str) -> str:
        """Get the appropriate color for CriticMarkup type."""
        color_map = {
            'addition': '#155724',    # Green
            'deletion': '#721c24',    # Red  
            'substitution': '#004085', # Blue
            'highlight': '#856404',   # Yellow/Orange
            'comment': '#856404',     # Yellow/Orange
            '': 'black'              # Default
        }
        return color_map.get(critic_type, 'black')
    
    def _on_click(self, event):
        """Handle mouse click events for links."""
        import webbrowser
        
        # Get click coordinates
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        
        # Check if click is on a link
        for bbox, url in self.links:
            x1, y1, x2, y2 = bbox
            if x1 <= x <= x2 and y1 <= y <= y2:
                logging.info(f"Opening link: {url}")
                try:
                    webbrowser.open(url)
                except Exception as e:
                    logging.error(f"Error opening link: {e}")
                break
    
    def _on_motion(self, event):
        """Handle mouse motion events to change cursor over links."""
        # Get mouse coordinates
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        
        # Check if mouse is over a link
        over_link = False
        for bbox, url in self.links:
            x1, y1, x2, y2 = bbox
            if x1 <= x <= x2 and y1 <= y <= y2:
                over_link = True
                break
        
        # Change cursor
        if over_link:
            self.config(cursor="hand2")
        else:
            self.config(cursor="")


# Example usage and testing
if __name__ == "__main__":
    # Create a test window
    root = tk.Tk()
    root.title("MarkdownCanvas Test")
    root.geometry("800x600")

    # Create a frame for the canvas and scrollbar
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create the MarkdownCanvas
    canvas = MarkdownCanvas(frame, bg='white')

    # Create scrollbar
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Test markdown content
    test_markdown = """# Main Heading

This is a **bold** paragraph with some *italic* text and even ***bold italic*** text.

## Secondary Heading

Here's a bullet list:

* First item with **bold text**
* Second item with *italic text*
* Third item with regular text

### Tertiary Heading

And here's a numbered list:

1. First numbered item
2. Second numbered item with **formatting**
3. Third numbered item

This is another paragraph that should wrap properly when the text becomes very long
and exceeds the width of the canvas area. The text should automatically move to the
next line.

* Another bullet point
* With more **bold** and *italic* formatting
* To test the rendering

4. Continuing numbered list
5. With more items
6. To test numbering

## Final Section

This demonstrates the basic **Markdown** rendering capabilities of the *MarkdownCanvas* widget.
"""

    # Render the test content
    canvas.render_markdown(test_markdown)

    # Start the GUI
    root.mainloop()
