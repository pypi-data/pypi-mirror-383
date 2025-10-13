"""
CriticMarkup Parser

Extracts CriticMarkup changes from document text.
"""

import re
from typing import List
from .critic_change import CriticChange, ChangeType


class CriticParser:
    """Parser for extracting CriticMarkup changes from text."""

    def __init__(self) -> None:
        """Initialize the parser with regex patterns."""
        # Define patterns for each CriticMarkup element
        self.patterns = {
            ChangeType.ADDITION: re.compile(r'\{\+\+(.*?)\+\+\}', re.DOTALL),
            ChangeType.DELETION: re.compile(r'\{--(.*?)--\}', re.DOTALL),
            ChangeType.SUBSTITUTION: re.compile(r'\{~~(.*?)~>(.*?)~~\}', re.DOTALL),
            ChangeType.COMMENT: re.compile(r'\{>>(.*?)<<\}', re.DOTALL),
            ChangeType.HIGHLIGHT: re.compile(r'\{==(.*?)==\}', re.DOTALL),
        }

    def parse(self, text: str) -> List[CriticChange]:
        """
        Parse text and extract all CriticMarkup changes.

        Args:
            text: The document text to parse

        Returns:
            List of CriticChange objects, sorted by position
        """
        changes: List[CriticChange] = []

        # Process additions
        for match in self.patterns[ChangeType.ADDITION].finditer(text):
            change = self._create_change(
                text=text,
                match=match,
                change_type=ChangeType.ADDITION,
                new_text=match.group(1)
            )
            changes.append(change)

        # Process deletions
        for match in self.patterns[ChangeType.DELETION].finditer(text):
            change = self._create_change(
                text=text,
                match=match,
                change_type=ChangeType.DELETION,
                old_text=match.group(1)
            )
            changes.append(change)

        # Process substitutions
        for match in self.patterns[ChangeType.SUBSTITUTION].finditer(text):
            change = self._create_change(
                text=text,
                match=match,
                change_type=ChangeType.SUBSTITUTION,
                old_text=match.group(1),
                new_text=match.group(2)
            )
            changes.append(change)

        # Process comments
        for match in self.patterns[ChangeType.COMMENT].finditer(text):
            change = self._create_change(
                text=text,
                match=match,
                change_type=ChangeType.COMMENT,
                comment_text=match.group(1)
            )
            changes.append(change)

        # Process highlights
        for match in self.patterns[ChangeType.HIGHLIGHT].finditer(text):
            change = self._create_change(
                text=text,
                match=match,
                change_type=ChangeType.HIGHLIGHT,
                new_text=match.group(1)
            )
            changes.append(change)

        # Sort by position in document
        changes.sort(key=lambda c: c.start_pos)

        return changes

    def _create_change(
        self,
        text: str,
        match: re.Match[str],
        change_type: ChangeType,
        old_text: str = "",
        new_text: str = "",
        comment_text: str = ""
    ) -> CriticChange:
        """
        Create a CriticChange object from a regex match.

        Args:
            text: The full document text
            match: The regex match object
            change_type: Type of change
            old_text: Old text (for deletions/substitutions)
            new_text: New text (for additions/substitutions/highlights)
            comment_text: Comment text (for comments)

        Returns:
            CriticChange object
        """
        start_pos = match.start()
        end_pos = match.end()

        # Calculate line number (1-indexed)
        line_number = text[:start_pos].count('\n') + 1

        return CriticChange(
            change_type=change_type,
            line_number=line_number,
            start_pos=start_pos,
            end_pos=end_pos,
            old_text=old_text if old_text else None,
            new_text=new_text if new_text else None,
            comment_text=comment_text if comment_text else None,
            original_markup=match.group(0)
        )
