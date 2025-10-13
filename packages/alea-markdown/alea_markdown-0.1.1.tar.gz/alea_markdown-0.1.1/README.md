# ALEA Markdown

A flexible, configurable HTML to Markdown conversion library for Python that 
supports extremely large HTML documents and provides auto-normalization of
output text.

## Features

- Multiple parser backends for different HTML parsing needs
  - Auto-selection based on content size or complexity
  - LXML parser for standard HTML documents
  - Regex parser for large documents or memory-constrained environments
  - Markdownify integration for small documents (optional dependency)
- Configurable Markdown style output
- Support for GitHub Flavored Markdown
- Handles tables, code blocks, and other rich HTML elements
- Command-line interface for batch processing files
- Normalizes output for consistent, clean Markdown

## Installation

```bash
pip install alea-markdown
```

For additional features:

```bash
pip install "alea-markdown[markdownify]"
```

## Quick Start

```python
from alea_markdown import AutoParser

# Initialize the parser
parser = AutoParser()

# Convert HTML to Markdown
markdown = parser.parse("<h1>Hello World</h1><p>This is a test.</p>")
print(markdown)
```

## Command Line Usage

```bash
# Convert a single file
alea-md convert input.html -o output.md

# Convert all HTML files in a directory
alea-md convert --dir input_directory --output-dir output_directory

# Specify parser and style
alea-md convert input.html -o output.md --parser lxml --style github
```

## How Auto Parser Works

The `AutoParser` selects the appropriate parser based on input HTML size:

- For small files (< 128KB by default): Tries markdownify first (if available), then LXML, then regex
- For medium files (128KB - 2MB): Tries LXML first, then markdownify, then regex
- For large files (> 2MB): Tries regex first, then LXML, then markdownify

If a parser fails to convert the HTML properly, AutoParser automatically falls back to the next parser in the list until it finds one that works successfully.

You can customize these thresholds:

```python
from alea_markdown import AutoParser, ParserConfig

# Custom thresholds (in bytes)
config = ParserConfig(
    small_size_threshold=256*1024,  # 256KB
    large_size_threshold=4*1024*1024  # 4MB
)
parser = AutoParser(parser_config=config)
```

## Parser Types

The library provides multiple parser backends:

- **Auto**: Automatically selects the most appropriate parser based on file size
- **LXML**: Fast and precise HTML parsing for most standard HTML documents
- **Regex**: Regular expression-based parser for very large documents
- **Markdownify**: Uses the markdownify library for small documents (requires optional dependency)
- **Rust**: See `alea-markdown-rust` library

## Configuration

```python
from alea_markdown import AutoParser, ParserConfig, MarkdownStyle

# Configure how the HTML is parsed
config = ParserConfig(
    markdown_style=MarkdownStyle.GITHUB,
    output_links=True,
    output_images=True,
    table_support=True,
    strikethrough_support=True,
)

# Create parser with configuration
parser = AutoParser(parser_config=config)

# Convert HTML to Markdown
markdown = parser.parse(html_content)
```

## Markdown Normalization

The library applies normalization to ensure consistent, clean Markdown output. Normalization is enabled by default in both the CLI and API.

### Normalization Features

