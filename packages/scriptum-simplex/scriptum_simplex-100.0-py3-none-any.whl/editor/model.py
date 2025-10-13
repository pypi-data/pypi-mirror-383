"""
Model component for Scriptum Simplex.
Handles data storage and business logic following MVC architecture.
"""

import os
from typing import Optional, Any
import criticmarkup
from .markdown_parser import MarkdownParser
from .document_metadata import DocumentMetadata


class Model:
    """
    Model class that manages the application's data and business logic.
    Stores raw text, file path, and handles file I/O operations.
    """

    def __init__(self) -> None:
        """Initialize the model with default values."""
        self.raw_text: str = ""
        self.file_path: Optional[str] = None
        self.is_dirty: bool = False

        # Initialize CriticMarkup processor
        self.critic = criticmarkup.CriticMarkup()

        # Initialize Marko parser with GFM extension
        self.parser: MarkdownParser = MarkdownParser()

        # Cache for parsed AST (invalidated when text changes)
        self._ast_cache: Optional[Any] = None
        self._processed_text_cache: Optional[str] = None
        
        # Document metadata manager
        self.metadata: DocumentMetadata = DocumentMetadata()

    def set_text(self, text: str) -> None:
        """
        Set the raw text content and mark as dirty if changed.

        Args:
            text: The new text content
        """
        if self.raw_text != text:
            self.raw_text = text
            self.is_dirty = True
            # Invalidate caches when text changes
            self._ast_cache = None
            self._processed_text_cache = None

    def get_text(self) -> str:
        """
        Get the current raw text content.

        Returns:
            The current raw text
        """
        return self.raw_text

    def get_processed_text(self) -> str:
        """
        Get the text after CriticMarkup processing (cached).

        Returns:
            Text with CriticMarkup processed
        """
        if self._processed_text_cache is None:
            self._processed_text_cache = self.critic.process(self.raw_text)
        return self._processed_text_cache

    def get_ast(self) -> Any:
        """
        Get the parsed AST of the document (cached).

        The AST is generated from the CriticMarkup-processed text.

        Returns:
            Marko Document AST node
        """
        if self._ast_cache is None:
            processed_text = self.get_processed_text()
            self._ast_cache = self.parser.parse(processed_text)
        return self._ast_cache

    def render_html(self) -> str:
        """
        Convert the raw text through CriticMarkup and then Markdown to HTML.

        Returns:
            Complete HTML string ready for display
        """
        try:
            # Get CriticMarkup-processed text (cached)
            processed_text = self.get_processed_text()

            # Convert Markdown to HTML using Marko
            html_content = self.parser.render_html(processed_text)

            # Wrap in a complete HTML document with basic styling
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}

        /* CriticMarkup styles */
        .critic.addition {{
            background-color: #d4edda;
            color: #155724;
            text-decoration: none;
        }}

        .critic.deletion {{
            background-color: #f8d7da;
            color: #721c24;
            text-decoration: line-through;
        }}

        .critic.substitution {{
            background-color: #fff3cd;
            color: #856404;
        }}

        .critic.comment {{
            background-color: #e2e3e5;
            color: #383d41;
            font-style: italic;
        }}

        .critic.highlight {{
            background-color: #ffeaa7;
            color: #2d3436;
        }}

        /* Standard markdown styles */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}

        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}

        pre {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}

        blockquote {{
            border-left: 4px solid #dee2e6;
            margin: 0;
            padding-left: 1em;
            color: #6c757d;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}

        th, td {{
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            text-align: left;
        }}

        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
            return full_html

        except Exception as e:
            # Return error message in HTML format
            return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
    <div style="color: red; font-family: monospace;">
        <h3>Rendering Error:</h3>
        <p>{str(e)}</p>
    </div>
</body>
</html>
"""

    def new_file(self) -> None:
        """Create a new file by clearing content and resetting state."""
        self.raw_text = ""
        self.file_path = None
        self.is_dirty = False
        # Invalidate caches
        self._ast_cache = None
        self._processed_text_cache = None

    def open_file(self, file_path: str) -> bool:
        """
        Open a file and load its contents.

        Args:
            file_path: Path to the file to open

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.raw_text = file.read()
                self.file_path = file_path
                self.is_dirty = False
                # Invalidate caches
                self._ast_cache = None
                self._processed_text_cache = None
                
                # Load metadata for this document
                self.metadata = DocumentMetadata(file_path)
                
                return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False

    def save_file(self) -> bool:
        """
        Save the current content to the current file path.

        Returns:
            True if successful, False otherwise
        """
        if self.file_path is None:
            return False

        return self.save_file_as(self.file_path)

    def save_file_as(self, file_path: str) -> bool:
        """
        Save the current content to a specified file path.

        Args:
            file_path: Path where to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.raw_text)
                self.file_path = file_path
                self.is_dirty = False
                
                # Update metadata with new file path
                self.metadata.markdown_file_path = file_path
                
                return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def get_file_name(self) -> str:
        """
        Get the current file name for display purposes.

        Returns:
            File name or "Untitled" if no file is open
        """
        if self.file_path:
            return os.path.basename(self.file_path)
        return "Untitled"

    def has_unsaved_changes(self) -> bool:
        """
        Check if there are unsaved changes.

        Returns:
            True if there are unsaved changes
        """
        return self.is_dirty
