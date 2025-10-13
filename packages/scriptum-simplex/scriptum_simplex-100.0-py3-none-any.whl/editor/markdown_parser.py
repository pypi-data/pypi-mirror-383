"""
Markdown parser adapter for Scriptum Simplex.
Provides a clean abstraction layer over the Marko parser.
"""

from typing import Any, List
from marko import Markdown
from marko.ext.gfm import make_extension as make_gfm


class MarkdownParser:
    """
    Adapter for Marko markdown parser with GitHub Flavored Markdown extensions.

    This class provides a clean interface for parsing markdown text and rendering
    it to various formats. It uses Marko with GFM extension which includes support
    for tables, strikethrough, task lists, and other GitHub-specific features.

    Attributes:
        markdown: The configured Marko Markdown instance with GFM extension
    """

    def __init__(self) -> None:
        """
        Initialize the MarkdownParser with GFM extension.

        The GFM (GitHub Flavored Markdown) extension adds support for:
        - Tables
        - Strikethrough text
        - Task lists
        - Autolinks
        """
        # Use GFM extension which includes tables, strikethrough, etc.
        self.markdown: Markdown = Markdown(extensions=[make_gfm()])

    def parse(self, text: str) -> Any:
        """
        Parse markdown text and return an Abstract Syntax Tree (AST).

        The AST can be traversed to inspect document structure or used
        with custom renderers to output to different formats.

        Args:
            text: Markdown text to parse

        Returns:
            Marko Document AST node containing the parsed structure

        Example:
            >>> parser = MarkdownParser()
            >>> ast = parser.parse("# Hello World\\n\\nThis is **bold**.")
            >>> # Walk the AST or render with custom renderer
        """
        return self.markdown.parse(text)

    def render_html(self, text: str) -> str:
        """
        Render markdown text directly to HTML.

        This is a convenience method for backward compatibility with the
        existing codebase that uses HTML rendering.

        Args:
            text: Markdown text to render

        Returns:
            HTML string representation of the markdown

        Example:
            >>> parser = MarkdownParser()
            >>> html = parser.render_html("**Bold** and *italic*")
            >>> print(html)
            <p><strong>Bold</strong> and <em>italic</em></p>
        """
        return self.markdown(text)

    def render_to_canvas(self, text: str, canvas: Any) -> None:
        """
        Render markdown text to a Canvas widget using AST.

        This method parses the text to an AST and uses a custom CanvasRenderer
        to output directly to the MarkdownCanvas widget.

        Args:
            text: Markdown text to render
            canvas: MarkdownCanvas instance to render to
        """
        import logging
        logging.info(f"MarkdownParser.render_to_canvas called with {len(text)} chars")
        
        from .canvas_renderer import CanvasRenderer

        # Parse text to AST
        logging.info("Parsing text to AST...")
        ast = self.parse(text)
        logging.info(f"AST parsed, type: {type(ast)}, children: {len(ast.children) if hasattr(ast, 'children') else 'no children'}")

        # Create renderer and render to canvas
        logging.info("Creating CanvasRenderer...")
        renderer = CanvasRenderer(canvas)
        logging.info("Calling renderer.render...")
        renderer.render(ast)
        logging.info("render_to_canvas completed")

    def get_extension_names(self) -> List[str]:
        """
        Get list of active extension names.

        Returns:
            List of extension names currently loaded
        """
        # Marko stores extensions differently - this is a helper for debugging
        return ['gfm']  # Currently only GFM is loaded
