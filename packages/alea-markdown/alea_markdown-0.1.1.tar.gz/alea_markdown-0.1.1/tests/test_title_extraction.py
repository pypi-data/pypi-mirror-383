"""
Test for title extraction and output as H1 in the regex parser.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_title_extraction")

# Test HTML with a title
html_with_title = """<!DOCTYPE html>
<html>
<head>
    <title>Test Document Title</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>First Heading</h1>
    <p>This is a paragraph.</p>
    <h2>Second Heading</h2>
    <p>This is another paragraph.</p>
</body>
</html>"""

# Test HTML with HTML entities in title
html_with_entities_in_title = """<!DOCTYPE html>
<html>
<head>
    <title>Title with &amp; entities &gt; in it</title>
</head>
<body>
    <p>This is a paragraph.</p>
</body>
</html>"""

# Test HTML without a title
html_without_title = """<!DOCTYPE html>
<html>
<body>
    <h1>First Heading</h1>
    <p>This is a paragraph.</p>
</body>
</html>"""

# Create parser with explicit regex type
parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Test with title
logger.info("Testing HTML with title")
result_with_title = parser.parse(html_with_title)
print("\nHTML with title result:")
print(result_with_title)
if "# Test Document Title" in result_with_title:
    print("SUCCESS: Title extracted and displayed as H1")
else:
    print("FAILURE: Title not found as H1 in output")

# Test with HTML entities in title
logger.info("Testing HTML with entities in title")
result_with_entities = parser.parse(html_with_entities_in_title)
print("\nHTML with entities in title result:")
print(result_with_entities)
if "# Title with & entities > in it" in result_with_entities:
    print("SUCCESS: Title with entities correctly extracted and displayed as H1")
else:
    print("FAILURE: Title with entities not properly processed")

# Test without title
logger.info("Testing HTML without title")
result_without_title = parser.parse(html_without_title)
print("\nHTML without title result:")
print(result_without_title)
# Just check if any title-like heading is added before the content's first heading
if (
    "# First Heading" in result_without_title
    and not result_without_title.strip().startswith("# First Heading")
):
    print("FAILURE: Extra H1 title found but no title was present in HTML")
else:
    print("SUCCESS: No extra title H1 added when no title tag exists")

# Test with title same as first heading
html_with_duplicate_title = """<!DOCTYPE html>
<html>
<head>
    <title>First Heading</title>
</head>
<body>
    <h1>First Heading</h1>
    <p>The title and first heading are the same.</p>
</body>
</html>"""

logger.info("Testing HTML with duplicate title")
result_duplicate_title = parser.parse(html_with_duplicate_title)
print("\nHTML with duplicate title result:")
print(result_duplicate_title)

# Count occurrences of "# First Heading"
heading_count = result_duplicate_title.count("# First Heading")
if heading_count == 1:
    print("SUCCESS: Duplicate heading was removed")
else:
    print(f"FAILURE: Found {heading_count} occurrences of the same heading")
