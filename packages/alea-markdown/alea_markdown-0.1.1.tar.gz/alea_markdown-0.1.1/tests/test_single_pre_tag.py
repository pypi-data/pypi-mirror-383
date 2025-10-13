"""
Simpler test for <pre> tag handling to debug the issue.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_single_pre_tag")

# Very simple HTML with just a pre tag
html_with_pre = """<!DOCTYPE html>
<html>
<body>
    <h1>Pre Tag Test</h1>
    <pre>This is preformatted text
that should be in a code block.</pre>
</body>
</html>"""

# Create parser with explicit Regex type
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Parse the HTML
logger.info("Parsing HTML with pre tag using Regex parser")
regex_result = regex_parser.parse(html_with_pre)

# Print the result
print("\nRegex Parser Result:\n")
print(regex_result)

# Expected result
expected_output = """# Pre Tag Test

```
This is preformatted text
that should be in a code block.
```"""

if expected_output in regex_result:
    print("\nSUCCESS: Pre tag was properly formatted as a code block")
else:
    print("\nFAILURE: Pre tag was not properly formatted")
    print(f"Expected:\n{expected_output}")
