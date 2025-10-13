"""
Test for adaptive parser selection based on file size.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig
import logging
from alea_markdown.logger import set_level, get_logger
from unittest.mock import patch


def test_adaptive_parser_selection():
    """Test that the parser automatically selects between markdownify, lxml, and regex based on file size."""
    # Set up logging
    set_level(logging.DEBUG)
    logger = get_logger("test_adaptive")

    # Create HTML content for different sizes
    small_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Small Test File</title>
    </head>
    <body>
        <h1>Small Test File</h1>
        <p>This is a <strong>small</strong> HTML file that should use markdownify.</p>
    </body>
    </html>
    """

    # Generate a medium HTML file
    medium_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medium Test File</title>
    </head>
    <body>
        <h1>Medium Test File</h1>
        <p>This is a <strong>medium</strong> HTML file that should use lxml.</p>
    """
    # Add content to make it medium sized
    for i in range(200):
        medium_html += f"<p>Medium content paragraph {i}</p>\n"
    medium_html += "</body></html>"

    # Generate a large HTML file
    large_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Large Test File</title>
    </head>
    <body>
        <h1>Large Test File</h1>
        <p>This is a <strong>large</strong> HTML file that should use regex.</p>
    """
    # Add content to make it large sized
    for i in range(5000):
        large_html += f"<p>Large content paragraph {i}</p>\n"
    large_html += "</body></html>"

    # Create parser with custom thresholds to make testing easier
    parser = AutoParser(
        ParserConfig(
            small_size_threshold=1000,  # 1KB
            large_size_threshold=10000,  # 10KB
        )
    )

    # Log sizes for debugging
    logger.debug(f"Small HTML size: {len(small_html)} bytes")
    logger.debug(f"Medium HTML size: {len(medium_html)} bytes")
    logger.debug(f"Large HTML size: {len(large_html)} bytes")
    logger.debug(f"Small size threshold: {parser.config.small_size_threshold} bytes")
    logger.debug(f"Large size threshold: {parser.config.large_size_threshold} bytes")

    # Set up mock to track which parser is used
    with patch.object(parser, "_try_parser") as mock_try_parser:
        # Setup mock to identify which parser was tried first
        mock_try_parser.return_value = "# Test\n\nContent"

        # Small file (should use markdownify)
        parser.parse(small_html)
        first_parser_small = mock_try_parser.call_args[0][0]
        assert first_parser_small == "markdownify", (
            f"Expected markdownify but got {first_parser_small}"
        )

        # Reset mock
        mock_try_parser.reset_mock()

        # Medium file (should use lxml)
        parser.parse(medium_html)
        first_parser_medium = mock_try_parser.call_args[0][0]
        assert first_parser_medium == "lxml", (
            f"Expected lxml but got {first_parser_medium}"
        )

        # Reset mock
        mock_try_parser.reset_mock()

        # Large file (should use regex)
        parser.parse(large_html)
        first_parser_large = mock_try_parser.call_args[0][0]
        assert first_parser_large == "regex", (
            f"Expected regex but got {first_parser_large}"
        )

    # Also test with real parsers (not mocked)
    parser_real = AutoParser(
        ParserConfig(
            small_size_threshold=1000,  # 1KB
            large_size_threshold=10000,  # 10KB
        )
    )

    # These should parse without errors, though we can't easily check which parser was used
    small_result = parser_real.parse(small_html)
    medium_result = parser_real.parse(medium_html)
    large_result = parser_real.parse(large_html)

    # Verify content is preserved in all cases
    assert "Small Test File" in small_result
    assert "Medium Test File" in medium_result
    assert "Large Test File" in large_result


if __name__ == "__main__":
    test_adaptive_parser_selection()
    print("Test completed successfully!")
