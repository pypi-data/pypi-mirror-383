"""Tests for inka_clean.heading_adjuster module."""

from inka_clean.heading_adjuster import HeadingAdjuster


class TestHeadingAdjustment:
    """Test heading level adjustment functionality."""

    def test_no_headings_in_content(self) -> None:
        """Content without headings should pass through unchanged."""
        content = "Just plain text\nwith no headings\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        assert result == content

    def test_adjust_h1_in_h2_context(self) -> None:
        """# should become ### when context is ## (level 2)."""
        content = "# Answer Heading\n\nSome content.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        assert result == "### Answer Heading\n\nSome content.\n"

    def test_adjust_h2_in_h2_context(self) -> None:
        """## should become #### when context is ## (level 2)."""
        content = "## Subheading\n\nContent.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        assert result == "#### Subheading\n\nContent.\n"

    def test_adjust_h3_in_h2_context(self) -> None:
        """### should become ##### when context is ## (level 2)."""
        content = "### Deeper\n\nContent.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        assert result == "##### Deeper\n\nContent.\n"

    def test_cap_at_h6(self) -> None:
        """Heading levels should cap at H6 (######)."""
        content = "#### Level 4\n\n##### Level 5\n\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=4)
        # context 4 + h4 = 8, capped at 6
        # context 4 + h5 = 9, capped at 6
        assert "###### Level 4" in result
        assert "###### Level 5" in result

    def test_context_h1(self) -> None:
        """When context is # (level 1), # in content becomes ##."""
        content = "# Answer\n\nText.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)
        assert result == "## Answer\n\nText.\n"

    def test_context_h3(self) -> None:
        """When context is ### (level 3), # becomes ####."""
        content = "# Title\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=3)
        assert result == "#### Title\n"

    def test_no_context_defaults_h2(self) -> None:
        """When context_level is 0, should default to H2 behavior."""
        content = "# Title\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=0)
        # 0 should default to 2 in the implementation
        assert result == "### Title\n"


class TestCodeBlockPreservation:
    """Test that code blocks are not modified."""

    def test_preserve_code_block_hashes(self) -> None:
        """Hashes inside code blocks should not be adjusted."""
        content = """Some text.

```python
# This is a comment
## Another comment
```

More text.
"""
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        # Code block content should be unchanged
        assert "# This is a comment" in result
        assert "## Another comment" in result

    def test_preserve_inline_code_hashes(self) -> None:
        """Hashes in inline code should not be adjusted."""
        content = "Use `#include` for C headers.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=2)
        assert result == content

    def test_multiple_code_blocks(self) -> None:
        """Multiple code blocks should all be preserved."""
        content = """# Real Heading

```
# Not a heading
```

## Another Heading

```bash
## Also not a heading
```
"""
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)

        # Real headings adjusted
        assert "## Real Heading" in result
        assert "### Another Heading" in result

        # Code blocks preserved
        assert "```\n# Not a heading\n```" in result
        assert "## Also not a heading" in result


class TestHeadingFormats:
    """Test various heading formats."""

    def test_atx_headings_only(self) -> None:
        """Only ATX-style headings (#) should be processed."""
        content = """# ATX Heading

Setext Heading
==============

Another ATX
-----------

This is not a setext heading because it has wrong format.
"""
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)

        # ATX heading should be adjusted
        assert "## ATX Heading" in result

        # Setext-style should be left alone (we only handle ATX)
        assert "==============" in result
        assert "-----------" in result

    def test_whitespace_preservation(self) -> None:
        """Whitespace after # should be preserved."""
        content = "#  Title with double space\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)
        # Should preserve the double space
        assert "##  Title with double space" in result

    def test_empty_heading_content(self) -> None:
        """Headings with no content should be handled."""
        content = "### \n\nSome text.\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)
        assert "#### \n" in result


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_multiple_sections_different_contexts(
        self, heading_hierarchy_file: str
    ) -> None:
        """Each inka section should have its own context."""
        # This test verifies the parser integrates correctly with heading adjuster
        from inka_clean.parser import InkaParser

        parser = InkaParser()
        result = parser.parse(heading_hierarchy_file)

        # The answer heading should be adjusted relative to "## Outer Heading"
        # Original: # Answer Heading
        # Context: level 2 (##)
        # Result: ### Answer Heading
        assert "### Answer Heading" in result
        assert "answer text" in result

    def test_nested_headings_in_inka_content(self) -> None:
        """Inka content with multiple heading levels."""
        content = """## Context

---
Deck: test

1. Question
> # Main
>
> Text
>
> ## Sub
>
> More text

---
"""
        from inka_clean.parser import InkaParser

        parser = InkaParser()
        result = parser.parse(content)

        # Context is level 2, so:
        # # Main -> ### Main
        # ## Sub -> #### Sub
        assert "### Main" in result
        assert "#### Sub" in result

    def test_heading_without_space(self) -> None:
        """#NoSpace should not be treated as heading."""
        content = "#NoSpace\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)
        # Should not be modified since it's not a valid ATX heading
        assert result == content

    def test_trailing_hashes(self) -> None:
        """Headings with trailing # should work."""
        content = "# Title #\n"
        adjuster = HeadingAdjuster()
        result = adjuster.adjust(content, context_level=1)
        assert "## Title #" in result
