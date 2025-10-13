"""
Test script and style tag removal with the markdownify parser.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_script_removal")

# Create an HTML document with script and style tags
html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Script Removal</title>
    <style>
        body { font-family: sans-serif; }
        h1 { color: blue; }
    </style>
</head>
<body>
    <h1>Test Script Removal</h1>
    <p>This is a paragraph before the script.</p>
    <script>
        // This JavaScript code should be removed
        console.log("This should be removed");
        alert("This should also be removed");
        
        function testFunction() {
            return "This entire function should be removed";
        }
    </script>
    <p>This is a paragraph after the script.</p>
    <div>
        <h2>Second section</h2>
        <style>
            .special {
                color: red;
                font-weight: bold;
            }
        </style>
        <p class="special">This paragraph has special styling, but the style tag should be removed.</p>
    </div>
</body>
</html>"""

# Test with different parsers to verify script/style removal

# Test with markdownify parser
markdownify_parser = AutoParser(ParserConfig(parser_type=ParserType.MARKDOWNIFY))
logger.info("Parsing HTML with script and style tags using markdownify parser")
markdownify_result = markdownify_parser.parse(html)

# Test with regex parser
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))
logger.info("Parsing HTML with script and style tags using regex parser")
regex_result = regex_parser.parse(html)

# Test with lxml parser
lxml_parser = AutoParser(ParserConfig(parser_type=ParserType.LXML))
logger.info("Parsing HTML with script and style tags using lxml parser")
lxml_result = lxml_parser.parse(html)

# Print the results
print("\nMarkdownify Parser Result:\n")
print(markdownify_result)

print("\nRegex Parser Result:\n")
print(regex_result)

print("\nLXML Parser Result:\n")
print(lxml_result)

# Check for script content in the outputs
for parser_name, result in [
    ("Markdownify", markdownify_result),
    ("Regex", regex_result),
    ("LXML", lxml_result),
]:
    if "This should be removed" in result:
        print(f"\nWARNING: Script content was not removed by {parser_name} parser!")
    else:
        print(
            f"\nSUCCESS: Script content was removed correctly by {parser_name} parser!"
        )

    # Check for style content in the output
    if "font-family" in result:
        print(f"WARNING: Style content was not removed by {parser_name} parser!")
    else:
        print(f"SUCCESS: Style content was removed correctly by {parser_name} parser!")
