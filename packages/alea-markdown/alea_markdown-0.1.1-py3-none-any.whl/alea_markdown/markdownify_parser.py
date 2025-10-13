"""
alea_markdown.markdownify_parser - Wrapper for markdownify.markdownify to convert HTML to Markdown.

This module provides a wrapper for the markdownify library to convert HTML to Markdown.
It includes pre-processing to strip script and style tags using regular expressions.

This module requires the optional 'markdownify' dependency. To use it, install with:
pip install "alea-markdown-converter[markdownify]"
"""

# imports
try:
    import markdownify
except ImportError:
    raise ImportError(
        "The markdownify package is required for this module. "
        'Install it with: pip install "alea-markdown-converter[markdownify]"'
    )
import re
from typing import Optional, Dict, Any

# project imports
from alea_markdown.base.parser_config import ParserConfig
from alea_markdown.logger import get_logger


class MarkdownifyParser:
    """A wrapper for markdownify.markdownify to convert HTML to Markdown.

    This class wraps the markdownify.markdownify function to convert HTML to Markdown.
    It is not a subclass of HTMLToMarkdownParser since we're just providing a simple
    adapter to the markdownify library.
    """

    def __init__(self, config: ParserConfig = None) -> None:
        """Initialize the MarkdownifyParser.

        Args:
            config (ParserConfig, optional): Configuration options for the parser. Defaults to None.
        """
        self.config = config or ParserConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing %s", self.__class__.__name__)

    def _strip_tags_with_regex(self, html_str: str) -> str:
        """Strip script and style tags using regular expressions.

        Args:
            html_str (str): The HTML string to process

        Returns:
            str: The HTML string with script and style tags removed
        """
        # Strip script tags and their content
        html_str = re.sub(
            r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
            "",
            html_str,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Strip style tags and their content
        html_str = re.sub(
            r"<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>",
            "",
            html_str,
            flags=re.IGNORECASE | re.DOTALL,
        )

        return html_str

    def parse(self, html_str: str, **kwargs) -> Optional[str]:
        """Parse HTML string and convert it to Markdown.

        Args:
            html_str (str): The input HTML string to be parsed.
            **kwargs: Additional keyword arguments to pass to markdownify.markdownify.

        Returns:
            Optional[str]: The converted Markdown, or None if failed.
        """
        if not html_str or not html_str.strip():
            self.logger.warning("Empty HTML provided to markdownify parser")
            return ""

        self.logger.debug("Parsing HTML with markdownify (%s chars)", len(html_str))

        # Pre-process to strip script and style tags using regex
        original_size = len(html_str)
        html_str = self._strip_tags_with_regex(html_str)
        new_size = len(html_str)

        if original_size != new_size:
            self.logger.debug(
                "Stripped script/style tags with regex: %s -> %s chars (%s bytes removed)",
                original_size,
                new_size,
                original_size - new_size,
            )

        # Map our config options to markdownify options
        options: Dict[str, Any] = {
            # We've already stripped script and style tags with regex,
            # but set strip list for any additional tags to strip
            "strip": [] if self.config.preserve_comments else ["noscript", "meta"],
            # Strip whitespace pre and post
            # Output links unless disabled
            "convert_links": self.config.output_links,
            # Output images unless disabled
            "convert_img": self.config.output_images,
            # Heading style as ATX like other parsers
            "heading_style": "ATX",
        }

        # Add any additional options from kwargs (overriding defaults)
        options.update(kwargs)

        try:
            # Use markdownify.markdownify to do the conversion
            md_result = markdownify.markdownify(html_str, **options)
            return md_result
        except Exception as e:
            self.logger.error("Error parsing HTML with markdownify: %s", str(e))
            return None
