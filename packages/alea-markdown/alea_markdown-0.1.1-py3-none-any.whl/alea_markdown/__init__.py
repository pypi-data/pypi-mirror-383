"""
alea_markdown - HTML to Markdown conversion library

This package provides tools for converting HTML content to Markdown format
with configurable parsing options. It supports multiple parsing backends
and customizable conversion rules.

Usage:
    from alea_markdown import AutoParser

    parser = AutoParser()
    markdown = parser.parse_html("<html><body><p>Hello World!</p></body></html>")
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.lxml_parser import LXMLHTMLParser
from alea_markdown.regex_parser import RegexHTMLParser
from alea_markdown.base.parser import HTMLToMarkdownParser
from alea_markdown.base.parser_config import ParserConfig, MarkdownStyle, ParserType

__version__ = "0.1.1"
__author__ = "ALEA Institute <hello@aleainstitute.ai>"
__license__ = "MIT"
__maintainer__ = "ALEA Institute"
__email__ = "hello@aleainstitute.ai"
__all__ = [
    "AutoParser",
    "LXMLHTMLParser",
    "RegexHTMLParser",
    "HTMLToMarkdownParser",
    "ParserConfig",
    "MarkdownStyle",
    "ParserType",
]
