"""
Pure test for pre/code handling with a simple straightforward document.
"""

from alea_markdown.auto_parser import AutoParser
from alea_markdown.base.parser_config import ParserConfig, ParserType
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging
set_level(logging.DEBUG)
logger = get_logger("test_pure_pre_code")

# Simple HTML with just the three forms of code
html_simple = """<!DOCTYPE html>
<html>
<body>
    <h1>Code Test</h1>
    
    <h2>Pre Only</h2>
    <pre id="simple-pre">This is preformatted text.</pre>
    
    <h2>Pre with Code</h2>
    <pre><code>function example() {
    console.log("This is a code block");
}</code></pre>
    
    <h2>Pre with Code and Language</h2>
    <pre><code class="language-python">def example():
    print("This is Python code")
</code></pre>
    
    <h2>Inline Code</h2>
    <p>This is <code>inline code</code> in a paragraph.</p>
</body>
</html>"""

# Create parser with explicit Regex type
regex_parser = AutoParser(ParserConfig(parser_type=ParserType.REGEX))

# Parse the HTML
logger.info("Parsing simple pre/code HTML using Regex parser")
regex_result = regex_parser.parse(html_simple)

# Print the result
print("\nRegex Parser Result:\n")
print(regex_result)

# Verify each case is properly formatted
expected_blocks = [
    "```\nThis is preformatted text.\n```",
    '```\nfunction example() {\n    console.log("This is a code block");\n}\n```',
    '```python\ndef example():\n    print("This is Python code")\n```',
    "`inline code`",
]

# Find and print all <pre> elements in the output for debugging
pre_blocks = [line for line in regex_result.split("\n\n") if "```" in line]
print("\nFound code blocks in output:")
for i, block in enumerate(pre_blocks):
    print(f"Block {i + 1}:\n{block}")

success = True
# Alternate approach to find the pre-only block
pre_pattern = "```\nThis is preformatted text.\n```"
if pre_pattern in regex_result:
    print("\nSUCCESS: Found expected block 1 (direct check)")
else:
    print("\nFAILURE: Missing expected block 1 (direct check)")
    success = False

# Check if each code block is correctly formatted
for i, block in enumerate(expected_blocks[1:], start=2):
    if block in regex_result:
        print(f"\nSUCCESS: Found expected block {i}")
    else:
        print(f"\nFAILURE: Missing expected block {i}:")
        print(block)
        success = False

if success:
    print("\nAll code blocks were properly formatted!")
else:
    print("\nSome code blocks were not properly formatted.")
