"""
Property Editor Dialog

Dialog for editing CSS property values.
"""

import tkinter as tk
from tkinter import messagebox, colorchooser
try:
    import ttkbootstrap as ttk  # type: ignore
except ImportError:
    from tkinter import ttk
from typing import Optional, Callable
import re


class PropertyEditorDialog(tk.Toplevel):
    """Dialog for editing a CSS property value."""

    def __init__(
        self,
        parent: tk.Widget,
        element_name: str,
        property_name: str,
        current_value: str,
        on_save: Optional[Callable[[str, str, str], None]] = None
    ) -> None:
        """
        Initialize property editor dialog.

        Args:
            parent: Parent widget
            element_name: CSS element name (e.g., 'h1', 'paragraph')
            property_name: CSS property name (e.g., 'color', 'font-size')
            current_value: Current property value
            on_save: Callback function(element, property, new_value)
        """
        super().__init__(parent)
        
        self.element_name = element_name
        self.property_name = property_name
        self.current_value = current_value
        self.on_save = on_save
        self.result: Optional[str] = None
        
        self.title(f"Edit {element_name}.{property_name}")
        self.geometry("500x300")
        self.resizable(True, True)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            header,
            text="Edit Property",
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT)
        
        # Property info
        info_frame = ttk.LabelFrame(self, text="Property Information", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X)
        
        ttk.Label(info_grid, text="Element:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_grid, text=self.element_name).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2
        )
        
        ttk.Label(info_grid, text="Property:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2
        )
        ttk.Label(info_grid, text=self.property_name).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2
        )
        
        # Value editor
        editor_frame = ttk.LabelFrame(self, text="Value", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Value input
        input_frame = ttk.Frame(editor_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.value_var = tk.StringVar(value=self.current_value)
        self.value_entry = ttk.Entry(
            input_frame,
            textvariable=self.value_var,
            font=('Consolas', 10)
        )
        self.value_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Special buttons based on property type
        if self._is_color_property():
            ttk.Button(
                input_frame,
                text="Pick Color",
                command=self._pick_color,
                width=12
            ).pack(side=tk.LEFT)
        
        # Suggestions
        suggestions_frame = ttk.Frame(editor_frame)
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(suggestions_frame, text="Common values:").pack(anchor=tk.W)
        
        suggestions_list = ttk.Frame(suggestions_frame)
        suggestions_list.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(suggestions_list)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.suggestions_listbox = tk.Listbox(
            suggestions_list,
            yscrollcommand=scrollbar.set,
            font=('Consolas', 9)
        )
        self.suggestions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.suggestions_listbox.yview)
        
        # Populate suggestions
        self._populate_suggestions()
        
        # Bind double-click to select suggestion
        self.suggestions_listbox.bind('<Double-Button-1>', self._on_suggestion_select)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        try:
            # Try ttkbootstrap buttons
            ttk.Button(
                button_frame,
                text="Save",
                command=self._on_save,
                bootstyle="success"  # type: ignore
            ).pack(side=tk.RIGHT, padx=2)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel,
                bootstyle="secondary"  # type: ignore
            ).pack(side=tk.RIGHT, padx=2)
            
            ttk.Button(
                button_frame,
                text="Reset",
                command=self._on_reset,
                bootstyle="warning"  # type: ignore
            ).pack(side=tk.LEFT, padx=2)
        except Exception:
            # Fallback to standard buttons
            ttk.Button(
                button_frame,
                text="Save",
                command=self._on_save
            ).pack(side=tk.RIGHT, padx=2)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self._on_cancel
            ).pack(side=tk.RIGHT, padx=2)
            
            ttk.Button(
                button_frame,
                text="Reset",
                command=self._on_reset
            ).pack(side=tk.LEFT, padx=2)
        
        # Bind Enter key
        self.value_entry.bind('<Return>', lambda e: self._on_save())
        self.value_entry.bind('<Escape>', lambda e: self._on_cancel())
        
        # Focus on entry
        self.value_entry.focus_set()
        self.value_entry.select_range(0, tk.END)

    def _is_color_property(self) -> bool:
        """Check if this is a color property."""
        color_props = [
            'color', 'background-color', 'border-color',
            'background', 'border', 'outline-color'
        ]
        return any(prop in self.property_name.lower() for prop in color_props)

    def _pick_color(self) -> None:
        """Open color picker dialog."""
        current = self.value_var.get()
        
        # Try to parse current color
        initial_color = None
        if current.startswith('#'):
            initial_color = current
        
        color = colorchooser.askcolor(
            color=initial_color,
            title="Pick Color",
            parent=self
        )
        
        if color and color[1]:
            self.value_var.set(color[1])

    def _populate_suggestions(self) -> None:
        """Populate suggestions based on property type."""
        suggestions = self._get_suggestions_for_property()
        
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)

    def _get_suggestions_for_property(self) -> list:
        """Get common value suggestions for the property."""
        prop = self.property_name.lower()
        
        # Color properties
        if 'color' in prop or 'background' in prop:
            return [
                '#000000  (black)',
                '#FFFFFF  (white)',
                '#FF0000  (red)',
                '#00FF00  (green)',
                '#0000FF  (blue)',
                '#808080  (gray)',
                '#C0C0C0  (silver)',
                'transparent',
                'inherit',
                'currentColor'
            ]
        
        # Font size
        if 'font-size' in prop or 'size' in prop:
            return [
                '12px', '14px', '16px', '18px', '20px', '24px',
                '1em', '1.2em', '1.5em', '2em',
                '1rem', '1.2rem', '1.5rem', '2rem',
                'inherit'
            ]
        
        # Font weight
        if 'font-weight' in prop or 'weight' in prop:
            return [
                'normal', 'bold', 'bolder', 'lighter',
                '100', '200', '300', '400', '500',
                '600', '700', '800', '900', 'inherit'
            ]
        
        # Font family
        if 'font-family' in prop or 'family' in prop:
            return [
                'Arial, sans-serif',
                'Helvetica, sans-serif',
                'Times New Roman, serif',
                'Georgia, serif',
                'Courier New, monospace',
                'Consolas, monospace',
                'Verdana, sans-serif',
                'inherit'
            ]
        
        # Text align
        if 'text-align' in prop or 'align' in prop:
            return ['left', 'center', 'right', 'justify', 'inherit']
        
        # Display
        if 'display' in prop:
            return [
                'block', 'inline', 'inline-block', 'flex',
                'grid', 'none', 'inherit'
            ]
        
        # Margin/Padding
        if 'margin' in prop or 'padding' in prop:
            return [
                '0', '5px', '10px', '15px', '20px',
                '0.5em', '1em', '1.5em', '2em',
                '0 auto', 'inherit'
            ]
        
        # Border
        if 'border' in prop:
            return [
                '1px solid #000',
                '2px solid #000',
                '1px dashed #000',
                '1px dotted #000',
                'none',
                'inherit'
            ]
        
        # Width/Height
        if 'width' in prop or 'height' in prop:
            return [
                'auto', '100%', '50%', '25%',
                '100px', '200px', '300px',
                'inherit'
            ]
        
        # Generic
        return ['inherit', 'initial', 'unset', 'auto', 'none']

    def _on_suggestion_select(self, event: tk.Event) -> None:
        """Handle suggestion selection."""
        selection = self.suggestions_listbox.curselection()
        if selection:
            value = self.suggestions_listbox.get(selection[0])
            # Extract just the value (before any comment)
            value = value.split('(')[0].strip()
            self.value_var.set(value)

    def _on_save(self) -> None:
        """Handle save button."""
        new_value = self.value_var.get().strip()
        
        if not new_value:
            messagebox.showwarning(
                "Empty Value",
                "Please enter a value or click Cancel.",
                parent=self
            )
            return
        
        # Basic validation
        if not self._validate_value(new_value):
            response = messagebox.askyesno(
                "Invalid Value",
                f"The value '{new_value}' may not be valid for this property.\n\n"
                "Save anyway?",
                parent=self
            )
            if not response:
                return
        
        self.result = new_value
        
        # Call callback
        if self.on_save:
            self.on_save(self.element_name, self.property_name, new_value)
        
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel button."""
        self.result = None
        self.destroy()

    def _on_reset(self) -> None:
        """Handle reset button."""
        self.value_var.set(self.current_value)

    def _validate_value(self, value: str) -> bool:
        """
        Basic validation of CSS value.
        
        Args:
            value: Value to validate
            
        Returns:
            True if value seems valid
        """
        # Allow common keywords
        keywords = [
            'inherit', 'initial', 'unset', 'auto', 'none',
            'normal', 'bold', 'italic', 'transparent'
        ]
        if value.lower() in keywords:
            return True
        
        # Allow hex colors
        if re.match(r'^#[0-9A-Fa-f]{3,8}$', value):
            return True
        
        # Allow rgb/rgba
        if re.match(r'^rgba?\([^)]+\)$', value):
            return True
        
        # Allow sizes with units
        if re.match(r'^-?\d+(\.\d+)?(px|em|rem|%|pt|vh|vw|ch|ex)$', value):
            return True
        
        # Allow numbers
        if re.match(r'^-?\d+(\.\d+)?$', value):
            return True
        
        # Allow quoted strings (for font families, etc.)
        if value.startswith('"') and value.endswith('"'):
            return True
        if value.startswith("'") and value.endswith("'"):
            return True
        
        # For complex values (borders, etc.), just accept them
        # More sophisticated validation would require a CSS parser
        return True
