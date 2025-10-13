"""
Integration tests for Critic Table workflow.

Tests that accept/reject buttons properly update the preview pane.
"""

import unittest
from editor.critic_parser import CriticParser
from editor.critic_change import ChangeStatus


class TestCriticWorkflow(unittest.TestCase):
    """Test the complete critic workflow."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.parser = CriticParser()
        self.sample_text = """# Test Document

This has {++an addition++} here.
This has {--a deletion--} here.
This has {~~old~>new~~} here.
"""

    def test_parse_sample_text(self) -> None:
        """Test that sample text is parsed correctly."""
        changes = self.parser.parse(self.sample_text)
        
        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[0].change_type.value, "Addition")
        self.assertEqual(changes[1].change_type.value, "Deletion")
        self.assertEqual(changes[2].change_type.value, "Substitution")

    def test_accept_addition(self) -> None:
        """Test that accepting an addition produces correct text."""
        changes = self.parser.parse(self.sample_text)
        addition = changes[0]
        
        # Accept the addition
        addition.status = ChangeStatus.ACCEPTED
        replacement = addition.get_accepted_text()
        
        self.assertEqual(replacement, "an addition")

    def test_reject_addition(self) -> None:
        """Test that rejecting an addition removes it."""
        changes = self.parser.parse(self.sample_text)
        addition = changes[0]
        
        # Reject the addition
        addition.status = ChangeStatus.REJECTED
        replacement = addition.get_rejected_text()
        
        self.assertEqual(replacement, "")

    def test_accept_deletion(self) -> None:
        """Test that accepting a deletion removes the text."""
        changes = self.parser.parse(self.sample_text)
        deletion = changes[1]
        
        # Accept the deletion
        deletion.status = ChangeStatus.ACCEPTED
        replacement = deletion.get_accepted_text()
        
        self.assertEqual(replacement, "")

    def test_reject_deletion(self) -> None:
        """Test that rejecting a deletion keeps the text."""
        changes = self.parser.parse(self.sample_text)
        deletion = changes[1]
        
        # Reject the deletion
        deletion.status = ChangeStatus.REJECTED
        replacement = deletion.get_rejected_text()
        
        self.assertEqual(replacement, "a deletion")

    def test_accept_substitution(self) -> None:
        """Test that accepting a substitution uses new text."""
        changes = self.parser.parse(self.sample_text)
        substitution = changes[2]
        
        # Accept the substitution
        substitution.status = ChangeStatus.ACCEPTED
        replacement = substitution.get_accepted_text()
        
        self.assertEqual(replacement, "new")

    def test_reject_substitution(self) -> None:
        """Test that rejecting a substitution keeps old text."""
        changes = self.parser.parse(self.sample_text)
        substitution = changes[2]
        
        # Reject the substitution
        substitution.status = ChangeStatus.REJECTED
        replacement = substitution.get_rejected_text()
        
        self.assertEqual(replacement, "old")

    def test_apply_changes_to_text(self) -> None:
        """Test applying accepted/rejected changes to text."""
        changes = self.parser.parse(self.sample_text)
        
        # Accept first change (addition)
        changes[0].status = ChangeStatus.ACCEPTED
        
        # Reject second change (deletion - keeps original)
        changes[1].status = ChangeStatus.REJECTED
        
        # Accept third change (substitution - uses new)
        changes[2].status = ChangeStatus.ACCEPTED
        
        # Apply changes in reverse order
        text = self.sample_text
        for change in sorted(changes, key=lambda c: c.start_pos, reverse=True):
            if change.status == ChangeStatus.ACCEPTED:
                replacement = change.get_accepted_text()
            elif change.status == ChangeStatus.REJECTED:
                replacement = change.get_rejected_text()
            else:
                continue
            
            text = text[:change.start_pos] + replacement + text[change.end_pos:]
        
        # Verify the text has been modified correctly
        self.assertIn("an addition", text)
        self.assertNotIn("{++", text)  # Markup should be removed
        self.assertIn("a deletion", text)  # Rejected deletion keeps text
        self.assertNotIn("{--", text)  # Markup should be removed
        self.assertIn("new", text)  # Accepted substitution uses new
        self.assertNotIn("old", text)  # Old text should be gone
        self.assertNotIn("{~~", text)  # Markup should be removed

    def test_pending_changes_remain_unchanged(self) -> None:
        """Test that pending changes are not modified."""
        changes = self.parser.parse(self.sample_text)
        
        # Leave all changes as PENDING
        text = self.sample_text
        for change in sorted(changes, key=lambda c: c.start_pos, reverse=True):
            if change.status == ChangeStatus.ACCEPTED:
                replacement = change.get_accepted_text()
            elif change.status == ChangeStatus.REJECTED:
                replacement = change.get_rejected_text()
            else:
                continue  # Skip pending
            
            text = text[:change.start_pos] + replacement + text[change.end_pos:]
        
        # Text should be unchanged since all are pending
        self.assertEqual(text, self.sample_text)


if __name__ == '__main__':
    unittest.main()
