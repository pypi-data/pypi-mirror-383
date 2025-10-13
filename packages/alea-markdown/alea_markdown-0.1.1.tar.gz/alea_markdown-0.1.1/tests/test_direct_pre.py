"""
Direct test for simple pre tag to see what's being generated.
"""

from alea_markdown.regex_parser import RegexHTMLParser
from alea_markdown.base.parser_config import ParserConfig
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_direct_pre")

# Create a regex parser directly
parser = RegexHTMLParser(ParserConfig())

# Input HTML with just a pre tag
html = "<pre>This is preformatted text.</pre>"

# Get block patterns from the parser
pre_pattern = parser.block_patterns["pre_only"]

# Find the matches
matches = pre_pattern.findall(html)
print(f"Matches from pre_only pattern: {matches}")

# Expected output
expected = "```\nThis is preformatted text.\n```"

# Manually test the handler
if matches:
    attributes, content = matches[0]
    result = parser._handle_pre_only(matches[0])
    print(f"\nGenerated output: {repr(result)}")
    print(f"Expected output: {repr(expected)}")
    if result == expected:
        print("MATCH: Output formats match")
    else:
        print("MISMATCH: Output formats don't match")
else:
    print("No matches found with pre_only pattern")
