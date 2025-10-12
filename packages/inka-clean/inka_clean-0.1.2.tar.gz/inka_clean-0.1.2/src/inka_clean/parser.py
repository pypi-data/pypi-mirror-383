"""Parser for removing inka2 metadata from markdown files."""

import re
from enum import Enum, auto
from typing import Optional

from .heading_adjuster import HeadingAdjuster


class State(Enum):
    """Parser states."""

    NORMAL = auto()
    IN_CODE_BLOCK = auto()
    IN_INKA_SECTION = auto()


class InkaParser:
    """Parse markdown and remove inka2 metadata while preserving content."""

    def __init__(self) -> None:
        """Initialize parser with heading adjuster."""
        self.heading_adjuster = HeadingAdjuster()

    def parse(self, content: str) -> str:
        """
        Parse markdown content and remove inka2 metadata.

        This is a single-pass state machine parser that:
        1. Tracks state (NORMAL, IN_CODE_BLOCK, IN_INKA_SECTION)
        2. Preserves code blocks and regular markdown
        3. Removes inka2 metadata from inka sections
        4. Adjusts heading levels in inka content

        Args:
            content: Markdown content to parse

        Returns:
            Cleaned markdown content
        """
        if not content:
            return ""

        lines = content.splitlines(keepends=True)
        output = []
        state = State.NORMAL
        current_heading_level = 0  # Track last seen heading level
        inka_buffer: list[str] = []
        inka_context_level = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Track code blocks (highest priority)
            if line.strip().startswith("```"):
                if state == State.IN_CODE_BLOCK:
                    state = State.NORMAL
                elif state == State.NORMAL:
                    state = State.IN_CODE_BLOCK
                output.append(line)
                i += 1
                continue

            # Inside code block - pass through unchanged
            if state == State.IN_CODE_BLOCK:
                output.append(line)
                i += 1
                continue

            # Track heading level in NORMAL state
            if state == State.NORMAL:
                level = self._get_heading_level(line)
                if level is not None:
                    current_heading_level = level

            # Detect inka section start
            if state == State.NORMAL and line.strip() == "---":
                if self._is_inka_section_start(lines, i):
                    state = State.IN_INKA_SECTION
                    inka_context_level = current_heading_level
                    inka_buffer = []
                    i += 1
                    continue
                else:
                    # Regular thematic break
                    output.append(line)
                    i += 1
                    continue

            # Process inka section content
            if state == State.IN_INKA_SECTION:
                if line.strip() == "---":
                    # End of section - process buffer
                    cleaned = self._clean_inka_content(inka_buffer)
                    if cleaned:  # Only add if there's content
                        adjusted = self.heading_adjuster.adjust(
                            cleaned, inka_context_level
                        )
                        output.append(adjusted)
                    state = State.NORMAL
                    i += 1
                    continue
                else:
                    # Buffer inka content
                    inka_buffer.append(line)
                    i += 1
                    continue

            # Normal state - pass through
            output.append(line)
            i += 1

        # Handle unclosed inka section
        if state == State.IN_INKA_SECTION and inka_buffer:
            cleaned = self._clean_inka_content(inka_buffer)
            if cleaned:
                adjusted = self.heading_adjuster.adjust(cleaned, inka_context_level)
                output.append(adjusted)

        return "".join(output)

    def _is_inka_section_start(self, lines: list[str], i: int) -> bool:
        """
        Check if a --- line starts an inka section.

        Args:
            lines: All content lines
            i: Index of the --- line

        Returns:
            True if this is an inka section start
        """
        # Look ahead for Deck:, Tags:, or <!--ID: patterns
        for offset in range(1, min(5, len(lines) - i)):
            line = lines[i + offset].strip()

            # Check for inka metadata
            if line.startswith("Deck:") or line.startswith("Tags:"):
                return True

            # Check for ID comment or numbered question
            if line.startswith("<!--ID:") or (
                line and line[0].isdigit() and ". " in line[:4]
            ):
                return True

            # Empty lines are ok, keep looking
            if not line:
                continue

            # Non-inka content found, this is not an inka section
            break

        return False

    def _clean_inka_content(self, lines: list[str]) -> str:
        """
        Remove metadata and prefixes from inka content.

        Args:
            lines: Lines from within an inka section

        Returns:
            Cleaned content string
        """
        cleaned = []

        for line in lines:
            stripped = line.strip()

            # Skip metadata lines
            if stripped.startswith("Deck:") or stripped.startswith("Tags:"):
                continue

            # Skip ID comments
            if stripped.startswith("<!--ID:") and stripped.endswith("-->"):
                continue

            # Skip empty lines at start
            if not cleaned and not stripped:
                continue

            # Handle answer prefix (> )
            if stripped.startswith(">"):
                # Remove > and optional space after it
                content = line.lstrip()
                if content.startswith("> "):
                    cleaned_line = content[2:]
                elif content.startswith(">"):
                    cleaned_line = content[1:]
                else:
                    cleaned_line = content
                cleaned.append(cleaned_line)
                continue

            # Handle question numbering (1. )
            if stripped and stripped[0].isdigit():
                # Check for number + period + space pattern
                match = re.match(r"^(\d+)\.\s+(.*)", stripped)
                if match:
                    cleaned.append(match.group(2) + "\n")
                    continue

            # Regular line - keep as is
            cleaned.append(line)

        return "".join(cleaned)

    def _get_heading_level(self, line: str) -> Optional[int]:
        """
        Get ATX heading level from a line.

        Args:
            line: Line to check

        Returns:
            Heading level (1-6) or None
        """
        match = re.match(r"^(#{1,6})\s", line)
        if match:
            return len(match.group(1))
        return None
