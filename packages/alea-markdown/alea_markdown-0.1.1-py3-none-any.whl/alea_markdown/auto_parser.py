"""
alea_markdown.auto_parser - AutoParser class for automatic HTML -> Markdown parsing.

This module defines the AutoParser class for automatically converting HTML to Markdown using a set of rules.
The AutoParser tries different parsers in sequence and uses the first successful one.
"""

# imports
import time
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Type, List

# project imports
from alea_markdown.base.parser import HTMLToMarkdownParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
from alea_markdown.normalizer import MarkdownNormalizer, NormalizerConfig

from alea_markdown.logger import get_logger

# Try to import parsers now for better error reporting
try:
    from alea_markdown.markdownify_parser import MarkdownifyParser
except ImportError:
    pass


class AutoParser:
    """Automatic HTML to Markdown parser, which handles detecting and applying the appropriate
    parser based on the input HTML content.

    This class attempts to parse HTML using multiple parsers in order of preference,
    falling back to the next parser if one fails. By default, it tries to use
    markdownify first, then lxml, and finally regex.
    """

    def __init__(
        self,
        parser_config: ParserConfig = None,
        normalizer_config: NormalizerConfig = None,
        *,
        config: ParserConfig = None,
    ) -> None:
        """Initialize the AutoParser.

        Args:
            parser_config (ParserConfig, optional): The parser configuration. Defaults to None.
            normalizer_config (NormalizerConfig, optional): The normalizer configuration. Defaults to None.
            config (ParserConfig, optional): Alias for parser_config for backward compatibility. Defaults to None.
        """
        # Support both parser_config and config parameters for backward compatibility
        actual_config = parser_config or config or ParserConfig()
        self.config = actual_config
        self.normalizer_config = normalizer_config or NormalizerConfig()
        self.normalizer = MarkdownNormalizer(self.normalizer_config)

        # Setup logger
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing %s", self.__class__.__name__)

        # Only log details at debug level
        if self.logger.isEnabledFor(10):  # DEBUG level is 10
            self.logger.debug(
                "Parser configuration: style=%s, sanitize=%s",
                self.config.markdown_style.value,
                self.config.sanitize_html,
            )
            self.logger.debug(
                "Normalizer configuration: max_newlines=%s, trim_trailing_whitespace=%s",
                self.normalizer_config.max_newlines,
                self.normalizer_config.trim_trailing_whitespace,
            )

        # Statistics for tracking parser performance
        self._stats: Dict[str, Any] = {
            "parse_time": 0,
            "parser_times": {},
            "successful_parser": None,
            "failed_parsers": [],
        }

        # Detected available parsers - initialize with known parser classes for performance
        self._available_parsers: Dict[str, Type[HTMLToMarkdownParser]] = {}
        self._detect_available_parsers()

        # Parser instances cache - only create parsers when needed
        self._parser_instances: Dict[str, HTMLToMarkdownParser] = {}

        # Validate include_tags and exclude_tags
        if self.config.include_tags and self.config.exclude_tags:
            self.logger.error(
                "Both include_tags and exclude_tags provided - this is not allowed"
            )
            raise ValueError(
                "Only one of include_tags or exclude_tags can be set, not both."
            )

        # Log configuration details only in debug mode
        if self.logger.isEnabledFor(10):  # DEBUG level is 10
            if self.config.include_tags:
                self.logger.debug(
                    "Using include_tags filter with %s tags",
                    len(self.config.include_tags),
                )
            if self.config.exclude_tags:
                self.logger.debug(
                    "Using exclude_tags filter with %s tags",
                    len(self.config.exclude_tags),
                )
            if self.config.simple_mode:
                self.logger.debug("Simple mode enabled")

    def _detect_available_parsers(self) -> None:
        """Detect available parsers for HTML to Markdown conversion."""
        self.logger.debug("Detecting available parsers")

        # Try to import markdownify parser
        try:
            from alea_markdown.markdownify_parser import MarkdownifyParser

            self._available_parsers["markdownify"] = MarkdownifyParser
            self.logger.debug("Markdownify parser available")
        except ImportError:
            self.logger.warning(
                "Markdownify parser not available (missing dependencies)"
            )

        # Try to import LXML parser
        try:
            from alea_markdown.lxml_parser import LXMLHTMLParser

            self._available_parsers["lxml"] = LXMLHTMLParser
            self.logger.debug("LXML parser available")
        except ImportError:
            self.logger.warning("LXML parser not available (missing dependencies)")

        # Try to import Regex parser
        try:
            from alea_markdown.regex_parser import RegexHTMLParser

            self._available_parsers["regex"] = RegexHTMLParser
            self.logger.debug("Regex parser available")
        except ImportError:
            self.logger.warning("Regex parser not available (missing dependencies)")

        # Only log at INFO if there's a problem
        if not self._available_parsers:
            self.logger.error(
                "No parsers available! HTML to Markdown conversion will fail."
            )
        else:
            self.logger.debug(
                "Detected %s available parsers: %s",
                len(self._available_parsers),
                ", ".join(self._available_parsers.keys()),
            )

    def parse(self, input_html: str, **kwargs) -> str:
        """Parse HTML string and convert it to Markdown.

        Args:
            input_html (str): The input HTML string to be parsed.
            kwargs: Additional keyword arguments for the parser.

        Returns:
            str: The converted Markdown string.

        Raises:
            ValueError: If the input HTML is invalid or cannot be parsed.
        """
        self.logger.debug("Parsing HTML content (%s chars)", len(input_html))
        start_time = time.time()

        # Reset statistics - only if debug is enabled to save performance
        if self.logger.isEnabledFor(10):  # DEBUG level is 10
            self._stats = {
                "parse_time": 0,
                "parser_times": {},
                "successful_parser": None,
                "failed_parsers": [],
            }

        if kwargs and self.logger.isEnabledFor(10):
            self.logger.debug("Additional parser kwargs: %s", kwargs)

        # Check for specific parser type in config - faster path
        if self.config.parser_type != ParserType.AUTO:
            parser_type = self.config.parser_type.value
            self.logger.debug("Using specified parser type: %s", parser_type)
            return self._try_specific_parser(parser_type, input_html, **kwargs)

        # Check the file size to determine default parser
        file_size = len(input_html)

        # Default parser orders based on file size
        small_file_parsers = ["markdownify", "lxml", "regex"]
        medium_file_parsers = ["lxml", "markdownify", "regex"]
        large_file_parsers = ["regex", "lxml", "markdownify"]

        # Adjust orders if markdownify is not available
        if "markdownify" not in self._available_parsers:
            small_file_parsers = ["lxml", "regex"]
            medium_file_parsers = ["lxml", "regex"]
            large_file_parsers = ["regex", "lxml"]

        # Use appropriate parser order based on file size
        if file_size < self.config.small_size_threshold:
            self.logger.debug(
                "Small file size (%s bytes, below %s bytes): using %s as default",
                file_size,
                self.config.small_size_threshold,
                small_file_parsers[0] if small_file_parsers else "no parser available",
            )
            parser_order = small_file_parsers

        # Use lxml for medium files (between small_size_threshold and large_size_threshold)
        elif file_size < self.config.large_size_threshold:
            self.logger.debug(
                "Medium file size (%s bytes, between %s and %s bytes): using %s as default",
                file_size,
                self.config.small_size_threshold,
                self.config.large_size_threshold,
                medium_file_parsers[0]
                if medium_file_parsers
                else "no parser available",
            )
            parser_order = medium_file_parsers

        # Use regex for large files (above large_size_threshold)
        else:
            self.logger.debug(
                "Large file size (%s bytes, above %s bytes): using %s as default",
                file_size,
                self.config.large_size_threshold,
                large_file_parsers[0] if large_file_parsers else "no parser available",
            )
            parser_order = large_file_parsers

        # Try each parser in order until one succeeds
        for parser_name in parser_order:
            if parser_name in self._available_parsers:
                try:
                    result = self._try_parser(parser_name, input_html, **kwargs)
                    if result:
                        # Only track stats if debug logging is enabled
                        if self.logger.isEnabledFor(10):
                            self._stats["successful_parser"] = parser_name
                            self._stats["parse_time"] = time.time() - start_time
                            self.logger.debug(
                                "Successfully parsed with %s parser in %.2f seconds",
                                parser_name,
                                self._stats["parser_times"].get(parser_name, 0),
                            )
                            self.logger.debug("Parse statistics: %s", self._stats)
                        return result
                except Exception as e:
                    if self.logger.isEnabledFor(10):
                        self._stats["failed_parsers"].append(parser_name)
                    self.logger.warning("%s parser failed: %s", parser_name, e)

        # If we get here, all parsers failed
        error_msg = "All parsers failed, unable to convert HTML to Markdown"
        self.logger.error(error_msg)
        if self.logger.isEnabledFor(10):
            self._stats["parse_time"] = time.time() - start_time
            self.logger.debug("Parse statistics: %s", self._stats)
        raise ValueError(error_msg)

    def _try_specific_parser(self, parser_type: str, input_html: str, **kwargs) -> str:
        """Try a specific parser based on configuration.

        Args:
            parser_type (str): The parser type to use
            input_html (str): The HTML content to parse
            **kwargs: Additional parser arguments

        Returns:
            str: The parsed Markdown content

        Raises:
            ValueError: If the parser is not available or fails
        """
        # Check if the specified parser is available
        if parser_type not in self._available_parsers:
            error_msg = f"Specified parser '{parser_type}' is not available"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Try the specified parser
        result = self._try_parser(parser_type, input_html, **kwargs)
        if result:
            self.logger.debug(
                "Successfully parsed with specified %s parser", parser_type
            )
            return result

        error_msg = f"Specified parser '{parser_type}' failed to parse the HTML"
        self.logger.error(error_msg)
        raise ValueError(error_msg)

    def _try_parser(self, parser_name: str, input_html: str, **kwargs) -> Optional[str]:
        """Try parsing with a specific parser.

        Args:
            parser_name (str): The name of the parser to try
            input_html (str): The HTML content to parse
            **kwargs: Additional parser arguments

        Returns:
            Optional[str]: The parsed Markdown or None if parsing failed

        Raises:
            Exception: If the parser raises an exception
        """
        parser_class = self._available_parsers.get(parser_name)
        if not parser_class:
            self.logger.warning("Parser %s not available", parser_name)
            return None

        if self.logger.isEnabledFor(10):  # DEBUG level is 10
            self.logger.debug("Attempting to parse with %s parser", parser_name)

        parser_start_time = time.time()

        try:
            # Use cached parser instance if available, otherwise create a new one
            parser_instance = self._parser_instances.get(parser_name)
            if parser_instance is None:
                parser_instance = parser_class(self.config)
                self._parser_instances[parser_name] = parser_instance

            # Parse the HTML
            output = parser_instance.parse(input_html, **kwargs)

            # Check if output is valid
            if output is not None and output.strip():
                # Only track timing stats if debug logging is enabled
                if self.logger.isEnabledFor(10):
                    parser_time = time.time() - parser_start_time
                    self._stats["parser_times"][parser_name] = parser_time
                    self.logger.debug(
                        "%s parser succeeded in %.2f seconds", parser_name, parser_time
                    )

                # Apply normalization to the output
                normalized_output = self.normalizer.normalize(output.strip())

                # Always add a single final newline
                if not normalized_output.endswith("\n"):
                    normalized_output += "\n"

                if self.logger.isEnabledFor(10):
                    self.logger.debug(
                        "Normalized markdown from %s to %s chars",
                        len(output.strip()),
                        len(normalized_output),
                    )

                return normalized_output
            else:
                self.logger.warning("%s parser returned empty output", parser_name)
                return None

        except Exception as e:
            if self.logger.isEnabledFor(10):
                parser_time = time.time() - parser_start_time
                self._stats["parser_times"][parser_name] = parser_time
                self.logger.debug(traceback.format_exc())
            self.logger.error("Error parsing HTML with %s: %s", parser_name, e)
            raise

    def get_available_parsers(self) -> List[str]:
        """Get a list of available parser names.

        Returns:
            List[str]: List of available parser names
        """
        return list(self._available_parsers.keys())


