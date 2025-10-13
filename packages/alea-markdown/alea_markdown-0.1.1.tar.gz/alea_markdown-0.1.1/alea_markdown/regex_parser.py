"""
alea_markdown.regex_parser - RegexHTMLParser for converting HTML to Markdown.

This module contains the RegexHTMLParser class, which implements
the HTMLToMarkdownParser interface using regular expressions to
convert HTML to Markdown.
"""

# imports
import re
import time
import traceback
from typing import List, Dict, Any, Match, Tuple

# packages
from alea_markdown.logger import get_logger

# project
from alea_markdown.base.parser import HTMLToMarkdownParser
from alea_markdown.base.parser_config import ParserConfig, MarkdownStyle


class RegexHTMLParser(HTMLToMarkdownParser):
    """A regex-based HTML to Markdown parser.

    This class implements the HTMLToMarkdownParser interface using
    regular expressions to convert HTML to Markdown.
    """

    def __init__(self, config: ParserConfig = None) -> None:
        """Initialize the RegexHTMLParser.

        Args:
            config (ParserConfig, optional): Configuration for the parser.
                Defaults to None.
        """
        super().__init__(config)
        self.config = config or ParserConfig()

        # Set up class logger
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing %s", self.__class__.__name__)
        self.logger.debug(
            "Parser configuration: style=%s, sanitize=%s",
            self.config.markdown_style.value,
            self.config.sanitize_html,
        )

        # Statistics for tracking
        self._stats = self._create_empty_stats()

        # Compile regular expressions for better performance
        self._compile_regex_patterns()

    def _create_empty_stats(self) -> Dict[str, Any]:
        """Create empty statistics dictionary.

        Returns:
            Dict[str, Any]: Empty statistics dictionary.
        """
        return {
            "parse_time": 0,
            "pattern_matches": {},
            "warnings": 0,
            "conversion_counts": {},
        }

    def _truncate_preview(
        self, text: str, max_length: int = 30, replace_newlines: bool = False
    ) -> str:
        """Create a preview of text with ellipsis if needed.

        Args:
            text (str): Text to preview
            max_length (int, optional): Maximum length of preview. Defaults to 30.
            replace_newlines (bool, optional): Whether to replace newlines with \\n. Defaults to False.

        Returns:
            str: Truncated text preview.
        """
        if not text:
            return ""

        preview = text
        if replace_newlines:
            preview = preview.replace("\n", "\\n")

        if len(preview) > max_length:
            return preview[:max_length] + "..."
        return preview

    def _apply_markdown_style(self, content: str, style_type: str) -> str:
        """Apply Markdown style markers to content.

        Args:
            content (str): Content to style
            style_type (str): Style type (emphasis, strong, code_block, etc.)

        Returns:
            str: Content with style markers applied.
        """
        style_map = {
            "emphasis": "*"
            if self.config.markdown_style != MarkdownStyle.CUSTOM
            else self.config.custom_emphasis_style,
            "strong": "**"
            if self.config.markdown_style != MarkdownStyle.CUSTOM
            else self.config.custom_strong_style,
            "code_block": "```"
            if self.config.markdown_style != MarkdownStyle.CUSTOM
            else self.config.custom_code_block_style,
            "list_marker": "-"
            if self.config.markdown_style != MarkdownStyle.CUSTOM
            else self.config.custom_list_marker,
            "heading": "#"
            if self.config.markdown_style != MarkdownStyle.CUSTOM
            else self.config.custom_heading_style,
        }

        marker = style_map.get(style_type, "")

        if style_type in ["emphasis", "strong"]:
            return f"{marker}{content}{marker}"

        return marker

    def _compile_regex_patterns(self) -> None:
        """Compile regular expressions for better performance."""
        self.logger.debug("Compiling regular expression patterns")

        # Block-level patterns
        self.block_patterns = {
            "container": re.compile(
                r"<(article|section|div|span).*?>(.*?)</\1>", re.DOTALL
            ),
            "heading": re.compile(r"<h([1-6]).*?>(.*?)</h\1>", re.DOTALL),
            "paragraph": re.compile(r"<p.*?>(.*?)</p>", re.DOTALL),
            "list": re.compile(r"<(ul|ol).*?>(.*?)</\1>", re.DOTALL),
            "blockquote": re.compile(r"<blockquote.*?>(.*?)</blockquote>", re.DOTALL),
            "pre_code": re.compile(
                r"<pre\b[^>]*>\s*<code\b([^>]*)>(.*?)</code>\s*</pre>", re.DOTALL
            ),
            "pre_only": re.compile(
                r"<pre\b(?!.*<code\b)([^>]*)>(.*?)</pre>", re.DOTALL
            ),
            "hr": re.compile(r"<hr.*?>", re.DOTALL),
            "table": re.compile(r"<table.*?>(.*?)</table>", re.DOTALL),
            "definition_list": re.compile(r"<dl.*?>(.*?)</dl>", re.DOTALL),
        }

        # Inline patterns
        self.inline_patterns = {
            "link": re.compile(r'<a\s+href="(.*?)".*?>(.*?)</a>', re.DOTALL),
            "image": re.compile(r'<img\s+src="(.*?)"\s+alt="(.*?)".*?>', re.DOTALL),
            "emphasis": re.compile(r"<em.*?>(.*?)</em>", re.DOTALL),
            "strong": re.compile(r"<strong.*?>(.*?)</strong>", re.DOTALL),
            "inline_code": re.compile(
                r"<code\b(?!.*?</code>\s*</pre>).*?>(.*?)</code>", re.DOTALL
            ),
            "list_item": re.compile(r"<li.*?>(.*?)</li>", re.DOTALL),
            "table_row": re.compile(r"<tr.*?>(.*?)</tr>", re.DOTALL),
            "table_cell": re.compile(r"<t[hd].*?>(.*?)</t[hd]>", re.DOTALL),
            "dt": re.compile(r"<dt.*?>(.*?)</dt>", re.DOTALL),
            "dd": re.compile(r"<dd.*?>(.*?)</dd>", re.DOTALL),
        }

        # Other patterns
        self.other_patterns = {
            "html_tag": re.compile(r"<.*?>", re.DOTALL),
            "comment": re.compile(r"<!--.*?-->", re.DOTALL),
            "title": re.compile(
                r"<title[^>]*>(.*?)</title>", re.DOTALL | re.IGNORECASE
            ),
        }

        self.logger.debug(
            "Compiled %s block patterns, %s inline patterns, and %s other patterns",
            len(self.block_patterns),
            len(self.inline_patterns),
            len(self.other_patterns),
        )

    def parse(self, html_str: str, **kwargs) -> str:
        """Parse HTML and convert it to Markdown.

        Args:
            html_str (str): The HTML string to parse.
            **kwargs: Additional keyword arguments.

        Returns:
            str: The converted Markdown string.
        """
        self.logger.info("Parsing HTML content (%s chars)", len(html_str))
        start_time = time.time()

        # Reset statistics for this parse run
        self._stats = self._create_empty_stats()

        if kwargs:
            self.logger.debug("Additional parser kwargs: %s", kwargs)

        try:
            # Extract title before cleaning the HTML
            title = self._extract_title(html_str)

            # Remove comments
            html_str = self._remove_comments(html_str)

            # Always remove script and style tags
            html_str = self._remove_script_style_tags(html_str)

            # Strip other unwanted tags when simple_mode is True
            if self.config.simple_mode:
                html_str = self._strip_unwanted_tags(html_str)

            # Parse block elements
            self.logger.debug("Parsing block elements")
            blocks = self._parse_block_elements(html_str)
            self.logger.debug("Extracted %s Markdown blocks", len(blocks))

            # Add title as H1 header at the beginning if found
            if title:
                title_header = f"# {title}"

                # Check if first block is an H1 with the same content as the title
                duplicate_title = False
                if blocks and blocks[0].startswith("# "):
                    first_heading_content = blocks[0][2:].strip()
                    if first_heading_content == title:
                        self.logger.debug(
                            "Found duplicate title in H1, skipping title insertion"
                        )
                        duplicate_title = True

                if not duplicate_title:
                    self.logger.debug("Adding document title as H1: '%s'", title_header)
                    blocks.insert(0, title_header)

            # Join blocks with double newlines
            result = "\n\n".join(blocks)

            # Log statistics
            self._log_parse_stats(start_time, result)

            return result

        except Exception as e:
            traceback_string = traceback.format_exc()
            self.logger.error("Error parsing HTML: %s", e)
            self.logger.debug("Error details: %s", traceback_string)
            raise

    def _remove_comments(self, html_str: str) -> str:
        """Remove HTML comments from the input string.

        Args:
            html_str (str): HTML string with comments.

        Returns:
            str: HTML string without comments.
        """
        self.logger.debug("Removing HTML comments")
        html_without_comments = self.other_patterns["comment"].sub("", html_str)
        comment_count = len(html_str) - len(html_without_comments)
        if comment_count > 0:
            self.logger.debug(
                "Removed approximately %s characters of comments", comment_count
            )
        return html_without_comments

    def _extract_title(self, html_str: str) -> str:
        """Extract the title from the HTML document.

        Args:
            html_str (str): HTML string.

        Returns:
            str: The document title or empty string if no title found.
        """
        self.logger.debug("Extracting document title")
        title_match = self.other_patterns["title"].search(html_str)

        if not title_match:
            self.logger.debug("No title tag found in document")
            return ""

        # Get the title content
        title = title_match.group(1).strip()

        if not title:
            self.logger.debug("Found empty title tag")
            return ""

        # Clean title of any HTML tags
        title = self.other_patterns["html_tag"].sub("", title)

        # Unescape HTML entities in the title
        title = self._unescape_html_entities(title)

        self.logger.debug("Found document title: '%s'", title)
        return title

    def _remove_script_style_tags(self, html_str: str) -> str:
        """Remove script and style tags from HTML.

        Args:
            html_str (str): Original HTML string.

        Returns:
            str: HTML string without script and style tags.
        """
        self.logger.debug("Removing script and style tags")
        script_style_tags = ["script", "style"]
        self.logger.debug("Removing tags: %s", ", ".join(script_style_tags))

        orig_len = len(html_str)
        for tag in script_style_tags:
            pattern = re.compile(f"<{tag}.*?</{tag}>", re.DOTALL | re.IGNORECASE)
            html_str = pattern.sub("", html_str)

        cleaned_len = len(html_str)
        removed_chars = orig_len - cleaned_len
        if removed_chars > 0:
            self.logger.debug(
                "Removed %s characters of script and style tags", removed_chars
            )
        return html_str

    def _strip_unwanted_tags(self, html_str: str) -> str:
        """Strip unwanted tags from HTML in simple mode.

        Args:
            html_str (str): Original HTML string.

        Returns:
            str: Cleaned HTML string.
        """
        self.logger.debug("Simple mode enabled, removing unwanted tags")
        unwanted_tags = [
            "noscript",
            "head",
            "meta",
            "link",
            "title",
            "iframe",
        ]
        # Note: script and style tags are already removed by _remove_script_style_tags
        self.logger.debug("Removing tags: %s", ", ".join(unwanted_tags))

        orig_len = len(html_str)
        for tag in unwanted_tags:
            pattern = re.compile(f"<{tag}.*?</{tag}>", re.DOTALL | re.IGNORECASE)
            html_str = pattern.sub("", html_str)

        cleaned_len = len(html_str)
        removed_chars = orig_len - cleaned_len
        self.logger.debug("Removed %s characters of unwanted tags", removed_chars)
        return html_str

    def _log_parse_stats(self, start_time: float, result: str) -> None:
        """Log statistics after parsing.

        Args:
            start_time (float): Parsing start time.
            result (str): Parsed Markdown result.
        """
        self._stats["parse_time"] = time.time() - start_time
        self.logger.info(
            "HTML parsing completed in %.2f seconds", self._stats["parse_time"]
        )
        self.logger.debug(
            "Pattern match statistics: %s", self._stats["pattern_matches"]
        )
        self.logger.debug("Conversion counts: %s", self._stats["conversion_counts"])
        self.logger.debug("Output Markdown length: %s chars", len(result))

        if self._stats["warnings"] > 0:
            self.logger.warning("Completed with %s warnings", self._stats["warnings"])

    def _parse_block_elements(self, html: str) -> List[str]:
        """Parse block elements from HTML.

        Args:
            html (str): The HTML string to parse.

        Returns:
            List[str]: A list of parsed Markdown blocks in their original document order.
        """
        self.logger.debug("Starting block element parsing")

        # Initialize pattern match tracking
        for pattern_name in self.block_patterns:
            if pattern_name not in self._stats["pattern_matches"]:
                self._stats["pattern_matches"][pattern_name] = 0

            if pattern_name not in self._stats["conversion_counts"]:
                self._stats["conversion_counts"][pattern_name] = 0

        # Map block types to their handler methods
        block_handlers = {
            "container": self._handle_container,
            "heading": self._handle_heading,
            "paragraph": self._handle_paragraph,
            "list": self._handle_list,
            "blockquote": self._handle_blockquote,
            "pre_code": self._handle_pre_code,
            "pre_only": self._handle_pre_only,
            "hr": self._handle_horizontal_rule,
            "table": self._handle_table,
            "definition_list": self._handle_definition_list,
        }

        # Create a list to store all block elements with their positions
        all_blocks = []

        # Find all block elements with their positions
        for block_type, pattern in self.block_patterns.items():
            self.logger.debug("Searching for %s elements", block_type)
            # Use finditer to get positions of matches
            for match in pattern.finditer(html):
                start_pos = match.start()
                match_text = match.group(0)
                all_blocks.append((start_pos, block_type, match.groups(), match_text))

            # Update statistics
            matches_count = len([b for b in all_blocks if b[1] == block_type])
            self._stats["pattern_matches"][block_type] = matches_count
            if matches_count > 0:
                self.logger.debug("Found %s %s elements", matches_count, block_type)

        # Sort blocks by their position in the HTML
        all_blocks.sort(key=lambda x: x[0])
        self.logger.debug("Found %s total block elements", len(all_blocks))

        # Process blocks in order
        processed_blocks = []
        for i, (_, block_type, groups, original_match) in enumerate(all_blocks):
            handler = block_handlers.get(block_type)
            if not handler:
                self.logger.warning("No handler found for block type: %s", block_type)
                continue

            try:
                self.logger.debug(
                    "Processing %s element %s/%s", block_type, i + 1, len(all_blocks)
                )
                if block_type == "heading":
                    # Special case for headings which need the level parameter
                    level, content = groups
                    processed_block = handler((level, content), i, len(all_blocks))
                else:
                    # For other block types
                    processed_block = handler(
                        original_match if len(groups) == 0 else groups,
                        i,
                        len(all_blocks),
                    )

                if processed_block:
                    processed_blocks.append(processed_block)

                # Track successful conversions
                self._stats["conversion_counts"][block_type] += 1

            except Exception as e:
                self._stats["warnings"] += 1
                self.logger.error(
                    "Error converting %s element %s: %s", block_type, i + 1, e
                )
                self.logger.debug(
                    "Problematic content: %s...", str(original_match)[:100]
                )

        self.logger.debug(
            "Completed block element parsing, extracted %s blocks",
            len(processed_blocks),
        )
        return processed_blocks

    def _handle_container(self, match, *_) -> str:
        """Handle container element conversion.

        Args:
            match: Match with tag and content (tuple or string).

        Returns:
            str: Converted Markdown content.
        """
        if isinstance(match, tuple) and len(match) >= 2:
            tag, content = match
        else:
            # Extract container tag and content using regex if match is a string
            container_match = re.match(
                r"<(article|section|div|span).*?>(.*?)</\1>", match, re.DOTALL
            )
            if container_match:
                tag, content = container_match.groups()
            else:
                self.logger.warning("Invalid container match format")
                return ""

        # Skip container processing if it contains block elements that will be processed separately
        # This prevents duplication when containers (like div) have block elements that will be processed individually
        if tag in ["div", "section", "article", "span"]:
            block_patterns = [
                "<pre",
                "<h1",
                "<h2",
                "<h3",
                "<h4",
                "<h5",
                "<h6",
                "<ul",
                "<ol",
                "<dl",
                "<table",
                "<blockquote",
                "<p",
            ]

            # Advanced check: if any block pattern exists anywhere in the content
            if any(pattern in content for pattern in block_patterns):
                # Skip this container to avoid duplication
                self.logger.debug(
                    "Container <%s> contains block elements, skipping container processing",
                    tag,
                )
                return ""

            # Also skip if it's inside a pre tag, which will be handled separately
            # Fix: replaced html_str with content since html_str is undefined in this context
            if re.search(r"<pre\b.*?>.*?</" + tag + ">", content, re.DOTALL):
                self.logger.debug(
                    "Container <%s> is inside a pre tag, skipping container processing",
                    tag,
                )
                return ""

        self.logger.debug("Converting container <%s> (%s chars)", tag, len(content))
        return self._parse_inline_elements(content)

    def _handle_heading(self, match: Tuple[str, str], *_) -> str:
        """Handle heading element conversion.

        Args:
            match (Tuple[str, str]): Match with level and content.

        Returns:
            str: Converted Markdown heading.
        """
        level, content = match
        self.logger.debug("Converting h%s heading (%s chars)", level, len(content))
        return self._convert_headings(content, int(level))

    def _handle_paragraph(self, match, *_) -> str:
        """Handle paragraph element conversion.

        Args:
            match: Paragraph content (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown paragraph.
        """
        content = match[0] if isinstance(match, tuple) else match
        # Extract just the content if the whole tag was captured
        if content.startswith("<p"):
            content_match = re.match(r"<p.*?>(.*?)</p>", content, re.DOTALL)
            if content_match:
                content = content_match.group(1)

        content_preview = self._truncate_preview(content)
        self.logger.debug("Converting paragraph: %s", content_preview)
        return self._convert_paragraphs(content)

    def _handle_list(self, match, *_) -> str:
        """Handle list element conversion.

        Args:
            match: Match with list type and items (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown list.
        """
        if isinstance(match, tuple) and len(match) >= 2:
            list_type, items = match
        else:
            # Extract list type and items using regex if match is a string
            list_match = re.match(r"<(ul|ol).*?>(.*?)</\1>", match, re.DOTALL)
            if list_match:
                list_type, items = list_match.groups()
            else:
                self.logger.warning("Invalid list match format")
                return ""

        if items is None:
            self.logger.warning("List items are None, returning empty string")
            return ""

        self.logger.debug(
            "Converting %s list with %s items", list_type, items.count("<li")
        )
        return self._convert_lists(items, list_type)

    def _handle_blockquote(self, match, *_) -> str:
        """Handle blockquote element conversion.

        Args:
            match: Blockquote content (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown blockquote.
        """
        content = match[0] if isinstance(match, tuple) else match
        # Extract just the content if the whole tag was captured
        if content.startswith("<blockquote"):
            content_match = re.match(
                r"<blockquote.*?>(.*?)</blockquote>", content, re.DOTALL
            )
            if content_match:
                content = content_match.group(1)

        content_preview = self._truncate_preview(content, replace_newlines=True)
        self.logger.debug("Converting blockquote: %s", content_preview)
        return self._convert_blockquote(content)

    def _handle_pre_code(self, match, *_) -> str:
        """Handle <pre><code> combination for code blocks.

        Args:
            match: Code block content (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown code block.
        """
        if isinstance(match, tuple) and len(match) >= 2:
            attributes, content = match
        else:
            # Extract code attributes and content using regex if match is a string
            code_match = re.match(
                r"<pre\b[^>]*>\s*<code\b([^>]*)>(.*?)</code>\s*</pre>", match, re.DOTALL
            )
            if code_match:
                attributes, content = code_match.groups()
            else:
                self.logger.warning("Invalid pre-code block format")
                return ""

        content_preview = self._truncate_preview(content, replace_newlines=True)
        self.logger.debug("Converting pre-code block: %s", content_preview)

        # Extract language from attributes
        language = ""
        if attributes:
            lang_match = re.search(r'class="[^"]*language-(\w+)[^"]*"', attributes)
            if lang_match and self.config.code_language_class:
                language = lang_match.group(1)
                self.logger.debug("Detected code language: %s", language)

        # Clean up content - preserve whitespace but remove extra leading/trailing whitespace
        content = content.strip()

        # Unescape HTML entities in the code
        content = self._unescape_html_entities(content)

        # Apply code block style
        code_block_style = self._apply_markdown_style("", "code_block")

        # Format exactly as expected
        return f"{code_block_style}{language}\n{content}\n{code_block_style}"

    def _handle_pre_only(self, match, *_) -> str:
        """Handle <pre> tag without <code> tag conversion.

        Args:
            match: Pre tag content (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown code block.
        """
        if isinstance(match, tuple) and len(match) >= 2:
            attributes, content = match
        else:
            # Extract pre attributes and content using regex if match is a string
            pre_match = re.match(
                r"<pre\b(?!.*<code\b)([^>]*)>(.*?)</pre>", match, re.DOTALL
            )
            if pre_match:
                attributes, content = pre_match.groups()
            else:
                self.logger.warning("Invalid pre tag format")
                return ""

        content_preview = self._truncate_preview(content, replace_newlines=True)
        self.logger.debug("Converting standalone pre tag: %s", content_preview)

        # Preserve whitespace but remove any leading/trailing extra line breaks
        content = content.strip()

        # Unescape HTML entities in the content
        content = self._unescape_html_entities(content)

        # Apply code block style
        code_block_style = self._apply_markdown_style("", "code_block")

        # Format exactly as expected
        return f"{code_block_style}\n{content}\n{code_block_style}"

    def _handle_horizontal_rule(self, match, *_) -> str:
        """Handle horizontal rule element conversion.

        Args:
            match: Horizontal rule tag (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown horizontal rule.
        """
        self.logger.debug("Converting horizontal rule")
        return self._convert_horizontal_rule(match)

    def _handle_table(self, match, *_) -> str:
        """Handle table element conversion.

        Args:
            match: Table content (tuple or string).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown table.
        """
        content = match[0] if isinstance(match, tuple) else match
        # Extract just the content if the whole tag was captured
        if content.startswith("<table"):
            content_match = re.match(r"<table.*?>(.*?)</table>", content, re.DOTALL)
            if content_match:
                content = content_match.group(1)

        row_count = content.count("<tr")
        self.logger.debug("Converting table with %s rows", row_count)
        return self._convert_table(content)

    def _handle_definition_list(self, match, *_) -> str:
        """Handle definition list element conversion.

        Args:
            match: Definition list content (either a string or a tuple).
            total (int): Total number of elements.

        Returns:
            str: Converted Markdown definition list.
        """
        # Extract the content from the match
        content = match[0] if isinstance(match, tuple) else match
        self.logger.debug("Converting definition list")
        return self._convert_definition_list(content)

    def _convert_headings(self, element: str, level: int = None) -> str:
        """Convert HTML headings to Markdown.

        Args:
            element (str): The heading content.
            level (int, optional): The heading level (1-6). Defaults to None.

        Returns:
            str: The Markdown heading.
        """
        if level is None:
            level = 1

        content = self._parse_inline_elements(element)
        content_preview = self._truncate_preview(content)
        self.logger.debug("Converting h%s heading: '%s'", level, content_preview)

        heading_prefix = self._apply_markdown_style("", "heading") * level
        return f"{heading_prefix} {content}"

    def _convert_paragraphs(self, element: str) -> str:
        """Convert HTML paragraphs to Markdown.

        Args:
            element (str): The paragraph content.

        Returns:
            str: The Markdown paragraph.
        """
        content = self._parse_inline_elements(element)
        content_preview = self._truncate_preview(content)
        self.logger.debug("Converting paragraph content: '%s'", content_preview)
        return content

    def _convert_lists(self, items: str, list_type: str = None) -> str:
        """Convert HTML lists to Markdown.

        Args:
            items (str): The HTML list items.
            list_type (str, optional): The type of list ('ul' or 'ol'). Defaults to None.

        Returns:
            str: The Markdown list.
        """
        if not items:
            self.logger.warning("Empty list items, returning empty string")
            return ""

        list_items = self.inline_patterns["list_item"].findall(items)
        if not list_items:
            self.logger.warning("No list items found, returning empty string")
            return ""

        list_type_name = "ordered" if list_type == "ol" else "unordered"
        self.logger.debug(
            "Converting %s list with %s items", list_type_name, len(list_items)
        )

        converted_items = []
        for i, item in enumerate(list_items, 1):
            content = self._parse_inline_elements(item)
            content_preview = self._truncate_preview(content, 20)

            if list_type == "ol":
                self.logger.debug(
                    "Processing ordered list item %s: '%s'", i, content_preview
                )
                prefix = f"{i}. "
            else:
                prefix = f"{self._apply_markdown_style('', 'list_marker')} "
                self.logger.debug(
                    "Processing unordered list item %s: '%s'", i, content_preview
                )

            converted_items.append(f"{prefix}{content}")

        self.logger.debug(
            "List conversion complete, %s items converted", len(converted_items)
        )
        return "\n".join(converted_items)

    def _convert_blockquote(self, content: str) -> str:
        """Convert HTML blockquotes to Markdown.

        Args:
            content (str): The blockquote content.

        Returns:
            str: The Markdown blockquote.
        """
        parsed_content = self._parse_inline_elements(content)
        preview = self._truncate_preview(parsed_content, replace_newlines=True)
        self.logger.debug("Converting blockquote content: '%s'", preview)

        lines = parsed_content.split("\n")
        self.logger.debug("Blockquote has %s lines", len(lines))

        blockquote_lines = [f"> {line}" for line in lines]
        return "\n".join(blockquote_lines)

    def _convert_code(self, content: str) -> str:
        """Convert HTML code blocks to Markdown.

        Args:
            content (str): The code block content.

        Returns:
            str: The Markdown code block.
        """
        content_preview = self._truncate_preview(content, replace_newlines=True)
        self.logger.debug("Converting code block: '%s'", content_preview)

        # Check for language class
        lang = self._extract_code_language(content)

        # Apply code block style
        code_block_style = self._apply_markdown_style("", "code_block")

        return f"{code_block_style}{lang}\n{content}\n{code_block_style}"

    def _extract_code_language(self, content: str) -> str:
        """Extract language from code block content.

        Args:
            content (str): Code block content.

        Returns:
            str: Language identifier or empty string.
        """
        lang = ""
        lang_match = re.search(r'class="[^"]*language-(\w+)[^"]*"', content)
        if lang_match and self.config.code_language_class:
            lang = lang_match.group(1)
            self.logger.debug("Detected code language: %s", lang)

        return lang

    def _convert_horizontal_rule(self, _: str) -> str:
        """Convert HTML horizontal rules to Markdown.

        Args:
            _ (str): Unused parameter.

        Returns:
            str: The Markdown horizontal rule.
        """
        self.logger.debug("Converting horizontal rule")
        return "---"

    def _convert_table(self, content: str) -> str:
        """Convert HTML tables to Markdown.

        Args:
            content (str): The table content.

        Returns:
            str: The Markdown table.
        """
        if not self.config.table_support:
            self.logger.warning("Table conversion disabled in config, skipping table")
            self._stats["warnings"] += 1
            return ""

        # Extract table rows
        rows = self._extract_table_rows(content)
        if not rows:
            return ""

        # Process table rows
        return self._process_table_rows(rows)

    def _convert_definition_list(self, content: str) -> str:
        """Convert HTML definition lists to Markdown.

        Args:
            content (str): The definition list content.

        Returns:
            str: The Markdown definition list.
        """
        if not content:
            self.logger.warning("Empty definition list content, returning empty string")
            return ""

        # Find all dt and dd elements with their positions for sequential processing
        dt_pattern = r"<dt.*?>(.*?)</dt>"
        dd_pattern = r"<dd.*?>(.*?)</dd>"

        dt_matches = list(re.finditer(dt_pattern, content, re.DOTALL))
        dd_matches = list(re.finditer(dd_pattern, content, re.DOTALL))

        if not dt_matches:
            self.logger.warning("No definition terms found in the definition list")
            return ""

        self.logger.debug(
            "Found %s terms and %s descriptions", len(dt_matches), len(dd_matches)
        )

        # Process each term and its descriptions
        result = []

        # Group definitions with their terms based on order in the HTML
        for i, dt_match in enumerate(dt_matches):
            # Process term text
            term = dt_match.group(1)
            term_text = self._parse_inline_elements(term)
            term_preview = self._truncate_preview(term_text, 20)
            self.logger.debug(
                "Processing definition term %s: '%s'", i + 1, term_preview
            )

            # Add term to result
            result.append(term_text)

            # Find definitions that belong to this term (those before the next dt)
            dt_end_pos = dt_match.end()
            next_dt_start_pos = (
                dt_matches[i + 1].start() if i < len(dt_matches) - 1 else len(content)
            )

            # Get all dd elements between this dt and the next dt
            term_dds = [
                dd for dd in dd_matches if dt_end_pos < dd.start() < next_dt_start_pos
            ]

            if not term_dds:
                self.logger.warning("No descriptions found for term '%s'", term_preview)
                continue

            self.logger.debug(
                "Term '%s' has %s descriptions", term_preview, len(term_dds)
            )

            # Process each description
            for j, dd_match in enumerate(term_dds):
                desc = dd_match.group(1)
                desc_text = self._parse_inline_elements(desc)
                desc_preview = self._truncate_preview(desc_text, 30)
                self.logger.debug(
                    "Processing description %s: '%s'", j + 1, desc_preview
                )

                # Format using the colon style: term\n: definition
                result.append(f": {desc_text}")

            # Add a blank line between term-definition pairs
            if i < len(dt_matches) - 1:
                result.append("")

        return "\n".join(result)

    def _extract_table_rows(self, content: str) -> List[str]:
        """Extract rows from a table.

        Args:
            content (str): Table content.

        Returns:
            List[str]: List of table row strings.
        """
        # First check if table has structured sections
        has_thead = "<thead" in content
        has_tbody = "<tbody" in content
        has_tfoot = "<tfoot" in content

        self.logger.debug(
            "Table structure: thead=%s, tbody=%s, tfoot=%s",
            has_thead,
            has_tbody,
            has_tfoot,
        )

        rows = []

        # Extract rows in proper order: thead, tbody, tfoot
        if has_thead or has_tbody or has_tfoot:
            # Process in order: thead, tbody, tfoot
            if has_thead:
                thead_content = re.search(
                    r"<thead.*?>(.*?)</thead>", content, re.DOTALL
                )
                if thead_content:
                    thead_rows = self.inline_patterns["table_row"].findall(
                        thead_content.group(1)
                    )
                    self.logger.debug("Found %s rows in thead", len(thead_rows))
                    rows.extend(thead_rows)

            if has_tbody:
                tbody_content = re.search(
                    r"<tbody.*?>(.*?)</tbody>", content, re.DOTALL
                )
                if tbody_content:
                    tbody_rows = self.inline_patterns["table_row"].findall(
                        tbody_content.group(1)
                    )
                    self.logger.debug("Found %s rows in tbody", len(tbody_rows))
                    rows.extend(tbody_rows)

            if has_tfoot:
                tfoot_content = re.search(
                    r"<tfoot.*?>(.*?)</tfoot>", content, re.DOTALL
                )
                if tfoot_content:
                    tfoot_rows = self.inline_patterns["table_row"].findall(
                        tfoot_content.group(1)
                    )
                    self.logger.debug("Found %s rows in tfoot", len(tfoot_rows))
                    rows.extend(tfoot_rows)
        else:
            # Simple table without sections - extract all rows directly
            rows = self.inline_patterns["table_row"].findall(content)
            self.logger.debug("Found %s rows in simple table", len(rows))

        if not rows:
            self.logger.warning("Table has no rows, returning empty string")
            self._stats["warnings"] += 1
            return []

        self.logger.debug("Found %s total rows in table", len(rows))
        return rows

    def _process_table_rows(self, rows: List[str]) -> str:
        """Process table rows into Markdown format.

        Args:
            rows (List[str]): List of table row strings.

        Returns:
            str: Markdown table.
        """
        markdown_rows = []

        # Process each row
        for i, row in enumerate(rows):
            self.logger.debug("Processing table row %s/%s", i + 1, len(rows))
            cells = self.inline_patterns["table_cell"].findall(row)

            if not cells:
                self.logger.warning("Row %s has no cells, skipping", i + 1)
                self._stats["warnings"] += 1
                continue

            self.logger.debug("Row %s has %s cells", i + 1, len(cells))

            # Convert cell contents
            markdown_cells = []
            for j, cell in enumerate(cells):
                # Use a more selective approach for table cells to prevent duplication
                # Only convert basic inline elements without full recursive parsing
                cell_content = self._parse_table_cell_content(cell)
                preview = self._truncate_preview(cell_content, 15)
                self.logger.debug("Cell %s: '%s'", j + 1, preview)
                markdown_cells.append(cell_content)

            # Create row string
            formatted_row = "| " + " | ".join(markdown_cells) + " |"
            markdown_rows.append(formatted_row)

            # Add separator after header row
            if i == 0:
                self._add_table_separator(markdown_rows, len(cells))

        self.logger.debug(
            "Table conversion complete with %s rows (including separator)",
            len(markdown_rows),
        )
        return "\n".join(markdown_rows)

    def _add_table_separator(self, markdown_rows: List[str], num_cells: int) -> None:
        """Add table separator row after header.

        Args:
            markdown_rows (List[str]): Current list of markdown rows.
            num_cells (int): Number of cells in the header row.
        """
        self.logger.debug("Adding table separator row")
        separator = "| " + " | ".join(["---" for _ in range(num_cells)]) + " |"
        markdown_rows.append(separator)

    def _parse_inline_elements(self, html: str) -> str:
        """Parse inline elements from HTML.

        Args:
            html (str): The HTML string to parse.

        Returns:
            str: The parsed Markdown string.
        """
        self.logger.debug("Parsing inline elements (%s chars)", len(html))

        # Define inline element types and their processors
        inline_elements = [
            (
                "links",
                html.count("<a "),
                lambda h: self.inline_patterns["link"].sub(self._convert_links, h),
            ),
            (
                "images",
                html.count("<img "),
                lambda h: self.inline_patterns["image"].sub(self._convert_images, h),
            ),
            (
                "emphasis",
                html.count("<em"),
                lambda h: self.inline_patterns["emphasis"].sub(
                    self._convert_emphasis, h
                ),
            ),
            (
                "strong",
                html.count("<strong"),
                lambda h: self.inline_patterns["strong"].sub(self._convert_strong, h),
            ),
            (
                "inline code",
                # Count only code tags that aren't inside pre tags
                sum(1 for m in re.finditer(r"<code\b(?!.*?</code>\s*</pre>)", html)),
                lambda h: self.inline_patterns["inline_code"].sub(
                    self._convert_inline_code, h
                ),
            ),
        ]

        # Process each inline element type
        for element_type, count, processor in inline_elements:
            if count > 0:
                self.logger.debug(
                    "Processing %s elements (approx. %s)", element_type, count
                )
                html = processor(html)

        # Remove remaining HTML tags
        html = self._clean_remaining_html(html)

        # Unescape HTML entities
        html = self._unescape_html_entities(html)

        result = html.strip()
        self.logger.debug(
            "Inline elements parsing complete, result: %s chars", len(result)
        )
        return result

    def _clean_remaining_html(self, html: str) -> str:
        """Remove remaining HTML tags.

        Args:
            html (str): HTML with possible remaining tags.

        Returns:
            str: Cleaned text.
        """
        self.logger.debug("Removing remaining HTML tags")
        clean_html = self.other_patterns["html_tag"].sub("", html)
        tag_count = len(html) - len(clean_html)
        if tag_count > 0:
            self.logger.debug(
                "Removed approximately %s characters of HTML tags", tag_count
            )
        return clean_html

    def _convert_links(self, match: Match) -> str:
        """Convert HTML links to Markdown.

        Args:
            match (Match): The regex match object.

        Returns:
            str: The Markdown link.
        """
        href, content = match.groups()
        href_preview = self._truncate_preview(href)
        content_preview = self._truncate_preview(content, 20)

        self.logger.debug("Converting link: '%s' -> %s", content_preview, href_preview)

        if self.config.output_links:
            return f"[{content}]({href})"

        self.logger.debug("Link URLs disabled in config, returning link text only")
        return content

    def _convert_images(self, match: Match) -> str:
        """Convert HTML images to Markdown.

        Args:
            match (Match): The regex match object.

        Returns:
            str: The Markdown image.
        """
        src, alt = match.groups()
        src_preview = self._truncate_preview(src)
        alt_preview = self._truncate_preview(alt, 20)

        self.logger.debug("Converting image: %s (alt: %s)", src_preview, alt_preview)

        if self.config.output_images:
            return f"![{alt}]({src})"

        self.logger.debug("Image URLs disabled in config, returning alt text only")
        return alt

    def _convert_emphasis(self, match: Match) -> str:
        """Convert HTML emphasis to Markdown.

        Args:
            match (Match): The regex match object.

        Returns:
            str: The Markdown emphasis.
        """
        content = match.group(1)
        content_preview = self._truncate_preview(content, 20)
        self.logger.debug("Converting emphasis: '%s'", content_preview)
        return self._apply_markdown_style(content, "emphasis")

    def _convert_strong(self, match: Match) -> str:
        """Convert HTML strong to Markdown.

        Args:
            match (Match): The regex match object.

        Returns:
            str: The Markdown strong emphasis.
        """
        content = match.group(1)
        content_preview = self._truncate_preview(content, 20)
        self.logger.debug("Converting strong text: '%s'", content_preview)
        return self._apply_markdown_style(content, "strong")

    def _convert_inline_code(self, match: Match) -> str:
        """Convert HTML inline code to Markdown.

        Args:
            match (Match): The regex match object.

        Returns:
            str: The Markdown inline code.
        """
        content = match.group(1)
        content_preview = self._truncate_preview(content, 20)
        self.logger.debug("Converting inline code: '%s'", content_preview)
        return f"`{content}`"

    def _parse_table_cell_content(self, html: str) -> str:
        """Parse table cell content with a simplified approach to prevent duplication.

        This method selectively parses inline elements commonly found in table cells
        without the recursive nature that can lead to duplication.

        Args:
            html (str): The HTML content of a table cell.

        Returns:
            str: The parsed Markdown string for the table cell.
        """
        self.logger.debug("Parsing table cell content (%s chars)", len(html))

        # Special handling for list content within a cell
        if "<ul" in html or "<ol" in html:
            self.logger.debug("Table cell contains a list, preserving it")
            # For cells with lists, preserve the HTML format as in the expected output
            return html.strip()

        # Simplified inline processing - direct string operations without recursion
        # First clean any nested block elements that might cause duplication
        clean_html = html

        # Remove any nested tables or block elements that might get parsed twice
        block_patterns = [
            r"<table.*?</table>",
            r"<h[1-6].*?</h[1-6]>",
            r"<blockquote.*?</blockquote>",
        ]

        for pattern in block_patterns:
            clean_html = re.sub(pattern, "", clean_html, flags=re.DOTALL)

        # Now process basic inline elements directly
        # Links
        clean_html = self.inline_patterns["link"].sub(self._convert_links, clean_html)

        # Emphasis
        clean_html = self.inline_patterns["emphasis"].sub(
            self._convert_emphasis, clean_html
        )

        # Strong
        clean_html = self.inline_patterns["strong"].sub(
            self._convert_strong, clean_html
        )

        # Inline code - fix the pattern name
        clean_html = self.inline_patterns["inline_code"].sub(
            self._convert_inline_code, clean_html
        )

        # Remove remaining HTML tags
        clean_html = self.other_patterns["html_tag"].sub("", clean_html)

        # Unescape HTML entities
        clean_html = self._unescape_html_entities(clean_html)

        return clean_html.strip()

    def _unescape_html_entities(self, text: str) -> str:
        """Unescape HTML entities.

        Args:
            text (str): The text containing HTML entities.

        Returns:
            str: The text with unescaped HTML entities.
        """
        self.logger.debug("Unescaping HTML entities")

        entities = {
            "&lt;": "<",
            "&gt;": ">",
            "&amp;": "&",
            "&quot;": '"',
            "&#39;": "'",
            "&nbsp;": " ",
            "&copy;": "©",
            "&reg;": "®",
            "&trade;": "™",
        }

        # Count entities for debugging
        entity_count = 0
        for entity, char in entities.items():
            count = text.count(entity)
            if count > 0:
                entity_count += count
                self.logger.debug(
                    "Replacing %s instances of %s with '%s'", count, entity, char
                )
                text = text.replace(entity, char)

        if entity_count > 0:
            self.logger.debug("Unescaped %s HTML entities in total", entity_count)

        return text
