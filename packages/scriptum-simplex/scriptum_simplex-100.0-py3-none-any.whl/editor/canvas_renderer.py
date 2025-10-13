"""
Canvas renderer for Marko AST.

This module provides a custom Marko renderer that outputs directly to a
MarkdownCanvas widget, bypassing HTML as an intermediate format.
"""

from typing import Any, List, Sequence, TYPE_CHECKING
from marko.renderer import Renderer
from marko import block, inline
from marko.element import Element

if TYPE_CHECKING:
    from .markdown_canvas import MarkdownCanvas


class CanvasRenderer(Renderer):
    """
    Custom Marko renderer that renders AST directly to MarkdownCanvas.

    This renderer walks the Marko AST and calls the appropriate rendering
    methods on the MarkdownCanvas widget, reusing all existing rendering
    logic for headings, lists, paragraphs, etc.
    """

    def __init__(self, canvas: 'MarkdownCanvas') -> None:
        """
        Initialize the Canvas renderer.

        Args:
            canvas: MarkdownCanvas instance to render to
        """
        super().__init__()
        self.canvas = canvas

    def render_document(self, element: block.Document) -> None:
        """
        Render the root document element.

        Args:
            element: Marko Document node
        """
        import logging
        logging.info(f"CanvasRenderer.render_document called with {len(element.children)} children")
        
        # Clear canvas and reset position
        logging.info("Clearing canvas...")
        self.canvas.delete('all')
        self.canvas.current_y = self.canvas.text_margin
        logging.info(f"Canvas cleared, current_y set to {self.canvas.current_y}")

        # Render all children
        logging.info("Rendering children...")
        for i, child in enumerate(element.children):
            logging.info(f"Rendering child {i}: {child.__class__.__name__}")
            self.render(child)
            logging.info(f"Child {i} rendered, current_y now: {self.canvas.current_y}")

        # Update scroll region
        logging.info("Updating scroll region...")
        self.canvas.update_scrollregion()
        logging.info("render_document completed")

    def render_heading(self, element: block.Heading) -> None:
        """
        Render a heading element.

        Args:
            element: Marko Heading node
        """
        # Extract text from children
        text = self._extract_text(element.children)

        # Map heading level to font key
        level_map = {1: 'h1', 2: 'h2', 3: 'h3'}
        level = level_map.get(element.level, 'h3')

        # Use existing MarkdownCanvas method
        self.canvas._render_heading(text, level)

    def render_paragraph(self, element: block.Paragraph) -> None:
        """
        Render a paragraph element with support for inline links.

        Args:
            element: Marko Paragraph node
        """
        # Check if paragraph contains links
        has_links = self._contains_links(element.children)
        
        if has_links:
            # Render paragraph with link support
            self._render_paragraph_with_links(element.children)
        else:
            # Extract text with inline formatting
            text = self._extract_text(element.children)
            # Use existing MarkdownCanvas method
            self.canvas._render_paragraph(text)

    def render_list(self, element: block.List) -> None:
        """
        Render a list (ordered or unordered).

        Args:
            element: Marko List node
        """
        for i, item in enumerate(element.children, start=1):
            # item is an Element, but we know it's a ListItem
            # Extract text from list item
            text = self._extract_text_from_list_item(item)

            # Render based on list type
            if element.ordered:
                self.canvas._render_numbered_list_item(text, i)
            else:
                self.canvas._render_bullet_list_item(text)

    def render_list_item(self, element: block.ListItem) -> str:
        """
        Render a list item (called by render_list).

        Args:
            element: Marko ListItem node

        Returns:
            Rendered text (not used directly, extracted by render_list)
        """
        # List items are handled by render_list
        return ""

    def render_fenced_code(self, element: block.FencedCode) -> None:
        """
        Render a fenced code block.

        Args:
            element: Marko FencedCode node
        """
        # Get code lines
        if element.children:
            raw_code = element.children[0]
            # Extract code text from raw_code element
            code_text = (raw_code.children if hasattr(raw_code, 'children')
                         else str(raw_code))
            code_lines = (code_text.split('\n')
                          if isinstance(code_text, str) else [])
        else:
            code_lines = []

        # Use existing MarkdownCanvas method
        self.canvas._render_code_block(code_lines)

    def render_code_block(self, element: block.CodeBlock) -> None:
        """
        Render an indented code block.

        Args:
            element: Marko CodeBlock node
        """
        # Get code lines
        if element.children:
            raw_code = element.children[0]
            # Extract code text from raw_code element
            code_text = (raw_code.children if hasattr(raw_code, 'children')
                         else str(raw_code))
            code_lines = (code_text.split('\n')
                          if isinstance(code_text, str) else [])
        else:
            code_lines = []

        # Use existing MarkdownCanvas method
        self.canvas._render_code_block(code_lines)

    def render_table(self, element: Any) -> None:
        """
        Render a table element with proper column alignment and formatting.

        Args:
            element: Marko Table node with TableRow children
        """
        # Extract table data from AST
        rows: List[List[str]] = []
        alignments: List[str] = []

        for row in element.children:
            cells = []
            row_alignments = []

            for cell in row.children:
                # Extract cell text
                cell_text = self._extract_text_from_cell(cell)
                cells.append(cell_text)

                # Get alignment (default to left)
                align = getattr(cell, 'align', None) or 'left'
                row_alignments.append(align)

            rows.append(cells)
            # Use first row's alignments for all rows
            if not alignments:
                alignments = row_alignments

        # Use the new table rendering method
        self.canvas._render_table_from_ast(rows, alignments)

    def _extract_text_from_cell(self, cell: Any) -> str:
        """
        Extract text content from a table cell.

        Args:
            cell: TableCell node

        Returns:
            Text content of the cell with inline formatting preserved
        """
        if not hasattr(cell, 'children') or not cell.children:
            return ""

        parts = []
        for child in cell.children:
            if hasattr(child, 'children'):
                # It's an element, render it
                result = self.render(child)
                if result:
                    parts.append(result)
            elif isinstance(child, str):
                parts.append(child)

        return ''.join(parts)

    def render_quote(self, element: block.Quote) -> None:
        """
        Render a block quote with left border.

        Args:
            element: Marko Quote node
        """
        # Extract text from quote
        text = self._extract_text(element.children)

        # Add spacing before quote
        self.canvas.current_y += self.canvas.line_spacing
        
        # Calculate dimensions
        quote_indent = 30  # Space for left border
        quote_left = self.canvas.envelope_left + quote_indent
        quote_width = self.canvas.envelope_width - quote_indent - 20
        
        # Measure text height
        font = self.canvas.fonts['italic']
        # Estimate lines (rough calculation)
        char_width = font.measure('M')
        chars_per_line = max(1, quote_width // char_width)
        estimated_lines = max(1, len(text) // chars_per_line + 1)
        line_height = font.metrics('linespace')
        text_height = estimated_lines * line_height
        
        quote_top = self.canvas.current_y
        quote_bottom = quote_top + text_height + 20  # Add padding
        
        # Draw background if theme specifies one
        if (hasattr(self.canvas.current_theme.colors, 'blockquote_bg') and 
            self.canvas.current_theme.colors.blockquote_bg != 'transparent'):
            self.canvas.create_rectangle(
                self.canvas.envelope_left, quote_top - 5,
                self.canvas.envelope_right, quote_bottom,
                fill=self.canvas.current_theme.colors.blockquote_bg,
                outline=''
            )
        
        # Draw left border (thick colored line)
        border_color = (self.canvas.current_theme.colors.blockquote_border 
                       if hasattr(self.canvas.current_theme.colors, 'blockquote_border')
                       else self.canvas.current_theme.colors.link)
        self.canvas.create_rectangle(
            self.canvas.envelope_left + 10, quote_top,
            self.canvas.envelope_left + 15, quote_bottom,
            fill=border_color,
            outline=''
        )
        
        # Render quote text
        self.canvas.create_text(
            quote_left,
            self.canvas.current_y,
            text=text,
            font=font,
            anchor='nw',
            fill=self.canvas.current_theme.colors.text,
            width=quote_width
        )
        
        # Update position
        self.canvas.current_y = quote_bottom + self.canvas.paragraph_spacing

    def render_thematic_break(self, element: block.ThematicBreak) -> None:
        """
        Render a horizontal rule.

        Args:
            element: Marko ThematicBreak node
        """
        self.canvas.current_y += self.canvas.paragraph_spacing
        self.canvas.create_line(
            self.canvas.envelope_left,
            self.canvas.current_y,
            self.canvas.envelope_right,
            self.canvas.current_y,
            fill='#cccccc',
            width=1
        )
        self.canvas.current_y += self.canvas.paragraph_spacing

    # Inline element renderers (return strings for inline formatting)

    def render_raw_text(self, element: inline.RawText) -> str:
        """Render raw text."""
        return element.children

    def render_strong_emphasis(self, element: inline.StrongEmphasis) -> str:
        """
        Render bold text.

        Returns:
            Text with markdown bold markers for existing parser
        """
        text = self._extract_text(element.children)
        return f"**{text}**"

    def render_emphasis(self, element: inline.Emphasis) -> str:
        """
        Render italic text.

        Returns:
            Text with markdown italic markers for existing parser
        """
        text = self._extract_text(element.children)
        return f"*{text}*"

    def render_code_span(self, element: inline.CodeSpan) -> str:
        """
        Render inline code.

        Returns:
            Text with code markers
        """
        return f"`{element.children}`"

    def render_line_break(self, element: inline.LineBreak) -> str:
        """Render a line break."""
        return "\n"

    def render_link(self, element: inline.Link) -> str:
        """
        Render a link.

        For now, just render the link text.
        TODO: Make links clickable in Phase 5
        """
        text = self._extract_text(element.children)
        return text

    def render_image(self, element: inline.Image) -> None:
        """
        Render an image.

        Args:
            element: Marko Image node
        """
        # Extract image path and alt text
        image_path = element.dest if hasattr(element, 'dest') else ''
        alt_text = self._extract_text(element.children) if hasattr(element, 'children') else element.title or 'untitled'
        
        # Use canvas method to render image
        self.canvas._render_image(image_path, alt_text)

    # Helper methods

    def _extract_text(self, children: Sequence[Element]) -> str:
        """
        Extract text from AST children, preserving inline formatting.

        Args:
            children: Sequence of AST child nodes

        Returns:
            Text with inline markdown markers preserved
        """
        if not children:
            return ""

        parts = []
        for child in children:
            if hasattr(child, 'children'):
                # Recurse for nested elements
                result = self.render(child)
                if result:
                    parts.append(result)
            elif isinstance(child, str):
                parts.append(child)

        return ''.join(parts)

    def _extract_text_from_list_item(self, list_item: block.ListItem) -> str:
        """
        Extract text from a list item, handling nested elements.

        Args:
            list_item: ListItem node

        Returns:
            Text content of the list item
        """
        parts = []
        for child in list_item.children:
            if hasattr(child, 'children'):
                text = self._extract_text(child.children)
                parts.append(text)
            elif isinstance(child, str):
                parts.append(child)

        return ' '.join(parts)
    
    def _contains_links(self, children: Sequence[Element]) -> bool:
        """
        Check if children contain any Link elements.
        
        Args:
            children: Sequence of AST child nodes
            
        Returns:
            True if any child is a Link element
        """
        for child in children:
            if child.__class__.__name__ == 'Link':
                return True
            if hasattr(child, 'children') and self._contains_links(child.children):
                return True
        return False
    
    def _render_paragraph_with_links(self, children: Sequence[Element]) -> None:
        """
        Render a paragraph that contains links.
        
        Args:
            children: Sequence of inline elements including links
        """
        self.canvas.current_y += self.canvas.line_spacing
        
        current_x = self.canvas.envelope_left
        current_y = self.canvas.current_y
        line_height = self.canvas.fonts['normal'].metrics('linespace')
        
        for child in children:
            if isinstance(child, str):
                # Regular text
                text_width = self.canvas.fonts['normal'].measure(child)
                self.canvas.create_text(
                    current_x, current_y,
                    text=child,
                    font=self.canvas.fonts['normal'],
                    anchor='nw',
                    fill='black'
                )
                current_x += text_width
            elif child.__class__.__name__ == 'Link':
                # Render link
                link_text = self._extract_text(child.children)
                url = child.dest if hasattr(child, 'dest') else '#'
                link_width = self.canvas._render_link(link_text, url, current_x, current_y)
                current_x += link_width
            else:
                # Other inline elements (bold, italic, etc.)
                text = self.render(child)
                if text:
                    text_width = self.canvas.fonts['normal'].measure(text)
                    self.canvas.create_text(
                        current_x, current_y,
                        text=text,
                        font=self.canvas.fonts['normal'],
                        anchor='nw',
                        fill='black'
                    )
                    current_x += text_width
        
        # Update current_y for next element
        self.canvas.current_y = current_y + line_height + self.canvas.line_spacing
