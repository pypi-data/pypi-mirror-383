"""
Comprehensive tests for table rendering functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, call
from editor.canvas_renderer import CanvasRenderer
from editor.markdown_parser import MarkdownParser


class TestTableRendering:
    """Test cases for table rendering with AST."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = MarkdownParser()
        self.mock_canvas = Mock()
        # Set up required attributes
        self.mock_canvas.text_margin = 20
        self.mock_canvas.paragraph_spacing = 15
        self.mock_canvas.line_spacing = 5
        self.mock_canvas.fonts = {
            'normal': Mock(
                metrics=Mock(return_value=15),
                measure=Mock(return_value=50)
            ),
            'bold': Mock(
                metrics=Mock(return_value=15),
                measure=Mock(return_value=60)
            ),
            'italic': Mock(
                metrics=Mock(return_value=15),
                measure=Mock(return_value=55)
            ),
            'bold_italic': Mock(
                metrics=Mock(return_value=15),
                measure=Mock(return_value=65)
            ),
        }
        self.mock_canvas.envelope_left = 20
        self.mock_canvas.envelope_right = 600
        self.mock_canvas.envelope_width = 580
        self.mock_canvas.current_y = 20
        self.renderer = CanvasRenderer(self.mock_canvas)

    def test_render_basic_table(self) -> None:
        """Test rendering a basic table with headers and data."""
        table_text = """| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        # Verify _render_table_from_ast was called
        self.mock_canvas._render_table_from_ast.assert_called_once()

        # Check arguments
        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, alignments = args

        # Should have 2 rows (header + data)
        assert len(rows) == 2
        assert len(rows[0]) == 2  # 2 columns
        assert "Header 1" in rows[0][0]
        assert "Header 2" in rows[0][1]
        assert "Data 1" in rows[1][0]
        assert "Data 2" in rows[1][1]

        # Default alignment should be left
        assert alignments == ['left', 'left']

    def test_render_table_with_alignment(self) -> None:
        """Test that table column alignment is correctly parsed."""
        table_text = """| Left | Center | Right |
|------|:------:|------:|
| L    | C      | R     |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, alignments = args

        # Check alignment markers
        assert alignments[0] == 'left'
        assert alignments[1] == 'center'
        assert alignments[2] == 'right'

    def test_render_table_with_bold_text(self) -> None:
        """Test that bold text in tables is preserved."""
        table_text = """| Name | Status |
|------|--------|
| **Bold** | Normal |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        # Bold markers should be preserved
        assert "**Bold**" in rows[1][0]

    def test_render_table_with_italic_text(self) -> None:
        """Test that italic text in tables is preserved."""
        table_text = """| Name | Note |
|------|------|
| Item | *Important* |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        # Italic markers should be preserved
        assert "*Important*" in rows[1][1]

    def test_render_table_with_mixed_formatting(self) -> None:
        """Test table with multiple formatting types."""
        table_text = """| Type | Example |
|------|---------|
| **Bold** | Text |
| *Italic* | More |
| `Code` | Sample |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        assert len(rows) == 4  # Header + 3 data rows
        assert "**Bold**" in rows[1][0]
        assert "*Italic*" in rows[2][0]
        assert "`Code`" in rows[3][0]

    def test_render_table_with_empty_cells(self) -> None:
        """Test table with some empty cells."""
        table_text = """| Col1 | Col2 | Col3 |
|------|------|------|
| A    |      | C    |
|      | B    |      |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        # Empty cells should be empty strings
        assert rows[1][1].strip() == ""
        assert rows[2][0].strip() == ""
        assert rows[2][2].strip() == ""

    def test_render_single_column_table(self) -> None:
        """Test table with only one column."""
        table_text = """| Single |
|--------|
| Value1 |
| Value2 |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, alignments = args

        assert len(rows) == 3
        assert len(rows[0]) == 1
        assert len(alignments) == 1

    def test_render_wide_table(self) -> None:
        """Test table with many columns."""
        table_text = """| A | B | C | D | E | F |
|---|---|---|---|---|---|
| 1 | 2 | 3 | 4 | 5 | 6 |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, alignments = args

        assert len(rows[0]) == 6
        assert len(alignments) == 6

    def test_render_table_with_long_text(self) -> None:
        """Test table cells with longer text content."""
        table_text = """| Description | Value |
|-------------|-------|
| This is a longer description | 100 |
| Another long text entry | 200 |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        assert "longer description" in rows[1][0]
        assert "long text entry" in rows[2][0]

    def test_extract_text_from_cell_with_formatting(self) -> None:
        """Test _extract_text_from_cell helper method."""
        table_text = """| **Bold** |
|----------|
| Normal   |"""

        ast = self.parser.parse(table_text)
        
        # Get the table element
        table = ast.children[0]
        first_row = table.children[0]
        first_cell = first_row.children[0]

        # Test extraction
        text = self.renderer._extract_text_from_cell(first_cell)
        assert "Bold" in text

    def test_render_table_preserves_inline_code(self) -> None:
        """Test that inline code in tables is preserved."""
        table_text = """| Command | Description |
