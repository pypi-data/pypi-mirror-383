#!/usr/bin/env python3
"""
Command-line interface for alea-markdown-converter.
Converts HTML files to Markdown format.
"""

import argparse
import sys
from typing import Optional, Tuple

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType, MarkdownStyle
from alea_markdown.normalizer import NormalizerConfig


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert HTML to Markdown.", prog="alea-md"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert HTML to Markdown")

    input_group = convert_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "input",
        nargs="?",
        type=str,
        help="Input HTML file path",
    )
    input_group.add_argument(
        "--dir",
        type=str,
        help="Process all HTML files in the given directory",
    )

    output_group = convert_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output Markdown file path (or stdout if not specified)",
    )
    output_group.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for processed files (required with --dir)",
    )

    convert_parser.add_argument(
        "--parser",
        type=str,
        choices=["auto", "lxml", "markdownify", "regex"],
        default="auto",
        help="Parser to use (default: auto)",
    )

    convert_parser.add_argument(
        "--style",
        type=str,
        choices=["github", "commonmark", "standard"],
        default="github",
        help="Markdown style to use (default: github)",
    )

    convert_parser.add_argument(
        "--normalize",
        action="store_true",
        default=True,
        help="Apply markdown normalization (default: True)",
    )

    convert_parser.add_argument(
        "--no-normalize",
        action="store_false",
        dest="normalize",
        help="Disable markdown normalization",
    )

    convert_parser.add_argument(
        "--max-newlines",
        type=int,
        default=2,
        help="Maximum consecutive newlines in normalized output (default: 2)",
    )

    convert_parser.add_argument(
        "--small-size-threshold",
        type=int,
        default=128 * 1024,  # 128KB
        help="Size threshold in bytes for small files (below this: markdownify, above this: lxml) (default: 131072)",
    )

    convert_parser.add_argument(
        "--large-size-threshold",
        type=int,
        default=2048 * 1024,  # 2MB
        help="Size threshold in bytes for large files (below this: lxml, above this: regex) (default: 2097152)",
    )

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")

    # Global arguments
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Show version information and exit",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (INFO level)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (DEBUG level)",
    )

    return parser.parse_args()


def get_parser_type(parser_name: str) -> ParserType:
    """Convert parser name string to ParserType enum."""
    parser_map = {
        "auto": ParserType.AUTO,
        "lxml": ParserType.LXML,
        "markdownify": ParserType.MARKDOWNIFY,
        "regex": ParserType.REGEX,
    }
    return parser_map.get(parser_name.lower(), ParserType.AUTO)


def get_markdown_style(style_name: str) -> MarkdownStyle:
    """Convert style name string to MarkdownStyle enum."""
    style_map = {
        "github": MarkdownStyle.GITHUB,
        "commonmark": MarkdownStyle.COMMONMARK,
        "standard": MarkdownStyle.STANDARD,
    }
    return style_map.get(style_name.lower(), MarkdownStyle.GITHUB)


def read_input(input_path: Optional[str]) -> str:
    """Read HTML input from file or stdin."""
    if input_path:
        with open(input_path, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return sys.stdin.read()


def write_output(output_path: Optional[str], content: str) -> None:
    """Write Markdown output to file or stdout."""
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)
    else:
        sys.stdout.write(content)


