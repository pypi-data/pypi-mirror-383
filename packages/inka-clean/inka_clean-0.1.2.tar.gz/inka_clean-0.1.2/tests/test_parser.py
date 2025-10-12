"""Tests for inka_clean.parser module."""

from inka_clean.parser import InkaParser


class TestParserBasics:
    """Test basic parsing functionality."""

    def test_parse_empty_input(self) -> None:
        """Empty input should return empty output."""
        parser = InkaParser()
        result = parser.parse("")
        assert result == ""

    def test_parse_no_inka_sections(self, no_inka_file: str) -> None:
        """Files without inka sections should pass through unchanged."""
        parser = InkaParser()
        result = parser.parse(no_inka_file)
        assert result == no_inka_file


class TestMetadataRemoval:
    """Test removal of inka2 metadata."""

    def test_strip_deck_metadata(self) -> None:
        """Deck: lines should be removed."""
        content = """---
Deck: test::deck
Tags: tag1

1. Question
> Answer

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "Deck:" not in result
        assert "Question" in result
        assert "Answer" in result

    def test_strip_tags_metadata(self) -> None:
        """Tags: lines should be removed."""
        content = """---
Deck: test
Tags: tag1 tag2 tag3

1. Question
> Answer

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "Tags:" not in result
        assert "tag1" not in result

    def test_strip_id_comments(self) -> None:
        """<!--ID:...--> comments should be removed."""
        content = """---
Deck: test

<!--ID:1755681272665-->
1. Question
> Answer

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "<!--ID:" not in result
        assert "1755681272665" not in result


class TestPrefixStripping:
    """Test removal of question numbers and answer prefixes."""

    def test_strip_question_numbers(self) -> None:
        """'1. ' prefix should be removed from questions."""
        content = """---
Deck: test

1. How to do something?
> Answer here

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "How to do something?" in result
        assert "1. How" not in result

    def test_strip_answer_prefix(self) -> None:
        """'> ' prefix should be removed from answers."""
        content = """---
Deck: test

1. Question
> Answer line 1
> Answer line 2

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "Answer line 1" in result
        assert "Answer line 2" in result
        # Check that > prefix is not present at start of line
        lines = result.strip().split("\n")
        answer_lines = [line for line in lines if "Answer line" in line]
        for line in answer_lines:
            assert not line.strip().startswith(">")


class TestMultipleSections:
    """Test handling of multiple inka sections."""

    def test_parse_single_inka_section(self, single_inka_file: str) -> None:
        """Single inka section should be processed correctly."""
        parser = InkaParser()
        result = parser.parse(single_inka_file)

        # Metadata should be removed
        assert "---" not in result or result.count("---") == 0
        assert "Deck:" not in result
        assert "Tags:" not in result
        assert "<!--ID:" not in result

        # Content should be preserved
        assert "how to format text paragraphs?" in result
        assert "`gq`" in result
        assert "Navigation" in result

    def test_parse_multiple_inka_sections(self) -> None:
        """Multiple inka sections should all be processed."""
        content = """# Title

---
Deck: deck1

1. Question 1
> Answer 1

---

## Section 2

---
Deck: deck2

2. Question 2
> Answer 2

---
"""
        parser = InkaParser()
        result = parser.parse(content)

        assert "Question 1" in result
        assert "Answer 1" in result
        assert "Question 2" in result
        assert "Answer 2" in result
        assert "Deck:" not in result


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_preserve_code_blocks_with_triple_dash(self, code_blocks_file: str) -> None:
        """Code blocks containing --- should be preserved."""
        parser = InkaParser()
        result = parser.parse(code_blocks_file)

        # Code block content should be preserved
        assert "```bash" in result
        assert "this should be preserved" in result

    def test_preserve_code_blocks_with_gt_prefix(self) -> None:
        """Code blocks with > characters should be preserved."""
        content = """# Test

```python
# Comment
> This is in code
```

Regular content.
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "> This is in code" in result

    def test_preserve_regular_ordered_lists(self, code_blocks_file: str) -> None:
        """Ordered lists outside inka sections should be preserved."""
        parser = InkaParser()
        result = parser.parse(code_blocks_file)

        # Regular lists should remain
        assert "1. This is a regular list" in result
        assert "2. Not inside inka section" in result

    def test_preserve_regular_blockquotes(self, code_blocks_file: str) -> None:
        """Blockquotes outside inka sections should be preserved."""
        parser = InkaParser()
        result = parser.parse(code_blocks_file)

        # Regular blockquotes should remain
        assert "> Regular blockquote" in result
        assert "> Should be preserved" in result

    def test_preserve_thematic_breaks(self, no_inka_file: str) -> None:
        """Thematic breaks (---) outside inka sections should be preserved."""
        parser = InkaParser()
        result = parser.parse(no_inka_file)

        # Regular --- should remain (not followed by Deck:/Tags:)
        assert "---" in result

    def test_handle_unclosed_section(self) -> None:
        """Unclosed inka section should be handled gracefully."""
        content = """# Title

---
Deck: test

1. Question
> Answer

No closing ---
"""
        parser = InkaParser()
        result = parser.parse(content)
        # Should not crash and should attempt to process
        assert isinstance(result, str)

    def test_multiline_answers(self) -> None:
        """Multi-line answers with > prefix should be handled."""
        content = """---
Deck: test

1. Question
> Line 1
> Line 2
> Line 3

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_cloze_deletions(self) -> None:
        """Cloze deletion syntax should be preserved."""
        content = """---
Deck: test

1. If it {{c1::looks like a duck}}, it is a {{c2::duck}}.

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "{{c1::looks like a duck}}" in result
        assert "{{c2::duck}}" in result

    def test_mixed_content(self) -> None:
        """Complex mix of inka and regular markdown should work."""
        content = """# Main

Regular paragraph.

1. Regular list
2. Another item

---
Deck: test

1. Inka question
> Inka answer

---

> Regular quote

## Section 2

More content.
"""
        parser = InkaParser()
        result = parser.parse(content)

        # Regular content preserved
        assert "Regular paragraph" in result
        assert "1. Regular list" in result
        assert "> Regular quote" in result

        # Inka content cleaned
        assert "Deck:" not in result
        assert "Inka question" in result
        assert "Inka answer" in result


class TestInkaDetection:
    """Test inka section detection logic."""

    def test_dash_line_without_deck_not_inka(self) -> None:
        """--- without Deck:/Tags: should not be treated as inka section."""
        content = """# Title

---

Regular content.
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "---" in result  # Should be preserved

    def test_dash_line_with_deck_is_inka(self) -> None:
        """--- followed by Deck: should be detected as inka section."""
        content = """---
Deck: test

1. Q
> A

---
"""
        parser = InkaParser()
        result = parser.parse(content)
        assert "---" not in result
        assert "Deck:" not in result
