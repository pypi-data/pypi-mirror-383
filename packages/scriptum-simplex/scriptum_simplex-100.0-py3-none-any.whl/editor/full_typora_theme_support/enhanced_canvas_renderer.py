"""
Enhanced Canvas Renderer for Marko AST with Typora Theme Support.

This renderer extends the basic CanvasRenderer to work with EnhancedMarkdownCanvas
and support CriticMarkup annotations with proper theme styling.
"""

from typing import Any, List
from marko.renderer import Renderer
from marko import block, inline
from marko.element import Element
import re
import logging


class EnhancedCanvasRenderer(Renderer):
    """
    Custom Marko renderer that renders AST to EnhancedMarkdownCanvas with:
    - Full Typora theme support
    - CriticMarkup annotations
    - Syntax highlighting
    - Proper text wrapping
    """

    def __init__(self, canvas: Any) -> None:
        """
        Initialize the Enhanced Canvas renderer.

        Args:
            canvas: EnhancedMarkdownCanvas instance to render to
        """
        super().__init__()
        self.canvas = canvas
        
        # CriticMarkup patterns
        self.critic_patterns = {
            'addition': re.compile(r'\{\+\+(.*?)\+\+\}', re.DOTALL),
            'deletion': re.compile(r'\{--(.*?)--\}', re.DOTALL),
            'substitution': re.compile(r'\{~~(.*?)~>(.*?)~~\}', re.DOTALL),
            'comment': re.compile(r'\{>>(.*?)<<\}', re.DOTALL),
            'highlight': re.compile(r'\{==(.*?)==\}', re.DOTALL),
        }

    def render_document(self, element: block.Document) -> None:
        """
        Render the root document element.

        Args:
            element: Marko Document node
        """
        logging.info(f"EnhancedCanvasRenderer: Rendering document with {len(element.children)} children")
        
        # Canvas is already cleared by render_markdown
        # Just render all children
        for i, child in enumerate(element.children):
            logging.info(f"  Rendering child {i}: {child.__class__.__name__}")
            self.render(child)

    def render_heading(self, element: block.Heading) -> None:
        """
        Render a heading element.

        Args:
            element: Marko Heading node
        """
        text = self._extract_text(element.children)
        self.canvas._render_heading(text, element.level)

    def render_paragraph(self, element: block.Paragraph) -> None:
        """
        Render a paragraph with CriticMarkup support and text wrapping.

        Args:
            element: Marko Paragraph node
        """
        text = self._extract_text(element.children)
        
        # Process CriticMarkup if present
        if self._has_criticmarkup(text):
            self._render_paragraph_with_criticmarkup(text)
        else:
            self.canvas._render_paragraph(text)

    def render_list(self, element: block.List) -> None:
        """
        Render a list (ordered or unordered).

        Args:
            element: Marko List node
        """
        items = []
        for item in element.children:
            text = self._extract_text_from_list_item(item)
            items.append(text)
        
        self.canvas._render_list(items, ordered=element.ordered)

    def render_list_item(self, element: block.ListItem) -> str:
        """List items are handled by render_list."""
        return ""

    def render_fenced_code(self, element: block.FencedCode) -> None:
        """
        Render a fenced code block with syntax highlighting.

        Args:
            element: Marko FencedCode node
        """
        # Get code text
        if element.children:
            raw_code = element.children[0]
            code_text = (raw_code.children if hasattr(raw_code, 'children')
                        else str(raw_code))
            if not isinstance(code_text, str):
                code_text = str(code_text)
        else:
            code_text = ""
        
        # Remove trailing newline if present
        code_text = code_text.rstrip('\n')
        
        self.canvas._render_code_block(code_text)

    def render_code_block(self, element: block.CodeBlock) -> None:
        """
        Render an indented code block.

        Args:
            element: Marko CodeBlock node
        """
        if element.children:
            code_text = str(element.children[0]).rstrip('\n')
        else:
            code_text = ""
        
        self.canvas._render_code_block(code_text)

    def render_thematic_break(self, element: block.ThematicBreak) -> None:
        """
        Render a horizontal rule.

        Args:
            element: Marko ThematicBreak node
        """
        self.canvas._render_hr()

    def render_quote(self, element: block.Quote) -> None:
        """
        Render a blockquote.

        Args:
            element: Marko Quote node
        """
        text = self._extract_text(element.children)
        self.canvas._render_blockquote(text)
    
    def render_table(self, element: Any) -> None:
        """
        Render a table element.

        Args:
            element: Marko Table node
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

        # Render table (simple version for now)
        self._render_simple_table(rows, alignments)
    
    def _extract_text_from_cell(self, cell: Any) -> str:
        """Extract text content from a table cell."""
        if not hasattr(cell, 'children') or not cell.children:
            return ""

        parts = []
        for child in cell.children:
            if hasattr(child, 'children'):
                result = self.render(child)
                if result:
                    parts.append(result)
            elif isinstance(child, str):
                parts.append(child)

        return ''.join(parts)
    
    def _render_simple_table(self, rows: List[List[str]], alignments: List[str]) -> None:
        """Render a table with full theme support."""
        if not rows:
            return
        
        # Use the full table rendering method from EnhancedMarkdownCanvas
        self.canvas._render_table_from_ast(rows, alignments)

    def render_link(self, element: inline.Link) -> str:
        """
        Render a link (returns text for now, full support later).

        Args:
            element: Marko Link node
        """
        text = self._extract_text(element.children)
        return text

    def render_emphasis(self, element: inline.Emphasis) -> str:
        """
        Render emphasis (italic).

        Args:
            element: Marko Emphasis node
        """
        text = self._extract_text(element.children)
        return text  # TODO: Add italic support

    def render_strong_emphasis(self, element: inline.StrongEmphasis) -> str:
        """
        Render strong emphasis (bold).

        Args:
            element: Marko StrongEmphasis node
        """
        text = self._extract_text(element.children)
        return text  # TODO: Add bold support

    def render_code_span(self, element: inline.CodeSpan) -> str:
        """
        Render inline code.

        Args:
            element: Marko CodeSpan node
        """
        return element.children  # Return raw text

    def render_raw_text(self, element: inline.RawText) -> str:
        """
        Render raw text.

        Args:
            element: Marko RawText node
        """
        return element.children

    def render_line_break(self, element: inline.LineBreak) -> str:
        """Render line break."""
        return '\n'

    # Helper methods

    def _extract_text(self, children: List[Any]) -> str:
        """Extract plain text from AST children."""
        if not children:
            return ""
        
        text_parts = []
        for child in children:
            if isinstance(child, str):
                text_parts.append(child)
            elif hasattr(child, 'children'):
                if isinstance(child.children, str):
                    text_parts.append(child.children)
                elif isinstance(child.children, list):
                    text_parts.append(self._extract_text(child.children))
                else:
                    text_parts.append(str(child.children))
            else:
                # Try to render the element
                rendered = self.render(child)
                if rendered:
                    text_parts.append(str(rendered))
        
        return ''.join(text_parts)

    def _extract_text_from_list_item(self, item: Any) -> str:
        """Extract text from a list item."""
        if hasattr(item, 'children'):
            return self._extract_text(item.children)
        return str(item)

    def _has_criticmarkup(self, text: str) -> bool:
        """Check if text contains CriticMarkup annotations."""
        for pattern in self.critic_patterns.values():
            if pattern.search(text):
                return True
        return False

    def _render_paragraph_with_criticmarkup(self, text: str) -> None:
        """
        Render a paragraph with CriticMarkup annotations.
        
        For now, we'll render it as plain text with the annotations visible.
        TODO: Add visual styling for additions, deletions, etc.
        """
        # For now, just render as normal paragraph
        # Future: Parse and render with colors/strikethrough
        self.canvas._render_paragraph(text)