def process_file(
    input_file: str,
    output_file: str,
    parser_config: ParserConfig,
    normalizer_config: Optional[NormalizerConfig],
) -> bool:
    """Process a single HTML file and convert to Markdown.

    Args:
        input_file: Path to input HTML file
        output_file: Path to output Markdown file
        parser_config: Parser configuration
        normalizer_config: Normalizer configuration

    Returns:
        bool: True if successful, False otherwise
    """
    from alea_markdown.logger import get_logger

    logger = get_logger("cli")

    try:
        # Read input file
        with open(input_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Parse HTML to Markdown
        parser = AutoParser(
            parser_config=parser_config, normalizer_config=normalizer_config
        )
        logger.info(f"Converting {input_file} to markdown...")
        markdown_content = parser.parse(html_content)

        # Ensure the output ends with a newline
        if markdown_content and not markdown_content.endswith("\n"):
            markdown_content += "\n"

        # Write output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.info(f"Successfully converted {input_file} to {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error processing {input_file}: {e}")
        return False


def process_directory(
    input_dir: str,
    output_dir: str,
    parser_config: ParserConfig,
    normalizer_config: Optional[NormalizerConfig],
) -> Tuple[int, int]:
    """Process all HTML files in a directory.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        parser_config: Parser configuration
        normalizer_config: Normalizer configuration

    Returns:
        Tuple[int, int]: (success_count, failure_count)
    """
    import os
    from alea_markdown.logger import get_logger

    logger = get_logger("cli")
    success_count = 0
    failure_count = 0

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all HTML files
    html_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith((".html", ".htm")):
                html_files.append(os.path.join(root, file))

    if not html_files:
        logger.warning(f"No HTML files found in {input_dir}")
        return 0, 0

    logger.info(f"Found {len(html_files)} HTML files to process")

    # Process each file
    for input_file in html_files:
        # Determine output path
        rel_path = os.path.relpath(input_file, input_dir)
        output_file = os.path.join(output_dir, rel_path)

        # Change extension to .md
        output_file = os.path.splitext(output_file)[0] + ".md"

        # Create output subdirectories if needed
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Process the file
        if process_file(input_file, output_file, parser_config, normalizer_config):
            success_count += 1
        else:
            failure_count += 1

    return success_count, failure_count


def main() -> int:
    """Main CLI entry point."""
    from alea_markdown import __version__
    from alea_markdown.logger import set_level, get_logger
    import logging

    args = parse_args()
    logger = get_logger("cli")

    # Handle version requests
    if args.version or getattr(args, "command", None) == "version":
        print(f"alea-markdown-converter {__version__}")
        return 0

    # Set logging level based on command line arguments
    if args.debug:
        set_level(logging.DEBUG)
    elif args.verbose:
        set_level(logging.INFO)
    else:
        set_level(logging.WARNING)

    # If no command was specified
    if getattr(args, "command", None) is None:
        print(
            "Error: No command specified. Use 'convert' or 'version'.", file=sys.stderr
        )
        return 1

    # Handle convert command
    if args.command == "convert":
        try:
            # Configure parser
            parser_type = get_parser_type(args.parser)
            markdown_style = get_markdown_style(args.style)
            parser_config = ParserConfig(
                parser_type=parser_type,
                markdown_style=markdown_style,
                small_size_threshold=args.small_size_threshold,
                large_size_threshold=args.large_size_threshold,
            )

            # Configure normalizer - either use default settings or disabled
            normalizer_config = None
            if args.normalize:
                normalizer_config = NormalizerConfig(
                    max_newlines=args.max_newlines,
                    trim_trailing_whitespace=True,
                    normalize_inline_spacing=True,
                    normalize_headings=True,
                    normalize_list_markers=True,
                )

            # Create parser instance and check if requested parser is available
            auto_parser = AutoParser(
                parser_config=parser_config, normalizer_config=normalizer_config
            )
            available_parsers = auto_parser.get_available_parsers()

            # Check if markdownify was explicitly requested but not available
            if (
                parser_type == ParserType.MARKDOWNIFY
                and "markdownify" not in available_parsers
            ):
                print(
                    "Error: markdownify parser was requested but is not available.",
                    file=sys.stderr,
                )
                print(
                    "To use markdownify, install with: pip install alea-markdown-converter[markdownify]",
                    file=sys.stderr,
                )
                return 1

            # Process directory if specified
            if args.dir:
                if not args.output_dir:
                    print(
                        "Error: --output-dir is required when using --dir",
                        file=sys.stderr,
                    )
                    return 1

                success, failure = process_directory(
                    args.dir, args.output_dir, parser_config, normalizer_config
                )

                logger.info(
                    f"Processed {success + failure} files: {success} succeeded, {failure} failed"
                )
                return 0 if failure == 0 else 1

            # Process single file
            else:
                # Read input
                html_content = read_input(args.input)

                # Parse HTML to Markdown
                markdown_content = auto_parser.parse(html_content)

                # Ensure the output ends with a newline
                if markdown_content and not markdown_content.endswith("\n"):
                    markdown_content += "\n"

                # Write output
                write_output(args.output, markdown_content)
                return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if args.debug:
                import traceback

                traceback.print_exc()
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
