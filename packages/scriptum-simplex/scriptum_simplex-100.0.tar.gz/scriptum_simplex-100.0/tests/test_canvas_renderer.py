"""
Unit tests for the CanvasRenderer class.
"""

import pytest
from unittest.mock import Mock, MagicMock
from editor.canvas_renderer import CanvasRenderer
from editor.markdown_parser import MarkdownParser


class TestCanvasRenderer:
    """Test cases for the CanvasRenderer class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = MarkdownParser()
        self.mock_canvas = Mock()
        # Set up required attributes
        self.mock_canvas.text_margin = 20
        self.mock_canvas.paragraph_spacing = 15
        self.mock_canvas.line_spacing = 5
        self.mock_canvas.fonts = {
            'normal': Mock(metrics=Mock(return_value=15), measure=Mock(return_value=50)),
            'italic': Mock(metrics=Mock(return_value=15)),
        }
        self.mock_canvas.envelope_left = 20
        self.mock_canvas.envelope_right = 600
        self.mock_canvas.envelope_width = 580
        self.mock_canvas.current_y = 20
        # Mock the _render_link method to return a width
        self.mock_canvas._render_link = Mock(return_value=50)
        self.renderer = CanvasRenderer(self.mock_canvas)

    def test_initialization(self) -> None:
        """Test that CanvasRenderer initializes correctly."""
        assert self.renderer.canvas == self.mock_canvas

    def test_render_document_clears_canvas(self) -> None:
        """Test that rendering a document clears the canvas."""
        ast = self.parser.parse("# Hello")
        self.renderer.render(ast)

        # Verify canvas was cleared
        self.mock_canvas.delete.assert_called_with('all')
        self.mock_canvas.update_scrollregion.assert_called()

    def test_render_heading(self) -> None:
        """Test rendering a heading element."""
        ast = self.parser.parse("# Level 1 Heading")
        self.renderer.render(ast)

        # Verify heading render method was called
        self.mock_canvas._render_heading.assert_called()
        args = self.mock_canvas._render_heading.call_args[0]
        assert "Level 1 Heading" in args[0]
        assert args[1] == 'h1'

    def test_render_multiple_heading_levels(self) -> None:
        """Test rendering different heading levels."""
        text = "# H1\n\n## H2\n\n### H3"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Should call render_heading 3 times
        assert self.mock_canvas._render_heading.call_count == 3

    def test_render_paragraph(self) -> None:
        """Test rendering a paragraph."""
        ast = self.parser.parse("This is a simple paragraph.")
        self.renderer.render(ast)

        # Verify paragraph render method was called
        self.mock_canvas._render_paragraph.assert_called()
        args = self.mock_canvas._render_paragraph.call_args[0]
        assert "simple paragraph" in args[0]

    def test_render_bold_text(self) -> None:
        """Test that bold text is preserved in rendered output."""
        ast = self.parser.parse("This is **bold** text.")
        self.renderer.render(ast)

        # Check that bold markers are preserved
        args = self.mock_canvas._render_paragraph.call_args[0]
        assert "**bold**" in args[0]

    def test_render_italic_text(self) -> None:
        """Test that italic text is preserved in rendered output."""
        ast = self.parser.parse("This is *italic* text.")
        self.renderer.render(ast)

        # Check that italic markers are preserved
        args = self.mock_canvas._render_paragraph.call_args[0]
        assert "*italic*" in args[0]

    def test_render_bullet_list(self) -> None:
        """Test rendering a bullet list."""
        text = "- Item 1\n- Item 2\n- Item 3"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify bullet list items were rendered
        assert self.mock_canvas._render_bullet_list_item.call_count == 3

    def test_render_numbered_list(self) -> None:
        """Test rendering a numbered list."""
        text = "1. First\n2. Second\n3. Third"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify numbered list items were rendered
        assert self.mock_canvas._render_numbered_list_item.call_count == 3

    def test_render_code_block(self) -> None:
        """Test rendering a fenced code block."""
        text = "```python\ndef hello():\n    print('world')\n```"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify code block render method was called
        self.mock_canvas._render_code_block.assert_called()
        # Check that code was passed
        args = self.mock_canvas._render_code_block.call_args[0]
        assert isinstance(args[0], list)

    def test_render_table(self) -> None:
        """Test that table rendering calls the AST method."""
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify that _render_table_from_ast was called
        self.mock_canvas._render_table_from_ast.assert_called()

    def test_render_complex_document(self) -> None:
        """Test rendering a complex document with multiple elements."""
        text = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Subtitle

- Bullet item 1
- Bullet item 2

1. Numbered item 1
2. Numbered item 2

```
code block
```
"""
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify various render methods were called
        assert self.mock_canvas._render_heading.call_count >= 2
        assert self.mock_canvas._render_paragraph.call_count >= 1
        assert self.mock_canvas._render_bullet_list_item.call_count >= 2
        assert self.mock_canvas._render_numbered_list_item.call_count >= 2
        assert self.mock_canvas._render_code_block.call_count >= 1

    def test_render_empty_document(self) -> None:
        """Test rendering an empty document."""
        ast = self.parser.parse("")
        self.renderer.render(ast)

        # Canvas should still be cleared
        self.mock_canvas.delete.assert_called_with('all')
        self.mock_canvas.update_scrollregion.assert_called()

    def test_render_horizontal_rule(self) -> None:
        """Test rendering a horizontal rule (thematic break)."""
        text = "---"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify create_line was called for the rule
        self.mock_canvas.create_line.assert_called()

    def test_extract_text_from_inline_elements(self) -> None:
        """Test that inline text extraction works correctly."""
        text = "Text with **bold** and *italic* and `code`."
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify paragraph was rendered with inline formatting
        args = self.mock_canvas._render_paragraph.call_args[0]
        assert "**bold**" in args[0]
        assert "*italic*" in args[0]

    def test_render_link(self) -> None:
        """Test that links are rendered with clickable support."""
        text = "This is a [link](http://example.com) in text."
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify _render_link was called with the URL
        self.mock_canvas._render_link.assert_called()
        call_args = self.mock_canvas._render_link.call_args[0]
        assert "link" in call_args[0]  # link text
        assert "http://example.com" in call_args[1]  # URL

    def test_render_nested_list(self) -> None:
        """Test rendering a list with nested elements."""
        text = "- Item with **bold**\n- Item with *italic*"
        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify list items were rendered with inline formatting
        assert self.mock_canvas._render_bullet_list_item.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
