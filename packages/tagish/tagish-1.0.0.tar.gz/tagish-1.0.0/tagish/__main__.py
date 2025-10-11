#!/usr/bin/env python3
"""
tagish CLI tool

Usage:
    tagish <path>                    # Convert json/toml to tagish format
    tagish <path> --format <format>  # Convert tagish to json/toml format


This module only handle cli in/out, and uses the api.py module for the acutual work. Testing should, hence be done only to verify that the cli can parse a program strings and calls the right functions with the right arguments.
"""

import argparse
import sys
from pathlib import Path

from . import api as tagish


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert between tagish, JSON, and TOML formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tagish data.json              # Convert JSON to tagish format (output to stdout)
  tagish config.toml            # Convert TOML to tagish format (output to stdout)
  tagish data.tagish --format json    # Convert tagish to JSON (output to stdout)
  tagish data.tagish --format toml    # Convert tagish to TOML (not supported for output)
        """,
    )

    parser.add_argument(
        "path", type=Path, help="Input file path (json, toml, or tagish format)"
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "toml"],
        help="Output format (only used when converting FROM tagish TO other formats)",
    )

    parser.add_argument(
        "--no-indent", action="store_true", help="Disable pretty-printing/indentation"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.path.exists():
        print(f"Error: Input file '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        # Detect input format
        input_format = tagish.detect_format(args.path)

        # Determine conversion direction and output format
        if args.format:
            # Converting FROM tagish TO specified format
            if input_format != "tagish":
                print(
                    f"Error: --format can only be used with tagish input files, but input is {input_format}",
                    file=sys.stderr,
                )
                sys.exit(1)

            if args.format == "toml":
                print(
                    "Error: Converting to TOML format is not supported (TOML is read-only in Python stdlib)",
                    file=sys.stderr,
                )
                sys.exit(1)

            output_format = args.format
        else:
            # Converting TO tagish FROM json/toml
            if input_format == "tagish":
                print(
                    "Error: Input is already in tagish format. Use --format to convert to another format.",
                    file=sys.stderr,
                )
                sys.exit(1)
            output_format = "tagish"

        # Load data
        data = tagish.load_file(args.path, input_format)

        # Output data to stdout
        tagish.output_to_stdout(data, output_format, indent=not args.no_indent)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
