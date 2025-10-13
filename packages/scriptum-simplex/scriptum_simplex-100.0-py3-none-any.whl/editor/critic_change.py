"""
CriticMarkup Change Data Model

Represents a single CriticMarkup change in a document.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    """Type of CriticMarkup change."""
    ADDITION = "Addition"
    DELETION = "Deletion"
    SUBSTITUTION = "Substitution"
    HIGHLIGHT = "Highlight"
    COMMENT = "Comment"


class ChangeStatus(Enum):
    """Status of a CriticMarkup change."""
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


@dataclass
class CriticChange:
    """
    Represents a single CriticMarkup change.

    Attributes:
        change_type: Type of change (addition, deletion, etc.)
        line_number: Line number where the change appears (1-indexed)
        start_pos: Character position in the document where change starts
        end_pos: Character position in the document where change ends
        old_text: Original text (for deletions and substitutions)
        new_text: New text (for additions and substitutions)
        comment_text: Comment text (for comments)
        status: Current status (pending, accepted, rejected)
        original_markup: The original CriticMarkup syntax
    """
    change_type: ChangeType
    line_number: int
    start_pos: int
    end_pos: int
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    comment_text: Optional[str] = None
    status: ChangeStatus = ChangeStatus.PENDING
    original_markup: str = ""

    def get_display_text(self) -> str:
        """
        Get text to display in the table based on change type.

        Returns:
            Formatted text for display
        """
        if self.change_type == ChangeType.ADDITION:
            return self.new_text or ""
        elif self.change_type == ChangeType.DELETION:
            return self.old_text or ""
        elif self.change_type == ChangeType.SUBSTITUTION:
            return f"{self.old_text} → {self.new_text}"
        elif self.change_type == ChangeType.HIGHLIGHT:
            return self.new_text or ""
        elif self.change_type == ChangeType.COMMENT:
            return self.comment_text or ""
        return ""

    def get_accepted_text(self) -> str:
        """
        Get the text that should replace the markup when accepted.

        Returns:
            Text to use when change is accepted
        """
        if self.change_type == ChangeType.ADDITION:
            return self.new_text or ""
        elif self.change_type == ChangeType.DELETION:
            return ""  # Remove the deleted text
        elif self.change_type == ChangeType.SUBSTITUTION:
            return self.new_text or ""
        elif self.change_type == ChangeType.HIGHLIGHT:
            return self.new_text or ""  # Keep highlighted text
        elif self.change_type == ChangeType.COMMENT:
            return ""  # Remove comment
        return ""

    def get_rejected_text(self) -> str:
        """
        Get the text that should replace the markup when rejected.

        Returns:
            Text to use when change is rejected
        """
        if self.change_type == ChangeType.ADDITION:
            return ""  # Remove the addition
        elif self.change_type == ChangeType.DELETION:
            return self.old_text or ""  # Keep the original text
        elif self.change_type == ChangeType.SUBSTITUTION:
            return self.old_text or ""  # Keep the old text
        elif self.change_type == ChangeType.HIGHLIGHT:
            return self.new_text or ""  # Keep text, remove highlight
        elif self.change_type == ChangeType.COMMENT:
            return ""  # Remove comment
        return ""

    def get_color(self) -> str:
        """
        Get the color code for this change type.

        Returns:
            Hex color code
        """
        colors = {
            ChangeType.ADDITION: "#d4edda",      # Green
            ChangeType.DELETION: "#f8d7da",      # Red
            ChangeType.SUBSTITUTION: "#cce7ff",  # Blue
            ChangeType.HIGHLIGHT: "#fff3cd",     # Yellow
            ChangeType.COMMENT: "#fff3cd",       # Yellow
        }
        return colors.get(self.change_type, "#ffffff")
