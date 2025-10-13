"""
Theme Editor Main Window

Main window for the Typora Theme Editor & Tester tool.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
try:
    import ttkbootstrap as ttk  # type: ignore
except ImportError:
    from tkinter import ttk
import logging
from pathlib import Path
from typing import Any

from .config import ThemeEditorConfig
from .theme_manager import ThemeManager
from .property_editor_dialog import PropertyEditorDialog
from ..full_typora_theme_support.enhanced_canvas import EnhancedMarkdownCanvas


class ThemeEditorWindow(ttk.Window if 'ttk' in dir() and hasattr(ttk, 'Window') else tk.Tk):  # type: ignore
    """Main window for theme editor."""

    def __init__(self) -> None:
        """Initialize the theme editor window."""
        super().__init__(themename="cosmo")  # type: ignore

        self.title("Scriptum Simplex - Theme Editor")

        # Load configuration
        self.editor_config = ThemeEditorConfig()
        geometry = self.editor_config.get("window_geometry", "1400x900")
        self.geometry(geometry)

        # Initialize managers
        self.theme_manager = ThemeManager()

        # Create UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()

        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        logging.info("Theme Editor window initialized")

    def _create_menu(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Theme...", command=self._load_theme, accelerator="Ctrl+O")
        file_menu.add_separator()

        # Recent themes submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Themes", menu=self.recent_menu)
        self._update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save_theme, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_theme_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing, accelerator="Alt+F4")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Revert Changes", command=self._revert_changes)
        edit_menu.add_command(label="Reset to Defaults", command=self._reset_to_defaults)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reload Preview", command=self._reload_preview)
        view_menu.add_command(label="Clear Output", command=self._clear_output)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)

        # Bind keyboard shortcuts
        self.bind_all("<Control-o>", lambda e: self._load_theme())
        self.bind_all("<Control-s>", lambda e: self._save_theme())
        self.bind_all("<Control-Shift-S>", lambda e: self._save_theme_as())

    def _create_toolbar(self) -> None:
        """Create toolbar."""
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Buttons
        ttk.Button(
            toolbar,
            text="Load Theme",
            command=self._load_theme,
            bootstyle="primary"  # type: ignore
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Save",
            command=self._save_theme,
            bootstyle="success"  # type: ignore
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Load Markdown",
            command=self._load_markdown,
            bootstyle="info"  # type: ignore
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Reload",
            command=self._reload_preview,
            bootstyle="secondary"  # type: ignore
        ).pack(side=tk.LEFT, padx=2)

        # Theme label
        self.theme_label = ttk.Label(
            toolbar,
            text="No theme loaded",
            bootstyle="inverse-secondary"  # type: ignore
        )
        self.theme_label.pack(side=tk.LEFT, padx=20)

        # Modified indicator
        self.modified_label = ttk.Label(toolbar, text="")
        self.modified_label.pack(side=tk.LEFT, padx=10)

    def _create_main_content(self) -> None:
        """Create main content area."""
        # Main paned window
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left pane: Preview
        self._create_preview_pane()

        # Middle pane: Properties
        self._create_properties_pane()

        # Right pane: Output/Debug
        self._create_output_pane()

    def _create_preview_pane(self) -> None:
        """Create preview pane."""
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=2)

        ttk.Label(
            left_frame,
            text="Preview",
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W, padx=5, pady=5)

        # Canvas frame with scrollbar
        canvas_frame = ttk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.preview_canvas = EnhancedMarkdownCanvas(canvas_frame, bg='white')
        preview_scroll = ttk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=self.preview_canvas.yview
        )
        self.preview_canvas.configure(yscrollcommand=preview_scroll.set)

        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_properties_pane(self) -> None:
        """Create properties pane."""
        middle_frame = ttk.Frame(self.paned)
        self.paned.add(middle_frame, weight=1)

        # Header with edit button
        header_frame = ttk.Frame(middle_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            header_frame,
            text="Theme Properties",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            header_frame,
            text="Edit",
            command=self._edit_selected_property,
            bootstyle="info",  # type: ignore
            width=10
        ).pack(side=tk.RIGHT)

        # Tree view for properties
        tree_frame = ttk.Frame(middle_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Value',),
            show='tree headings'
        )
        self.tree.heading('#0', text='Property')
        self.tree.heading('Value', text='Value')
        self.tree.column('#0', width=250)
        self.tree.column('Value', width=250)

        tree_scroll = ttk.Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_selected_property())

    def _create_output_pane(self) -> None:
        """Create output/debug pane."""
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)

        # Header with edit button
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(
            header_frame,
            text="CSS Variables",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)

        ttk.Button(
            header_frame,
            text="Edit Variable",
            command=self._edit_css_variable,
            bootstyle="info",  # type: ignore
            width=15
        ).pack(side=tk.RIGHT)

        # CSS Variables list
        vars_frame = ttk.Frame(right_frame)
        vars_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create listbox for variables
        list_frame = ttk.Frame(vars_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.css_vars_listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 9),
            selectmode=tk.SINGLE
        )
        
        vars_scroll = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.css_vars_listbox.yview
        )
        self.css_vars_listbox.configure(yscrollcommand=vars_scroll.set)

        self.css_vars_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vars_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click to edit
        self.css_vars_listbox.bind('<Double-Button-1>', lambda e: self._edit_css_variable())

        # Info text area (read-only)
        info_label = ttk.Label(right_frame, text="Theme Info:", font=('Arial', 9, 'bold'))
        info_label.pack(anchor=tk.W, padx=5, pady=(10, 2))

        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=10,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure tags
        self.output_text.tag_config('heading', font=('Arial', 10, 'bold'))

    def _create_status_bar(self) -> None:
        """Create status bar."""
        self.status_bar = ttk.Label(
            self,
            text="Ready",
            bootstyle="inverse-dark",  # type: ignore
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

    def _edit_selected_property(self) -> None:
        """Edit the selected property in the tree."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a property to edit.")
            return
        
        item_id = selection[0]
        parent_id = self.tree.parent(item_id)
        
        # Check if it's a property (not an element header)
        if not parent_id:
            messagebox.showinfo("Invalid Selection", "Please select a property, not an element header.")
            return
        
        # Get property info
        property_name = self.tree.item(item_id)['text']
        current_value = self.tree.item(item_id)['values'][0] if self.tree.item(item_id)['values'] else ""
        
        # Get element name from parent
        element_text = self.tree.item(parent_id)['text']
        element_name = element_text.split('(')[0].strip()
        
        # Open editor dialog
        dialog = PropertyEditorDialog(
            self,
            element_name,
            property_name,
            current_value,
            on_save=self._on_property_saved
        )
        self.wait_window(dialog)

    def _on_property_saved(self, element: str, property_name: str, new_value: str) -> None:
        """
        Handle property save from editor dialog.
        
        Args:
            element: Element name
            property_name: Property name
            new_value: New property value
        """
        logging.info(f"Property saved: {element}.{property_name} = {new_value}")
        
        # Update the theme styles
        success = self.theme_manager.update_property(element, property_name, new_value)
        
        if success:
            # Update the tree view
            self._update_property_in_tree(element, property_name, new_value)
            
            # Update modified indicator
            self._update_modified_indicator()
            
            # Update preview with new styles
            if self.theme_manager.current_styles:
                self.preview_canvas.set_theme(self.theme_manager.current_styles)
                self._load_default_sample()
            
            self._set_status(f"Updated {element}.{property_name}")
        else:
            messagebox.showerror(
                "Update Failed",
                f"Failed to update {element}.{property_name}\n\nCheck the log for details."
            )

    def _edit_css_variable(self) -> None:
        """Edit the selected CSS variable."""
        selection = self.css_vars_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a CSS variable to edit.")
            return
        
        # Get the selected variable
        var_line = self.css_vars_listbox.get(selection[0])
        
        # Parse variable name and value
        if ':' in var_line:
            var_name, current_value = var_line.split(':', 1)
            var_name = var_name.strip()
            current_value = current_value.strip()
        else:
            messagebox.showerror("Parse Error", "Could not parse CSS variable.")
            return
        
        # Open editor dialog
        dialog = PropertyEditorDialog(
            self,
            "CSS Variable",
            var_name,
            current_value,
            on_save=self._on_css_variable_saved
        )
        self.wait_window(dialog)

    def _on_css_variable_saved(self, _element: str, var_name: str, new_value: str) -> None:
        """
        Handle CSS variable save from editor dialog.
        
        Args:
            _element: Unused (always "CSS Variable")
            var_name: Variable name
            new_value: New variable value
        """
        logging.info(f"CSS variable saved: {var_name} = {new_value}")
        
        # Update the CSS variable
        success = self.theme_manager.update_css_variable(var_name, new_value)
        
        if success:
            # Refresh the CSS variables display
            self._display_css_variables()
            
            # Update modified indicator
            self._update_modified_indicator()
            
            # Update preview (CSS variables might affect rendering)
            if self.theme_manager.current_styles:
                self.preview_canvas.set_theme(self.theme_manager.current_styles)
                self._load_default_sample()
            
            self._set_status(f"Updated CSS variable {var_name}")
        else:
            messagebox.showerror(
                "Update Failed",
                f"Failed to update CSS variable {var_name}\n\nCheck the log for details."
            )

    def _update_property_in_tree(self, element: str, property_name: str, new_value: str) -> None:
        """
        Update a property value in the tree view.
        
        Args:
            element: Element name
            property_name: Property name
            new_value: New value
        """
        # Find the element node
        for item_id in self.tree.get_children():
            item_text = self.tree.item(item_id)['text']
            item_element = item_text.split('(')[0].strip()
            
            if item_element == element:
                # Find the property child
                for child_id in self.tree.get_children(item_id):
                    if self.tree.item(child_id)['text'] == property_name:
                        # Update the value
                        self.tree.item(child_id, values=(new_value,))
                        logging.info(f"Updated tree: {element}.{property_name} = {new_value}")
                        return

    def _load_theme(self) -> None:
        """Load a theme folder."""
        folder_path = filedialog.askdirectory(title="Select Typora Theme Folder")

        if not folder_path:
            return

        self._set_status(f"Loading theme from: {folder_path}")
        self.update()

        # Load theme
        styles = self.theme_manager.load_theme(Path(folder_path))

        if styles:
            theme_name = self.theme_manager.get_theme_name()
            self.theme_label.config(text=f"Theme: {theme_name}")
            self._set_status(f"Successfully loaded: {theme_name}")

            # Add to recent themes
            self.editor_config.add_recent_theme(Path(folder_path))
            self._update_recent_menu()

            # Apply theme to preview
            self.preview_canvas.set_theme(styles)

            # Load default sample
            self._load_default_sample()

            # Display properties
            self._display_theme_properties(styles)
            self._display_css_variables()

            self._update_modified_indicator()
        else:
            self._set_status("Failed to load theme")
            messagebox.showerror("Error", "Failed to load theme. Check the log for details.")

    def _load_markdown(self) -> None:
        """Load a markdown file."""
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_text = f.read()

            self._set_status(f"Rendering: {file_path}")
            self.update()

            self.preview_canvas.render_markdown(markdown_text)
            self._set_status(f"Loaded: {Path(file_path).name}")

        except Exception as e:
            self._set_status(f"Error loading file: {e}")
            logging.error(f"Error loading markdown file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def _load_default_sample(self) -> None:
        """Load the default sample markdown."""
        sample_name = self.editor_config.get("default_sample", "comprehensive.md")
        sample_path = Path(__file__).parent / "samples" / sample_name

        if sample_path.exists():
            try:
                with open(sample_path, 'r', encoding='utf-8') as f:
                    markdown_text = f.read()
                self.preview_canvas.render_markdown(markdown_text)
                logging.info(f"Loaded default sample: {sample_name}")
            except Exception as e:
                logging.error(f"Error loading default sample: {e}")

    def _save_theme(self) -> None:
        """Save the current theme."""
        if not self.theme_manager.current_styles:
            messagebox.showwarning("Warning", "No theme loaded to save.")
            return

        if not self.theme_manager.is_modified:
            messagebox.showinfo("Info", "No changes to save.")
            return

        # Confirm save
        if not messagebox.askyesno("Confirm Save", "Save changes to the current theme?"):
            return

        self._set_status("Saving theme...")
        self.update()

        success = self.theme_manager.save_theme(backup=self.editor_config.get("create_backups", True))

        if success:
            self._set_status("Theme saved successfully")
            self._update_modified_indicator()
            messagebox.showinfo("Success", "Theme saved successfully!")
        else:
            self._set_status("Failed to save theme")
            messagebox.showerror("Error", "Failed to save theme. Check the log for details.")

    def _save_theme_as(self) -> None:
        """Save the current theme with a new name."""
        if not self.theme_manager.current_styles:
            messagebox.showwarning("Warning", "No theme loaded to save.")
            return

        # Ask for new theme name
        new_name = simpledialog.askstring("Save As", "Enter new theme name:")
        if not new_name:
            return

        # Ask for save location
        folder_path = filedialog.askdirectory(title="Select Save Location")
        if not folder_path:
            return

        new_path = Path(folder_path) / new_name

        self._set_status(f"Saving theme as '{new_name}'...")
        self.update()

        success = self.theme_manager.save_theme_as(new_path, new_name)

        if success:
            self.theme_label.config(text=f"Theme: {new_name}")
            self._set_status(f"Theme saved as '{new_name}'")
            self._update_modified_indicator()
            messagebox.showinfo("Success", f"Theme saved as '{new_name}'!")
        else:
            self._set_status("Failed to save theme")
            messagebox.showerror("Error", "Failed to save theme. Check the log for details.")

    def _revert_changes(self) -> None:
        """Revert all changes to the original theme."""
        if not self.theme_manager.is_modified:
            messagebox.showinfo("Info", "No changes to revert.")
            return

        if not messagebox.askyesno("Confirm Revert", "Revert all changes to the original theme?"):
            return

        if self.theme_manager.revert_changes():
            self._set_status("Changes reverted")
            self._reload_preview()
            self._update_modified_indicator()
            messagebox.showinfo("Success", "Changes reverted successfully!")
        else:
            messagebox.showerror("Error", "Failed to revert changes.")

    def _reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        if not messagebox.askyesno("Confirm Reset", "Reset all settings to defaults?"):
            return

        self.editor_config.reset_to_defaults()
        msg = "Settings reset to defaults. Restart the application for changes to take effect."
        messagebox.showinfo("Success", msg)

    def _reload_preview(self) -> None:
        """Reload the preview."""
        if self.theme_manager.current_styles:
            self.preview_canvas.set_theme(self.theme_manager.current_styles)
            self._load_default_sample()
            self._set_status("Preview reloaded")

    def _clear_output(self) -> None:
        """Clear the output pane."""
        self.output_text.delete('1.0', tk.END)
        self._display_css_variables()

    def _display_theme_properties(self, styles: Any) -> None:
        """Display theme properties in tree view."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add elements
        elements = [
            'body', 'write', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'paragraph', 'link', 'link_hover', 'ul', 'ol', 'li',
            'code', 'code_block', 'blockquote', 'blockquote_before',
            'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'img'
        ]

        for element_name in elements:
            props = styles.get_element(element_name)

            # Count non-None properties
            prop_count = sum(
                1 for attr in dir(props)
                if not attr.startswith('_')
                and not callable(getattr(props, attr))
                and getattr(props, attr) is not None
            )

            if prop_count > 0:
                # Add element node
                element_node = self.tree.insert(
                    '',
                    'end',
                    text=f"{element_name} ({prop_count} properties)",
                    open=False
                )

                # Add properties
                for attr in sorted(dir(props)):
                    if not attr.startswith('_') and not callable(getattr(props, attr)):
                        value = getattr(props, attr)
                        if value:
                            css_name = attr.replace('_', '-')
                            self.tree.insert(
                                element_node,
                                'end',
                                text=css_name,
                                values=(str(value),)
                            )

    def _display_css_variables(self) -> None:
        """Display CSS variables in listbox and info in output pane."""
        # Clear listbox
        self.css_vars_listbox.delete(0, tk.END)
        
        # Populate CSS variables listbox
        css_vars = self.theme_manager.get_css_variables()
        if css_vars:
            for var_name, var_value in sorted(css_vars.items()):
                self.css_vars_listbox.insert(tk.END, f"{var_name}: {var_value}")
        
        # Update info text
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)

        self.output_text.insert(tk.END, "=== THEME SUMMARY ===\n\n", 'heading')
        self.output_text.insert(tk.END, f"Theme Name: {self.theme_manager.get_theme_name()}\n")
        self.output_text.insert(tk.END, f"CSS Variables: {len(css_vars)}\n")
        self.output_text.insert(tk.END, f"Theme Path: {self.theme_manager.current_theme_path}\n")
        
        self.output_text.config(state=tk.DISABLED)

    def _update_recent_menu(self) -> None:
        """Update recent themes menu."""
        self.recent_menu.delete(0, tk.END)

        recent_themes = self.editor_config.get_recent_themes()
        if recent_themes:
            for theme_path in recent_themes:
                self.recent_menu.add_command(
                    label=theme_path.name,
                    command=lambda p=theme_path: self._load_recent_theme(p)
                )
            self.recent_menu.add_separator()
            self.recent_menu.add_command(
                label="Clear Recent",
                command=self._clear_recent_themes
            )
        else:
            self.recent_menu.add_command(label="(No recent themes)", state=tk.DISABLED)

    def _load_recent_theme(self, theme_path: Path) -> None:
        """Load a theme from recent list."""
        if theme_path.exists():
            self._set_status(f"Loading recent theme: {theme_path.name}")
            styles = self.theme_manager.load_theme(theme_path)
            if styles:
                self.theme_label.config(text=f"Theme: {self.theme_manager.get_theme_name()}")
                self.preview_canvas.set_theme(styles)
                self._load_default_sample()
                self._display_theme_properties(styles)
                self._display_css_variables()
                self._update_modified_indicator()
        else:
            messagebox.showerror("Error", f"Theme folder not found:\n{theme_path}")
            self.editor_config.get_recent_themes()  # This will clean up non-existent paths

    def _clear_recent_themes(self) -> None:
        """Clear recent themes list."""
        self.editor_config.clear_recent_themes()
        self._update_recent_menu()

    def _update_modified_indicator(self) -> None:
        """Update the modified indicator."""
        if self.theme_manager.is_modified:
            self.modified_label.config(text="● Modified", foreground="orange")
        else:
            self.modified_label.config(text="")

    def _set_status(self, message: str) -> None:
        """Set status bar message."""
        self.status_bar.config(text=message)

    def _show_documentation(self) -> None:
        """Show documentation."""
        doc_text = (
            "Theme Editor Documentation\n\n"
            "1. Load a Typora theme folder\n"
            "2. View and edit CSS properties\n"
            "3. See live preview of changes\n"
            "4. Save modified theme\n\n"
            "For more information, see the user guide."
        )
        messagebox.showinfo("Documentation", doc_text)

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About Theme Editor",
            "Scriptum Simplex - Theme Editor\n\n"
            "A comprehensive tool for editing and testing Typora themes.\n\n"
            "Version: 1.0.0\n"
            "© 2025 Scriptum Simplex"
        )

    def _on_closing(self) -> None:
        """Handle window closing."""
        if self.theme_manager.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self._save_theme()

        # Save window geometry
        self.editor_config.set("window_geometry", self.geometry())
        self.editor_config.save()

        self.destroy()


def main() -> None:
    """Run the theme editor."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    app = ThemeEditorWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
