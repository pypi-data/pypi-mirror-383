#!/usr/bin/env python3
"""CLI entry point for inka-clean."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .parser import InkaParser


def main() -> int:
    """
    Main CLI entry point.

    Reads markdown from stdin or file, removes inka2 metadata,
    and writes cleaned content to stdout.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        prog="inka-clean",
        description="Remove inka2 metadata from markdown files while preserving content",
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Input markdown file (default: read from stdin)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output to stderr",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.file:
            if not args.file.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                return 1

            if args.verbose:
                print(f"Processing file: {args.file}", file=sys.stderr)

            content = args.file.read_text(encoding="utf-8")
        else:
            if args.verbose:
                print("Reading from stdin...", file=sys.stderr)

            content = sys.stdin.read()

        # Process
        inka_parser = InkaParser()
        result = inka_parser.parse(content)

        # Write output to stdout
        sys.stdout.write(result)

        if args.verbose:
            print("Processing complete", file=sys.stderr)

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
