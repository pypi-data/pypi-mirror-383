# inka-clean

Remove inka2 metadata from markdown files while preserving content and adjusting heading hierarchy.

## Overview

`inka-clean` is a Unix pipeline tool that processes markdown files containing [inka2](https://github.com/sysid/inka2) flashcard sections. It removes inka2 metadata (delimiters, deck/tag specifications, ID comments, question numbers, answer prefixes) while preserving the actual content and intelligently adjusting heading levels to fit the surrounding markdown hierarchy.

## Installation

```bash
uv tool install inka-clean
# or for development
cd inka-clean && make install
```

## Usage

As a Unix pipeline tool (stdin → stdout):

```bash
# Read from stdin, write to stdout
cat file.md | inka-clean > output.md

# Direct file redirection
inka-clean < input.md > output.md

# With file argument
inka-clean input.md > output.md

# Chain with other tools
cat file.md | inka-clean | pandoc -o output.html
```

## Example

**Input:**
```markdown
## Outer Heading
Some content.

---
Deck: tools::vim
Tags: vim

<!--ID:1755681272665-->
1. How to format text paragraphs?
> `gq`
> `gqap` (current paragraph)

---

### Another Heading
More content.
```

**Output:**
```markdown
## Outer Heading
Some content.

How to format text paragraphs?
`gq`
`gqap` (current paragraph)

### Another Heading
More content.
```

## Features

- **Metadata removal**: Strips `---` delimiters, `Deck:`, `Tags:`, `<!--ID:-->` comments
- **Prefix stripping**: Removes `1. ` question numbers and `> ` answer prefixes
- **Heading adjustment**: Adjusts heading levels in inka2 content relative to surrounding context
- **Edge case handling**: Preserves code blocks, regular ordered lists, blockquotes, thematic breaks
- **Performance**: < 20ms for typical files
- **Unix philosophy**: Pure stdin/stdout, composable with other tools

## Development

```bash
# Run tests (TDD)
make test

# Type check
make ty

# Lint and format
make lint
make format

# Run benchmarks
make bench
```

## License

MIT
# inka-clean