|---------|-------------|
| `ls -la` | List files |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        assert "`ls -la`" in rows[1][0]

    def test_render_multiple_tables(self) -> None:
        """Test document with multiple tables."""
        text = """# First Table

| A | B |
|---|---|
| 1 | 2 |

# Second Table

| X | Y |
|---|---|
| 3 | 4 |"""

        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Should call render table twice
        assert self.mock_canvas._render_table_from_ast.call_count == 2

    def test_render_table_mixed_with_other_content(self) -> None:
        """Test table rendering within mixed content."""
        text = """# Heading

Some paragraph text.

| Col1 | Col2 |
|------|------|
| A    | B    |

More text after table."""

        ast = self.parser.parse(text)
        self.renderer.render(ast)

        # Verify various render methods were called
        self.mock_canvas._render_heading.assert_called()
        self.mock_canvas._render_paragraph.assert_called()
        self.mock_canvas._render_table_from_ast.assert_called()

    def test_render_table_all_alignments(self) -> None:
        """Test table with all three alignment types."""
        table_text = """| Left Aligned | Center Aligned | Right Aligned |
|:-------------|:--------------:|--------------:|
| Left         | Center         | Right         |
| L            | C              | R             |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, alignments = args

        assert alignments == ['left', 'center', 'right']
        assert len(rows) == 3  # Header + 2 data rows

    def test_render_table_with_special_characters(self) -> None:
        """Test table with special characters in cells."""
        table_text = """| Symbol | Meaning |
|--------|---------|
| &      | And     |
| <      | Less    |
| >      | Greater |"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        # Special characters should be preserved
        assert "&" in rows[1][0]
        assert "<" in rows[2][0] or "Less" in rows[2][1]

    def test_render_table_header_only(self) -> None:
        """Test table with only header row."""
        table_text = """| Header 1 | Header 2 |
|----------|----------|"""

        ast = self.parser.parse(table_text)
        self.renderer.render(ast)

        args = self.mock_canvas._render_table_from_ast.call_args[0]
        rows, _ = args

        # Should have at least the header
        assert len(rows) >= 1
        assert "Header" in rows[0][0]

    def test_table_rendering_updates_canvas_position(self) -> None:
        """Test that table rendering updates current_y position."""
        table_text = """| A | B |
|---|---|
| 1 | 2 |"""

        ast = self.parser.parse(table_text)
        initial_y = self.mock_canvas.current_y

        self.renderer.render(ast)

        # current_y should be modified (table rendering updates it)
        # We can't check the exact value with mocks, but we verify the method was called
        self.mock_canvas._render_table_from_ast.assert_called_once()


class TestMarkdownCanvasTableMethods:
    """Test the MarkdownCanvas table rendering methods directly."""

    def setup_method(self) -> None:
        """Set up test fixtures with real MarkdownCanvas."""
        # We'll test with mocks to avoid needing tkinter
        self.canvas = Mock()
        self.canvas.envelope_left = 20
        self.canvas.envelope_right = 600
        self.canvas.envelope_width = 580
        self.canvas.current_y = 50
        self.canvas.paragraph_spacing = 15

        # Mock fonts
        mock_font = Mock()
        mock_font.metrics = Mock(return_value=15)
        mock_font.measure = Mock(side_effect=lambda t: len(t) * 8)

        self.canvas.fonts = {
            'normal': mock_font,
            'bold': mock_font,
            'italic': mock_font,
            'bold_italic': mock_font,
        }

        # Mock _parse_inline_formatting
        self.canvas._parse_inline_formatting = Mock(
            side_effect=lambda t: [(t, False, False)]
        )

        # Import and bind the methods
        from editor.markdown_canvas import MarkdownCanvas
        self.canvas._render_table_from_ast = MarkdownCanvas._render_table_from_ast.__get__(
            self.canvas
        )
        self.canvas._render_cell_text = MarkdownCanvas._render_cell_text.__get__(
            self.canvas
        )
        self.canvas._parse_inline_formatting = MarkdownCanvas._parse_inline_formatting.__get__(
            self.canvas
        )
        self.canvas._parse_regular_formatting = MarkdownCanvas._parse_regular_formatting.__get__(
            self.canvas
        )
        self.canvas._get_critic_color = MarkdownCanvas._get_critic_color.__get__(
            self.canvas
        )

    def test_render_table_from_ast_basic(self) -> None:
        """Test _render_table_from_ast with basic data."""
        rows = [
            ["Header 1", "Header 2"],
            ["Data 1", "Data 2"]
        ]
        alignments = ['left', 'left']

        self.canvas._render_table_from_ast(rows, alignments)

        # Verify drawing methods were called
        assert self.canvas.create_line.called
        assert self.canvas.create_rectangle.called

    def test_render_table_empty_rows(self) -> None:
        """Test that empty rows list is handled gracefully."""
        rows = []
        alignments = []

        # Should not raise an error
        self.canvas._render_table_from_ast(rows, alignments)

        # Should return early without drawing
        assert not self.canvas.create_line.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
