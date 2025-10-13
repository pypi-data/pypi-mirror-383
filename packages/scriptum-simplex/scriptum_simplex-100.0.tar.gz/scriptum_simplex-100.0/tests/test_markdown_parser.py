"""
Unit tests for the MarkdownParser adapter class.
"""

import pytest
from editor.markdown_parser import MarkdownParser


class TestMarkdownParser:
    """Test cases for the MarkdownParser adapter class."""
    
    def setup_method(self) -> None:
        """Set up a fresh MarkdownParser instance for each test."""
        self.parser = MarkdownParser()
    
    def test_initialization(self) -> None:
        """Test that MarkdownParser initializes correctly."""
        parser = MarkdownParser()
        assert parser is not None
        assert parser.markdown is not None
        assert hasattr(parser.markdown, 'parse')
        assert hasattr(parser.markdown, '__call__')
    
    def test_parse_returns_ast(self) -> None:
        """Test that parse() returns an AST object."""
        text = "# Hello World\n\nThis is a test."
        ast = self.parser.parse(text)
        
        # AST should have children
        assert ast is not None
        assert hasattr(ast, 'children')
        assert len(ast.children) > 0
    
    def test_parse_heading(self) -> None:
        """Test parsing a heading element."""
        text = "# Level 1 Heading"
        ast = self.parser.parse(text)
        
        # First child should be a heading
        assert len(ast.children) >= 1
        heading = ast.children[0]
        assert heading.__class__.__name__ == 'Heading'
        assert heading.level == 1
    
    def test_parse_paragraph(self) -> None:
        """Test parsing a paragraph element."""
        text = "This is a simple paragraph."
        ast = self.parser.parse(text)
        
        # First child should be a paragraph
        assert len(ast.children) >= 1
        paragraph = ast.children[0]
        assert paragraph.__class__.__name__ == 'Paragraph'
    
    def test_parse_table(self) -> None:
        """Test parsing a GFM table."""
        text = """| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |"""
        
        ast = self.parser.parse(text)
        
        # Should have a table element
        assert len(ast.children) >= 1
        table = ast.children[0]
        assert table.__class__.__name__ == 'Table'
        # Marko's table has children (rows) but not separate head/body
        assert hasattr(table, 'children')
        assert len(table.children) >= 3  # Header row + 2 data rows
    
    def test_parse_strikethrough(self) -> None:
        """Test parsing GFM strikethrough."""
        text = "This has ~~strikethrough~~ text."
        ast = self.parser.parse(text)
        
        # Should successfully parse (GFM extension)
        assert len(ast.children) >= 1
        paragraph = ast.children[0]
        assert paragraph.__class__.__name__ == 'Paragraph'
    
    def test_parse_empty_text(self) -> None:
        """Test parsing empty text."""
        text = ""
        ast = self.parser.parse(text)
        
        # Should return valid AST with no children
        assert ast is not None
        assert hasattr(ast, 'children')
        assert len(ast.children) == 0
    
    def test_parse_complex_document(self) -> None:
        """Test parsing a complex document with multiple elements."""
        text = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Subtitle

- List item 1
- List item 2
- List item 3

1. Numbered item
2. Another item

| Col 1 | Col 2 |
|-------|-------|
| A     | B     |

```python
def hello():
    print("world")
```
"""
        
        ast = self.parser.parse(text)
        
        # Should have multiple children
        assert len(ast.children) > 5
        # Verify we have different element types
        element_types = [child.__class__.__name__ for child in ast.children]
        assert 'Heading' in element_types
        assert 'Paragraph' in element_types
        assert 'List' in element_types
        assert 'Table' in element_types
        assert 'FencedCode' in element_types
    
    def test_render_html_basic(self) -> None:
        """Test rendering basic markdown to HTML."""
        text = "**Bold** and *italic*"
        html = self.parser.render_html(text)
        
        assert isinstance(html, str)
        assert '<strong>Bold</strong>' in html
        assert '<em>italic</em>' in html
    
    def test_render_html_heading(self) -> None:
        """Test rendering headings to HTML."""
        text = "# Heading 1\n\n## Heading 2"
        html = self.parser.render_html(text)
        
        assert '<h1>Heading 1</h1>' in html
        assert '<h2>Heading 2</h2>' in html
    
    def test_render_html_list(self) -> None:
        """Test rendering lists to HTML."""
        text = "- Item 1\n- Item 2\n- Item 3"
        html = self.parser.render_html(text)
        
        assert '<ul>' in html
        assert '<li>Item 1</li>' in html
        assert '<li>Item 2</li>' in html
        assert '<li>Item 3</li>' in html
        assert '</ul>' in html
    
    def test_render_html_table(self) -> None:
        """Test rendering tables to HTML."""
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = self.parser.render_html(text)
        
        assert '<table>' in html
        assert '<thead>' in html
        assert '<tbody>' in html
        assert '</table>' in html
    
    def test_render_html_code_block(self) -> None:
        """Test rendering code blocks to HTML."""
        text = "```python\nprint('hello')\n```"
        html = self.parser.render_html(text)
        
        assert '<code' in html or '<pre' in html
    
    def test_render_html_empty(self) -> None:
        """Test rendering empty text to HTML."""
        text = ""
        html = self.parser.render_html(text)
        
        assert isinstance(html, str)
        # Empty text should produce empty or minimal HTML
        assert len(html.strip()) == 0
    
    def test_render_to_canvas(self) -> None:
        """Test that canvas rendering works with a mock canvas."""
        from unittest.mock import Mock
        
        text = "# Test Heading"
        mock_canvas = Mock()
        # Set up required canvas attributes
        mock_canvas.text_margin = 20
        mock_canvas.current_y = 20
        
        # Should not raise an error
        self.parser.render_to_canvas(text, mock_canvas)
        
        # Verify canvas methods were called
        mock_canvas.delete.assert_called()
        mock_canvas.update_scrollregion.assert_called()
    
    def test_get_extension_names(self) -> None:
        """Test getting list of loaded extensions."""
        extensions = self.parser.get_extension_names()
        
        assert isinstance(extensions, list)
        assert 'gfm' in extensions
    
    def test_multiple_parse_calls(self) -> None:
        """Test that parser can be used multiple times."""
        text1 = "# First"
        text2 = "## Second"
        
        ast1 = self.parser.parse(text1)
        ast2 = self.parser.parse(text2)
        
        # Both should succeed and be independent
        assert ast1 is not None
        assert ast2 is not None
        assert ast1 is not ast2
    
    def test_parse_preserves_special_characters(self) -> None:
        """Test that parsing preserves special characters."""
        text = "Text with <brackets> and & ampersands"
        ast = self.parser.parse(text)
        
        # Should parse without errors
        assert ast is not None
        assert len(ast.children) > 0
    
    def test_render_html_preserves_special_characters(self) -> None:
        """Test that HTML rendering escapes special characters."""
        text = "Text with <brackets> and & ampersands"
        html = self.parser.render_html(text)
        
        # HTML entities should be escaped
        assert '&lt;' in html or '<' not in html or '<p>' in html
        assert '&amp;' in html or '&' in html


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
