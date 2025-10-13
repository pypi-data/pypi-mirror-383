"""
Tests for the Regex HTML to Markdown parser with Level 1 (basic HTML) files.
"""

import pytest

from alea_markdown.regex_parser import RegexHTMLParser
from alea_markdown.base.parser_config import ParserConfig
from alea_markdown.normalizer import MarkdownNormalizer, NormalizerConfig
from tests.util.diff import assert_markdown_equal


def normalize_markdown_for_test(markdown: str) -> str:
    """Normalize markdown content for test comparisons.

    This helper function applies standardized normalization to markdown content
    to ensure consistent comparison in tests, addressing common issues like:
    - Extra whitespace
    - Inconsistent newlines
    - Other formatting differences that don't affect semantic content

    Args:
        markdown (str): The markdown content to normalize

    Returns:
        str: Normalized markdown content
    """
    normalizer_config = NormalizerConfig(
        max_newlines=2,  # Limit consecutive newlines
        normalize_inline_spacing=True,  # Fix extra spaces between words
        trim_trailing_whitespace=True,  # Remove trailing whitespace
    )
    normalizer = MarkdownNormalizer(normalizer_config)
    return normalizer.normalize(markdown)


def test_regex_parser_basic_html4(resources_dir):
    """Test Regex parser with basic HTML 4.01 document."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "basic_html4.html"
    md_file = resources_dir / "level1" / "basic_html4.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_regex_parser_basic_html5(resources_dir):
    """Test Regex parser with basic HTML5 document."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "basic_html5.html"
    md_file = resources_dir / "level1" / "basic_html5.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_regex_parser_empty(resources_dir):
    """Test Regex parser with empty HTML document."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "empty.html"
    md_file = resources_dir / "level1" / "empty.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_regex_parser_html_no_doctype(resources_dir):
    """Test Regex parser with HTML document missing DOCTYPE declaration."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "html_no_doctype.html"
    md_file = resources_dir / "level1" / "html_no_doctype.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_regex_parser_whitespace_only(resources_dir):
    """Test Regex parser with HTML document containing only whitespace."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "whitespace_only.html"
    md_file = resources_dir / "level1" / "whitespace_only.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_regex_parser_xhtml_strict(resources_dir):
    """Test Regex parser with XHTML strict document."""
    # Setup parser
    parser = RegexHTMLParser(ParserConfig())

    # Get test file paths
    html_file = resources_dir / "level1" / "xhtml_strict.html"
    md_file = resources_dir / "level1" / "xhtml_strict.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content)

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


# Benchmark tests for level1 files
LEVEL1_HTML_FILES = [
    # filename, description
    ("basic_html4", "HTML 4.01 document"),
    ("basic_html5", "HTML5 document with semantic elements"),
    ("empty", "Empty HTML document with only a comment"),
    ("html_no_doctype", "HTML without DOCTYPE declaration"),
    ("whitespace_only", "HTML with only whitespace"),
    ("xhtml_strict", "XHTML strict document"),
]


@pytest.mark.parametrize("test_file,description", LEVEL1_HTML_FILES)
def test_benchmark_regex_parser_level1(
    benchmark, resources_dir, test_file, description
):
    """Benchmark Regex parser with basic HTML documents.

    This test runs benchmarks on level1 HTML files and includes
    information about file characteristics to help analyze the relationship between
    file complexity and parsing performance.
    """
    parser = RegexHTMLParser(ParserConfig())
    html_file = resources_dir / "level1" / f"{test_file}.html"
    html_content = html_file.read_text(encoding="utf-8")

    # Run the benchmark
    result = benchmark(parser.parse, html_content)

    # Verify the result is not empty
    assert result is not None

    # Additional file-specific checks
    if test_file not in ("empty", "whitespace_only"):
        assert result  # Should contain non-empty content

    # Add metadata about the test file for results analysis
    benchmark.extra_info["file_size"] = len(html_content)
    benchmark.extra_info["description"] = description
    benchmark.extra_info["file_name"] = html_file.name
    benchmark.extra_info["directory"] = "level1"
