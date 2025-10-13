"""
Unit tests for the Model class.
Tests the core functionality of data handling and CriticMarkup rendering.
"""

import pytest
import tempfile
import os
from editor.model import Model


class TestModel:
    """Test cases for the Model class."""
    
    def setup_method(self):
        """Set up a fresh Model instance for each test."""
        self.model = Model()
    
    def test_initial_state(self):
        """Test that the model initializes with correct default values."""
        assert self.model.raw_text == ""
        assert self.model.file_path is None
        assert self.model.is_dirty is False
        assert self.model.get_file_name() == "Untitled"
        assert not self.model.has_unsaved_changes()
    
    def test_set_and_get_text(self):
        """Test setting and getting text content."""
        test_text = "# Hello World\n\nThis is a test."
        
        self.model.set_text(test_text)
        
        assert self.model.get_text() == test_text
        assert self.model.is_dirty is True
        assert self.model.has_unsaved_changes()
    
    def test_set_same_text_no_dirty_flag(self):
        """Test that setting the same text doesn't mark as dirty."""
        test_text = "Same text"
        
        self.model.set_text(test_text)
        assert self.model.is_dirty is True
        
        # Reset dirty flag
        self.model.is_dirty = False
        
        # Set same text again
        self.model.set_text(test_text)
        assert self.model.is_dirty is False
    
    def test_render_basic_markdown(self):
        """Test rendering basic Markdown without CriticMarkup."""
        markdown_text = """# Hello World

This is **bold** and *italic* text.

- List item 1
- List item 2

```python
print("Hello, World!")
```
"""
        
        self.model.set_text(markdown_text)
        html_output = self.model.render_html()
        
        # Check that HTML is generated
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "<h1>Hello World</h1>" in html_output
        assert "<strong>bold</strong>" in html_output
        assert "<em>italic</em>" in html_output
        assert "<ul>" in html_output
        assert "<li>List item 1</li>" in html_output
        # Marko uses code with class attribute for language info
        assert '<code class="language-python">' in html_output or "<code>" in html_output
    
    def test_render_criticmarkup_additions(self):
        """Test rendering CriticMarkup additions."""
        text_with_additions = "This is a sentence {++with an addition++} in it."
        
        self.model.set_text(text_with_additions)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        # The exact HTML output depends on the criticmarkup library implementation
        # We just verify that the text is processed and HTML is generated
        assert "addition" in html_output
    
    def test_render_criticmarkup_deletions(self):
        """Test rendering CriticMarkup deletions."""
        text_with_deletions = "This is a sentence {--with a deletion--} in it."
        
        self.model.set_text(text_with_deletions)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "deletion" in html_output
    
    def test_render_criticmarkup_substitutions(self):
        """Test rendering CriticMarkup substitutions."""
        text_with_substitutions = "This is {~~old text~>new text~~} in a sentence."
        
        self.model.set_text(text_with_substitutions)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        # Should contain both old and new text in some form
        assert "text" in html_output
    
    def test_render_criticmarkup_comments(self):
        """Test rendering CriticMarkup comments."""
        text_with_comments = "This is a sentence{>>with a comment<<} in it."
        
        self.model.set_text(text_with_comments)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "comment" in html_output
    
    def test_render_criticmarkup_highlights(self):
        """Test rendering CriticMarkup highlights."""
        text_with_highlights = "This is {==highlighted text==} in a sentence."
        
        self.model.set_text(text_with_highlights)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "highlighted" in html_output
    
    def test_render_combined_markdown_and_criticmarkup(self):
        """Test rendering combined Markdown and CriticMarkup."""
        combined_text = """# Test Document

This is **bold text** with {++an addition++}.

## List with Changes

- Item 1 {--to be removed--}
- {++New item++}
- Item with {~~old~>new~~} substitution

{>>This is a comment about the list<<}

### Code with Changes

```python
def hello():
    {--print("Old message")--}
    {++print("New message")++}
```

{==This is an important note.==}
"""
        
        self.model.set_text(combined_text)
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "<h1>Test Document</h1>" in html_output
        assert "<strong>bold text</strong>" in html_output
        assert "addition" in html_output
        assert "substitution" in html_output
        assert "comment" in html_output
        assert "important note" in html_output
    
    def test_render_empty_text(self):
        """Test rendering empty text."""
        self.model.set_text("")
        html_output = self.model.render_html()
        
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        # Should still generate valid HTML structure
        assert "<body>" in html_output
        assert "</body>" in html_output
    
    def test_new_file(self):
        """Test creating a new file."""
        # Set some initial state
        self.model.set_text("Some text")
        self.model.file_path = "/some/path.md"
        
        # Create new file
        self.model.new_file()
        
        assert self.model.raw_text == ""
        assert self.model.file_path is None
        assert self.model.is_dirty is False
        assert self.model.get_file_name() == "Untitled"
    
    def test_file_operations_with_temp_file(self):
        """Test file save and open operations using a temporary file."""
        test_content = """# Test File

This is a test file with {++additions++} and {--deletions--}.

## Features

- CriticMarkup support
- {~~Old~>New~~} substitutions
- {>>Comments<<}
- {==Highlights==}
"""
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test save_file_as
            self.model.set_text(test_content)
            assert self.model.save_file_as(temp_path) is True
            assert self.model.file_path == temp_path
            assert self.model.is_dirty is False
            assert os.path.basename(temp_path) in self.model.get_file_name()
            
            # Test that file was actually written
            with open(temp_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == test_content
            
            # Test open_file
            new_model = Model()
            assert new_model.open_file(temp_path) is True
            assert new_model.get_text() == test_content
            assert new_model.file_path == temp_path
            assert new_model.is_dirty is False
            
            # Test save_file (save to existing path)
            new_content = test_content + "\n\nAdditional content"
            new_model.set_text(new_content)
            assert new_model.is_dirty is True
            assert new_model.save_file() is True
            assert new_model.is_dirty is False
            
            # Verify the save
            with open(temp_path, 'r', encoding='utf-8') as f:
                final_content = f.read()
            assert final_content == new_content
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_file_without_path(self):
        """Test that save_file returns False when no file path is set."""
        self.model.set_text("Some content")
        assert self.model.save_file() is False
    
    def test_open_nonexistent_file(self):
        """Test opening a file that doesn't exist."""
        nonexistent_path = "/path/that/does/not/exist.md"
        assert self.model.open_file(nonexistent_path) is False
        assert self.model.file_path is None
        assert self.model.raw_text == ""
    
    def test_save_to_invalid_path(self):
        """Test saving to an invalid path."""
        self.model.set_text("Some content")
        # Try to save to a path with invalid characters (on Windows)
        invalid_path = "/invalid/path/with\x00null/character.md"
        assert self.model.save_file_as(invalid_path) is False

    def test_get_processed_text(self):
        """Test getting CriticMarkup-processed text."""
        text = "This has {++an addition++} and {--a deletion--}."
        self.model.set_text(text)

        processed = self.model.get_processed_text()

        # Should contain HTML spans for CriticMarkup
        assert isinstance(processed, str)
        assert 'class="critic addition"' in processed
        assert 'class="critic deletion"' in processed

    def test_get_processed_text_caching(self):
        """Test that processed text is cached."""
        text = "# Hello World"
        self.model.set_text(text)

        # First call
        processed1 = self.model.get_processed_text()
        # Second call should return cached value
        processed2 = self.model.get_processed_text()

        assert processed1 == processed2
        assert processed1 is processed2  # Same object reference

    def test_get_ast(self):
        """Test getting the parsed AST."""
        text = "# Heading\n\nParagraph text."
        self.model.set_text(text)

        ast = self.model.get_ast()

        # Should return an AST with children
        assert ast is not None
        assert hasattr(ast, 'children')
        assert len(ast.children) > 0

    def test_get_ast_with_criticmarkup(self):
        """Test that AST includes processed CriticMarkup."""
        text = "Text with {++addition++}."
        self.model.set_text(text)

        ast = self.model.get_ast()

        # AST should be generated from CriticMarkup-processed text
        assert ast is not None
        assert hasattr(ast, 'children')

    def test_get_ast_caching(self):
        """Test that AST is cached."""
        text = "# Test"
        self.model.set_text(text)

        # First call
        ast1 = self.model.get_ast()
        # Second call should return cached value
        ast2 = self.model.get_ast()

        assert ast1 is ast2  # Same object reference

    def test_cache_invalidation_on_set_text(self):
        """Test that caches are invalidated when text changes."""
        self.model.set_text("# First")
        ast1 = self.model.get_ast()
        processed1 = self.model.get_processed_text()

        # Change text
        self.model.set_text("# Second")
        ast2 = self.model.get_ast()
        processed2 = self.model.get_processed_text()

        # Should be different objects (cache was invalidated)
        assert ast1 is not ast2
        assert processed1 != processed2

    def test_cache_invalidation_on_new_file(self):
        """Test that caches are invalidated on new file."""
        self.model.set_text("# Test")
        ast1 = self.model.get_ast()

        self.model.new_file()
        self.model.set_text("# New")
        ast2 = self.model.get_ast()

        assert ast1 is not ast2

    def test_cache_invalidation_on_open_file(self):
        """Test that caches are invalidated when opening a file."""
        self.model.set_text("# Test")
        ast1 = self.model.get_ast()

        # Create a temp file and open it
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Different")
            temp_path = f.name

        try:
            self.model.open_file(temp_path)
            ast2 = self.model.get_ast()

            assert ast1 is not ast2
        finally:
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__])
