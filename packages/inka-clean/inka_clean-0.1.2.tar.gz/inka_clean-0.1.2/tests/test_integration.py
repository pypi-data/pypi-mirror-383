"""Integration tests for inka-clean CLI."""

import pytest
import subprocess
import sys
from pathlib import Path


class TestCLI:
    """Test CLI functionality."""

    def test_stdin_stdout(self, tmp_path: Path) -> None:
        """Test reading from stdin and writing to stdout."""
        input_content = """---
Deck: test

1. Question
> Answer

---
"""
        # Run the CLI
        result = subprocess.run(
            [sys.executable, "-m", "inka_clean"],
            input=input_content,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Question" in result.stdout
        assert "Answer" in result.stdout
        assert "Deck:" not in result.stdout

    def test_file_argument(self, tmp_path: Path) -> None:
        """Test with file argument."""
        input_file = tmp_path / "input.md"
        input_file.write_text("""---
Deck: test

1. Q
> A

---
""")

        result = subprocess.run(
            [sys.executable, "-m", "inka_clean", str(input_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Q" in result.stdout
        assert "A" in result.stdout
        assert "Deck:" not in result.stdout

    def test_file_not_found(self) -> None:
        """Test error handling for non-existent file."""
        result = subprocess.run(
            [sys.executable, "-m", "inka_clean", "/nonexistent/file.md"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()

    def test_verbose_mode(self, tmp_path: Path) -> None:
        """Test verbose output to stderr."""
        input_file = tmp_path / "test.md"
        input_file.write_text("# Test\n")

        result = subprocess.run(
            [sys.executable, "-m", "inka_clean", "-v", str(input_file)],
            capture_output=True,
            text=True,
        )

        # Verbose should write something to stderr
        assert result.returncode == 0
        # stdout should still have the content
        assert "# Test" in result.stdout


class TestEncoding:
    """Test encoding handling."""

    def test_encoding_utf8(self, tmp_path: Path) -> None:
        """Test UTF-8 encoding with special characters."""
        content = """# Überschrift

---
Deck: test

1. Wie geht's?
> Gut, danke! 你好

---
"""
        input_file = tmp_path / "test.md"
        input_file.write_text(content, encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "inka_clean", str(input_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Überschrift" in result.stdout
        assert "Wie geht's?" in result.stdout
        assert "你好" in result.stdout


class TestLineEndings:
    """Test line ending handling."""

    def test_line_endings_unix(self) -> None:
        """Test Unix line endings (LF)."""
        content = "# Title\n\nContent\n"
        result = subprocess.run(
            [sys.executable, "-m", "inka_clean"],
            input=content,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Title" in result.stdout

    def test_line_endings_windows(self) -> None:
        """Test Windows line endings (CRLF)."""
        content = "# Title\r\n\r\nContent\r\n"
        result = subprocess.run(
            [sys.executable, "-m", "inka_clean"],
            input=content,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Title" in result.stdout


class TestPerformance:
    """Test performance with various file sizes."""

    @pytest.mark.benchmark
    def test_large_file_performance(self, tmp_path: Path, benchmark) -> None:
        """Test performance with large file (100KB)."""
        # Generate large file with multiple inka sections
        sections = []
        for i in range(100):
            section = f"""## Section {i}

Some content here.

---
Deck: test

1. Question {i}
> Answer {i}
> More answer text
> Even more

---

Regular content after section {i}.
"""
            sections.append(section)

        content = "\n".join(sections)
        input_file = tmp_path / "large.md"
        input_file.write_text(content)

        # Benchmark the parsing
        from inka_clean.parser import InkaParser

        parser = InkaParser()

        def parse_file():
            return parser.parse(content)

        result = benchmark(parse_file)

        # Verify correctness
        assert "Question 50" in result
        assert "Answer 50" in result
        assert "Deck:" not in result

        # Performance assertion - should be under 100ms (100000 microseconds)
        # benchmark.stats gives us mean in seconds
        assert benchmark.stats.stats.mean < 0.1  # 100ms in seconds

    def test_medium_file_performance(self, tmp_path: Path) -> None:
        """Test performance with medium file (10KB)."""
        sections = []
        for i in range(10):
            section = f"""## Section {i}

---
Deck: test

1. Q{i}
> A{i}

---
"""
            sections.append(section)

        content = "\n".join(sections)
        input_file = tmp_path / "medium.md"
        input_file.write_text(content)

        import time
        from inka_clean.parser import InkaParser

        parser = InkaParser()
        start = time.perf_counter()
        result = parser.parse(content)
        elapsed = time.perf_counter() - start

        assert "Q5" in result
        assert elapsed < 0.02  # 20ms


class TestRealWorldExample:
    """Test with actual real-world markdown structure."""

    def test_vim_example(self) -> None:
        """Test with the VIM example from requirements."""
        content = """# VIM
[vimscript](vimscript)

---
Deck: tools::vim
Tags: vim

<!--ID:1755681272665-->
1. how to format text paragraphs?
> `gq`
> `gqap` (current paragraph)

<!--ID:1729415293052-->
1. how to make markdown text bold (surround with \\**)?
> Visual selection and then Surround: `Sv`

<!--ID:1710004398276-->
1. How to jump to byte 128 in file?
> `:goto 128`
> `11|` (jump to column)

---

## Navigation
```vi
80|                     jump to horizontal position 80
10 k,j                  jump n lines up/down
```

### Bookmarks
```txt
ma, `a                  bookmark a/A, jump back
```
"""
        from inka_clean.parser import InkaParser

        parser = InkaParser()
        result = parser.parse(content)

        # Check metadata removed
        assert "Deck:" not in result
        assert "Tags:" not in result
        assert "<!--ID:" not in result

        # Check content preserved
        assert "how to format text paragraphs?" in result
        assert "`gq`" in result
        assert "`gqap`" in result
        assert "how to make markdown text bold" in result

        # Check structure preserved
        assert "## Navigation" in result
        assert "### Bookmarks" in result
        assert "```vi" in result

        # Check prefixes removed
        assert not any(line.strip().startswith("1. how") for line in result.split("\n"))

    def test_heading_hierarchy_example(self) -> None:
        """Test the heading hierarchy example from requirements."""
        content = """## Outer Heading
bla bla

---
Deck: test
Tags: test

<!--ID:123-->
1. question
> # Answer Heading
>
> answer text

---

more markdown

### another heading
content here
"""
        from inka_clean.parser import InkaParser

        parser = InkaParser()
        result = parser.parse(content)

        # Check metadata removed
        assert "Deck:" not in result
        assert "---" not in result or result.count("---") == 0

        # Check heading adjusted: context is ##, so # becomes ###
        assert "### Answer Heading" in result

        # Check content preserved
        assert "question" in result
        assert "answer text" in result
        assert "## Outer Heading" in result
        assert "### another heading" in result
