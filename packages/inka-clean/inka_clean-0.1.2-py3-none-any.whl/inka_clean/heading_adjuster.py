"""Heading level adjustment for inka2 content."""

import re
from typing import Optional


class HeadingAdjuster:
    """Adjust markdown heading levels relative to context."""

    def adjust(self, content: str, context_level: int) -> str:
        """
        Adjust heading levels in content relative to context.

        Args:
            content: Markdown content with headings to adjust
            context_level: The heading level of the surrounding context (1-6)

        Returns:
            Content with adjusted heading levels
        """
        if context_level == 0:
            context_level = 2  # Default to H2

        lines = content.splitlines(keepends=True)
        code_block_ranges = self._find_code_blocks(lines)
        output = []

        for i, line in enumerate(lines):
            # Skip lines inside code blocks
            if self._is_in_code_block(i, code_block_ranges):
                output.append(line)
                continue

            # Check if line is a heading
            level = self._get_heading_level(line)
            if level is not None:
                # Adjust heading level (cap at H6)
                new_level = min(level + context_level, 6)
                adjusted = self._set_heading_level(line, new_level)
                output.append(adjusted)
            else:
                output.append(line)

        return "".join(output)

    def _find_code_blocks(self, lines: list[str]) -> list[tuple[int, int]]:
        """
        Find code block ranges in the content.

        Args:
            lines: List of content lines

        Returns:
            List of (start, end) line number tuples for code blocks
        """
        ranges = []
        in_block = False
        start = -1

        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                if in_block:
                    ranges.append((start, i))
                    in_block = False
                else:
                    start = i
                    in_block = True

        return ranges

    def _is_in_code_block(self, line_num: int, ranges: list[tuple[int, int]]) -> bool:
        """
        Check if a line number is inside a code block.

        Args:
            line_num: Line number to check
            ranges: List of code block ranges

        Returns:
            True if line is inside a code block
        """
        for start, end in ranges:
            if start <= line_num <= end:
                return True
        return False

    def _get_heading_level(self, line: str) -> Optional[int]:
        """
        Get ATX heading level from a line.

        Args:
            line: Line to check

        Returns:
            Heading level (1-6) or None if not a heading
        """
        match = re.match(r"^(#{1,6})\s", line)
        if match:
            return len(match.group(1))
        return None

    def _set_heading_level(self, line: str, level: int) -> str:
        """
        Set a line to a specific heading level.

        Args:
            line: Heading line to modify
            level: New heading level (1-6)

        Returns:
            Modified line with new heading level
        """
        match = re.match(r"^#{1,6}\s", line)
        if match:
            # Preserve everything after the initial hashes and space
            return "#" * level + line[match.end() - 1 :]
        return line
