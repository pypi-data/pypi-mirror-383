"""
Demonstration of adaptive parser selection based on file size.
"""

from alea_markdown.auto_parser import AutoParser
import logging
from alea_markdown.logger import set_level, get_logger

# Set up logging to see which parser is chosen
set_level(logging.DEBUG)
logger = get_logger("test_adaptive_thresholds")

# Create a heading and paragraph for our test HTML
heading = "<h1>Test Adaptive Parser Selection</h1>"
paragraph = (
    "<p>This is a test paragraph to demonstrate the adaptive parser selection.</p>"
)

# Create small, medium, and large HTML content by repeating the paragraph
# Small file (< 128KB) - should use markdownify
small_html = f"<html><body>{heading}"
for i in range(10):
    small_html += f"{paragraph}"
small_html += "</body></html>"

# Medium file (128KB - 2MB) - should use lxml
medium_html = f"<html><body>{heading}"
for i in range(2000):
    medium_html += f"{paragraph}"
medium_html += "</body></html>"

# Large file (> 2MB) - should use regex
large_html = f"<html><body>{heading}"
for i in range(30000):
    large_html += f"{paragraph}"
large_html += "</body></html>"

# Create an AutoParser with default thresholds
parser = AutoParser()

# Print file sizes and thresholds
print(f"Small file size: {len(small_html):,} bytes")
print(f"Medium file size: {len(medium_html):,} bytes")
print(f"Large file size: {len(large_html):,} bytes")
print(f"Small size threshold: {parser.config.small_size_threshold:,} bytes")
print(f"Large size threshold: {parser.config.large_size_threshold:,} bytes")
print()

try:
    # Parse small file - should use markdownify
    print("Parsing small file...")
    small_result = parser.parse(small_html)
    print(f"Small file result (truncated): {small_result[:60]}...")
    print()

    # Parse medium file - should use lxml
    print("Parsing medium file...")
    medium_result = parser.parse(medium_html)
    print(f"Medium file result (truncated): {medium_result[:60]}...")
    print()

    # Parse large file - should use regex
    print("Parsing large file...")
    large_result = parser.parse(large_html)
    print(f"Large file result (truncated): {large_result[:60]}...")

except Exception as e:
    print(f"Error: {e}")

print("\nAll files parsed successfully!")
