"""
Integration example showing how to use MarkdownCanvas in Scriptum Simplex.

This module demonstrates how to replace or supplement the HTML preview
with the lightweight MarkdownCanvas widget.
"""

import tkinter as tk
from tkinter import ttk
from markdown_canvas import MarkdownCanvas


class MarkdownCanvasPreview:
    """
    A preview pane using MarkdownCanvas instead of HTML rendering.
    Can be used as a drop-in replacement for the HTML preview.
    """
    
    def __init__(self, parent_frame):
        """
        Initialize the MarkdownCanvas preview pane.
        
        Args:
            parent_frame: The parent frame to contain the preview
        """
        self.parent_frame = parent_frame
        self._create_preview_pane()
        
    def _create_preview_pane(self):
        """Create the preview pane with MarkdownCanvas."""
        # Preview label
        preview_label = ttk.Label(
            self.parent_frame, 
            text="Preview (MarkdownCanvas)", 
            font=("Arial", 10, "bold")
        )
        preview_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
        
        # Create frame for canvas and scrollbar
        canvas_frame = ttk.Frame(self.parent_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the MarkdownCanvas
        self.canvas = MarkdownCanvas(
            canvas_frame,
            bg='#f8f9fa',  # Light gray background like the original preview
            relief=tk.FLAT,
            borderwidth=0
        )
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_preview(self, markdown_text: str):
        """
        Update the preview with new Markdown content.
        
        Args:
            markdown_text: The Markdown text to render
        """
        self.canvas.render_markdown(markdown_text)


def create_demo_window():
    """Create a demo window showing the MarkdownCanvas integration."""
    
    # Create main window
    root = tk.Tk()
    root.title("MarkdownCanvas Integration Demo")
    root.geometry("1000x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create paned window for side-by-side layout
    paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    
    # Create left pane (Editor)
    editor_frame = ttk.Frame(paned_window)
    paned_window.add(editor_frame, weight=1)
    
    # Editor label
    editor_label = ttk.Label(editor_frame, text="Editor", font=("Arial", 10, "bold"))
    editor_label.pack(anchor=tk.W, padx=5, pady=(5, 0))
    
    # Create text editor
    text_frame = ttk.Frame(editor_frame)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    text_editor = tk.Text(
        text_frame,
        wrap=tk.WORD,
        font=("Consolas", 11),
        bg="white",
        fg="black"
    )
    
    # Scrollbar for text editor
    text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_editor.yview)
    text_editor.configure(yscrollcommand=text_scrollbar.set)
    
    text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create right pane (Preview)
    preview_frame = ttk.Frame(paned_window)
    paned_window.add(preview_frame, weight=1)
    
    # Create MarkdownCanvas preview
    preview = MarkdownCanvasPreview(preview_frame)
    
    # Sample content
    sample_content = """# Integration Demo

This demonstrates how **MarkdownCanvas** can be integrated into Scriptum Simplex.

## Benefits

* **Lightweight**: No web engine required
* **Fast**: Direct canvas rendering
* **Customizable**: Easy to modify appearance
* **Native**: Pure Tkinter implementation

## Supported Features

### Text Formatting
- **Bold text** using **asterisks** or __underscores__
- *Italic text* using *asterisks* or _underscores_

### Lists
1. Numbered lists work perfectly
2. With proper **formatting** support
3. And automatic numbering

* Bullet lists also work
* With various *formatting* options
* Including **mixed** *styles*

### Headings
All three heading levels are supported with appropriate sizing.

## Usage

Simply replace the HTML preview with:

```python
preview = MarkdownCanvasPreview(preview_frame)
preview.update_preview(markdown_text)
```

Try editing the text on the left to see live updates!
"""
    
    # Insert sample content
    text_editor.insert(tk.END, sample_content)
    
    # Function to update preview
    def update_preview(event=None):
        content = text_editor.get("1.0", tk.END + "-1c")
        preview.update_preview(content)
    
    # Bind text change events
    text_editor.bind('<KeyRelease>', update_preview)
    text_editor.bind('<Button-1>', update_preview)
    text_editor.bind('<ButtonRelease-1>', update_preview)
    
    # Initial preview update
    root.after(100, update_preview)
    
    # Set pane sizes after window is rendered
    def set_pane_sizes():
        try:
            window_width = root.winfo_width()
            if window_width > 50:
                sash_pos = int(window_width * 0.5)
                paned_window.sashpos(0, sash_pos)
        except tk.TclError:
            root.after(100, set_pane_sizes)
    
    root.after(200, set_pane_sizes)
    
    return root


if __name__ == "__main__":
    print("Starting MarkdownCanvas Integration Demo...")
    
    # Create and run the demo
    root = create_demo_window()
    root.mainloop()
    
    print("Demo completed.")
