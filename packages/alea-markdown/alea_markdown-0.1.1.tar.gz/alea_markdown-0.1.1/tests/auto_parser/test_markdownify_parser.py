"""
Tests for the MarkdownifyParser class.
"""

from unittest.mock import patch

from alea_markdown.markdownify_parser import MarkdownifyParser
from alea_markdown.base.parser_config import ParserConfig


def test_markdownify_parser_initialization():
    """Test that the MarkdownifyParser initializes correctly."""
    # Test with default configuration
    parser = MarkdownifyParser()
    assert parser.config is not None


def test_markdownify_parser_parse():
    """Test that the MarkdownifyParser parses HTML correctly."""
    html = "<h1>Test</h1><p>This is a <strong>test</strong> paragraph.</p>"

    # Mock markdownify.markdownify to return predictable output
    with patch(
        "markdownify.markdownify",
        return_value="# Test\n\nThis is a **test** paragraph.",
    ) as mock_markdownify:
        parser = MarkdownifyParser()
        result = parser.parse(html)

        # Verify the result
        assert result is not None
        assert "# Test" in result
        assert "This is a **test** paragraph" in result

        # Verify markdownify was called with the right parameters
        mock_markdownify.assert_called_once()
        assert mock_markdownify.call_args[0][0] == html


def test_markdownify_parser_with_empty_html():
    """Test that the MarkdownifyParser handles empty HTML content."""
    empty_html = ""
    whitespace_html = "   \n   "

    parser = MarkdownifyParser()

    # Empty HTML should return empty string
    assert parser.parse(empty_html) == ""

    # Whitespace-only HTML should return empty string
    assert parser.parse(whitespace_html) == ""


def test_markdownify_parser_with_links():
    """Test that the MarkdownifyParser handles links correctly."""
    html = '<p>This is a <a href="https://example.com">link</a>.</p>'

    # Test with links enabled (default)
    with patch(
        "markdownify.markdownify", return_value="This is a [link](https://example.com)."
    ) as mock_markdownify:
        parser_links_enabled = MarkdownifyParser()
        result_links_enabled = parser_links_enabled.parse(html)

        assert "[link](https://example.com)" in result_links_enabled
        # Verify convert_links was passed as True
        assert mock_markdownify.call_args[1]["convert_links"] == True

    # Test with links disabled
    with patch(
        "markdownify.markdownify", return_value="This is a link."
    ) as mock_markdownify:
        config_links_disabled = ParserConfig(output_links=False)
        parser_links_disabled = MarkdownifyParser(config_links_disabled)
        result_links_disabled = parser_links_disabled.parse(html)

        # Verify convert_links was passed as False
        assert mock_markdownify.call_args[1]["convert_links"] == False


def test_markdownify_parser_with_images():
    """Test that the MarkdownifyParser handles images correctly."""
    html = '<p>This is an <img src="image.jpg" alt="image">.</p>'

    # Test with images enabled (default)
    with patch(
        "markdownify.markdownify", return_value="This is an ![image](image.jpg)."
    ) as mock_markdownify:
        parser_images_enabled = MarkdownifyParser()
        result_images_enabled = parser_images_enabled.parse(html)

        assert "![image](image.jpg)" in result_images_enabled
        # Verify convert_img was passed as True
        assert mock_markdownify.call_args[1]["convert_img"] == True

    # Test with images disabled
    with patch(
        "markdownify.markdownify", return_value="This is an ."
    ) as mock_markdownify:
        config_images_disabled = ParserConfig(output_images=False)
        parser_images_disabled = MarkdownifyParser(config_images_disabled)
        result_images_disabled = parser_images_disabled.parse(html)

        # Verify convert_img was passed as False
        assert mock_markdownify.call_args[1]["convert_img"] == False


def test_markdownify_parser_with_comments():
    """Test that the MarkdownifyParser handles HTML comments correctly."""
    html = "<p>Before<!-- This is a comment -->After</p>"

    # Test with comments removed (default)
    with patch(
        "markdownify.markdownify", return_value="BeforeAfter"
    ) as mock_markdownify:
        parser_strip_comments = MarkdownifyParser()
        result_strip_comments = parser_strip_comments.parse(html)

        assert "BeforeAfter" in result_strip_comments
        # Verify strip was set correctly
        assert "noscript" in mock_markdownify.call_args[1]["strip"]

    # Test with comments preserved
    with patch(
        "markdownify.markdownify", return_value="Before<!-- This is a comment -->After"
    ) as mock_markdownify:
        config_preserve_comments = ParserConfig(preserve_comments=True)
        parser_preserve_comments = MarkdownifyParser(config_preserve_comments)
        result_preserve_comments = parser_preserve_comments.parse(html)

        # Verify strip was set to an empty list
        assert mock_markdownify.call_args[1]["strip"] == []


def test_markdownify_strip_script_and_style_tags():
    """Test that the MarkdownifyParser strips script and style tags using regex."""
    html = """
    <html>
    <head>
        <style type="text/css">
            body { font-family: Arial; }
            h1 { color: red; }
        </style>
    </head>
    <body>
        <h1>Test Page</h1>
        <p>This is a test paragraph.</p>
        <script type="text/javascript">
            alert('Hello world!');
            console.log('This should be removed');
        </script>
        <p>Another paragraph after the script.</p>
    </body>
    </html>
    """

    # Test directly with the internal regex method
    parser = MarkdownifyParser()
    stripped_html = parser._strip_tags_with_regex(html)

    # The script and style tags should be removed
    assert "body { font-family: Arial; }" not in stripped_html
    assert "alert('Hello world!');" not in stripped_html
    assert "console.log('This should be removed');" not in stripped_html

    # But the actual content should be preserved
    assert "<h1>Test Page</h1>" in stripped_html
    assert "<p>This is a test paragraph.</p>" in stripped_html
    assert "<p>Another paragraph after the script.</p>" in stripped_html

    # Now test with the full parse method using a mock
    with patch("markdownify.markdownify") as mock_markdownify:
        parser.parse(html)

        # Get the HTML that was passed to markdownify
        html_passed_to_markdownify = mock_markdownify.call_args[0][0]

        # Verify script and style content is not in the passed HTML
        assert "body { font-family: Arial; }" not in html_passed_to_markdownify
        assert "alert('Hello world!');" not in html_passed_to_markdownify


def test_markdownify_parser_error_handling():
    """Test that the MarkdownifyParser handles errors gracefully."""
    html = "<h1>Test</h1>"

    # Test with markdownify raising an exception
    with patch(
        "markdownify.markdownify", side_effect=Exception("Test error")
    ) as mock_markdownify:
        parser = MarkdownifyParser()
        result = parser.parse(html)

        # Should return None on error
        assert result is None
