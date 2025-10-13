"""
Tests for the LXML HTML to Markdown parser with Level 3 (complex HTML) files.
"""

import pytest

from alea_markdown.lxml_parser import LXMLHTMLParser
from alea_markdown.base.parser_config import ParserConfig
from tests.util.diff import assert_markdown_equal


def test_lxml_parser_html_with_deep_nesting(resources_dir):
    """Test LXML parser with deeply nested HTML elements."""
    # Setup parser with test_mode enabled
    config = ParserConfig(test_mode=True)
    parser = LXMLHTMLParser(config)

    # Get test file paths
    html_file = resources_dir / "level3" / "html_with_deep_nesting.html"
    md_file = resources_dir / "level3" / "html_with_deep_nesting.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown
    actual_md = parser.parse(html_content, include_title=False)

    # Strip trailing newlines from actual_md to match expected format
    actual_md = actual_md.rstrip("\n")

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_lxml_parser_broken_html_mismatched_tags(resources_dir):
    """Test LXML parser with HTML containing mismatched tags."""
    # Setup parser with test_mode enabled
    config = ParserConfig(test_mode=True)
    parser = LXMLHTMLParser(config)

    # Get test file paths
    html_file = resources_dir / "level3" / "broken_html_mismatched_tags.html"
    md_file = resources_dir / "level3" / "broken_html_mismatched_tags.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown with include_title=False to match existing tests
    actual_md = parser.parse(html_content, include_title=False)

    # Strip trailing newlines from actual_md to match expected format
    actual_md = actual_md.rstrip("\n")

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


def test_lxml_parser_broken_html_unclosed_tags(resources_dir):
    """Test LXML parser with HTML containing unclosed tags."""
    # Setup parser with test_mode enabled
    config = ParserConfig(test_mode=True)
    parser = LXMLHTMLParser(config)

    # Get test file paths
    html_file = resources_dir / "level3" / "broken_html_unclosed_tags.html"
    md_file = resources_dir / "level3" / "broken_html_unclosed_tags.md"

    # Read files
    html_content = html_file.read_text(encoding="utf-8")
    expected_md = md_file.read_text(encoding="utf-8").strip()

    # Parse HTML to Markdown with include_title=False to match existing tests
    actual_md = parser.parse(html_content, include_title=False)

    # Strip trailing newlines from actual_md to match expected format
    actual_md = actual_md.rstrip("\n")

    # Assert the results match expected output
    assert_markdown_equal(expected_md, actual_md, html_path=html_file)


# Add more level3 tests as needed


# Benchmark tests for level3 files
LEVEL3_HTML_FILES = [
    # filename, description
    ("html_with_deep_nesting", "HTML with deeply nested elements"),
    ("broken_html_mismatched_tags", "HTML with mismatched opening/closing tags"),
    ("broken_html_unclosed_tags", "HTML with unclosed tags"),
    # Add other level3 files as they become available
]


@pytest.mark.parametrize("test_file,description", LEVEL3_HTML_FILES)
def test_benchmark_lxml_parser_level3(benchmark, resources_dir, test_file, description):
    """Benchmark LXML parser with complex HTML documents.

    This test runs benchmarks on level3 HTML files and includes
    information about file characteristics to help analyze the relationship between
    file complexity and parsing performance.
    """
    # Setup parser with test_mode enabled
    config = ParserConfig(test_mode=True)
    parser = LXMLHTMLParser(config)

    html_file = resources_dir / "level3" / f"{test_file}.html"
    html_content = html_file.read_text(encoding="utf-8")

    # Run the benchmark
    result = benchmark(
        lambda html: parser.parse(html, include_title=False), html_content
    )

    # Verify the result is not empty
    assert result is not None
    assert result  # Should contain non-empty content

    # Add metadata about the test file for results analysis
    benchmark.extra_info["file_size"] = len(html_content)
    benchmark.extra_info["description"] = description
    benchmark.extra_info["file_name"] = html_file.name
    benchmark.extra_info["directory"] = "level3"
