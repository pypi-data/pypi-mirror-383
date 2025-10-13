"""
Critic Table Widget

Treeview-based table for displaying and managing CriticMarkup changes.
"""

import tkinter as tk
try:
    import ttkbootstrap as ttk  # type: ignore
    from ttkbootstrap import Style  # type: ignore
    HAS_TTKBOOTSTRAP = True
    Frame = ttk.Frame
except ImportError:
    from tkinter import ttk
    HAS_TTKBOOTSTRAP = False
    Frame = ttk.Frame
from typing import List, Optional, Callable
from .critic_change import CriticChange, ChangeType, ChangeStatus


class CriticTable(Frame):  # type: ignore[misc]
    """Treeview table for displaying CriticMarkup changes."""

    def __init__(
        self,
        parent: tk.Widget,
        on_row_click: Optional[Callable[[CriticChange], None]] = None
    ) -> None:
        """
        Initialize the Critic Table.

        Args:
            parent: Parent widget
            on_row_click: Callback function when a row is clicked
        """
        super().__init__(parent)
        self.on_row_click = on_row_click
        self.changes: List[CriticChange] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        # Define columns
        columns = ('type', 'line', 'old_text', 'new_text', 'comment', 'status')

        # Create Treeview
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        # Define column headings
        self.tree.heading('type', text='Type')
        self.tree.heading('line', text='Line')
        self.tree.heading('old_text', text='Old Text')
        self.tree.heading('new_text', text='New Text')
        self.tree.heading('comment', text='Comment')
        self.tree.heading('status', text='Status')

        # Configure column widths
        self.tree.column('type', width=100, minwidth=80)
        self.tree.column('line', width=60, minwidth=50)
        self.tree.column('old_text', width=200, minwidth=100)
        self.tree.column('new_text', width=200, minwidth=100)
        self.tree.column('comment', width=200, minwidth=100)
        self.tree.column('status', width=80, minwidth=60)

        # Create scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind click event
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        # Configure tags for color coding
        self._setup_tags()

    def _setup_tags(self) -> None:
        """Set up tags for color coding rows using theme colors."""
        # Try to get theme colors from ttkbootstrap
        if HAS_TTKBOOTSTRAP:
            try:
                style = Style.get_instance()
                colors = style.colors

                # Use theme colors with fallbacks
                add_bg = colors.success if hasattr(colors, 'success') else '#d4edda'
                del_bg = colors.danger if hasattr(colors, 'danger') else '#f8d7da'
                sub_bg = colors.info if hasattr(colors, 'info') else '#cce7ff'
                warn_bg = colors.warning if hasattr(colors, 'warning') else '#fff3cd'
                gray_fg = colors.secondary if hasattr(colors, 'secondary') else '#999999'

                self.tree.tag_configure('addition', background=add_bg)
                self.tree.tag_configure('deletion', background=del_bg)
                self.tree.tag_configure('substitution', background=sub_bg)
                self.tree.tag_configure('highlight', background=warn_bg)
                self.tree.tag_configure('comment', background=warn_bg)
                self.tree.tag_configure('grayed', foreground=gray_fg)
            except Exception:
                # Fallback to default colors
                self._setup_default_colors()
        else:
            self._setup_default_colors()

    def _setup_default_colors(self) -> None:
        """Set up default colors when theme colors are unavailable."""
        self.tree.tag_configure('addition', background='#d4edda')
        self.tree.tag_configure('deletion', background='#f8d7da')
        self.tree.tag_configure('substitution', background='#cce7ff')
        self.tree.tag_configure('highlight', background='#fff3cd')
        self.tree.tag_configure('comment', background='#fff3cd')
        self.tree.tag_configure('grayed', foreground='#999999')

    def load_changes(self, changes: List[CriticChange]) -> None:
        """
        Load changes into the table.

        Args:
            changes: List of CriticChange objects to display
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Store changes
        self.changes = changes

        # Add changes to tree
        for idx, change in enumerate(changes):
            self._add_change_to_tree(change, idx)

    def _add_change_to_tree(self, change: CriticChange, idx: int) -> None:
        """
        Add a single change to the tree.

        Args:
            change: CriticChange object to add
            idx: Index of the change (used as item ID)
        """
        # Prepare values for columns
        values = (
            change.change_type.value,
            str(change.line_number),
            change.old_text or '',
            change.new_text or '',
            change.comment_text or '',
            change.status.value
        )

        # Determine tags
        tags = [self._get_type_tag(change.change_type)]
        if change.status != ChangeStatus.PENDING:
            tags.append('grayed')

        # Insert into tree
        self.tree.insert('', 'end', iid=str(idx), values=values, tags=tags)

    def _get_type_tag(self, change_type: ChangeType) -> str:
        """
        Get the tag name for a change type.

        Args:
            change_type: Type of change

        Returns:
            Tag name for color coding
        """
        tag_map = {
            ChangeType.ADDITION: 'addition',
            ChangeType.DELETION: 'deletion',
            ChangeType.SUBSTITUTION: 'substitution',
            ChangeType.HIGHLIGHT: 'highlight',
            ChangeType.COMMENT: 'comment',
        }
        return tag_map.get(change_type, '')

    def _on_tree_select(self, event: object) -> None:
        """
        Handle tree selection event.

        Args:
            event: Tkinter event object
        """
        selection = self.tree.selection()
        if selection and self.on_row_click:
            # Get the selected item ID
            item_id = selection[0]
            idx = int(item_id)

            # Get the corresponding change
            if 0 <= idx < len(self.changes):
                change = self.changes[idx]
                self.on_row_click(change)

    def update_change_status(self, idx: int, status: ChangeStatus) -> None:
        """
        Update the status of a change.

        Args:
            idx: Index of the change to update
            status: New status
        """
        if 0 <= idx < len(self.changes):
            # Update the change object
            self.changes[idx].status = status

            # Update the tree item
            item_id = str(idx)
            if self.tree.exists(item_id):
                # Update status column
                values = list(self.tree.item(item_id, 'values'))
                values[5] = status.value
                self.tree.item(item_id, values=values)

                # Update tags (add grayed if not pending)
                current_tags = list(self.tree.item(item_id, 'tags'))
                if status != ChangeStatus.PENDING and 'grayed' not in current_tags:
                    current_tags.append('grayed')
                elif status == ChangeStatus.PENDING and 'grayed' in current_tags:
                    current_tags.remove('grayed')
                self.tree.item(item_id, tags=current_tags)

    def get_selected_change(self) -> Optional[CriticChange]:
        """
        Get the currently selected change.

        Returns:
            Selected CriticChange object, or None if nothing selected
        """
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            idx = int(item_id)
            if 0 <= idx < len(self.changes):
                return self.changes[idx]
        return None

    def get_selected_index(self) -> Optional[int]:
        """
        Get the index of the currently selected change.

        Returns:
            Index of selected change, or None if nothing selected
        """
        selection = self.tree.selection()
        if selection:
            return int(selection[0])
        return None

    def remove_non_pending_changes(self) -> None:
        """Remove all accepted/rejected changes from the table."""
        # Get items to remove
        items_to_remove = []
        for idx, change in enumerate(self.changes):
            if change.status != ChangeStatus.PENDING:
                items_to_remove.append(idx)

        # Remove from tree (in reverse order to maintain indices)
        for idx in reversed(items_to_remove):
            item_id = str(idx)
            if self.tree.exists(item_id):
                self.tree.delete(item_id)

        # Remove from changes list
        self.changes = [c for c in self.changes if c.status == ChangeStatus.PENDING]

        # Rebuild tree with new indices
        self.load_changes(self.changes)
