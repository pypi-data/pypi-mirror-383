"""
alea_markdown.normalizer - Normalize and clean up Markdown output.

This module provides utilities for normalizing Markdown content by:
- Limiting consecutive newlines
- Cleaning up excessive spaces
- Normalizing heading formats
- Standardizing list markers
- And other formatting improvements
"""

import re
from typing import Dict, Any, List, Optional, Callable, Pattern
from dataclasses import dataclass, field

from alea_markdown.logger import get_logger

# Set up module logger
logger = get_logger(__name__)


@dataclass
class NormalizerConfig:
    """Configuration for Markdown normalization.

    This class defines the rules for normalizing Markdown content.
    """

    # Maximum number of consecutive newlines allowed
    max_newlines: int = 3

    # Whether to trim trailing whitespace from lines
    trim_trailing_whitespace: bool = True

    # Whether to normalize heading styles (e.g., "### " instead of "#  #  # ")
    normalize_headings: bool = True

    # Whether to normalize list markers (-, *, +) to a consistent style
    normalize_list_markers: bool = True

    # The list marker to use when normalizing unordered lists
    list_marker: str = "-"

    # Whether to normalize link formats
    normalize_links: bool = True

    # Whether to normalize image formats
    normalize_images: bool = True

    # Whether to ensure single spaces around inline elements
    normalize_inline_spacing: bool = True

    # Whether to normalize code block delimiters
    normalize_code_blocks: bool = True

    # Whether to enforce consistent table formatting
    normalize_tables: bool = True

    # Whether to ensure correct character encoding (UTF-8)
    normalize_encoding: bool = True

    # How to handle encoding errors ('replace', 'ignore', 'strict')
    encoding_errors: str = "replace"

    # Target encoding for output
    target_encoding: str = "utf-8"

    # Custom normalizer functions
    custom_normalizers: List[Callable[[str], str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the normalizer configuration."""
        logger.debug(
            "Initializing NormalizerConfig: max_newlines=%s, "
            "trim_trailing_whitespace=%s, "
            "normalize_headings=%s, "
            "normalize_encoding=%s",
            self.max_newlines,
            self.trim_trailing_whitespace,
            self.normalize_headings,
            self.normalize_encoding,
        )

        # Validate configuration
        if self.max_newlines < 1:
            logger.warning("max_newlines must be at least 1, setting to 1")
            self.max_newlines = 1

        if self.list_marker not in ["-", "*", "+"]:
            logger.warning(
                "Invalid list marker '%s', defaulting to '-'", self.list_marker
            )
            self.list_marker = "-"

        if self.encoding_errors not in ["replace", "ignore", "strict"]:
            logger.warning(
                "Invalid encoding_errors value '%s', defaulting to 'replace'",
                self.encoding_errors,
            )
            self.encoding_errors = "replace"


class MarkdownNormalizer:
    """Normalizes Markdown content based on configuration rules.

    This class applies various normalization rules to Markdown content to
    improve consistency and readability.
    """

    def __init__(self, config: Optional[NormalizerConfig] = None) -> None:
        """Initialize the Markdown normalizer.

        Args:
            config (Optional[NormalizerConfig]): Configuration for normalization rules.
                Defaults to None, which uses the default configuration.
        """
        self.config = config or NormalizerConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info("Initializing %s", self.__class__.__name__)

        # Compile regular expressions for better performance
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regular expression patterns for normalization."""
        self.patterns: Dict[str, Pattern] = {
            # Match consecutive newlines
            "consecutive_newlines": re.compile(
                r"\n{" + str(self.config.max_newlines + 1) + r",}"
            ),
            # Match trailing whitespace
            "trailing_whitespace": re.compile(r"[ \t]+$", re.MULTILINE),
            # Match inconsistent heading formats (e.g., "#  #  # " or "###    ")
            "heading_format": re.compile(r"^(#+)[ \t]*(.+?)[ \t]*$", re.MULTILINE),
            # Match unordered list markers
            "list_markers": re.compile(r"^([ \t]*)[-*+][ \t]+", re.MULTILINE),
            # Match ordered list items with excessive spaces
            "ordered_list_items": re.compile(r"^([ \t]*)(\d+\.)[ \t]+", re.MULTILINE),
            # Match code block fences with inconsistent formatting
            "code_blocks": re.compile(r"^(`{3,}|~{3,})(.*)$", re.MULTILINE),
            # Match multiple spaces (not at line start, not after list markers)
            "multiple_spaces": re.compile(
                r"(?<!\n)(?<!^)(?<![-*+] )[ ]{2,}", re.MULTILINE
            ),
            # Match reference-style links
            "reference_links": re.compile(r"\[([^\]]+)\]\[([^\]]*)\]"),
            # Match URL-style links
            "url_links": re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
            # Match image syntax
            "images": re.compile(r"!\[([^\]]*)\]\(([^)]+)\)"),
            # Match table rows
            "table_rows": re.compile(r"^\|.*\|$", re.MULTILINE),
            # Match table separators
            "table_separators": re.compile(r"^\|[-: |]+\|$", re.MULTILINE),
        }

        self.logger.debug(
            "Compiled %s regex patterns for normalization", len(self.patterns)
        )

    def normalize(self, markdown: str) -> str:
        """Normalize Markdown content according to the configuration.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        self.logger.info("Normalizing Markdown content (%s chars)", len(markdown))

        # Early exit for empty content
        if not markdown or not markdown.strip():
            self.logger.debug("Empty or whitespace-only content, returning as is")
            return markdown

        # Apply normalizations based on config
        result = markdown

        # Helper function to check if all normalizations are disabled
        def all_normalizations_disabled():
            # Group 1: Basic text normalizations
            basic_disabled = (
                not self.config.max_newlines
                and not self.config.trim_trailing_whitespace
                and not self.config.normalize_inline_spacing
                and not self.config.normalize_encoding
            )

            # Group 2: Markdown element normalizations
            elements_disabled = (
                not self.config.normalize_headings
                and not self.config.normalize_list_markers
                and not self.config.normalize_links
                and not self.config.normalize_images
            )

            # Group 3: Block element normalizations
            blocks_disabled = (
                not self.config.normalize_code_blocks
                and not self.config.normalize_tables
                and not self.config.custom_normalizers
            )

            return basic_disabled and elements_disabled and blocks_disabled

        # Skip normalization entirely if all normalizations are disabled
        if all_normalizations_disabled():
            self.logger.debug("All normalizations disabled, returning original content")
            return markdown

        normalizer_methods = []

        # Only apply enabled normalizations
        if self.config.normalize_encoding:
            normalizer_methods.append(self._normalize_encoding)
        if self.config.max_newlines > 0:
            normalizer_methods.append(self._normalize_newlines)
        if self.config.trim_trailing_whitespace:
            normalizer_methods.append(self._normalize_trailing_whitespace)
        if self.config.normalize_headings:
            normalizer_methods.append(self._normalize_headings)
        if self.config.normalize_list_markers:
            normalizer_methods.append(self._normalize_list_markers)
        if self.config.normalize_links or self.config.normalize_images:
            normalizer_methods.append(self._normalize_links_and_images)
        if self.config.normalize_inline_spacing:
            normalizer_methods.append(self._normalize_inline_spacing)
        if self.config.normalize_code_blocks:
            normalizer_methods.append(self._normalize_code_blocks)
        if self.config.normalize_tables:
            normalizer_methods.append(self._normalize_tables)
        if self.config.custom_normalizers:
            normalizer_methods.append(self._apply_custom_normalizers)

        for normalizer in normalizer_methods:
            result = normalizer(result)

        self.logger.info("Normalization complete, output: %s chars", len(result))
        return result

    def _normalize_newlines(self, markdown: str) -> str:
        """Normalize consecutive newlines.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if self.config.max_newlines < 1:
            return markdown

        original_length = len(markdown)
        replacement = "\n" * self.config.max_newlines
        result = self.patterns["consecutive_newlines"].sub(replacement, markdown)

        if len(result) != original_length:
            self.logger.debug(
                "Normalized newlines: %s characters removed",
                original_length - len(result),
            )

        return result

    def _normalize_trailing_whitespace(self, markdown: str) -> str:
        """Remove trailing whitespace from lines.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.trim_trailing_whitespace:
            # Make sure we return exactly the original content without normalization
            return markdown

        original_length = len(markdown)
        result = self.patterns["trailing_whitespace"].sub("", markdown)

        if len(result) != original_length:
            self.logger.debug(
                "Removed trailing whitespace: %s characters removed",
                original_length - len(result),
            )

        return result

    def _normalize_headings(self, markdown: str) -> str:
        """Normalize heading formats.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.normalize_headings:
            # Skip normalization but return the original markdown exactly
            return markdown

        def normalize_heading(match: re.Match) -> str:
            """Format heading with single space after #s."""
            hashes, content = match.groups()
            return f"{hashes} {content}"

        original = markdown
        result = self.patterns["heading_format"].sub(normalize_heading, markdown)

        if result != original:
            self.logger.debug("Normalized heading formats")

        return result

    def _normalize_list_markers(self, markdown: str) -> str:
        """Normalize list markers to a consistent style.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.normalize_list_markers:
            return markdown

        # Normalize unordered list markers
        def normalize_unordered_marker(match: re.Match) -> str:
            """Convert any list marker to the configured marker."""
            indent = match.group(1)
            return f"{indent}{self.config.list_marker} "

        # Normalize ordered list markers (ensure single space after number)
        def normalize_ordered_marker(match: re.Match) -> str:
            """Ensure consistent spacing after ordered list markers."""
            indent, number = match.groups()
            return f"{indent}{number} "

        original = markdown
        result = self.patterns["list_markers"].sub(normalize_unordered_marker, markdown)
        result = self.patterns["ordered_list_items"].sub(
            normalize_ordered_marker, result
        )

        if result != original:
            self.logger.debug("Normalized list markers")

        return result

    def _normalize_links_and_images(self, markdown: str) -> str:
        """Normalize link and image formats.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not (self.config.normalize_links or self.config.normalize_images):
            return markdown

        original = markdown
        result = markdown

        if self.config.normalize_links:
            # Normalize URL-style links (ensure no extra spaces)
            def normalize_url_link(match: re.Match) -> str:
                """Format links consistently."""
                text, url = match.groups()
                return f"[{text.strip()}]({url.strip()})"

            # Normalize reference-style links
            def normalize_ref_link(match: re.Match) -> str:
                """Format reference links consistently."""
                text, ref = match.groups()
                if ref:
                    return f"[{text.strip()}][{ref.strip()}]"
                return f"[{text.strip()}][]"

            result = self.patterns["url_links"].sub(normalize_url_link, result)
            result = self.patterns["reference_links"].sub(normalize_ref_link, result)

        if self.config.normalize_images:
            # Normalize image syntax
            def normalize_image(match: re.Match) -> str:
                """Format image links consistently."""
                alt, url = match.groups()
                return f"![{alt.strip()}]({url.strip()})"

            result = self.patterns["images"].sub(normalize_image, result)

        if result != original:
            self.logger.debug("Normalized links and images")

        return result

    def _normalize_inline_spacing(self, markdown: str) -> str:
        """Normalize spacing around inline elements.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.normalize_inline_spacing:
            return markdown

        original = markdown

        # First, make a pass over the string to ensure inline code spans are
        # handled without relying on catastrophic-backtracking regexes.
        result = self._preserve_inline_code(markdown)

        # Only normalize text outside of code blocks
        # Split the text by code blocks and normalize each part individually
        in_code_block = False

        # Simple code block detection - not perfect but works for most cases
        lines = result.split("\n")
        current_part: List[str] = []

        for line in lines:
            if line.strip().startswith("```"):
                # Toggle code block state
                in_code_block = not in_code_block
                current_part.append(line)
            elif in_code_block:
                # Inside code block, don't normalize
                current_part.append(line)
            else:
                # Outside code block, normalize
                normalized_line = self.patterns["multiple_spaces"].sub(" ", line)
                current_part.append(normalized_line)

        result = "\n".join(current_part)

        if result != original:
            self.logger.debug("Normalized inline spacing")

        return result

    def _preserve_inline_code(self, markdown: str) -> str:
        """Return markdown while scanning inline code spans in linear time.

        The previous implementation used a backtracking-heavy regex that could
        explode on long unmatched backtick runs. This parser walks the string
        once, copying inline code spans through unchanged.
        """

        if "`" not in markdown:
            return markdown

        parts: List[str] = []
        last_pos = 0
        length = len(markdown)
        i = 0

        while i < length:
            if markdown[i] != "`":
                i += 1
                continue

            fence_start = i
            while i < length and markdown[i] == "`":
                i += 1

            fence_len = i - fence_start
            if fence_len == 0:
                i += 1
                continue

            closing_index = markdown.find("`" * fence_len, i)
            if closing_index == -1:
                parts.append(markdown[last_pos:])
                return "".join(parts)

            closing_end = closing_index + fence_len
            parts.append(markdown[last_pos:fence_start])
            parts.append(markdown[fence_start:closing_end])

            i = closing_end
            last_pos = closing_end

        parts.append(markdown[last_pos:])

        if not parts:
            return markdown

        return "".join(parts)

    def _normalize_code_blocks(self, markdown: str) -> str:
        """Normalize code block delimiters.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.normalize_code_blocks:
            return markdown

        # Standardize code block fences to three backticks
        def normalize_code_fence(match: re.Match) -> str:
            """Format code fences consistently."""
            _, lang = match.groups()
            # Make sure to handle the case where there's a space between backticks and language
            lang_str = lang.strip()
            if lang_str:
                return f"```{lang_str}"
            else:
                return "```"

        original = markdown
        result = self.patterns["code_blocks"].sub(normalize_code_fence, markdown)

        if result != original:
            self.logger.debug("Normalized code blocks")

        # Note: We do not modify the content inside code blocks,
        # as that could break code indentation and formatting
        return result

    def _normalize_tables(self, markdown: str) -> str:
        """Normalize table formatting.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        if not self.config.normalize_tables:
            return markdown

        # Find all tables (need to process each table individually)
        table_sections: List[Dict[str, Any]] = []

        # First find all table separator rows
        separator_matches = list(self.patterns["table_separators"].finditer(markdown))

        for sep_match in separator_matches:
            # For each separator, find the header row (previous line)
            sep_start = sep_match.start()
            sep_end = sep_match.end()

            # Find the header row (previous non-blank line)
            header_end = sep_start
            header_start = markdown.rfind("\n", 0, header_end)
            if header_start == -1:
                header_start = 0
            else:
                header_start += 1  # Skip the newline

            header_row = markdown[header_start:header_end]

            # Only process if it looks like a table row
            if not self.patterns["table_rows"].match(header_row):
                continue

            # Now find all subsequent table rows until a blank line or non-table row
            body_start = sep_end + 1  # After separator plus newline
            if body_start >= len(markdown):
                continue

            body_lines = []
            current_pos = body_start
            while True:
                line_end = markdown.find("\n", current_pos)
                if line_end == -1:
                    line_end = len(markdown)

                line = markdown[current_pos:line_end]

                # Stop if blank line or not a table row
                if not line.strip() or not line.strip().startswith("|"):
                    break

                body_lines.append(line)
                if line_end == len(markdown):
                    break
                current_pos = line_end + 1

            # Now we have the complete table
            table_sections.append(
                {
                    "header": header_row,
                    "separator": sep_match.group(),
                    "body_lines": body_lines,
                    "start": int(header_start),
                    "end": int(current_pos),
                }
            )

        # No tables found
        if not table_sections:
            return markdown

        # Process each table
        result = markdown
        offset = 0  # Track changes in string length

        for table in table_sections:
            # Get normalized table text - need to cast types for mypy
            normalized_table = self._normalize_single_table(
                str(table["header"]),
                str(table["separator"]),
                [str(line) for line in table.get("body_lines", [])],
            )

            # Replace the table in the result string
            start_pos = int(table["start"]) + offset
            end_pos = int(table["end"]) + offset
            original_table = result[start_pos:end_pos]
            result = result[:start_pos] + normalized_table + result[end_pos:]

            # Update offset for later replacements
            offset += len(normalized_table) - len(original_table)

        if result != markdown:
            self.logger.debug("Normalized %s tables", len(table_sections))

        return result

    def _get_column_alignments(self, separator_row: str) -> List[Dict[str, Any]]:
        """Extract column alignments from the separator row.

        Args:
            separator_row (str): The separator row of the table.

        Returns:
            List[Dict[str, Any]]: List of column information with alignment details.
        """
        columns: List[Dict[str, Any]] = []
        parts = separator_row.split("|")
        for i, part in enumerate(parts):
            if i in (0, len(parts) - 1):
                continue  # Skip empty parts at start/end

            # Determine alignment
            part = part.strip()
            left_aligned = part.startswith(":")
            right_aligned = part.endswith(":")
            alignment = (
                "center"
                if left_aligned and right_aligned
                else ("right" if right_aligned else "left")
            )

            # Determine minimum width (at least 3 for separator)
            width = max(3, len(str(part)))

            columns.append({"width": width, "align": alignment})

        return columns

    def _normalize_single_table(
        self, header_row: str, separator_row: str, body_rows: List[str]
    ) -> str:
        """Normalize a single table's formatting.

        Args:
            header_row (str): The header row of the table.
            separator_row (str): The separator row of the table.
            body_rows (List[str]): The body rows of the table.

        Returns:
            str: The normalized table.
        """
        # Parse column widths and alignments from the separator row
        columns = self._get_column_alignments(separator_row)

        # Extract header cells
        header_cells = self._split_table_row(header_row)

        # Update column widths based on header content
        for i, cell in enumerate(header_cells):
            if i < len(columns):
                columns[i]["width"] = max(int(columns[i]["width"]), len(str(cell)))
            else:
                # Header has more columns than separator, add new column info
                columns.append({"width": len(str(cell)), "align": "left"})

        # Update column widths based on body content
        for row in body_rows:
            cells = self._split_table_row(row)
            for i, cell in enumerate(cells):
                if i < len(columns):
                    columns[i]["width"] = max(int(columns[i]["width"]), len(str(cell)))
                else:
                    # Row has more columns than header, add new column info
                    columns.append({"width": len(str(cell)), "align": "left"})

        # Rebuild the table with consistent formatting
        formatted_header = self._format_table_row(header_cells, columns)

        # Build separator row
        separator_cells = []
        for col in columns:
            width = int(col["width"])  # Convert to int for calculations
            if col["align"] == "center":
                separator_cells.append(":" + "-" * (width - 2) + ":")
            elif col["align"] == "right":
                separator_cells.append("-" * (width - 1) + ":")
            else:  # left aligned
                separator_cells.append("-" * width)

        formatted_separator = self._format_table_row(
            separator_cells, columns, is_separator=True
        )

        # Format body rows
        formatted_body = []
        for row in body_rows:
            cells = self._split_table_row(row)
            formatted_body.append(self._format_table_row(cells, columns))

        # Combine all parts of the table
        return "\n".join([formatted_header, formatted_separator] + formatted_body)

    def _split_table_row(self, row: str) -> List[str]:
        """Split a table row into its cell contents.

        Args:
            row (str): The table row to split.

        Returns:
            List[str]: The cell contents.
        """
        # Split by pipe and remove empty start/end cells
        parts = row.split("|")
        return [part.strip() for part in parts[1:-1] if parts]

    def _format_table_row(
        self,
        cells: List[str],
        columns: List[Dict[str, Any]],
        is_separator: bool = False,
    ) -> str:
        """Format a table row with consistent spacing.

        Args:
            cells (List[str]): The cell contents.
            columns (List[Dict[str, Any]]): Column width and alignment information.
            is_separator (bool, optional): Whether this is a separator row. Defaults to False.

        Returns:
            str: The formatted table row.
        """
        formatted_cells = []

        # Ensure cells array is at least as long as columns array
        while len(cells) < len(columns):
            cells.append("")

        for i, cell in enumerate(cells):
            if i >= len(columns):
                # More cells than columns, use default formatting
                formatted_cells.append(cell)
                continue

            width = columns[i]["width"]
            if is_separator:
                # Separator cells don't need special alignment
                formatted_cells.append(cell)
            else:
                align = columns[i]["align"]
                if align == "right":
                    formatted_cells.append(cell.rjust(width))
                elif align == "center":
                    formatted_cells.append(cell.center(width))
                else:  # left aligned
                    formatted_cells.append(cell.ljust(width))

        # Create the formatted row with proper spacing
        row_content = "| " + " | ".join(formatted_cells) + " |"

        return row_content

    def _normalize_encoding(self, markdown: str) -> str:
        """Normalize text encoding to ensure UTF-8 compatibility.

        This method handles potential encoding issues by:
        1. Ensuring the string is properly decoded to Python's internal Unicode representation
        2. Re-encoding to the target encoding (default: UTF-8)
        3. Handling any errors according to the configured strategy

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The encoding-normalized Markdown content.
        """
        if not self.config.normalize_encoding:
            return markdown

        try:
            # Only apply encoding normalization if needed
            # First try to encode/decode with the target encoding
            encoded = markdown.encode(
                self.config.target_encoding, errors=self.config.encoding_errors
            )
            decoded = encoded.decode(self.config.target_encoding)

            if decoded != markdown:
                self.logger.debug(
                    "Fixed encoding issues using %s encoding with '%s' error handling",
                    self.config.target_encoding,
                    self.config.encoding_errors,
                )
            return decoded

        except (UnicodeError, LookupError) as e:
            # If there's an error with the specified encoding, log it and fall back to UTF-8
            self.logger.warning(
                "Error normalizing encoding: %s. Falling back to UTF-8 with 'replace'",
                e,
            )
            try:
                # Fall back to UTF-8 with 'replace' error handling
                encoded = markdown.encode("utf-8", errors="replace")
                return encoded.decode("utf-8")
            except Exception as e2:
                # In the very unlikely case this also fails, log and return original
                self.logger.error("Failed to normalize encoding: %s", e2)
                return markdown

    def _apply_custom_normalizers(self, markdown: str) -> str:
        """Apply custom normalizer functions.

        Args:
            markdown (str): The Markdown content to normalize.

        Returns:
            str: The normalized Markdown content.
        """
        result = markdown

        for i, normalizer in enumerate(self.config.custom_normalizers):
            try:
                original = result
                result = normalizer(result)
                if result != original:
                    self.logger.debug("Applied custom normalizer %s", i + 1)
            except Exception as e:
                self.logger.warning("Error in custom normalizer %s: %s", i + 1, e)

        return result


def normalize_markdown(markdown: str, config: Optional[NormalizerConfig] = None) -> str:
    """Normalize Markdown content with the given configuration.

    This is a convenience function that creates a MarkdownNormalizer instance
    and uses it to normalize the given Markdown content.

    Args:
        markdown (str): The Markdown content to normalize.
        config (Optional[NormalizerConfig], optional): The normalizer configuration.
            Defaults to None.

    Returns:
        str: The normalized Markdown content.
    """
    normalizer = MarkdownNormalizer(config)
    return normalizer.normalize(markdown)


class NormalizerBuilder:
    """Builder for creating a MarkdownNormalizer with customized configuration.

    This builder provides a fluent interface for creating normalizer instances
    with specific settings.
    """

    def __init__(self):
        """Initialize the builder with default settings."""
        self.config_params = {
            "max_newlines": 3,
            "trim_trailing_whitespace": True,
            "normalize_headings": True,
            "normalize_list_markers": True,
            "list_marker": "-",
            "normalize_links": True,
            "normalize_images": True,
            "normalize_inline_spacing": True,
            "normalize_code_blocks": True,
            "normalize_tables": True,
            "normalize_encoding": True,
            "encoding_errors": "replace",
            "target_encoding": "utf-8",
            "custom_normalizers": None,
        }

    def with_max_newlines(self, max_newlines: int) -> "NormalizerBuilder":
        """Set maximum consecutive newlines."""
        self.config_params["max_newlines"] = max_newlines
        return self

    def with_trim_whitespace(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable trailing whitespace trimming."""
        self.config_params["trim_trailing_whitespace"] = enabled
        return self

    def with_heading_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable heading normalization."""
        self.config_params["normalize_headings"] = enabled
        return self

    def with_list_normalization(
        self, enabled: bool, marker: str = "-"
    ) -> "NormalizerBuilder":
        """Configure list normalization settings."""
        self.config_params["normalize_list_markers"] = enabled
        self.config_params["list_marker"] = marker
        return self

    def with_link_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable link normalization."""
        self.config_params["normalize_links"] = enabled
        return self

    def with_image_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable image normalization."""
        self.config_params["normalize_images"] = enabled
        return self

    def with_spacing_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable inline spacing normalization."""
        self.config_params["normalize_inline_spacing"] = enabled
        return self

    def with_code_block_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable code block normalization."""
        self.config_params["normalize_code_blocks"] = enabled
        return self

    def with_table_normalization(self, enabled: bool) -> "NormalizerBuilder":
        """Enable or disable table normalization."""
        self.config_params["normalize_tables"] = enabled
        return self

    def with_encoding_normalization(
        self, enabled: bool = True, errors: str = "replace", target: str = "utf-8"
    ) -> "NormalizerBuilder":
        """Configure encoding normalization.

        Args:
            enabled (bool, optional): Whether to enable encoding normalization. Defaults to True.
            errors (str, optional): How to handle encoding errors ('replace', 'ignore', 'strict').
                Defaults to "replace".
            target (str, optional): Target encoding for output. Defaults to "utf-8".

        Returns:
            NormalizerBuilder: The builder instance for method chaining.
        """
        self.config_params["normalize_encoding"] = enabled
        self.config_params["encoding_errors"] = errors
        self.config_params["target_encoding"] = target
        return self

    def with_custom_normalizers(
        self, normalizers: List[Callable[[str], str]]
    ) -> "NormalizerBuilder":
        """Add custom normalizer functions."""
        self.config_params["custom_normalizers"] = normalizers
        return self

    def build(self) -> MarkdownNormalizer:
        """Build and return the configured normalizer instance."""
        config = NormalizerConfig(**self.config_params)
        return MarkdownNormalizer(config)


def create_normalizer(
    max_newlines: int = 3,
    trim_trailing_whitespace: bool = True,
    normalize_headings: bool = True,
    normalize_list_markers: bool = True,
    list_marker: str = "-",
    normalize_links: bool = True,
    normalize_images: bool = True,
    normalize_inline_spacing: bool = True,
    normalize_code_blocks: bool = True,
    normalize_tables: bool = True,
    normalize_encoding: bool = True,
    encoding_errors: str = "replace",
    target_encoding: str = "utf-8",
    custom_normalizers: Optional[List[Callable[[str], str]]] = None,
) -> MarkdownNormalizer:
    """Create a MarkdownNormalizer with the specified configuration.

    This function is maintained for backward compatibility.
    Consider using the NormalizerBuilder class for a more flexible interface.

    Args:
        max_newlines (int, optional): Maximum consecutive newlines. Defaults to 3.
        trim_trailing_whitespace (bool, optional): Whether to trim trailing whitespace.
            Defaults to True.
        normalize_headings (bool, optional): Whether to normalize heading formats.
            Defaults to True.
        normalize_list_markers (bool, optional): Whether to normalize list markers.
            Defaults to True.
        list_marker (str, optional): List marker to use. Defaults to "-".
        normalize_links (bool, optional): Whether to normalize links. Defaults to True.
        normalize_images (bool, optional): Whether to normalize images. Defaults to True.
        normalize_inline_spacing (bool, optional): Whether to normalize inline spacing.
            Defaults to True.
        normalize_code_blocks (bool, optional): Whether to normalize code blocks.
            Defaults to True.
        normalize_tables (bool, optional): Whether to normalize tables. Defaults to True.
        normalize_encoding (bool, optional): Whether to ensure consistent encoding.
            Defaults to True.
        encoding_errors (str, optional): How to handle encoding errors ('replace',
            'ignore', 'strict'). Defaults to "replace".
        target_encoding (str, optional): Target encoding for output. Defaults to "utf-8".
        custom_normalizers (Optional[List[Callable[[str], str]]], optional): Custom normalizer
            functions. Defaults to None.

    Returns:
        MarkdownNormalizer: The configured normalizer.
    """
    # Use the builder pattern internally to reduce the argument list complexity
    return (
        NormalizerBuilder()
        .with_max_newlines(max_newlines)
        .with_trim_whitespace(trim_trailing_whitespace)
        .with_heading_normalization(normalize_headings)
        .with_list_normalization(normalize_list_markers, list_marker)
        .with_link_normalization(normalize_links)
        .with_image_normalization(normalize_images)
        .with_spacing_normalization(normalize_inline_spacing)
        .with_code_block_normalization(normalize_code_blocks)
        .with_table_normalization(normalize_tables)
        .with_encoding_normalization(
            normalize_encoding, encoding_errors, target_encoding
        )
        .with_custom_normalizers(custom_normalizers or [])
        .build()
    )
