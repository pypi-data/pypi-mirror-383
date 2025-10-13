"""
Performance benchmark tests comparing alea-markdown vs markdownify.
"""

import os
import pytest
import time
import logging
from typing import List, Tuple

from markdownify import markdownify
from alea_markdown.auto_parser import AutoParser
from alea_markdown.lxml_parser import LXMLHTMLParser
from alea_markdown.regex_parser import RegexHTMLParser
from alea_markdown.base.parser_config import ParserConfig, ParserType, MarkdownStyle
from alea_markdown.logger import set_level

# Set logging to WARNING to reduce test output noise
set_level(logging.WARNING)


# Fixture to load test HTML files
@pytest.fixture
def test_html_files() -> List[Tuple[str, str]]:
    """Load test HTML files from the resources directory."""
    test_files = []
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")

    # Files to skip (empty or problematic files)
    skip_files = ["empty.html", "whitespace_only.html"]

    # Get all HTML files from all levels
    for level_dir in ["level1", "level2", "level3"]:
        level_path = os.path.join(resources_dir, level_dir)
        if not os.path.exists(level_path):
            continue

        for filename in os.listdir(level_path):
            if filename.endswith(".html") and filename not in skip_files:
                file_path = os.path.join(level_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # Skip very small or empty files
                if len(html_content.strip()) < 10:
                    continue

                test_files.append((filename, html_content))

    return test_files


# Benchmarking test for AutoParser
def test_auto_parser_performance(test_html_files, benchmark):
    """Benchmark AutoParser performance."""
    parser = AutoParser()

    def parse_all_files():
        results = []
        for _, html in test_html_files:
            try:
                results.append(parser.parse(html))
            except Exception:
                # Skip files that can't be parsed
                continue
        return results

    benchmark(parse_all_files)


# Benchmarking test for LXML Parser
def test_lxml_parser_performance(test_html_files, benchmark):
    """Benchmark LXMLParser performance."""
    config = ParserConfig(
        parser_type=ParserType.LXML, markdown_style=MarkdownStyle.GITHUB
    )
    parser = LXMLHTMLParser(config)

    def parse_all_files():
        results = []
        for _, html in test_html_files:
            try:
                results.append(parser.parse(html))
            except Exception:
                # Skip files that can't be parsed
                continue
        return results

    benchmark(parse_all_files)


# Benchmarking test for Regex Parser
def test_regex_parser_performance(test_html_files, benchmark):
    """Benchmark RegexParser performance."""
    config = ParserConfig(
        parser_type=ParserType.REGEX, markdown_style=MarkdownStyle.GITHUB
    )
    parser = RegexHTMLParser(config)

    def parse_all_files():
        results = []
        for _, html in test_html_files:
            try:
                results.append(parser.parse(html))
            except Exception:
                # Skip files that can't be parsed
                continue
        return results

    benchmark(parse_all_files)


# Benchmarking test for markdownify
def test_markdownify_performance(test_html_files, benchmark):
    """Benchmark markdownify performance."""

    def parse_all_files():
        results = []
        for _, html in test_html_files:
            try:
                results.append(markdownify(html))
            except Exception:
                # Skip files that can't be parsed
                continue
        return results

    benchmark(parse_all_files)


# Detailed timing test comparing all parsers for each file
def test_timing_comparison(test_html_files):
    """Compare timing between all parsers for each test file."""
    auto_parser = AutoParser()

    # Create parsers
    lxml_config = ParserConfig(
        parser_type=ParserType.LXML, markdown_style=MarkdownStyle.GITHUB
    )
    regex_config = ParserConfig(
        parser_type=ParserType.REGEX, markdown_style=MarkdownStyle.GITHUB
    )
    lxml_parser = LXMLHTMLParser(lxml_config)
    regex_parser = RegexHTMLParser(regex_config)

    # Initialize timing arrays
    auto_parser_times = []
    lxml_parser_times = []
    regex_parser_times = []
    markdownify_times = []
    filenames = []

    for filename, html in test_html_files:
        try:
            # Time AutoParser
            start_time = time.time()
            auto_parser.parse(html)
            auto_parser_time = time.time() - start_time

            # Time LXML Parser
            start_time = time.time()
            lxml_parser.parse(html)
            lxml_parser_time = time.time() - start_time

            # Time Regex Parser
            start_time = time.time()
            regex_parser.parse(html)
            regex_parser_time = time.time() - start_time

            # Time markdownify
            start_time = time.time()
            markdownify(html)
            markdownify_time = time.time() - start_time

            auto_parser_times.append(auto_parser_time)
            lxml_parser_times.append(lxml_parser_time)
            regex_parser_times.append(regex_parser_time)
            markdownify_times.append(markdownify_time)
            filenames.append(filename)
        except Exception as e:
            print(f"Skipping file {filename}: {str(e)}")
            continue

    # Print the results
    print("\nPerformance comparison of all parsers:")
    print(
        f"{'Filename':<30} {'AutoParser (s)':<12} {'LXML (s)':<12} {'Regex (s)':<12} {'markdownify (s)':<12}"
    )
    print("-" * 90)

    total_auto = 0
    total_lxml = 0
    total_regex = 0
    total_markdownify = 0

    for i, filename in enumerate(filenames):
        auto_time = auto_parser_times[i]
        lxml_time = lxml_parser_times[i]
        regex_time = regex_parser_times[i]
        mark_time = markdownify_times[i]

        total_auto += auto_time
        total_lxml += lxml_time
        total_regex += regex_time
        total_markdownify += mark_time

        print(
            f"{filename:<30} {auto_time:<12.6f} {lxml_time:<12.6f} {regex_time:<12.6f} {mark_time:<12.6f}"
        )

    # Print totals
    print("-" * 90)
    print(
        f"{'TOTAL':<30} {total_auto:<12.6f} {total_lxml:<12.6f} {total_regex:<12.6f} {total_markdownify:<12.6f}"
    )

    # Print average ratios compared to markdownify
    if total_markdownify > 0:
        print(
            f"Average speedup vs markdownify:  AutoParser: {total_markdownify / total_auto:.2f}x  "
            f"LXML: {total_markdownify / total_lxml:.2f}x  "
            f"Regex: {total_markdownify / total_regex:.2f}x"
        )

    # Simple assertion to make pytest happy
    assert True


# Individual file benchmark tests
@pytest.mark.skip(reason="Warning: This test is slow and should be run separately")
def test_benchmark_by_complexity(test_html_files, benchmark):
    """Run benchmarks on individual files by complexity level."""

    # Group files by complexity level
    level1_files = [html for filename, html in test_html_files if "level1" in filename]
    level2_files = [html for filename, html in test_html_files if "level2" in filename]
    level3_files = [html for filename, html in test_html_files if "level3" in filename]

    # Create parsers
    auto_parser = AutoParser()
    lxml_config = ParserConfig(
        parser_type=ParserType.LXML, markdown_style=MarkdownStyle.GITHUB
    )
    regex_config = ParserConfig(
        parser_type=ParserType.REGEX, markdown_style=MarkdownStyle.GITHUB
    )
    lxml_parser = LXMLHTMLParser(lxml_config)
    regex_parser = RegexHTMLParser(regex_config)

    # Helper functions to safely parse files
    def safe_auto_parse(files):
        results = []
        for html in files:
            try:
                results.append(auto_parser.parse(html))
            except Exception:
                continue
        return results

    def safe_lxml_parse(files):
        results = []
        for html in files:
            try:
                results.append(lxml_parser.parse(html))
            except Exception:
                continue
        return results

    def safe_regex_parse(files):
        results = []
        for html in files:
            try:
                results.append(regex_parser.parse(html))
            except Exception:
                continue
        return results

    def safe_markdownify(files):
        results = []
        for html in files:
            try:
                results.append(markdownify(html))
            except Exception:
                continue
        return results

    # Benchmark each level
    if level1_files:
        benchmark.group = "Level 1 - Basic HTML"

        benchmark.name = "AutoParser"
        benchmark(lambda: safe_auto_parse(level1_files))

        benchmark.name = "LXML Parser"
        benchmark(lambda: safe_lxml_parse(level1_files))

        benchmark.name = "Regex Parser"
        benchmark(lambda: safe_regex_parse(level1_files))

        benchmark.name = "markdownify"
        benchmark(lambda: safe_markdownify(level1_files))

    if level2_files:
        benchmark.group = "Level 2 - Intermediate HTML"

        benchmark.name = "AutoParser"
        benchmark(lambda: safe_auto_parse(level2_files))

        benchmark.name = "LXML Parser"
        benchmark(lambda: safe_lxml_parse(level2_files))

        benchmark.name = "Regex Parser"
        benchmark(lambda: safe_regex_parse(level2_files))

        benchmark.name = "markdownify"
        benchmark(lambda: safe_markdownify(level2_files))

    if level3_files:
        benchmark.group = "Level 3 - Complex HTML"

        benchmark.name = "AutoParser"
        benchmark(lambda: safe_auto_parse(level3_files))

        benchmark.name = "LXML Parser"
        benchmark(lambda: safe_lxml_parse(level3_files))

        benchmark.name = "Regex Parser"
        benchmark(lambda: safe_regex_parse(level3_files))

        benchmark.name = "markdownify"
        benchmark(lambda: safe_markdownify(level3_files))


if __name__ == "__main__":
    pytest.main(["-xvs", os.path.basename(__file__)])
