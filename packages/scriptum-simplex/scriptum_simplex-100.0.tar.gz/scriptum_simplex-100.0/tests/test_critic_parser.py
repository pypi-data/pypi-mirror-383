"""
Unit tests for CriticParser.
"""

import unittest
from editor.critic_parser import CriticParser
from editor.critic_change import ChangeType, ChangeStatus


class TestCriticParser(unittest.TestCase):
    """Test cases for CriticParser class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = CriticParser()

    def test_parse_addition(self) -> None:
        """Test parsing addition markup."""
        text = "This is {++added text++} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, ChangeType.ADDITION)
        self.assertEqual(changes[0].new_text, "added text")
        self.assertEqual(changes[0].line_number, 1)
        self.assertEqual(changes[0].original_markup, "{++added text++}")

    def test_parse_deletion(self) -> None:
        """Test parsing deletion markup."""
        text = "This is {--deleted text--} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, ChangeType.DELETION)
        self.assertEqual(changes[0].old_text, "deleted text")
        self.assertEqual(changes[0].line_number, 1)

    def test_parse_substitution(self) -> None:
        """Test parsing substitution markup."""
        text = "This is {~~old text~>new text~~} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, ChangeType.SUBSTITUTION)
        self.assertEqual(changes[0].old_text, "old text")
        self.assertEqual(changes[0].new_text, "new text")
        self.assertEqual(changes[0].line_number, 1)

    def test_parse_comment(self) -> None:
        """Test parsing comment markup."""
        text = "This is {>>a comment<<} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, ChangeType.COMMENT)
        self.assertEqual(changes[0].comment_text, "a comment")
        self.assertEqual(changes[0].line_number, 1)

    def test_parse_highlight(self) -> None:
        """Test parsing highlight markup."""
        text = "This is {==highlighted text==} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, ChangeType.HIGHLIGHT)
        self.assertEqual(changes[0].new_text, "highlighted text")
        self.assertEqual(changes[0].line_number, 1)

    def test_parse_multiple_changes(self) -> None:
        """Test parsing multiple changes."""
        text = "This {++is++} a {--test--} document with {~~old~>new~~} changes."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[0].change_type, ChangeType.ADDITION)
        self.assertEqual(changes[1].change_type, ChangeType.DELETION)
        self.assertEqual(changes[2].change_type, ChangeType.SUBSTITUTION)

    def test_parse_multiline(self) -> None:
        """Test parsing changes across multiple lines."""
        text = "Line 1\nLine 2 with {++addition++}\nLine 3 with {--deletion--}"
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0].line_number, 2)
        self.assertEqual(changes[1].line_number, 3)

    def test_parse_empty_text(self) -> None:
        """Test parsing empty text."""
        text = ""
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 0)

    def test_parse_no_changes(self) -> None:
        """Test parsing text with no CriticMarkup."""
        text = "This is plain text with no markup."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 0)

    def test_changes_sorted_by_position(self) -> None:
        """Test that changes are sorted by position."""
        text = "End {--last--} middle {++second++} start {~~first~>1st~~}"
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 3)
        # Should be sorted by start position
        self.assertLess(changes[0].start_pos, changes[1].start_pos)
        self.assertLess(changes[1].start_pos, changes[2].start_pos)

    def test_default_status_is_pending(self) -> None:
        """Test that parsed changes have PENDING status."""
        text = "This is {++added text++} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(changes[0].status, ChangeStatus.PENDING)

    def test_multiline_change(self) -> None:
        """Test parsing a change that spans multiple lines."""
        text = "This is {++a change\nthat spans\nmultiple lines++} in the document."
        changes = self.parser.parse(text)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].new_text, "a change\nthat spans\nmultiple lines")
        self.assertEqual(changes[0].line_number, 1)


if __name__ == '__main__':
    unittest.main()
