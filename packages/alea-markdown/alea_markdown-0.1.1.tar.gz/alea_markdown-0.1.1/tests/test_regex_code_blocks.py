"""
Test for code block conversion in the RegexHTMLParser.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_regex_code_blocks")

# Test HTML with different code blocks
html_with_code_blocks = """<!DOCTYPE html>
<html>
<head>
    <title>Code Block Test</title>
</head>
<body>
    <h1>Code Block Examples</h1>
    <p>Below are examples of code blocks:</p>
    
    <h2>Simple Code Block</h2>
    <pre><code>function helloWorld() {
    console.log("Hello, World!");
}

helloWorld();</code></pre>

    <h2>Code Block with Language</h2>
    <pre><code class="language-python">def hello_world():
    print("Hello, World!")
    
hello_world()</code></pre>

    <h2>Inline Code</h2>
    <p>Here's some <code>inline code</code> within a paragraph.</p>
    
    <h2>Code Block with HTML Entities</h2>
    <pre><code>if (x &lt; 10) {
    console.log("x is less than 10");
} else if (x &gt; 10) {
    console.log("x is greater than 10");
}</code></pre>

    <h2>Just a Pre Tag</h2>
    <pre>This is preformatted text
without a code tag.
    It should preserve whitespace
      and line breaks.</pre>
</body>
</html>"""

# Create parser with explicit Regex type
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Parse the HTML
logger.info("Parsing HTML with code blocks using Regex parser")
regex_result = regex_parser.parse(html_with_code_blocks)

# Print the result
print("\nRegex Parser Result:\n")
print(regex_result)

# Check if code blocks are properly formatted
expected_blocks = [
    '```\nfunction helloWorld() {\n    console.log("Hello, World!");\n}\n\nhelloWorld();\n```',
    '```python\ndef hello_world():\n    print("Hello, World!")\n\nhello_world()\n```',
    "`inline code`",
    '```\nif (x < 10) {\n    console.log("x is less than 10");\n} else if (x > 10) {\n    console.log("x is greater than 10");\n}\n```',
    "```\nThis is preformatted text\nwithout a code tag.\n    It should preserve whitespace\n      and line breaks.\n```",
]

# Count successful code block conversions
successful_blocks = 0
for block in expected_blocks:
    if block in regex_result:
        successful_blocks += 1
        print(f"\nSUCCESS: Found expected code block:\n{block}")
    else:
        print(f"\nFAILURE: Missing expected code block:\n{block}")

print(
    f"\nTotal: Found {successful_blocks} out of {len(expected_blocks)} expected code blocks."
)
