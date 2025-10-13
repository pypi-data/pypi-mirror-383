"""
Test for <pre> tag inside a <div> to debug nested element handling.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_pre_in_div")

# HTML with a pre tag inside a div
html_with_pre_in_div = """<!DOCTYPE html>
<html>
<body>
    <h1>Pre Tag in Div Test</h1>
    <div class="code-container">
        <h2>Code Example</h2>
        <pre><code>function example() {
    return "This is an example";
}

example();</code></pre>
    </div>
</body>
</html>"""

# Create parser with explicit Regex type
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Parse the HTML
logger.info("Parsing HTML with pre tag in div using Regex parser")
regex_result = regex_parser.parse(html_with_pre_in_div)

# Print the result
print("\nRegex Parser Result:\n")
print(regex_result)

# Check for duplicated code blocks
code_block = (
    '```\nfunction example() {\n    return "This is an example";\n}\n\nexample();\n```'
)
inline_code = (
    '`function example() {\n    return "This is an example";\n}\n\nexample();`'
)

code_block_count = regex_result.count("```\nfunction example()")
inline_code_count = regex_result.count("`function example()")

print(f"\nCode block occurrences: {code_block_count}")
print(f"Inline code occurrences: {inline_code_count}")

if code_block_count == 1 and inline_code_count == 0:
    print("\nSUCCESS: Code block appears exactly once and in the right format")
elif code_block_count > 1:
    print("\nFAILURE: Code block appears multiple times")
elif inline_code_count > 0:
    print("\nFAILURE: Code appears as inline code when it should be a code block")