- **Character Encoding**: Ensures all output is valid UTF-8, handling problematic characters (default: replaces invalid characters)
- **Consecutive Newlines**: Limits runs of empty lines (default: max 3)
- **Whitespace**: Trims trailing whitespace from each line
- **Headings**: Standardizes heading format (e.g., `### Heading` instead of `###Heading`)
- **Lists**: Uses consistent list markers (default: `-`)
- **Links**: Normalizes link formats with consistent spacing
- **Images**: Standardizes image syntax
- **Inline Spacing**: Ensures proper spacing around inline elements
- **Code Blocks**: Normalizes code block fences (```) with consistent syntax
- **Tables**: Formats tables with proper alignment and spacing

### Customizing Normalization

You can customize the normalizer behavior:

```python
from alea_markdown import AutoParser
from alea_markdown.normalizer import NormalizerConfig

# Configure normalizer
normalizer_config = NormalizerConfig(
    # Text formatting
    max_newlines=2,                  # Limit consecutive newlines
    trim_trailing_whitespace=True,   # Remove trailing spaces
    normalize_inline_spacing=True,   # Cleanup excessive spaces
    
    # Markdown elements
    normalize_headings=True,         # Standardize heading format
    normalize_list_markers=True,     # Use consistent list markers
    list_marker="-",                 # Specify list marker style
    normalize_links=True,            # Standardize link formatting
    normalize_images=True,           # Standardize image formatting
    normalize_code_blocks=True,      # Standardize code block fences
    normalize_tables=True,           # Format tables consistently
    
    # Encoding options
    normalize_encoding=True,         # Ensure valid character encoding
    encoding_errors="replace",       # How to handle encoding errors ('replace', 'ignore', 'strict')
    target_encoding="utf-8"          # Target encoding for output
)

# Create parser with custom normalizer
parser = AutoParser(normalizer_config=normalizer_config)
```

### Using the Builder Pattern

For more fluid configuration, you can use the builder pattern:

```python
from alea_markdown import AutoParser
from alea_markdown.normalizer import NormalizerBuilder

# Create normalizer with builder pattern
normalizer = (
    NormalizerBuilder()
    .with_max_newlines(2)
    .with_trim_whitespace(True)
    .with_heading_normalization(True)
    .with_list_normalization(True, "-")
    .with_link_normalization(True)
    .with_table_normalization(True)
    .with_encoding_normalization(True, "replace", "utf-8")
    .build()
)

# Create parser with custom normalizer
parser = AutoParser(normalizer_config=normalizer.config)
```

### Disabling Normalization

In the CLI, use the `--no-normalize` flag to disable normalization:

```bash
alea-md convert input.html -o output.md --no-normalize
```

In the API, pass `None` as the normalizer config:

```python
from alea_markdown import AutoParser

# Create parser with normalization disabled
parser = AutoParser(normalizer_config=None)
```

## Advanced Usage

```python
from alea_markdown import LXMLHTMLParser, ParserConfig, MarkdownStyle

# Use a specific parser directly
config = ParserConfig(markdown_style=MarkdownStyle.COMMONMARK)
parser = LXMLHTMLParser(config)

# Parse with additional options
markdown = parser.parse(html_content, include_title=False)
```

## License

MIT License - see LICENSE file for details.


## Benchmarks

```
----------------------------------------------------------------------------------------------------------------------------------------- benchmark: 33 tests -----------------------------------------------------------------------------------------------------------------------------------------
Name (time in us)                                                                                                    Min                    Max                   Mean                StdDev                 Median                 IQR            Outliers           OPS            Rounds  Iterations
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_benchmark_regex_parser_level1[whitespace_only-HTML with only whitespace]                                     8.8350 (1.0)          33.5732 (1.0)           9.8373 (1.0)          1.2951 (1.0)           9.5153 (1.0)        0.2817 (1.0)     1895;3036  101,653.4208 (1.0)       28582           1
test_benchmark_regex_parser_level1[empty-Empty HTML document with only a comment]                                 9.0948 (1.03)        148.8868 (4.43)         10.4338 (1.06)         2.6371 (2.04)          9.8320 (1.03)       0.3190 (1.13)    2130;4320   95,842.1215 (0.94)      35918           1
test_benchmark_regex_parser_level2[minimal_html-Minimal valid HTML document]                                     17.6970 (2.00)        181.4924 (5.41)         19.2374 (1.96)         1.9252 (1.49)         18.9869 (2.00)       0.4580 (1.63)     666;1773   51,981.9839 (0.51)      15956           1
test_benchmark_lxml_parser_level1[empty-Empty HTML document with only a comment]                                 43.3209 (4.90)        229.3042 (6.83)         49.0213 (4.98)        13.5932 (10.50)        45.9310 (4.83)       1.3802 (4.90)     408;1144   20,399.2855 (0.20)       9406           1
test_benchmark_lxml_parser_level1[whitespace_only-HTML with only whitespace]                                     43.8062 (4.96)        104.9400 (3.13)         48.0767 (4.89)         5.9757 (4.61)         46.3990 (4.88)       1.6848 (5.98)      496;796   20,800.0770 (0.20)       7159           1
test_benchmark_regex_parser_level1[html_no_doctype-HTML without DOCTYPE declaration]                             52.6411 (5.96)      3,054.8698 (90.99)        61.4002 (6.24)        37.8607 (29.23)        55.9092 (5.88)       2.0033 (7.11)     363;1220   16,286.5929 (0.16)       8124           1
test_benchmark_regex_parser_level1[basic_html4-HTML 4.01 document]                                               53.7396 (6.08)        218.7272 (6.51)         57.9527 (5.89)         5.8006 (4.48)         57.0691 (6.00)       1.8566 (6.59)      289;589   17,255.4596 (0.17)       7788           1
test_benchmark_regex_parser_level2[html_with_comments-HTML with extensive comments]                              54.8912 (6.21)        128.5160 (3.83)         60.3079 (6.13)         6.9020 (5.33)         58.5364 (6.15)       2.0587 (7.31)     576;1035   16,581.5667 (0.16)      10134           1
test_benchmark_regex_parser_level2[html_with_script_style-HTML with script and style tags]                       55.3839 (6.27)        179.9879 (5.36)         60.2632 (6.13)         7.8122 (6.03)         58.0798 (6.10)       2.3050 (8.18)      225;448   16,593.8878 (0.16)       4514           1
test_benchmark_regex_parser_level2[html_fragment-HTML fragment without proper HTML structure]                    55.4821 (6.28)      1,212.0842 (36.10)        60.1522 (6.11)        14.1506 (10.93)        58.6221 (6.16)       1.6454 (5.84)      260;875   16,624.5067 (0.16)       9379           1
test_benchmark_regex_parser_level1[xhtml_strict-XHTML strict document]                                           66.1709 (7.49)        348.2830 (10.37)        74.2685 (7.55)        15.5207 (11.98)        70.6729 (7.43)       2.5457 (9.04)      328;850   13,464.6501 (0.13)       7667           1
test_benchmark_lxml_parser_level2[minimal_html-Minimal valid HTML document]                                      75.8301 (8.58)        164.2229 (4.89)         83.3346 (8.47)        11.0930 (8.57)         80.2097 (8.43)       2.9765 (10.57)     377;624   11,999.8141 (0.12)       5976           1
test_benchmark_regex_parser_level2[html_with_entities-HTML with various HTML entities]                           85.5178 (9.68)        192.3661 (5.73)         91.5897 (9.31)         9.0872 (7.02)         89.6589 (9.42)       2.5615 (9.09)      263;603   10,918.2638 (0.11)       6841           1
test_benchmark_regex_parser_level1[basic_html5-HTML5 document with semantic elements]                            91.4419 (10.35)       328.8998 (9.80)         98.9367 (10.06)       17.0024 (13.13)        95.3679 (10.02)      2.4128 (8.56)      231;575   10,107.4728 (0.10)       6180           1
test_benchmark_lxml_parser_level2[html_with_script_style-HTML with script and style tags]                       133.8660 (15.15)       550.6380 (16.40)       155.7913 (15.84)       41.0827 (31.72)       146.7085 (15.42)      7.5861 (26.93)     151;359    6,418.8440 (0.06)       3650           1
test_benchmark_lxml_parser_level1[html_no_doctype-HTML without DOCTYPE declaration]                             136.5379 (15.45)       595.6949 (17.74)       155.2293 (15.78)       37.0625 (28.62)       147.0740 (15.46)      6.6479 (23.60)     158;400    6,442.0843 (0.06)       3575           1
test_benchmark_lxml_parser_level2[html_fragment-HTML fragment without proper HTML structure]                    141.3389 (16.00)       614.0210 (18.29)       162.0187 (16.47)       51.7390 (39.95)       151.3371 (15.90)      6.7549 (23.98)     144;309    6,172.1277 (0.06)       3657           1
test_benchmark_lxml_parser_level1[basic_html4-HTML 4.01 document]                                               144.5184 (16.36)       278.4310 (8.29)        156.6076 (15.92)       10.2378 (7.91)        154.5339 (16.24)      6.5273 (23.17)     163;139    6,385.3865 (0.06)       2303           1
test_benchmark_lxml_parser_level2[html_with_comments-HTML with extensive comments]                              147.7953 (16.73)       585.3390 (17.43)       166.5864 (16.93)       43.0296 (33.23)       159.2687 (16.74)      5.1481 (18.27)      97;251    6,002.8899 (0.06)       3644           1
test_benchmark_lxml_parser_level2[html_with_entities-HTML with various HTML entities]                           154.7793 (17.52)       712.6727 (21.23)       179.7876 (18.28)       36.8619 (28.46)       168.5461 (17.71)     10.5626 (37.49)     224;437    5,562.1174 (0.05)       2961           1
test_benchmark_lxml_parser_level3[broken_html_mismatched_tags-HTML with mismatched opening/closing tags]        164.5111 (18.62)       629.8590 (18.76)       188.7114 (19.18)       47.1990 (36.44)       179.9834 (18.92)      8.4350 (29.94)     110;200    5,299.0960 (0.05)       3052           1
test_benchmark_lxml_parser_level3[broken_html_unclosed_tags-HTML with unclosed tags]                            166.9922 (18.90)       412.4320 (12.28)       183.6628 (18.67)       22.0906 (17.06)       178.7709 (18.79)      7.0170 (24.91)     210;309    5,444.7617 (0.05)       3596           1
test_benchmark_regex_parser_level2[eurlex_example_01-EURLex example HTML document]                              177.5101 (20.09)       469.0778 (13.97)       194.2385 (19.75)       25.3515 (19.58)       187.7137 (19.73)      6.4401 (22.86)     275;450    5,148.3100 (0.05)       4159           1
test_benchmark_lxml_parser_level1[xhtml_strict-XHTML strict document]                                           190.4038 (21.55)       352.8320 (10.51)       209.0480 (21.25)       12.8762 (9.94)        206.6207 (21.71)      9.1069 (32.33)     264;139    4,783.5910 (0.05)       2614           1
test_benchmark_regex_parser_level2[html_with_tables-HTML with table structures]                                 236.3957 (26.76)       631.2653 (18.80)       263.6206 (26.80)       54.0484 (41.73)       250.5817 (26.33)      6.7935 (24.11)     143;334    3,793.3306 (0.04)       2909           1
test_benchmark_lxml_parser_level1[basic_html5-HTML5 document with semantic elements]                            246.7148 (27.92)       422.8251 (12.59)       267.2671 (27.17)       13.1133 (10.13)       264.8965 (27.84)     11.1526 (39.59)     285;101    3,741.5754 (0.04)       2432           1
test_benchmark_lxml_parser_level2[eurlex_example_01-EURLex example HTML document]                               459.6980 (52.03)       833.4070 (24.82)       497.5776 (50.58)       34.0335 (26.28)       490.9260 (51.59)     21.1881 (75.21)      104;92    2,009.7367 (0.02)       1614           1
test_benchmark_lxml_parser_level3[html_with_deep_nesting-HTML with deeply nested elements]                      564.9631 (63.95)     1,234.2539 (36.76)       618.8158 (62.90)       68.6869 (53.04)       601.8698 (63.25)     20.2348 (71.82)      78;131    1,615.9898 (0.02)       1280           1
test_benchmark_lxml_parser_level2[html_with_tables-HTML with table structures]                                  818.1534 (92.60)     1,635.0523 (48.70)       882.0623 (89.66)       76.6186 (59.16)       866.8364 (91.10)     36.0126 (127.83)      32;41    1,133.7068 (0.01)        701           1
test_regex_parser_performance                                                                                 1,720.5919 (194.75)    3,488.3916 (103.90)    1,831.6756 (186.20)     169.2794 (130.71)    1,790.8940 (188.21)    59.1706 (210.03)      26;35      545.9482 (0.01)        520           1
test_lxml_parser_performance                                                                                  4,822.3804 (545.83)   10,444.8968 (311.11)    5,338.9981 (542.73)     689.7570 (532.60)    5,139.4075 (540.12)   375.0953 (>1000.0)     13;15      187.3011 (0.00)        158           1
test_markdownify_performance                                                                                 12,612.1403 (>1000.0)  26,319.4600 (783.94)   13,905.0298 (>1000.0)  1,840.2742 (>1000.0)  13,378.3142 (>1000.0)  916.4810 (>1000.0)       5;5       71.9164 (0.00)         74           1
test_auto_parser_performance                                                                                 13,551.0028 (>1000.0)  31,938.2981 (951.30)   15,697.5428 (>1000.0)  3,646.3839 (>1000.0)  14,622.3032 (>1000.0)  927.0826 (>1000.0)       5;7       63.7042 (0.00)         67           1
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```



# Examples

`tests/resources/level2/eurlex_example_01.html`

## markdownify

```
xml version="1.0" encoding="UTF-8"?

C\_2005131EN.01000802.xml

| | | | |
| --- | --- | --- | --- |
| 28.5.2005 | EN | Official Journal of the European Union | C 131/8 |

---

Non-opposition to a notified concentration

(Case COMP/3725 — Cargill/Pagnan)

(2005/C 131/08)

(Text with EEA relevance)

On 22 March 2005, the Commission decided not to oppose the above notified concentration and to declare it compatible with the common market. This decision is based on Article 6(1)(b) of Council Regulation (EC) No 139/2004. The full text of the decision is available only in English and will be made public after it is cleared of any business secrets it may contain. It will be available:

| | |
| --- | --- |
| — | from the Europa competition web site (http://europa.eu.int/comm/competition/mergers/cases/). This web site provides various facilities to help locate individual merger decisions, including company, case number, date and sectoral indexes, |

| | |
| --- | --- |
| — | in electronic form on the EUR-Lex website under document number 32005M3725. EUR-Lex is the on-line access to European law. (http://europa.eu.int/eur-lex/lex) |

---
```

## lxml

```
# C_2005131EN.01000802.xml

| 28.5.2005 | EN | Official Journal of the European Union | C 131/8 |
| --------- | -- | -------------------------------------- | ------- |

---

Non-opposition to a notified concentration

(Case COMP/3725 — Cargill/Pagnan)

(2005/C 131/08)

(Text with EEA relevance)

On 22 March 2005, the Commission decided not to oppose the above notified concentration and to declare it compatible with the common market. This decision is based on Article 6(1)(b) of Council Regulation (EC) No 139/2004. The full text of the decision is available only in English and will be made public after it is cleared of any business secrets it may contain. It will be available:

| — | from the Europa competition web site (http://europa.eu.int/comm/competition/mergers/cases/). This web site provides various facilities to help locate individual merger decisions, including company, case number, date and sectoral indexes, |
| - | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| — | in electronic form on the EUR-Lex website under document number 32005M3725. EUR-Lex is the on-line access to European law. (http://europa.eu.int/eur-lex/lex) |
| - | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |

---
```

## regex

```
# C_2005131EN.01000802.xml

| 28.5.2005 | EN | Official Journal of the European Union | C 131/8 |
| --- | --- | --- | --- |

28.5.2005

EN

Official Journal of the European Union

C 131/8

---

Non-opposition to a notified concentration

(Case COMP/3725 — Cargill/Pagnan)

(2005/C 131/08)

(Text with EEA relevance)

On 22 March 2005, the Commission decided not to oppose the above notified concentration and to declare it compatible with the common market. This decision is based on Article 6(1)(b) of Council Regulation (EC) No 139/2004. The full text of the decision is available only in English and will be made public after it is cleared of any business secrets it may contain. It will be available:

| — | from the Europa competition web site (http://europa.eu.int/comm/competition/mergers/cases/). This web site provides various facilities to help locate individual merger decisions, including company, case number, date and sectoral indexes, |
| --- | --- |

—

from the Europa competition web site (http://europa.eu.int/comm/competition/mergers/cases/). This web site provides various facilities to help locate individual merger decisions, including company, case number, date and sectoral indexes,

| — | in electronic form on the EUR-Lex website under document number 32005M3725. EUR-Lex is the on-line access to European law. (http://europa.eu.int/eur-lex/lex) |
| --- | --- |

—

in electronic form on the EUR-Lex website under document number 32005M3725. EUR-Lex is the on-line access to European law. (http://europa.eu.int/eur-lex/lex)

---
```
