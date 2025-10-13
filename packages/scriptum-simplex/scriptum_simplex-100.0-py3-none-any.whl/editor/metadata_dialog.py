"""
Metadata dialog for editing document metadata.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
from .document_metadata import DocumentMetadata


class MetadataDialog(tk.Toplevel):
    """Dialog for editing document metadata."""
    
    def __init__(self, parent, metadata: DocumentMetadata):
        """
        Initialize the metadata dialog.
        
        Args:
            parent: Parent window
            metadata: DocumentMetadata instance to edit
        """
        super().__init__(parent)
        
        self.metadata = metadata
        self.result = None
        
        self.title("Document Metadata")
        self.geometry("600x700")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_values()
        
        # Center dialog on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Document Info Tab
        self._create_document_tab(notebook)
        
        # Images Tab
        self._create_images_tab(notebook)
        
        # Export Tab
        self._create_export_tab(notebook)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT)
    
    def _create_document_tab(self, notebook):
        """Create the Document Info tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Document Info")
        
        # Create scrollable frame
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        ttk.Label(scrollable_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(scrollable_frame, width=50)
        self.title_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Author First Name
        ttk.Label(scrollable_frame, text="Author First Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_first_entry = ttk.Entry(scrollable_frame, width=50)
        self.author_first_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Author Last Name
        ttk.Label(scrollable_frame, text="Author Last Name:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.author_last_entry = ttk.Entry(scrollable_frame, width=50)
        self.author_last_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Organization
        ttk.Label(scrollable_frame, text="Organization:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.organization_entry = ttk.Entry(scrollable_frame, width=50)
        self.organization_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # URL
        ttk.Label(scrollable_frame, text="URL:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_entry = ttk.Entry(scrollable_frame, width=50)
        self.url_entry.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # License
        ttk.Label(scrollable_frame, text="License:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.license_entry = ttk.Entry(scrollable_frame, width=50)
        self.license_entry.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Original Publication Date
        ttk.Label(scrollable_frame, text="Original Pub. Date:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.orig_date_entry = ttk.Entry(scrollable_frame, width=50)
        self.orig_date_entry.grid(row=6, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="(e.g., 2025-01-07)", font=("Arial", 8)).grid(row=6, column=2, sticky=tk.W, padx=5)
        
        # Last Publication Date
        ttk.Label(scrollable_frame, text="Last Pub. Date:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.last_date_entry = ttk.Entry(scrollable_frame, width=50)
        self.last_date_entry.grid(row=7, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="(e.g., 2025-01-07)", font=("Arial", 8)).grid(row=7, column=2, sticky=tk.W, padx=5)
        
        # Summary
        ttk.Label(scrollable_frame, text="Summary:").grid(row=8, column=0, sticky=tk.NW, padx=5, pady=5)
        self.summary_text = scrolledtext.ScrolledText(scrollable_frame, width=50, height=6)
        self.summary_text.grid(row=8, column=1, sticky=tk.EW, padx=5, pady=5)
        
        scrollable_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_images_tab(self, notebook):
        """Create the Images tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Images")
        
        ttk.Label(tab, text="Image Root Path:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.image_path_entry = ttk.Entry(tab, width=50)
        self.image_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=10)
        
        ttk.Label(
            tab,
            text="Leave empty to use document directory.\nUse relative paths (e.g., ./images) or absolute paths.",
            font=("Arial", 9),
            foreground="gray"
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)
        
        tab.columnconfigure(1, weight=1)
    
    def _create_export_tab(self, notebook):
        """Create the Export tab."""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Export Settings")
        
        ttk.Label(tab, text="Export Theme:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.export_theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(
            tab,
            textvariable=self.export_theme_var,
            values=["default", "typora", "github"],
            state="readonly"
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(tab, text="Page Size:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.page_size_var = tk.StringVar()
        page_combo = ttk.Combobox(
            tab,
            textvariable=self.page_size_var,
            values=["A4", "Letter", "Legal"],
            state="readonly"
        )
        page_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
        
        self.include_toc_var = tk.BooleanVar()
        ttk.Checkbutton(
            tab,
            text="Include Table of Contents",
            variable=self.include_toc_var
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
    
    def _load_values(self):
        """Load current metadata values into widgets."""
        # Document info
        self.title_entry.insert(0, self.metadata.get_document_title())
        self.author_first_entry.insert(0, self.metadata.get_author_first_name())
        self.author_last_entry.insert(0, self.metadata.get_author_last_name())
        self.organization_entry.insert(0, self.metadata.get_organization())
        self.url_entry.insert(0, self.metadata.get_url())
        self.license_entry.insert(0, self.metadata.get_license())
        self.orig_date_entry.insert(0, self.metadata.get_original_publication_date())
        self.last_date_entry.insert(0, self.metadata.get_last_publication_date())
        self.summary_text.insert("1.0", self.metadata.get_summary())
        
        # Images
        self.image_path_entry.insert(0, self.metadata.metadata['images']['root_path'])
        
        # Export
        self.export_theme_var.set(self.metadata.get_export_theme())
        self.page_size_var.set(self.metadata.metadata['export'].get('page_size', 'A4'))
        self.include_toc_var.set(self.metadata.metadata['export'].get('include_toc', False))
    
    def _save_values(self):
        """Save widget values to metadata."""
        # Document info
        self.metadata.set_document_title(self.title_entry.get())
        self.metadata.set_author_first_name(self.author_first_entry.get())
        self.metadata.set_author_last_name(self.author_last_entry.get())
        self.metadata.set_organization(self.organization_entry.get())
        self.metadata.set_url(self.url_entry.get())
        self.metadata.set_license(self.license_entry.get())
        self.metadata.set_original_publication_date(self.orig_date_entry.get())
        self.metadata.set_last_publication_date(self.last_date_entry.get())
        self.metadata.set_summary(self.summary_text.get("1.0", tk.END).strip())
        
        # Images
        self.metadata.set_image_root_path(self.image_path_entry.get())
        
        # Export
        self.metadata.set_export_theme(self.export_theme_var.get())
        self.metadata.metadata['export']['page_size'] = self.page_size_var.get()
        self.metadata.metadata['export']['include_toc'] = self.include_toc_var.get()
    
    def _on_save(self):
        """Handle Save button click."""
        self._save_values()
        self.result = True
        self.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = False
        self.destroy()
    
    def show(self) -> bool:
        """
        Show the dialog and wait for result.
        
        Returns:
            True if user clicked Save, False if cancelled
        """
        self.wait_window()
        return self.result if self.result is not None else False
