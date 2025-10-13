"""Diff utilities for markdown comparison in tests."""

from typing import Optional
import difflib
from pathlib import Path


def diff_markdown(expected: str, actual: str, context_lines: int = 3) -> str:
    """
    Generate a context-specific difference between expected and actual markdown text.

    This function uses difflib to create a unified diff between the expected and
    actual markdown strings, highlighting where the transformation failed.

    Args:
        expected: The expected markdown output
        actual: The actual markdown output
        context_lines: Number of context lines to include in the diff (default: 3)

    Returns:
        A string containing a unified diff with context about what failed
    """
    if expected == actual:
        return ""

    # Split the strings into lines
    expected_lines = expected.splitlines(keepends=True)
    actual_lines = actual.splitlines(keepends=True)

    # Generate unified diff
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile="expected",
        tofile="actual",
        n=context_lines,
        lineterm="",
    )

    # Join the diff lines into a string
    diff_text = "\n".join(diff)

    if not diff_text:
        # If difflib didn't produce output but strings are different,
        # handle potential whitespace or other invisible character differences
        if expected.strip() == actual.strip():
            return "Markdown texts differ only in whitespace or line endings."
        else:
            # Add detailed character-by-character comparison
            return (
                "Markdown texts differ but no line differences detected. "
                f"Expected length: {len(expected)}, Actual length: {len(actual)}"
            )

    return diff_text


def save_diff_to_file(diff: str, html_path: Path) -> Path:
    """
    Save the diff to a file with .diff extension next to the input HTML file.

    Args:
        diff: The diff content to save
        html_path: Path to the input HTML file

    Returns:
        Path to the created diff file
    """
    # Create the diff file path with the same name as the HTML file but with .diff extension
    diff_path = html_path.with_suffix(".diff")

    # Write the diff to the file
    diff_path.write_text(diff, encoding="utf-8")

    return diff_path


def assert_markdown_equal(
    expected: str,
    actual: str,
    msg: Optional[str] = None,
    html_path: Optional[Path] = None,
) -> None:
    """
    Assert that two markdown strings are equal, with a detailed diff if they're not.

    Args:
        expected: The expected markdown output
        actual: The actual markdown output
        msg: Optional message prefix for the assertion error
        html_path: Optional path to the input HTML file to save diff next to

    Raises:
        AssertionError: If the markdown strings don't match, with detailed diff
    """
    if expected != actual:
        diff = diff_markdown(expected, actual)

        # Save diff to file if html_path is provided
        if html_path and diff:
            diff_path = save_diff_to_file(diff, html_path)
            diff_info = f"Diff saved to: {diff_path}"
            if msg:
                msg = f"{msg}\n{diff_info}"
            else:
                msg = diff_info

        error_msg = f"Markdown transformation failed.\n\n{diff}"

        if msg:
            error_msg = f"{msg}\n{error_msg}"

        raise AssertionError(error_msg)