# main method cli
if __name__ == "__main__":
    import argparse
    import sys

    # Setup root logger for CLI mode
    cli_logger = get_logger()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="AutoParser CLI")

    # Input/output paths
    parser.add_argument(
        "paths",
        type=Path,
        help="The path to the input HTML file, or input and output files",
        nargs="+",
    )

    # Parser selection
    parser.add_argument(
        "--parser",
        type=str,
        choices=["auto", "markdownify", "lxml", "regex"],
        default="auto",
        help="Parser to use (default: auto)",
    )

    # Simple mode
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple mode for parsing",
    )

    # Disable links
    parser.add_argument(
        "--disable-links",
        action="store_true",
        help="Disable links in the output Markdown",
    )

    # Disable images
    parser.add_argument(
        "--disable-images",
        action="store_true",
        help="Disable images in the output Markdown",
    )

    # Log level
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["debug", "info", "warning", "error"],
        default="info",
        help="Set logging level (default: info)",
    )

    args = parser.parse_args()

    # Set log level
    log_levels = {"debug": 10, "info": 20, "warning": 30, "error": 40}
    cli_logger.setLevel(log_levels[args.log_level])
    cli_logger.info("Log level set to %s", args.log_level.upper())

    try:
        # Map parser type argument to enum
        parser_type_map = {
            "auto": ParserType.AUTO,
            "markdownify": ParserType.MARKDOWNIFY,
            "lxml": ParserType.LXML,
            "regex": ParserType.REGEX,
        }

        # Create ParserConfig from arguments
        cli_logger.debug("Creating parser configuration")
        config = ParserConfig(
            parser_type=parser_type_map[args.parser],
            simple_mode=args.simple,
            output_links=not args.disable_links,
            output_images=not args.disable_images,
        )

        # Check if one or two paths provided
        if len(args.paths) == 1:
            cli_logger.debug("Reading input from %s", args.paths[0])
            html_str = args.paths[0].read_text(encoding="utf-8")
            args.output_path = None
        elif len(args.paths) == 2:
            cli_logger.debug("Reading input from %s", args.paths[0])
            html_str = args.paths[0].read_text(encoding="utf-8")
            args.output_path = args.paths[1]
            cli_logger.debug("Output will be written to %s", args.output_path)
        else:
            cli_logger.error("Invalid number of paths provided")
            raise ValueError(
                "Invalid number of paths provided. Please provide 1 or 2 paths."
            )

        # Create AutoParser
        cli_logger.debug("Initializing AutoParser")
        parser = AutoParser(parser_config=config)

        # Parse the input HTML
        cli_logger.info(
            "Parsing HTML file: %s (%s chars)", args.paths[0], len(html_str)
        )
        markdown_str = parser.parse(html_str)
        cli_logger.info(
            "Parsing complete, generated %s chars of Markdown", len(markdown_str)
        )

        # Write output markdown
        if args.output_path:
            cli_logger.info("Writing output to %s", args.output_path)
            args.output_path.write_text(markdown_str, encoding="utf-8")
            cli_logger.info("Conversion completed successfully")
        else:
            cli_logger.info("Writing output to stdout")
            print(markdown_str)

    except Exception as e:
        cli_logger.error("Error: %s", e)
        cli_logger.debug(traceback.format_exc())
        sys.exit(1)
