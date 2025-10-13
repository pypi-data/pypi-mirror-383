"""
Test for complex formatting with the RegexHTMLParser, focusing on the definition list.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger
import os

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_regex_complex_formatting")

# Path to the test resources
TEST_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
LEVEL3_DIR = os.path.join(TEST_RESOURCES_DIR, "level3")

# Read the complex formatting HTML file
html_file_path = os.path.join(LEVEL3_DIR, "html_with_complex_formatting.html")
with open(html_file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Read the expected Markdown result
md_file_path = os.path.join(LEVEL3_DIR, "html_with_complex_formatting.md")
with open(md_file_path, "r", encoding="utf-8") as f:
    expected_md = f.read()

# Create parser with explicit Regex type
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Parse the HTML
logger.info("Parsing HTML with complex formatting using Regex parser")
regex_result = regex_parser.parse(html_content)

# Print the result
print("\nRegex Parser Result:\n")
print(regex_result)

# Check if the definition list content is included
definition_list_content = """HTML
: HyperText Markup Language, a **standardized** system for tagging text files.

CSS
: Cascading Style Sheets, used to *describe* the look and formatting of a document.

JavaScript
: A programming language used to create `interactive` effects."""

if definition_list_content in regex_result:
    print("\nSUCCESS: Definition list content was properly converted to Markdown!")
else:
    print("\nFAILURE: Definition list content was not properly converted to Markdown.")
    print("\nExpected format:\n")
    print(definition_list_content)
