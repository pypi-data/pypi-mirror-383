"""
alea_markdown.base - Base modules and abstract classes for HTML to Markdown conversion

This package provides the foundational classes and interfaces for HTML to
Markdown conversion, including parsers, configuration, and type definitions.
"""

from alea_markdown.base.parser import HTMLToMarkdownParser
from alea_markdown.base.parser_config import (
    ParserConfig,
    ParserType,
    MarkdownStyle,
    get_default_config,
    create_github_flavored_config,
    create_commonmark_config,
)
from alea_markdown.base.html_types import HTMLElement, HTMLDocument
from alea_markdown.base.markdown_types import (
    MarkdownDocument,
    BlockElement,
    InlineElement,
)

from alea_markdown.logger import get_logger

# Module logger
logger = get_logger(__name__)

__all__ = [
    "HTMLToMarkdownParser",
    "ParserConfig",
    "ParserType",
    "MarkdownStyle",
    "get_default_config",
    "create_github_flavored_config",
    "create_commonmark_config",
    "HTMLElement",
    "HTMLDocument",
    "MarkdownDocument",
    "BlockElement",
    "InlineElement",
]
