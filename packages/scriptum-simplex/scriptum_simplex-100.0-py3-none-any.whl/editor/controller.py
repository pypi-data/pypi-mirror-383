"""
Controller component for Scriptum Simplex.
Connects the Model and View following MVC architecture.
"""

import logging
from .model import Model
from .view import View


class Controller:
    """
    Controller class that acts as the intermediary between Model and View.
    Handles all user interactions and coordinates between components.
    """
    
    def __init__(self):
        """Initialize the controller with Model and View instances."""
        logging.info("Initializing Controller...")
        # Create model and view instances
        logging.info("Creating Model...")
        self.model = Model()
        logging.info("Creating View...")
        self.view = View()
        
        # Connect the controller to the view
        logging.info("Connecting controller to view...")
        self.view.set_controller(self)
        
        # Track current theme
        self.current_theme = "default"
        
        # Initialize the interface
        logging.info("Initializing interface...")
        self._initialize_interface()
        logging.info("Controller initialization complete")
    
    def _initialize_interface(self):
        """Initialize the interface with default content and preview."""
        # Set initial text from the view's placeholder
        initial_text = self.view.get_editor_text()
        self.model.set_text(initial_text)
        
        # Update title immediately
        self._update_title()
        
        # Delay preview update to ensure canvas is fully initialized
        self.view.after(300, self._update_preview)
    
    def run(self):
        """Start the application main loop."""
        logging.info("Starting main loop...")
        self.view.mainloop()
        logging.info("Main loop ended")
    
    def on_text_change(self):
        """Handle text changes in the editor."""
        # Get current text from the view
        current_text = self.view.get_editor_text()
        
        # Update the model
        self.model.set_text(current_text)
        
        # Update the preview
        self._update_preview()
        
        # Update the title to show unsaved changes
        self._update_title()
    
    def new_file(self):
        """Handle creating a new file."""
        # Check for unsaved changes
        if self.model.has_unsaved_changes():
            if not self._ask_save_changes():
                return  # User cancelled
        
        # Create new file in model
        self.model.new_file()
        
        # Clear the editor
        self.view.set_editor_text("")
        
        # Update preview and title
        self._update_preview()
        self._update_title()
    
    def open_file(self, file_path: str):
        """
        Handle opening a file.
        
        Args:
            file_path: Path to the file to open
        """
        # Check for unsaved changes
        if self.model.has_unsaved_changes():
            if not self._ask_save_changes():
                return  # User cancelled
        
        # Try to open the file
        if self.model.open_file(file_path):
            # Update the view with the loaded content
            self.view.set_editor_text(self.model.get_text())
            
            # Update preview and title
            self._update_preview()
            self._update_title()
            
            self.view.show_info("File Opened", f"Successfully opened: {self.model.get_file_name()}")
        else:
            self.view.show_error("Error", f"Could not open file: {file_path}")
    
    def save_file(self):
        """Handle saving the current file."""
        if self.model.file_path is None:
            # No file path set, use Save As
            self.save_file()
        else:
            # Save to current file path
            if self.model.save_file():
                self._update_title()
                self.view.show_info("File Saved", f"Successfully saved: {self.model.get_file_name()}")
            else:
                self.view.show_error("Error", "Could not save file")
    
    def save_file_as(self, file_path: str = None):
        """
        Handle saving the file with a new name.
        
        Args:
            file_path: Path where to save the file (if None, will be requested from view)
        """
        if file_path is None:
            # This will be handled by the view's file dialog
            return
        
        if self.model.save_file_as(file_path):
            self._update_title()
            self.view.show_info("File Saved", f"Successfully saved: {self.model.get_file_name()}")
        else:
            self.view.show_error("Error", f"Could not save file: {file_path}")
    
    def change_theme(self, theme_name: str):
        """
        Change the application theme.
        
        Args:
            theme_name: Name of the theme to apply ('default', 'typora', 'github')
        """
        try:
            logging.info(f"Changing theme to: {theme_name}")
            
            # Apply the theme to the view
            self.view.apply_theme(theme_name)
            
            # Store the current theme
            self.current_theme = theme_name
            
            # Force a complete re-render to apply new fonts and colors
            # Get the current text and trigger a full preview update
            current_text = self.model.get_text()
            if current_text:
                self.view.update_preview(current_text)
            
            logging.info(f"Theme changed successfully to: {theme_name}")
            
        except Exception as e:
            logging.error(f"Error changing theme: {e}")
            self.view.show_error("Theme Error", f"Could not change theme: {str(e)}")
    
    def load_typora_theme(self, folder_path: str):
        """
        Load a Typora theme from a folder.
        
        Args:
            folder_path: Path to the Typora theme folder
        """
        try:
            from .full_typora_theme_support import FullTyporaThemeLoader
            from pathlib import Path
            
            logging.info(f"Loading Typora theme from folder: {folder_path}")
            
            # Create loader and load theme
            loader = FullTyporaThemeLoader()
            theme = loader.load_theme_from_folder(folder_path)
            
            if theme:
                # Apply the theme
                self.view.markdown_preview.set_theme(theme)
                
                # Force a complete re-render
                current_text = self.model.get_text()
                if current_text:
                    self.view.update_preview(current_text)
                
                theme_name = Path(folder_path).name
                self.view.show_info(
                    "Theme Loaded",
                    f"Successfully loaded Typora theme: {theme_name}\n\n"
                    f"CSS Variables: {len(loader.css_variables)} found"
                )
                logging.info(f"Successfully loaded and applied Typora theme: {theme_name}")
            else:
                self.view.show_error(
                    "Load Error",
                    "Could not load Typora theme. Please check the theme folder contains a valid CSS file."
                )
                
        except Exception as e:
            logging.error(f"Error loading Typora theme: {e}")
            import traceback
            traceback.print_exc()
            self.view.show_error("Theme Error", f"Could not load Typora theme: {str(e)}")
    
    def show_metadata_dialog(self):
        """Show the metadata editor dialog."""
        try:
            from .metadata_dialog import MetadataDialog
            
            # Check if we have a file open
            if not self.model.file_path:
                self.view.show_info(
                    "No File Open",
                    "Please save the document first before editing metadata."
                )
                return
            
            # Show dialog
            dialog = MetadataDialog(self.view, self.model.metadata)
            if dialog.show():
                # Save metadata to file
                if self.model.metadata.save():
                    self.view.show_info("Metadata Saved", "Document metadata has been saved successfully.")
                else:
                    self.view.show_error("Save Error", "Could not save metadata file.")
                    
        except Exception as e:
            logging.error(f"Error showing metadata dialog: {e}")
            self.view.show_error("Metadata Error", f"Could not open metadata dialog: {str(e)}")
    
    def on_closing(self):
        """Handle application closing."""
        # Check for unsaved changes
        if self.model.has_unsaved_changes():
            if not self._ask_save_changes():
                return  # User cancelled closing
        
        # Close the application
        self.view.destroy()
    
    def _update_preview(self):
        """Update the preview pane with rendered Markdown."""
        try:
            logging.info("Controller._update_preview called")
            # Get the raw markdown text and pass it directly to the view
            markdown_text = self.model.get_text()
            logging.info(f"Got text from model: {len(markdown_text)} characters")
            logging.info("Calling view.update_preview...")
            self.view.update_preview(markdown_text)
            logging.info("view.update_preview completed")
        except Exception as e:
            # Show error in preview
            logging.error(f"Error in _update_preview: {e}")
            error_markdown = f"""# Preview Error

An error occurred while rendering the preview:

**{str(e)}**
Please check your Markdown syntax and try again.
"""
            self.view.update_preview(error_markdown)
    
    def _update_title(self):
        """Update the window title and status bar with current file info."""
        filename = self.model.get_file_name()
        is_dirty = self.model.has_unsaved_changes()
        self.view.update_title(filename, is_dirty)
        self.view.update_status_bar(filename, is_dirty)
    
    def _ask_save_changes(self) -> bool:
        """
        Ask user if they want to save unsaved changes.
        
{{ ... }}
            True if user wants to continue (saved or discarded changes)
            False if user cancelled
        """
        filename = self.model.get_file_name()
        response = self.view.ask_yes_no(
            "Unsaved Changes",
            f"You have unsaved changes in '{filename}'.\n\nDo you want to save them?"
        )
        
        if response:  # User wants to save
            if self.model.file_path is None:
                # Need to use Save As dialog
                # This is a bit tricky - we need to trigger the Save As dialog
                # For now, we'll just save to a default location or ask user
                self.save_file()
                # Check if save was successful (file_path would be set)
                return self.model.file_path is not None
            else:
                # Save to existing file
                return self.model.save_file()
        
        # User chose not to save, continue with the operation
        return True


