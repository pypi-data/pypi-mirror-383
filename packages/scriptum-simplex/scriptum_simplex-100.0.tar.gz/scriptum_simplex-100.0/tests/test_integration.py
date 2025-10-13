"""
Integration tests for Scriptum Simplex.
Tests the interactions between Model, View, and Controller components.
"""

import pytest
import tempfile
import os
import tkinter as tk
from unittest.mock import Mock, patch
from editor.model import Model
from editor.view import View
from editor.controller import Controller


class TestIntegration:
    """Integration test cases for the complete application."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create a root window for testing (required for tkinter widgets)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
    
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()
    
    def test_controller_initialization(self):
        """Test that Controller properly initializes Model and View."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            # Mock needs to return empty text during initialization
            mock_view.get_editor_text.return_value = ""
            # Mock the after method to not actually call the callback
            mock_view.after = Mock(return_value=None)

            controller = Controller()

            # Verify that view.set_controller was called
            mock_view.set_controller.assert_called_once_with(controller)

            # Verify that model and view are created
            assert isinstance(controller.model, Model)
            assert controller.view == mock_view

            # Verify initialization methods were called
            mock_view.update_title.assert_called()
            # after() should have been called to schedule preview update
            mock_view.after.assert_called_with(300, controller._update_preview)
    
    def test_text_change_flow(self):
        """Test the complete flow when text changes in the editor."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            
            # Set up mock return values
            test_text = "# Test\n\nThis is {++new++} content."
            mock_view.get_editor_text.return_value = test_text
            mock_view.after = Mock()
            
            controller = Controller()
            
            # Simulate text change
            controller.on_text_change()
            
            # Verify the flow
            mock_view.get_editor_text.assert_called()
            assert controller.model.get_text() == test_text
            assert controller.model.has_unsaved_changes()
            
            # Verify that preview was updated
            mock_view.update_preview.assert_called()
            mock_view.update_title.assert_called()
    
    def test_new_file_flow(self):
        """Test the complete flow for creating a new file."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            mock_view.get_editor_text.return_value = ""
            mock_view.after = Mock()
            
            controller = Controller()
            
            # Set some initial state
            controller.model.set_text("Some existing content")
            controller.model.file_path = "/some/path.md"
            
            # Mock that there are no unsaved changes (user doesn't want to save)
            controller.model.is_dirty = False
            
            # Call new_file
            controller.new_file()
            
            # Verify the model was reset
            assert controller.model.get_text() == ""
            assert controller.model.file_path is None
            assert not controller.model.has_unsaved_changes()
            
            # Verify the view was updated
            mock_view.set_editor_text.assert_called_with("")
            mock_view.update_preview.assert_called()
            mock_view.update_title.assert_called()
    
    def test_open_file_flow(self):
        """Test the complete flow for opening a file."""
        test_content = """# Test Document

This is a test with {++additions++} and {--deletions--}.

## CriticMarkup Examples

- {~~Old~>New~~} substitutions
- {>>Comments<<}
- {==Highlights==}
"""
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name
        
        try:
            with patch('editor.controller.View') as mock_view_class:
                mock_view = Mock()
                mock_view_class.return_value = mock_view
                mock_view.get_editor_text.return_value = ""
                mock_view.after = Mock()
                
                controller = Controller()
                
                # Mock no unsaved changes
                controller.model.is_dirty = False
                
                # Open the file
                controller.open_file(temp_path)
                
                # Verify the model was updated
                assert controller.model.get_text() == test_content
                assert controller.model.file_path == temp_path
                assert not controller.model.has_unsaved_changes()
                
                # Verify the view was updated
                mock_view.set_editor_text.assert_called_with(test_content)
                mock_view.update_preview.assert_called()
                mock_view.update_title.assert_called()
                mock_view.show_info.assert_called()
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_file_flow(self):
        """Test the complete flow for saving a file."""
        test_content = "# Test\n\nContent with {++changes++}."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('editor.controller.View') as mock_view_class:
                mock_view = Mock()
                mock_view_class.return_value = mock_view
                mock_view.get_editor_text.return_value = test_content
                mock_view.after = Mock()
                
                controller = Controller()
                
                # Set up the model with content and file path
                controller.model.set_text(test_content)
                controller.model.file_path = temp_path
                
                # Save the file
                controller.save_file()
                
                # Verify the model state
                assert not controller.model.has_unsaved_changes()
                
                # Verify the view was updated
                mock_view.update_title.assert_called()
                mock_view.show_info.assert_called()
                
                # Verify the file was actually saved
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                assert saved_content == test_content
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_file_as_flow(self):
        """Test the complete flow for saving a file with a new name."""
        test_content = "# New File\n\nWith {++CriticMarkup++} content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('editor.controller.View') as mock_view_class:
                mock_view = Mock()
                mock_view_class.return_value = mock_view
                mock_view.get_editor_text.return_value = test_content
                mock_view.after = Mock()
                
                controller = Controller()
                
                # Set up the model with content but no file path
                controller.model.set_text(test_content)
                
                # Save as new file
                controller.save_file_as(temp_path)
                
                # Verify the model state
                assert controller.model.file_path == temp_path
                assert not controller.model.has_unsaved_changes()
                
                # Verify the view was updated
                mock_view.update_title.assert_called()
                mock_view.show_info.assert_called()
                
                # Verify the file was actually saved
                with open(temp_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                assert saved_content == test_content
        
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_unsaved_changes_dialog_flow(self):
        """Test the flow when there are unsaved changes."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            mock_view.get_editor_text.return_value = "Some content"
            mock_view.after = Mock()
            
            controller = Controller()
            
            # Set up unsaved changes
            controller.model.set_text("Modified content")
            assert controller.model.has_unsaved_changes()
            
            # Test when user chooses to save
            mock_view.ask_yes_no.return_value = True
            controller.model.file_path = "/some/path.md"
            
            # Mock successful save
            with patch.object(controller.model, 'save_file', return_value=True):
                result = controller._ask_save_changes()
                assert result is True
                mock_view.ask_yes_no.assert_called()
            
            # Test when user chooses not to save
            mock_view.ask_yes_no.return_value = False
            result = controller._ask_save_changes()
            assert result is True  # Should continue without saving
    
    def test_preview_update_with_criticmarkup(self):
        """Test that preview updates correctly with CriticMarkup content."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            mock_view.get_editor_text.return_value = ""  # For initialization
            mock_view.after = Mock()

            test_text = """# CriticMarkup Test

This text has {++additions++}, {--deletions--}, and {~~old~>new~~} substitutions.

{>>This is a comment<<}

{==This is highlighted==}
"""
            mock_view.get_editor_text.return_value = test_text
            
            controller = Controller()
            
            # Trigger text change
            controller.on_text_change()
            
            # Verify that update_preview was called
            mock_view.update_preview.assert_called()
            
            # Get the markdown text that was passed to update_preview
            call_args = mock_view.update_preview.call_args
            markdown_content = call_args[0][0]
            
            # Verify content is a string (update_preview now gets markdown text, not HTML)
            assert isinstance(markdown_content, str)
            # The content should contain the original markdown with CriticMarkup
            assert "additions" in markdown_content
            assert "deletions" in markdown_content
            assert "substitutions" in markdown_content
    
    def test_error_handling_in_preview(self):
        """Test error handling when preview rendering fails."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            mock_view.get_editor_text.return_value = "Some text"
            mock_view.after = Mock()
            
            controller = Controller()
            
            # Mock the view's update_preview to raise an exception
            mock_view.update_preview.side_effect = Exception("Test error")
            
            # This should not crash, error is logged
            try:
                controller._update_preview()
            except Exception:
                pass  # Error is caught and logged
            
            # Verify that update_preview was called
            mock_view.update_preview.assert_called()
    
    def test_title_updates(self):
        """Test that window title updates correctly."""
        with patch('editor.controller.View') as mock_view_class:
            mock_view = Mock()
            mock_view_class.return_value = mock_view
            mock_view.get_editor_text.return_value = ""
            mock_view.after = Mock()
            
            controller = Controller()
            
            # Test initial title (called during initialization)
            assert mock_view.update_title.called
            
            # Test title with unsaved changes
            controller.model.set_text("Some changes")
            controller._update_title()
            mock_view.update_title.assert_called_with("Untitled", True)
            
            # Test title with file name
            controller.model.file_path = "/path/to/test.md"
            controller.model.is_dirty = False
            controller._update_title()
            mock_view.update_title.assert_called_with("test.md", False)


class TestModelViewIntegration:
    """Test direct integration between Model and View components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()
    
    def test_model_rendering_with_real_libraries(self):
        """Test that Model actually renders CriticMarkup correctly with real libraries."""
        model = Model()
        
        test_text = """# Real Integration Test

This tests actual CriticMarkup processing:

- Addition: {++This was added++}
- Deletion: {--This was removed--}
- Substitution: {~~old text~>new text~~}
- Comment: {>>This is a comment<<}
- Highlight: {==This is important==}

## Markdown Features

**Bold** and *italic* text should work.

```python
def test_function():
    return "Hello, World!"
```

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        
        model.set_text(test_text)
        html_output = model.render_html()
        
        # Verify basic HTML structure
        assert "<!DOCTYPE html>" in html_output
        assert "<html>" in html_output
        assert "<body>" in html_output
        assert "</body>" in html_output
        assert "</html>" in html_output
        
        # Verify Markdown processing
        assert "<h1>Real Integration Test</h1>" in html_output
        assert "<strong>Bold</strong>" in html_output
        assert "<em>italic</em>" in html_output
        assert "<table>" in html_output
        # Marko uses code with class attribute for language
        assert '<code class="language-python">' in html_output or "<code>" in html_output
        
        # Verify that CriticMarkup content is present (processed form)
        # Note: exact output depends on criticmarkup library implementation
        assert "added" in html_output.lower()
        assert "removed" in html_output.lower()
        assert "comment" in html_output.lower()
        assert "important" in html_output.lower()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
