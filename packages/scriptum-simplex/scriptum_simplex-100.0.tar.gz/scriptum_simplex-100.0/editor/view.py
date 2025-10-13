"""
View component for Scriptum Simplex.
Handles the graphical user interface following MVC architecture.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re
import html
import logging
from .markdown_canvas import MarkdownCanvas
from .markdown_parser import MarkdownParser
from .full_typora_theme_support.enhanced_canvas import EnhancedMarkdownCanvas
from .full_typora_theme_support import FullTyporaThemeLoader
from .config import Config

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class View(ttk.Window):
    """
    View class that manages the entire graphical user interface.
    Creates the main window, menu, and all GUI components.
    """
    
    def __init__(self):
        """Initialize the main window and all GUI components."""
        logging.info("Initializing View...")
        super().__init__(themename="cosmo")
        
        self.controller = None
        self.parser = MarkdownParser()  # Create parser instance
        self.theme_loader = FullTyporaThemeLoader()  # Create theme loader
        self.app_config = Config()  # Load configuration (renamed to avoid conflict with tk.config())
        logging.info("Parser, theme loader, and config created")
        
        # Configure main window
        self.title("Scriptum Simplex")
        self.geometry("1200x800")
        self.minsize(800, 600)
        logging.info("Window configured")
        
        # Create the GUI components
        logging.info("Creating menu...")
        self._create_menu()
        logging.info("Creating main interface...")
        self._create_main_interface()
        logging.info("Main interface created")
        
        # Configure window closing behavior
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        logging.info("View initialization complete")
    
    def set_controller(self, controller):
        """
        Set the controller reference for handling user actions.
        
        Args:
            controller: The controller instance
        """
        self.controller = controller
    
    def _create_menu(self):
        """Create the menu bar with File and Edit menus."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._on_new, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._on_open, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._on_save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._on_save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._on_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._on_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._on_paste, accelerator="Ctrl+V")
        
        # Document menu
        document_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Document", menu=document_menu)
        document_menu.add_command(label="Metadata...", command=self._on_metadata)
        
        # Themes menu - built dynamically from config
        themes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Themes", menu=themes_menu)
        
        # Add themes from config
        theme_folders = self.app_config.get_theme_folders()
        if theme_folders:
            for folder_path in theme_folders:
                from pathlib import Path
                theme_name = Path(folder_path).name
                themes_menu.add_command(
                    label=theme_name,
                    command=lambda p=folder_path: self._load_theme_from_path(p)
                )
            themes_menu.add_separator()
        
        # Add custom theme loader
        themes_menu.add_command(label="Load Typora Theme...", command=self._on_load_typora_theme)
        themes_menu.add_separator()
        themes_menu.add_command(label="Preferences...", command=self._show_preferences)
        
        # Bind keyboard shortcuts
        self.bind_all("<Control-n>", lambda e: self._on_new())
        self.bind_all("<Control-o>", lambda e: self._on_open())
        self.bind_all("<Control-s>", lambda e: self._on_save())
        self.bind_all("<Control-Shift-S>", lambda e: self._on_save_as())
        self.bind_all("<Control-z>", lambda e: self._on_undo())
        self.bind_all("<Control-y>", lambda e: self._on_redo())
        self.bind_all("<Control-x>", lambda e: self._on_cut())
        self.bind_all("<Control-v>", lambda e: self._on_paste())
    
    def _create_main_interface(self):
        """Create the main interface with editor and preview panes."""
        logging.info("Creating main frame...")
        # Create main content area (editor and preview)
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        logging.info("Main interface created successfully")
        
        # Create paned window for resizable panes
        logging.info("Creating paned window...")
        self.paned_window = ttk.PanedWindow(main_container, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True)
        logging.info("Paned window created")
        
        # Create left pane (Editor)
        logging.info("Creating editor pane...")
        self._create_editor_pane()
        logging.info("Editor pane created")
        
        # Create right pane (Preview)
        logging.info("Creating preview pane...")
        self._create_preview_pane()
        logging.info("Preview pane created")
        
        # Create status bar at the bottom
        self._create_status_bar()
        
        # Set initial pane sizes (50/50 split) - wait for window to be fully rendered
        self.after(200, self._set_pane_sizes)
    
    def _set_pane_sizes(self):
        """Set the pane sizes to 50/50 split based on current window width."""
        try:
            # Get the current window width
            window_width = self.winfo_width()
            if window_width > 50:  # Make sure window is properly sized
                # Set sash position to 50% of window width for equal split
                sash_pos = int(window_width * 0.5)
                self.paned_window.sashpos(0, sash_pos)
        except tk.TclError:
            # If window isn't ready yet, try again in a moment
            self.after(100, self._set_pane_sizes)
    
    def _create_editor_pane(self):
        """Create the left pane with the text editor."""
        logging.info("Creating editor frame...")
        # Editor frame
        editor_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(editor_frame, weight=1)
        logging.info("Editor frame added to paned window")
        
        # Editor label
        editor_label = ttk.Label(editor_frame, text="Editor", font=("Arial", 10, "bold"))
        editor_label.pack(anchor=W, padx=5, pady=(5, 0))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(editor_frame)
        text_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Text widget
        self.text_editor = tk.Text(
            text_frame,
            wrap=tk.WORD,
            undo=True,
            maxundo=50,
            font=("Consolas", 11),
            bg="white",
            fg="black",
            insertbackground="black",
            selectbackground="#316AC5",
            selectforeground="white"
        )
        
        # Scrollbar for text widget
        text_scrollbar = ttk.Scrollbar(text_frame, orient=VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=text_scrollbar.set)
        
        # Pack text widget and scrollbar
        self.text_editor.pack(side=LEFT, fill=BOTH, expand=True)
        text_scrollbar.pack(side=RIGHT, fill=Y)
        logging.info("Text editor and scrollbar packed")
        
        # Configure CriticMarkup highlighting tags for editor
        self._setup_editor_critic_tags()
        
        # Bind text change events
        self.text_editor.bind('<KeyRelease>', self._on_text_change)
        self.text_editor.bind('<Button-1>', self._on_text_change)
        self.text_editor.bind('<ButtonRelease-1>', self._on_text_change)
        logging.info("Text editor events bound")
        
        # Add some helpful placeholder text
        placeholder_text = """# Welcome to Scriptum Simplex

This is a comprehensive **Markdown** editor with support for *CriticMarkup* syntax and advanced document navigation features.

## Introduction

This document serves as a demonstration of the editor's capabilities. You can use the outline view to navigate between sections quickly. The preview pane will show the rendered output with proper formatting.

### Getting Started

To use this editor effectively:
1. Type your markdown in the left pane
2. View the rendered output in the Preview tab
3. Use the Outline tab to navigate through your document
4. Check CriticMarkup changes in the Critic tab

## CriticMarkup Examples

CriticMarkup is a way to track changes in plain text documents. Here are the main syntax elements:

### Additions
Use {++addition++} syntax to mark new content that should be added to the document.

### Deletions  
Use {--deletion--} syntax to mark content that should be removed from the document.

### Substitutions
Use {~~old text~>new text~~} to show replacements where old text is replaced with new text.

### Highlights and Comments
Use {==highlight==} to mark important text, and {>>comment<<} to add editorial comments.

## Sample CriticMarkup Examples

Here are some {++working examples++} of CriticMarkup in action:

- This text has been {--removed--} from the document
- This {~~old word~>new word~~} shows a substitution  
- This is {==very important==} information
- {>>This is an editorial comment<<}

## Advanced Formatting

### Code Blocks

Here's a Python code example:

```python
def hello_world():
    print("Hello, World!")
    return True
```

### Lists and Nested Content

1. First item in ordered list
   - Nested bullet point
   - Another nested item
2. Second item with more content
3. Third item

### Tables and Data

| Feature | Status | Priority |
|---------|--------|----------|
| Preview | ✅ Complete | High |
| Outline | ✅ Complete | High |
| Tables | ✅ Complete | Medium |
| CriticMarkup | 🔄 In Progress | Medium |

## Document Structure

### Section A: Content Management
This section discusses how to manage your content effectively using the various features of the editor.

### Section B: Navigation Features  
The outline view provides quick navigation to any part of your document. Simply click on a heading to jump to that section.

### Section C: Export Options
Future versions will include export capabilities to various formats including HTML, PDF, and Word documents.

## Conclusion

This editor provides a comprehensive solution for writing and editing Markdown documents with CriticMarkup support. The dual-pane interface makes it easy to write and preview your content simultaneously.

### Final Notes
- Use the tabs to switch between different views
- The outline automatically updates as you type
- All changes are tracked and can be reviewed in the Critic tab

### Links and References

Check out the [Markdown Guide](https://www.markdownguide.org) for more information.

You can also visit [GitHub](https://github.com) for code repositories.

This document includes a footnote[^1] for additional information.

[^1]: This is a footnote with additional details about the editor.

Thank you for using Scriptum Simplex!
"""
        self.text_editor.insert(tk.END, placeholder_text)
        logging.info("Placeholder text inserted")
        
        # Apply initial CriticMarkup highlighting
        self._highlight_editor_criticmarkup()
    
    def _create_preview_pane(self):
        """Create the right pane with tabbed interface for preview and analysis."""
        logging.info("Creating preview frame...")
        # Preview frame
        preview_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(preview_frame, weight=1)
        logging.info("Preview frame added to paned window")

        # Create notebook (tabbed interface)
        logging.info("Creating notebook...")
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        logging.info("Notebook created and packed")

        # Tab 1: Preview
        logging.info("Creating preview tab...")
        self._create_preview_tab()
        logging.info("Preview tab created")

        # Tab 2: Outline (TreeView)
        logging.info("Creating outline tab...")
        self._create_outline_tab()
        logging.info("Outline tab created")

        # Tab 3: Critic
        logging.info("Creating critic tab...")
        self._create_critic_tab()
        logging.info("Critic tab created")

        # Tab 4: Supplements
        logging.info("Creating supplements tab...")
        self._create_supplements_tab()
        logging.info("Supplements tab created")
        
        # Tab 5: Metadata
        logging.info("Creating metadata tab...")
        self._create_metadata_tab()
        logging.info("Metadata tab created")
        
        # Trigger initial update of all tabs with placeholder text
        self.after(100, self._initial_tab_update)
    
    def _initial_tab_update(self):
        """Update all tabs with the initial placeholder text."""
        try:
            # Get the current text from editor
            current_text = self.text_editor.get('1.0', tk.END)
            logging.info(f"Initial tab update with {len(current_text)} characters")
            
            # Update all tabs
            self._update_outline_tree(current_text)
            self._update_critic(current_text)
            self._update_supplements(current_text)
            
        except Exception as e:
            logging.error(f"Error in initial tab update: {e}")
            import traceback
            traceback.print_exc()
    
    def _debug_canvas_after_pack(self):
        """Debug canvas state after packing is complete."""
        logging.info("=== CANVAS DEBUG AFTER PACK ===")
        try:
            # Check canvas size
            canvas_width = self.markdown_preview.winfo_width()
            canvas_height = self.markdown_preview.winfo_height()
            logging.info(f"Canvas size after pack: {canvas_width}x{canvas_height}")
            
            # Check if canvas is mapped (visible)
            is_mapped = self.markdown_preview.winfo_ismapped()
            logging.info(f"Canvas is mapped (visible): {is_mapped}")
            
            # Check parent frame size
            parent_width = self.markdown_preview.master.winfo_width()
            parent_height = self.markdown_preview.master.winfo_height()
            logging.info(f"Parent frame size: {parent_width}x{parent_height}")
            
            # Check canvas items again
            all_items = self.markdown_preview.find_all()
            logging.info(f"Canvas items after pack: {all_items}")
            
            # Try to force a redraw
            self.markdown_preview.update_idletasks()
            
            # If canvas is too small, try to fix it
            if canvas_width <= 1 or canvas_height <= 1:
                logging.error("Canvas has invalid size! Trying to fix...")
                self.markdown_preview.configure(width=400, height=300)
                
        except Exception as e:
            logging.error(f"Error in canvas debug: {e}")
            import traceback
            traceback.print_exc()

    def _create_preview_tab(self):
        """Create the Preview tab with MarkdownCanvas."""
        preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(preview_tab, text="Preview")

        # Create frame for canvas and scrollbar
        preview_text_frame = ttk.Frame(preview_tab)
        preview_text_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)

        # Create the EnhancedMarkdownCanvas with theme support
        logging.info("Creating EnhancedMarkdownCanvas in preview tab...")
        self.markdown_preview = EnhancedMarkdownCanvas(
            preview_text_frame,
            config=self.app_config,  # Pass configuration
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0
        )
        
        # Load default theme (try multiple paths)
        from pathlib import Path
        default_theme_paths = [
            Path("Data/Themes/Typora-GitHub-Themes-main/Typora-GitHub-Themes-main"),
            Path("c:/RH/Working Code/Markdown Critic/Data/Themes/Typora-GitHub-Themes-main/Typora-GitHub-Themes-main"),
            Path("c:/RH/Working Code/Markdown Critic/Data/Themes/typora-cobalt-theme-master-v1.4"),
        ]
        
        theme_loaded = False
        for theme_path in default_theme_paths:
            if theme_path.exists():
                try:
                    styles = self.theme_loader.load_theme_from_folder(str(theme_path))
                    self.markdown_preview.set_theme(styles)
                    logging.info(f"Default theme loaded from: {theme_path.name}")
                    theme_loaded = True
                    break
                except Exception as e:
                    logging.warning(f"Could not load theme from {theme_path}: {e}")
        
        if not theme_loaded:
            logging.warning("No default theme loaded - preview may not render correctly")
        
        # Set up image path resolver (will be connected to controller's model)
        if hasattr(self.markdown_preview, 'image_path_resolver'):
            self.markdown_preview.image_path_resolver = self._resolve_image_path
        
        # Force canvas initialization to prevent blank display issues
        self.markdown_preview.update()  # Critical: ensures canvas is ready for rendering
        logging.info("EnhancedMarkdownCanvas initialized")

        # Scrollbar for preview
        preview_scrollbar = ttk.Scrollbar(
            preview_text_frame, orient=VERTICAL, command=self.markdown_preview.yview
        )
        self.markdown_preview.configure(yscrollcommand=preview_scrollbar.set)

        # Pack canvas and scrollbar
        self.markdown_preview.pack(side=LEFT, fill=BOTH, expand=True)
        preview_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Schedule a delayed check of canvas size after packing
        self.after(500, self._debug_canvas_after_pack)

    def _create_outline_tab(self):
        """Create the Outline tab with TreeView showing document structure."""
        outline_tab = ttk.Frame(self.notebook)
        self.notebook.add(outline_tab, text="Outline")

        # Create frame for TreeView and scrollbar
        outline_frame = ttk.Frame(outline_tab)
        outline_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Create TreeView for outline
        self.outline_tree = ttk.Treeview(outline_frame, show='tree headings')
        self.outline_tree.heading('#0', text='Document Outline', anchor='w')
        
        # Configure TreeView columns - Type column first, then content
        self.outline_tree['columns'] = ('line',)
        self.outline_tree.column('#0', width=400, minwidth=300)
        self.outline_tree.column('line', width=60, minwidth=40)
        self.outline_tree.heading('line', text='Line')
        
        # Configure TreeView tags for styling
        self.outline_tree.tag_configure('heading', font=('Arial', 10, 'bold'))
        self.outline_tree.tag_configure('content', font=('Arial', 10, 'normal'))
        self.outline_tree.tag_configure('table', font=('Arial', 10, 'italic'))
        self.outline_tree.tag_configure('code', font=('Courier', 10, 'normal'))
        self.outline_tree.tag_configure('image', font=('Arial', 10, 'italic'))

        # Scrollbar for TreeView
        outline_scrollbar = ttk.Scrollbar(outline_frame, orient=VERTICAL, command=self.outline_tree.yview)
        self.outline_tree.configure(yscrollcommand=outline_scrollbar.set)

        # Pack TreeView and scrollbar
        self.outline_tree.pack(side=LEFT, fill=BOTH, expand=True)
        outline_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Bind double-click event for navigation
        self.outline_tree.bind('<Double-1>', self._on_outline_item_double_click)
        self.outline_tree.bind('<Button-1>', self._on_outline_item_click)
    
    def _on_outline_item_click(self, event):
        """Handle single click on outline item."""
        item = self.outline_tree.selection()[0] if self.outline_tree.selection() else None
        if item:
            self._navigate_to_outline_item(item)
    
    def _on_outline_item_double_click(self, event):
        """Handle double click on outline item."""
        item = self.outline_tree.selection()[0] if self.outline_tree.selection() else None
        if item:
            self._navigate_to_outline_item(item)
    
    def _navigate_to_outline_item(self, item):
        """Navigate both editor and preview to the selected outline item."""
        try:
            # Get line number from TreeView item (now first column)
            values = self.outline_tree.item(item, 'values')
            if values and len(values) > 0:
                line_num = values[0]  # Line column is now first
                if line_num and str(line_num).isdigit():
                    self._navigate_to_line(int(line_num))
                
        except (IndexError, ValueError) as e:
            logging.error(f"Error navigating to outline item: {e}")
    
    def _navigate_to_line(self, line_num: int):
        """Navigate both editor and preview to a specific line number."""
        try:
            logging.info(f"Navigating to line {line_num}")
            
            # Scroll editor to line
            self.text_editor.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_editor.see(f"{line_num}.0")
            
            # Highlight the line briefly
            self.text_editor.tag_remove("highlight", "1.0", tk.END)
            self.text_editor.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
            self.text_editor.tag_config("highlight", background="yellow")
            
            # Remove highlight after 3 seconds
            self.after(3000, lambda: self.text_editor.tag_remove("highlight", "1.0", tk.END))
            
            # Scroll preview to corresponding content
            self._scroll_preview_to_line(line_num)
            
            # Focus the editor
            self.text_editor.focus_set()
            
        except Exception as e:
            logging.error(f"Error navigating to line: {e}")
    
    def _scroll_preview_to_line(self, line_num):
        """Scroll the preview pane to show content corresponding to editor line."""
        try:
            # This is a simplified approach - in a full implementation,
            # we'd need to map editor lines to preview canvas positions
            # For now, we'll scroll proportionally
            total_lines = int(self.text_editor.index(tk.END).split('.')[0])
            if total_lines > 1:
                scroll_fraction = (line_num - 1) / (total_lines - 1)
                self.markdown_preview.yview_moveto(scroll_fraction)
                logging.info(f"Scrolled preview to fraction {scroll_fraction}")
        except Exception as e:
            logging.error(f"Error scrolling preview: {e}")
    
    def _update_outline_tree(self, markdown_text: str):
        """Update the TreeView outline with document structure."""
        try:
            # Check if outline_tree exists
            if not hasattr(self, 'outline_tree'):
                logging.error("outline_tree not found!")
                return
                
            # Clear existing items
            for item in self.outline_tree.get_children():
                self.outline_tree.delete(item)
            
            # Parse the markdown text line by line to build outline
            lines = markdown_text.split('\n')
            in_code_block = False
            
            for line_num, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()
                
                # Track code blocks
                if line.startswith('```'):
                    if not in_code_block:
                        # Start of code block
                        lang = line[3:].strip() or 'code'
                        self.outline_tree.insert('', 'end', 
                                                text=f"[Code Block: {lang}]",
                                                values=(str(line_num),),
                                                tags=('code',))
                        in_code_block = True
                    else:
                        in_code_block = False
                    continue
                
                # Skip content inside code blocks
                if in_code_block:
                    continue
                
                # Check for headings
                if line.startswith('#'):
                    level = 0
                    while level < len(line) and line[level] == '#':
                        level += 1
                    
                    if level <= 6 and level < len(line) and line[level] == ' ':
                        heading_text = line[level + 1:].strip()
                        # Show clean heading text without indentation (headings are left-aligned)
                        display_text = heading_text
                        
                        self.outline_tree.insert('', 'end', 
                                                text=display_text,
                                                values=(str(line_num),),
                                                tags=('heading',))
                
                # Check for tables
                elif line.startswith('|') and '|' in line[1:]:
                    # Only show the first table row as a summary
                    if not any(self.outline_tree.item(child, 'text').startswith('[Table]') 
                              for child in self.outline_tree.get_children()[-3:]):  # Check last few items
                        self.outline_tree.insert('', 'end',
                                                text="[Table]",
                                                values=(str(line_num),),
                                                tags=('table',))
                
                # Check for images
                elif line.startswith('![') and '](' in line:
                    # Extract alt text
                    alt_start = line.find('![') + 2
                    alt_end = line.find('](')
                    alt_text = line[alt_start:alt_end] if alt_end > alt_start else 'Image'
                    self.outline_tree.insert('', 'end',
                                            text=f"[Image: {alt_text}]",
                                            values=(str(line_num),),
                                            tags=('image',))
                
                # Check for substantial content paragraphs (first 50 chars)
                elif (line and 
                      not line.startswith(('-', '*', '>', '1.', '2.', '3.', '4.', '5.')) and  # Skip lists
                      not line.startswith('```') and  # Skip code
                      len(line.strip()) > 15):  # Only substantial content
                    
                    # Show first 50 characters for content with indentation
                    display_text = "  " + line[:50]
                    if len(line) > 50:
                        display_text += "..."
                    
                    self.outline_tree.insert('', 'end',
                                            text=display_text,
                                            values=(str(line_num),),
                                            tags=('content',))
            
            logging.info(f"Outline tree updated with {len(self.outline_tree.get_children())} items")
            
        except Exception as e:
            logging.error(f"Error updating outline tree: {e}")
            import traceback
            traceback.print_exc()

    def _create_critic_tab(self):
        """Create the Critic Table tab for managing CriticMarkup changes."""
        from .critic_table import CriticTable
        
        critic_tab = ttk.Frame(self.notebook)
        self.notebook.add(critic_tab, text="Critic Table")

        # Create button toolbar
        toolbar = ttk.Frame(critic_tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Accept/Reject buttons
        self.accept_btn = ttk.Button(
            toolbar,
            text="Accept Selected",
            command=self._accept_selected_change
        )
        self.accept_btn.pack(side=tk.LEFT, padx=2)

        self.reject_btn = ttk.Button(
            toolbar,
            text="Reject Selected",
            command=self._reject_selected_change
        )
        self.reject_btn.pack(side=tk.LEFT, padx=2)

        # Accept/Reject All buttons
        self.accept_all_btn = ttk.Button(
            toolbar,
            text="Accept All",
            command=self._accept_all_changes
        )
        self.accept_all_btn.pack(side=tk.LEFT, padx=2)

        self.reject_all_btn = ttk.Button(
            toolbar,
            text="Reject All",
            command=self._reject_all_changes
        )
        self.reject_all_btn.pack(side=tk.LEFT, padx=2)

        # Save button
        self.save_changes_btn = ttk.Button(
            toolbar,
            text="Save Changes",
            command=self._save_critic_changes,
            state=tk.DISABLED
        )
        self.save_changes_btn.pack(side=tk.LEFT, padx=10)

        # Status label
        self.critic_status_label = ttk.Label(toolbar, text="")
        self.critic_status_label.pack(side=tk.RIGHT, padx=5)

        # Create Critic Table
        self.critic_table = CriticTable(critic_tab, on_row_click=self._on_critic_row_click)
        self.critic_table.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Track if there are unsaved changes
        self.has_unsaved_critic_changes = False

    def _on_critic_row_click(self, change):
        """Handle clicking a row in the Critic Table - jump to that location in editor."""
        from .critic_change import CriticChange
        try:
            # Calculate the position in the text editor
            text_content = self.text_editor.get('1.0', tk.END)
            
            # Find the line in the editor
            lines = text_content.split('\n')
            if 1 <= change.line_number <= len(lines):
                # Jump to the line
                line_index = f"{change.line_number}.0"
                self.text_editor.see(line_index)
                self.text_editor.mark_set(tk.INSERT, line_index)
                
                # Highlight the line briefly
                line_end = f"{change.line_number}.end"
                self.text_editor.tag_remove('highlight_line', '1.0', tk.END)
                self.text_editor.tag_add('highlight_line', line_index, line_end)
                self.text_editor.tag_configure('highlight_line', background='#ffffcc')
                
                # Remove highlight after 2 seconds
                self.after(2000, lambda: self.text_editor.tag_remove('highlight_line', '1.0', tk.END))
                
                logging.info(f"Jumped to line {change.line_number} for {change.change_type.value}")
        except Exception as e:
            logging.error(f"Error jumping to critic change: {e}")

    def _accept_selected_change(self):
        """Accept the selected change in the Critic Table."""
        from .critic_change import ChangeStatus
        idx = self.critic_table.get_selected_index()
        if idx is not None:
            self.critic_table.update_change_status(idx, ChangeStatus.ACCEPTED)
            self.has_unsaved_critic_changes = True
            self.save_changes_btn.config(state=tk.NORMAL)
            self._update_critic_status()
            self._update_preview_with_critic_changes()

    def _reject_selected_change(self):
        """Reject the selected change in the Critic Table."""
        from .critic_change import ChangeStatus
        idx = self.critic_table.get_selected_index()
        if idx is not None:
            self.critic_table.update_change_status(idx, ChangeStatus.REJECTED)
            self.has_unsaved_critic_changes = True
            self.save_changes_btn.config(state=tk.NORMAL)
            self._update_critic_status()
            self._update_preview_with_critic_changes()

    def _accept_all_changes(self):
        """Accept all pending changes."""
        from .critic_change import ChangeStatus
        for idx, change in enumerate(self.critic_table.changes):
            if change.status == ChangeStatus.PENDING:
                self.critic_table.update_change_status(idx, ChangeStatus.ACCEPTED)
        self.has_unsaved_critic_changes = True
        self.save_changes_btn.config(state=tk.NORMAL)
        self._update_critic_status()
        self._update_preview_with_critic_changes()

    def _reject_all_changes(self):
        """Reject all pending changes."""
        from .critic_change import ChangeStatus
        for idx, change in enumerate(self.critic_table.changes):
            if change.status == ChangeStatus.PENDING:
                self.critic_table.update_change_status(idx, ChangeStatus.REJECTED)
        self.has_unsaved_critic_changes = True
        self.save_changes_btn.config(state=tk.NORMAL)
        self._update_critic_status()
        self._update_preview_with_critic_changes()

    def _update_critic_status(self):
        """Update the status label showing pending/accepted/rejected counts."""
        from .critic_change import ChangeStatus
        pending = sum(1 for c in self.critic_table.changes if c.status == ChangeStatus.PENDING)
        accepted = sum(1 for c in self.critic_table.changes if c.status == ChangeStatus.ACCEPTED)
        rejected = sum(1 for c in self.critic_table.changes if c.status == ChangeStatus.REJECTED)
        self.critic_status_label.config(
            text=f"Pending: {pending} | Accepted: {accepted} | Rejected: {rejected}"
        )

    def _update_preview_with_critic_changes(self):
        """Update the preview pane to show what the document will look like with accepted/rejected changes applied."""
        try:
            # Get current text from editor
            text = self.text_editor.get('1.0', tk.END)
            
            # Apply accepted/rejected changes to create preview text
            preview_text = self._apply_critic_changes_to_text(text)
            
            # Update the preview with the modified text
            self.markdown_preview.render_markdown(preview_text)
            
            logging.info("Preview updated with critic changes")
        except Exception as e:
            logging.error(f"Error updating preview with critic changes: {e}")
            import traceback
            traceback.print_exc()

    def _apply_critic_changes_to_text(self, text: str) -> str:
        """
        Apply accepted/rejected changes to text for preview.
        
        Args:
            text: Original text with CriticMarkup
            
        Returns:
            Text with accepted/rejected changes applied
        """
        from .critic_change import ChangeStatus
        
        # Sort changes by position (reverse order to maintain positions)
        changes = sorted(self.critic_table.changes, key=lambda c: c.start_pos, reverse=True)
        
        # Apply each change
        for change in changes:
            if change.status == ChangeStatus.ACCEPTED:
                replacement = change.get_accepted_text()
            elif change.status == ChangeStatus.REJECTED:
                replacement = change.get_rejected_text()
            else:
                continue  # Skip pending changes - leave markup as-is
            
            # Replace the markup with the appropriate text
            text = text[:change.start_pos] + replacement + text[change.end_pos:]
        
        return text

    def _save_critic_changes(self):
        """Apply accepted/rejected changes to the document."""
        try:
            # Get current text
            text = self.text_editor.get('1.0', tk.END)
            
            # Sort changes by position (reverse order to maintain positions)
            changes = sorted(self.critic_table.changes, key=lambda c: c.start_pos, reverse=True)
            
            # Apply each change
            from .critic_change import ChangeStatus
            for change in changes:
                if change.status == ChangeStatus.ACCEPTED:
                    replacement = change.get_accepted_text()
                elif change.status == ChangeStatus.REJECTED:
                    replacement = change.get_rejected_text()
                else:
                    continue  # Skip pending changes
                
                # Replace the markup with the appropriate text
                text = text[:change.start_pos] + replacement + text[change.end_pos:]
            
            # Update the editor
            self.text_editor.delete('1.0', tk.END)
            self.text_editor.insert('1.0', text)
            
            # Remove processed changes from table
            self.critic_table.remove_non_pending_changes()
            
            # Reset state
            self.has_unsaved_critic_changes = False
            self.save_changes_btn.config(state=tk.DISABLED)
            self._update_critic_status()
            
            # Refresh the preview
            self.update_preview()
            
            logging.info("Critic changes saved successfully")
        except Exception as e:
            logging.error(f"Error saving critic changes: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_editor_critic_tags(self):
        """Setup color tags for CriticMarkup in the text editor."""
        # Addition - Green background (same as Critic tab)
        self.text_editor.tag_configure('editor_addition', 
                                     background='#d4edda', 
                                     foreground='#155724')
        
        # Deletion - Red background  
        self.text_editor.tag_configure('editor_deletion',
                                     background='#f8d7da',
                                     foreground='#721c24')
        
        # Substitution - Blue background
        self.text_editor.tag_configure('editor_substitution',
                                     background='#cce7ff',
                                     foreground='#004085')
        
        # Highlight - Yellow background
        self.text_editor.tag_configure('editor_highlight',
                                     background='#fff3cd',
                                     foreground='#856404')
        
        # Comment - Yellow background, italic
        self.text_editor.tag_configure('editor_comment',
                                     background='#fff3cd',
                                     foreground='#856404',
                                     font=('Consolas', 11, 'italic'))
    
    def _highlight_editor_criticmarkup(self):
        """Apply CriticMarkup highlighting to the text editor."""
        try:
            import re
            
            # Get current text
            text = self.text_editor.get('1.0', tk.END)
            
            # Clear existing CriticMarkup tags
            for tag in ['editor_addition', 'editor_deletion', 'editor_substitution', 'editor_highlight', 'editor_comment']:
                self.text_editor.tag_delete(tag)
            
            # Define patterns and their corresponding tags
            patterns = [
                (r'\{\+\+([^}]+)\+\+\}', 'editor_addition'),      # {++addition++}
                (r'\{--([^}]+)--\}', 'editor_deletion'),          # {--deletion--}
                (r'\{~~([^}]+)~>([^}]+)~~\}', 'editor_substitution'),  # {~~old~>new~~}
                (r'\{==([^}]+)==\}', 'editor_highlight'),         # {==highlight==}
                (r'\{>>([^}]+)<<\}', 'editor_comment'),           # {>>comment<<}
            ]
            
            # Apply highlighting for each pattern
            for pattern, tag in patterns:
                for match in re.finditer(pattern, text):
                    start_line = text[:match.start()].count('\n') + 1
                    start_col = match.start() - text.rfind('\n', 0, match.start()) - 1
                    end_line = text[:match.end()].count('\n') + 1
                    end_col = match.end() - text.rfind('\n', 0, match.end()) - 1
                    
                    start_index = f"{start_line}.{start_col}"
                    end_index = f"{end_line}.{end_col}"
                    
                    self.text_editor.tag_add(tag, start_index, end_index)
                    
        except Exception as e:
            logging.error(f"Error highlighting editor CriticMarkup: {e}")

    def _create_supplements_tab(self):
        """Create the Supplements tab for footnotes and references."""
        supplements_tab = ttk.Frame(self.notebook)
        self.notebook.add(supplements_tab, text="Supplements")

        # Create text widget for supplements
        supplements_frame = ttk.Frame(supplements_tab)
        supplements_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.supplements_text = tk.Text(
            supplements_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="white",
            fg="black",
            state=tk.DISABLED
        )

        supplements_scrollbar = ttk.Scrollbar(
            supplements_frame, orient=VERTICAL, command=self.supplements_text.yview
        )
        self.supplements_text.configure(yscrollcommand=supplements_scrollbar.set)

        self.supplements_text.pack(side=LEFT, fill=BOTH, expand=True)
        supplements_scrollbar.pack(side=RIGHT, fill=Y)
    
    def _create_metadata_tab(self):
        """Create the Metadata tab for viewing and editing document metadata."""
        metadata_tab = ttk.Frame(self.notebook)
        self.notebook.add(metadata_tab, text="Metadata")
        
        # Create scrollable frame
        canvas = tk.Canvas(metadata_tab)
        scrollbar = ttk.Scrollbar(metadata_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Document Info Section
        ttk.Label(scrollable_frame, text="Document Information", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(10, 5)
        )
        
        # Title
        ttk.Label(scrollable_frame, text="Title:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_title = ttk.Entry(scrollable_frame, width=60)
        self.meta_title.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Author
        ttk.Label(scrollable_frame, text="Author First Name:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_author_first = ttk.Entry(scrollable_frame, width=60)
        self.meta_author_first.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Author Last Name:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_author_last = ttk.Entry(scrollable_frame, width=60)
        self.meta_author_last.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Organization
        ttk.Label(scrollable_frame, text="Organization:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_organization = ttk.Entry(scrollable_frame, width=60)
        self.meta_organization.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # URL
        ttk.Label(scrollable_frame, text="URL:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_url = ttk.Entry(scrollable_frame, width=60)
        self.meta_url.grid(row=5, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # License
        ttk.Label(scrollable_frame, text="License:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_license = ttk.Entry(scrollable_frame, width=60)
        self.meta_license.grid(row=6, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Dates
        ttk.Label(scrollable_frame, text="Original Pub. Date:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_orig_date = ttk.Entry(scrollable_frame, width=60)
        self.meta_orig_date.grid(row=7, column=1, sticky=tk.EW, padx=10, pady=5)
        
        ttk.Label(scrollable_frame, text="Last Pub. Date:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_last_date = ttk.Entry(scrollable_frame, width=60)
        self.meta_last_date.grid(row=8, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Summary
        ttk.Label(scrollable_frame, text="Summary:").grid(row=9, column=0, sticky=tk.NW, padx=10, pady=5)
        self.meta_summary = tk.Text(scrollable_frame, width=60, height=4, wrap=tk.WORD)
        self.meta_summary.grid(row=9, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Image Settings Section
        ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).grid(
            row=10, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=10
        )
        
        ttk.Label(scrollable_frame, text="Image Settings", font=("Arial", 12, "bold")).grid(
            row=11, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(10, 5)
        )
        
        ttk.Label(scrollable_frame, text="Image Root Path:").grid(row=12, column=0, sticky=tk.W, padx=10, pady=5)
        self.meta_image_path = ttk.Entry(scrollable_frame, width=60)
        self.meta_image_path.grid(row=12, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Save Button
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save Metadata", command=self._save_metadata_from_tab).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reload", command=self._load_metadata_to_tab).pack(side=tk.LEFT, padx=5)
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store canvas for later updates
        self.metadata_canvas = canvas
    
    def _load_metadata_to_tab(self):
        """Load metadata from model into the tab widgets."""
        if not self.controller or not hasattr(self.controller, 'model'):
            return
        
        metadata = self.controller.model.metadata
        
        # Load values
        self.meta_title.delete(0, tk.END)
        self.meta_title.insert(0, metadata.get_document_title())
        
        self.meta_author_first.delete(0, tk.END)
        self.meta_author_first.insert(0, metadata.get_author_first_name())
        
        self.meta_author_last.delete(0, tk.END)
        self.meta_author_last.insert(0, metadata.get_author_last_name())
        
        self.meta_organization.delete(0, tk.END)
        self.meta_organization.insert(0, metadata.get_organization())
        
        self.meta_url.delete(0, tk.END)
        self.meta_url.insert(0, metadata.get_url())
        
        self.meta_license.delete(0, tk.END)
        self.meta_license.insert(0, metadata.get_license())
        
        self.meta_orig_date.delete(0, tk.END)
        self.meta_orig_date.insert(0, metadata.get_original_publication_date())
        
        self.meta_last_date.delete(0, tk.END)
        self.meta_last_date.insert(0, metadata.get_last_publication_date())
        
        self.meta_summary.delete("1.0", tk.END)
        self.meta_summary.insert("1.0", metadata.get_summary())
        
        self.meta_image_path.delete(0, tk.END)
        self.meta_image_path.insert(0, metadata.metadata['images']['root_path'])
    
    def _save_metadata_from_tab(self):
        """Save metadata from tab widgets to model and file."""
        if not self.controller or not hasattr(self.controller, 'model'):
            self.show_error("No File", "Please save the document first.")
            return
        
        if not self.controller.model.file_path:
            self.show_error("No File", "Please save the document first before editing metadata.")
            return
        
        metadata = self.controller.model.metadata
        
        # Save values
        metadata.set_document_title(self.meta_title.get())
        metadata.set_author_first_name(self.meta_author_first.get())
        metadata.set_author_last_name(self.meta_author_last.get())
        metadata.set_organization(self.meta_organization.get())
        metadata.set_url(self.meta_url.get())
        metadata.set_license(self.meta_license.get())
        metadata.set_original_publication_date(self.meta_orig_date.get())
        metadata.set_last_publication_date(self.meta_last_date.get())
        metadata.set_summary(self.meta_summary.get("1.0", tk.END).strip())
        metadata.set_image_root_path(self.meta_image_path.get())
        
        # Save to file
        if metadata.save():
            self.show_info("Metadata Saved", "Document metadata has been saved successfully.")
        else:
            self.show_error("Save Error", "Could not save metadata file.")
    
    def _on_text_change(self, event=None):
        """Handle text change events in the editor."""
        if self.controller:
            # Apply CriticMarkup highlighting to editor
            self._highlight_editor_criticmarkup()
            # Small delay to avoid too frequent updates
            self.after_idle(self.controller.on_text_change)
    
    def _on_new(self):
        """Handle New file menu action."""
        if self.controller:
            self.controller.new_file()
    
    def _on_open(self):
        """Handle Open file menu action."""
        file_path = filedialog.askopenfilename(
            title="Open Markdown File",
            filetypes=[
                ("Markdown files", "*.md *.markdown *.mdown *.mkd"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path and self.controller:
            self.controller.open_file(file_path)
    
    def _on_save(self):
        """Handle Save file menu action."""
        if self.controller:
            self.controller.save_file()
    
    def _on_save_as(self):
        """Handle Save As menu action."""
        file_path = filedialog.asksaveasfilename(
            title="Save Markdown File",
            defaultextension=".md",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path and self.controller:
            self.controller.save_file_as(file_path)
    
    def _on_undo(self):
        """Handle Undo action."""
        try:
            self.text_editor.edit_undo()
        except tk.TclError:
            pass  # Nothing to undo
    
    def _on_redo(self):
        """Handle Redo action."""
        try:
            self.text_editor.edit_redo()
        except tk.TclError:
            pass  # Nothing to redo
    
    def _on_cut(self):
        """Handle Cut action."""
        try:
            self.text_editor.event_generate("<<Cut>>")
        except tk.TclError:
            pass
    
    def _on_copy(self):
        """Handle Copy action."""
        try:
            self.text_editor.event_generate("<<Copy>>")
        except tk.TclError:
            pass
    
    def _on_paste(self):
        """Handle Paste action."""
        try:
            self.text_editor.event_generate("<<Paste>>")
        except tk.TclError:
            pass
    
    def _on_metadata(self):
        """Handle Metadata menu option."""
        if self.controller:
            self.controller.show_metadata_dialog()
    
    def _on_theme_change(self, theme_name: str):
        """Handle theme change from menu."""
        if self.controller:
            self.controller.change_theme(theme_name)
    
    def _load_theme_from_path(self, theme_path: str):
        """Load theme from a configured path."""
        if self.controller:
            self.controller.load_typora_theme(theme_path)
    
    def _on_load_typora_theme(self):
        """Handle Load Typora Theme menu option."""
        from tkinter import filedialog
        
        folder_path = filedialog.askdirectory(
            title="Select Typora Theme Folder"
        )
        
        if folder_path and self.controller:
            self.controller.load_typora_theme(folder_path)
            # Add to config
            self.app_config.add_theme_folder(folder_path)
    
    def _show_preferences(self):
        """Show preferences dialog."""
        from .preferences_dialog import PreferencesDialog
        dialog = PreferencesDialog(self, self.app_config)
        dialog.grab_set()  # Make modal
    
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        self.status_bar = ttk.Frame(self, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status labels
        self.status_file = ttk.Label(self.status_bar, text="Untitled", anchor=tk.W)
        self.status_file.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        self.status_stats = ttk.Label(self.status_bar, text="Lines: 0 | Words: 0 | Chars: 0", anchor=tk.W)
        self.status_stats.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        self.status_cursor = ttk.Label(self.status_bar, text="Ln: 1, Col: 1", anchor=tk.W)
        self.status_cursor.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        self.status_theme = ttk.Label(self.status_bar, text="Theme: Default", anchor=tk.E)
        self.status_theme.pack(side=tk.RIGHT, padx=5)
        
        # Bind cursor movement to update status
        if hasattr(self, 'text_editor'):
            self.text_editor.bind('<KeyRelease>', self._update_status_bar_event)
            self.text_editor.bind('<ButtonRelease>', self._update_status_bar_event)
    
    def _update_status_bar_event(self, event=None):
        """Update status bar on text change."""
        self.after_idle(self.update_status_bar)
    
    def update_status_bar(self, filename="Untitled", is_dirty=False):
        """Update the status bar with current document info."""
        if not hasattr(self, 'status_bar'):
            return
        
        # Update filename
        status_text = f"{'*' if is_dirty else ''}{filename}"
        self.status_file.config(text=status_text)
        
        # Update statistics
        text = self.get_editor_text()
        lines = text.count('\n') + 1 if text else 0
        words = len(text.split()) if text else 0
        chars = len(text)
        self.status_stats.config(text=f"Lines: {lines} | Words: {words} | Chars: {chars}")
        
        # Update cursor position
        if hasattr(self, 'text_editor'):
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.status_cursor.config(text=f"Ln: {line}, Col: {int(col)+1}")
        
        # Update theme
        if hasattr(self, 'current_theme_var'):
            theme_name = self.current_theme_var.get().capitalize()
            self.status_theme.config(text=f"Theme: {theme_name}")
    
    def _on_closing(self):
        """Handle window closing event."""
        if self.controller:
            self.controller.on_closing()
        else:
            self.destroy()
    
    def get_editor_text(self) -> str:
        """
        Get the current text from the editor.
        
        Returns:
            Current text content
        """
        return self.text_editor.get("1.0", tk.END + "-1c")
    
    def set_editor_text(self, text: str):
        """
        Set the text in the editor.
        
        Args:
            text: Text to set in the editor
        """
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", text)

    def update_preview(self, markdown_text: str):
        """
        Update all tabs with new Markdown content.

        Args:
            markdown_text: Markdown text to display
        """
        try:
            logging.info(f"update_preview called with {len(markdown_text)} characters")
            
            # Check if markdown_preview exists
            if not hasattr(self, 'markdown_preview'):
                logging.error("markdown_preview not found!")
                return
            
            # Update Preview tab using enhanced renderer
            logging.info("Calling markdown_preview.render_markdown...")
            self.markdown_preview.render_markdown(markdown_text)
            logging.info("markdown_preview.render_markdown completed")

            # Update Outline tab (TreeView)
            logging.info("Updating outline TreeView...")
            self._update_outline_tree(markdown_text)
            logging.info("Outline TreeView updated")

            # Update Critic tab
            logging.info("Updating critic...")
            self._update_critic(markdown_text)
            logging.info("Critic updated")
            
            # Update Metadata tab
            logging.info("Loading metadata...")
            self._load_metadata_to_tab()
            logging.info("Metadata loaded")

            # Update Supplements tab
            logging.info("Updating supplements...")
            self._update_supplements(markdown_text)
            logging.info("Supplements updated")
            
            logging.info("update_preview completed successfully")
        except Exception as e:
            # Log error but don't crash
            logging.error(f"Error updating preview: {e}")
            import traceback
            traceback.print_exc()

    def _update_outline(self, markdown_text: str):
        """Extract and display document outline (headings)."""
        self.outline_text.config(state=tk.NORMAL)
        self.outline_text.delete("1.0", tk.END)

        # Parse AST to extract headings
        ast = self.parser.parse(markdown_text)
        outline_lines = []

        for child in ast.children:
            if hasattr(child, '__class__') and child.__class__.__name__ == 'Heading':
                level = child.level
                # Extract text from heading
                text = self._extract_text_from_element(child)
                indent = "  " * (level - 1)
                outline_lines.append(f"{indent}{'#' * level} {text}\n")

        if outline_lines:
            self.outline_text.insert("1.0", "".join(outline_lines))
        else:
            self.outline_text.insert("1.0", "No headings found in document.")

        self.outline_text.config(state=tk.DISABLED)

    def _update_critic(self, markdown_text: str):
        """Parse and display CriticMarkup changes in the Critic Table."""
        try:
            from .critic_parser import CriticParser
            
            # Check if critic_table exists
            if not hasattr(self, 'critic_table'):
                logging.error("critic_table not found!")
                return
            
            # Parse the text for CriticMarkup changes
            parser = CriticParser()
            changes = parser.parse(markdown_text)
            
            # Load changes into the table
            self.critic_table.load_changes(changes)
            
            # Update status label
            self._update_critic_status()
            
            logging.info(f"Loaded {len(changes)} CriticMarkup changes into table")
            
        except Exception as e:
            logging.error(f"Error updating critic table: {e}")
            import traceback
            traceback.print_exc()

    def _update_supplements(self, markdown_text: str):
        """Extract and display links, footnotes, and references."""
        try:
            import re
            
            # Check if supplements_text exists
            if not hasattr(self, 'supplements_text'):
                logging.error("supplements_text not found!")
                return
            
            # Enable text editing temporarily
            self.supplements_text.config(state=tk.NORMAL)
            
            # Clear existing content
            self.supplements_text.delete("1.0", tk.END)
            
            # Clear line number tags
            if not hasattr(self, 'supplement_line_tags'):
                self.supplement_line_tags = {}
            self.supplement_line_tags.clear()
            
            supplements_content = []
            lines = markdown_text.split('\n')
            
            # Find links [text](url) with line numbers
            if not hasattr(self, 'supplements_text'):
                return
                
            self.supplements_text.insert("1.0", "")
            current_line = 1
            
            # Find links with line numbers
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            link_items = []
            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(link_pattern, line):
                    text, url = match.groups()
                    link_items.append((line_num, text, url))
            
            if link_items:
                self.supplements_text.insert(tk.END, "=== LINKS ===\n")
                for i, (line_num, text, url) in enumerate(link_items, 1):
                    start_pos = self.supplements_text.index(tk.END)
                    self.supplements_text.insert(tk.END, f"{i}. {text}\n   → {url}\n\n")
                    end_pos = self.supplements_text.index(tk.END)
                    
                    # Create clickable tag
                    tag_name = f"link_{i}"
                    self.supplements_text.tag_add(tag_name, start_pos, end_pos)
                    self.supplements_text.tag_config(tag_name, foreground="blue", underline=False)
                    self.supplements_text.tag_bind(tag_name, "<Button-1>", 
                                                  lambda e, ln=line_num: self._navigate_to_line(ln))
                    self.supplements_text.tag_bind(tag_name, "<Enter>", 
                                                  lambda e, tn=tag_name: self.supplements_text.tag_config(tn, underline=True))
                    self.supplements_text.tag_bind(tag_name, "<Leave>", 
                                                  lambda e, tn=tag_name: self.supplements_text.tag_config(tn, underline=False))
            
            # Find images ![alt](src) with line numbers
            image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            image_items = []
            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(image_pattern, line):
                    alt, src = match.groups()
                    image_items.append((line_num, alt if alt else "No alt text", src))
            
            if image_items:
                self.supplements_text.insert(tk.END, "=== IMAGES ===\n")
                for i, (line_num, alt, src) in enumerate(image_items, 1):
                    start_pos = self.supplements_text.index(tk.END)
                    self.supplements_text.insert(tk.END, f"{i}. {alt}\n   → {src}\n\n")
                    end_pos = self.supplements_text.index(tk.END)
                    
                    # Create clickable tag
                    tag_name = f"image_{i}"
                    self.supplements_text.tag_add(tag_name, start_pos, end_pos)
                    self.supplements_text.tag_config(tag_name, foreground="blue", underline=False)
                    self.supplements_text.tag_bind(tag_name, "<Button-1>", 
                                                  lambda e, ln=line_num: self._navigate_to_line(ln))
                    self.supplements_text.tag_bind(tag_name, "<Enter>", 
                                                  lambda e, tn=tag_name: self.supplements_text.tag_config(tn, underline=True))
                    self.supplements_text.tag_bind(tag_name, "<Leave>", 
                                                  lambda e, tn=tag_name: self.supplements_text.tag_config(tn, underline=False))
            
            # Display placeholder if no content
            if not link_items and not image_items:
                self.supplements_text.insert("1.0", "No links or images found in the document.")
            
            # Disable text editing
            self.supplements_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logging.error(f"Error updating supplements: {e}")
            import traceback
            traceback.print_exc()

    def _extract_text_from_element(self, element):
        """Recursively extract text from an AST element."""
        if hasattr(element, 'children'):
            if isinstance(element.children, str):
                return element.children
            elif isinstance(element.children, list):
                parts = []
                for child in element.children:
                    if isinstance(child, str):
                        parts.append(child)
                    else:
                        parts.append(self._extract_text_from_element(child))
                return ''.join(parts)
        return ""
    
    def update_title(self, filename: str, has_unsaved_changes: bool = False):
        """
        Update the window title with filename and unsaved changes indicator.
        
        Args:
            filename: Name of the current file
            has_unsaved_changes: Whether there are unsaved changes
        """
        title = f"Scriptum Simplex - {filename}"
        if has_unsaved_changes:
            title += " *"
        self.title(title)
    
    def show_error(self, title: str, message: str):
        """
        Show an error dialog.
        
        Args:
            title: Dialog title
            message: Error message
        """
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """
        Show an info dialog.
        
        Args:
            title: Dialog title
            message: Info message
        """
        messagebox.showinfo(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """
        Show a yes/no dialog.
        
        Args:
            title: Dialog title
            message: Question message
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        return messagebox.askyesno(title, message)
    
    def apply_theme(self, theme_name: str):
        """
        Apply a theme to the preview canvas.
        
        Args:
            theme_name: Name of the theme to apply ('default', 'typora', 'github')
        """
        # Note: Old built-in themes (default, typora, github) are not compatible
        # with EnhancedMarkdownCanvas. Use "Load Typora Theme..." instead.
        
        logging.warning(f"Built-in theme '{theme_name}' not supported with EnhancedMarkdownCanvas")
        self.show_info(
            "Theme Not Supported",
            f"The built-in '{theme_name}' theme is not compatible with the enhanced renderer.\n\n"
            "Please use 'Themes → Load Typora Theme...' to load a full Typora theme folder."
        )
        
        # Update the theme variable to reflect the change
        self.current_theme_var.set(theme_name)
    
    def _resolve_image_path(self, image_path: str) -> str:
        """
        Resolve an image path using the document's metadata.
        
        Args:
            image_path: Image path from markdown
            
        Returns:
            Resolved absolute path to the image
        """
        if self.controller and hasattr(self.controller, 'model'):
            return self.controller.model.metadata.resolve_image_path(image_path)
        return image_path