# Additional utility functions that might be useful

def create_sample_document() -> str:
    """
    Create a sample document with CriticMarkup examples.
    
    Returns:
        Sample document text
    """
    return """# CriticMarkup Sample Document

This document demonstrates the various CriticMarkup syntax elements.

## Basic CriticMarkup Syntax

### Additions
Use `{++text++}` to mark text that should be added:
{++This sentence was added to provide more context.++}

### Deletions
Use `{--text--}` to mark text that should be deleted:
This is a sentence {--that contains unnecessary information--} about CriticMarkup.

### Substitutions
Use `{~~old text~>new text~~}` to mark text that should be replaced:
CriticMarkup is {~~good~>excellent~~} for tracking changes in documents.

### Comments
Use `{>>comment<<}` to add comments:
This feature is very useful{>>We should emphasize this more<<} for collaborative editing.

### Highlights
Use `{==text==}` to highlight important text:
{==This is the most important point in the entire document.==}

## Combining with Regular Markdown

CriticMarkup works seamlessly with regular Markdown syntax:

- **Bold text** with {++additions++}
- *Italic text* with {--deletions--}
- `Code snippets` with {~~old~>new~~} substitutions
- [Links](https://example.com) with {>>comments<<}

### Code Blocks

```python
def process_criticmarkup(text):
    # {++Add error handling++}
    {--# This is old code--}
    {~~return text~>return processed_text~~}
```

### Tables

| Feature | Status | {>>Notes<<} |
|---------|--------|-------------|
| Additions | {++Complete++} | Working well |
| Deletions | {--Incomplete--}{++Complete++} | Fixed bugs |
| Substitutions | {~~In Progress~>Complete~~} | Ready to ship |

## Advanced Usage

You can nest CriticMarkup within other Markdown elements:

> This is a blockquote with {++additional content++} and {~~old~>new~~} changes.

1. First item {>>This needs more detail<<}
2. {++Second item was added later++}
3. {--Third item should be removed--}

---

*This document demonstrates how CriticMarkup can be used to track changes in Markdown documents while maintaining readability.*
"""
