"""
Test for definition list conversion in the LXML parser.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_definition_list")

# Test HTML with a definition list
html_with_definition_list = """<!DOCTYPE html>
<html>
<head>
    <title>Definition List Test</title>
</head>
<body>
    <h1>Definition List Example</h1>
    <p>Below is a definition list.</p>
    
    <dl>
        <dt>HTML</dt>
        <dd>HyperText Markup Language, a <strong>standardized</strong> system for tagging text files.</dd>
        <dt>CSS</dt>
        <dd>Cascading Style Sheets, used to <em>describe</em> the look and formatting of a document.</dd>
        <dt>JavaScript</dt>
        <dd>A programming language used to create <code>interactive</code> effects.</dd>
    </dl>
    
    <p>And here's another paragraph after the list.</p>
</body>
</html>"""

# Create parser with explicit LXML type
lxml_parser = AutoParser(ParserConfig(parser_type=ParserType.LXML))

# Parse the HTML
logger.info("Parsing HTML with definition list using LXML parser")
lxml_result = lxml_parser.parse(html_with_definition_list)

# Print the result
print("\nLXML Parser Result:\n")
print(lxml_result)

# Check if definition list is properly formatted
expected_format = """HTML
: HyperText Markup Language, a **standardized** system for tagging text files.

CSS
: Cascading Style Sheets, used to *describe* the look and formatting of a document.

JavaScript
: A programming language used to create `interactive` effects."""

if expected_format in lxml_result:
    print("\nSUCCESS: Definition list was properly converted to Markdown!")
else:
    print("\nFAILURE: Definition list was not properly converted to Markdown.")
    print("\nExpected format:\n")
    print(expected_format)
