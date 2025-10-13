"""
Unit tests for CriticChange data model.
"""

import unittest
from editor.critic_change import CriticChange, ChangeType, ChangeStatus


class TestCriticChange(unittest.TestCase):
    """Test cases for CriticChange class."""

    def test_addition_display_text(self) -> None:
        """Test display text for addition."""
        change = CriticChange(
            change_type=ChangeType.ADDITION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            new_text="added text"
        )
        self.assertEqual(change.get_display_text(), "added text")

    def test_deletion_display_text(self) -> None:
        """Test display text for deletion."""
        change = CriticChange(
            change_type=ChangeType.DELETION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="deleted text"
        )
        self.assertEqual(change.get_display_text(), "deleted text")

    def test_substitution_display_text(self) -> None:
        """Test display text for substitution."""
        change = CriticChange(
            change_type=ChangeType.SUBSTITUTION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="old",
            new_text="new"
        )
        self.assertEqual(change.get_display_text(), "old → new")

    def test_addition_accepted_text(self) -> None:
        """Test accepted text for addition."""
        change = CriticChange(
            change_type=ChangeType.ADDITION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            new_text="added text"
        )
        self.assertEqual(change.get_accepted_text(), "added text")

    def test_deletion_accepted_text(self) -> None:
        """Test accepted text for deletion (should be empty)."""
        change = CriticChange(
            change_type=ChangeType.DELETION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="deleted text"
        )
        self.assertEqual(change.get_accepted_text(), "")

    def test_substitution_accepted_text(self) -> None:
        """Test accepted text for substitution (should be new text)."""
        change = CriticChange(
            change_type=ChangeType.SUBSTITUTION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="old",
            new_text="new"
        )
        self.assertEqual(change.get_accepted_text(), "new")

    def test_addition_rejected_text(self) -> None:
        """Test rejected text for addition (should be empty)."""
        change = CriticChange(
            change_type=ChangeType.ADDITION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            new_text="added text"
        )
        self.assertEqual(change.get_rejected_text(), "")

    def test_deletion_rejected_text(self) -> None:
        """Test rejected text for deletion (should be old text)."""
        change = CriticChange(
            change_type=ChangeType.DELETION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="deleted text"
        )
        self.assertEqual(change.get_rejected_text(), "deleted text")

    def test_substitution_rejected_text(self) -> None:
        """Test rejected text for substitution (should be old text)."""
        change = CriticChange(
            change_type=ChangeType.SUBSTITUTION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            old_text="old",
            new_text="new"
        )
        self.assertEqual(change.get_rejected_text(), "old")

    def test_default_status(self) -> None:
        """Test that default status is PENDING."""
        change = CriticChange(
            change_type=ChangeType.ADDITION,
            line_number=1,
            start_pos=0,
            end_pos=10,
            new_text="text"
        )
        self.assertEqual(change.status, ChangeStatus.PENDING)

    def test_color_codes(self) -> None:
        """Test that each change type has a color."""
        addition = CriticChange(
            change_type=ChangeType.ADDITION,
            line_number=1,
            start_pos=0,
            end_pos=10
        )
        self.assertEqual(addition.get_color(), "#d4edda")

        deletion = CriticChange(
            change_type=ChangeType.DELETION,
            line_number=1,
            start_pos=0,
            end_pos=10
        )
        self.assertEqual(deletion.get_color(), "#f8d7da")


if __name__ == '__main__':
    unittest.main()
