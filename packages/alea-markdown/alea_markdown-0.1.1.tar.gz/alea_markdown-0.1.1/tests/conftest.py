"""
Shared test fixtures and configuration for alea-markdown-converter tests.
"""

import pytest
from pathlib import Path


@pytest.fixture
def resources_dir() -> Path:
    """Return the path to the resources directory."""
    return Path(__file__).parent / "resources"


def html_test_files_all(resources_dir) -> list[Path]:
    """Return a list of HTML test files."""
    return sorted(resources_dir.rglob("*.html"))


def pair_test_files_all(resources_dir) -> list[tuple[Path, Path]]:
    """Return a list of .html with corresponding .md sidecar files."""
    return sorted(
        [
            (html_file, html_file.with_suffix(".md"))
            for html_file in resources_dir.rglob("*.html")
            if (html_file.with_suffix(".md")).exists()
        ]
    )


def html_test_files_level1(resources_dir):
    """Return a list of HTML test files in level1 directory."""
    return sorted(resources_dir.rglob("level1/*.html"))


def pair_test_files_level1(resources_dir):
    """Return a list of .html with corresponding .md sidecar files in level1 directory."""
    return sorted(
        [
            (html_file, html_file.with_suffix(".md"))
            for html_file in resources_dir.rglob("level1/*.html")
            if (html_file.with_suffix(".md")).exists()
        ]
    )


def html_test_files_level2(resources_dir):
    """Return a list of HTML test files in level2 directory."""
    return sorted(resources_dir.rglob("level2/*.html"))


def pair_test_files_level2(resources_dir):
    """Return a list of .html with corresponding .md sidecar files in level2 directory."""
    return sorted(
        [
            (html_file, html_file.with_suffix(".md"))
            for html_file in resources_dir.rglob("level2/*.html")
            if (html_file.with_suffix(".md")).exists()
        ]
    )


def html_test_files_level3(resources_dir):
    """Return a list of HTML test files in level3 directory."""
    return sorted(resources_dir.rglob("level3/*.html"))


def pair_test_files_level3(resources_dir):
    """Return a list of .html with corresponding .md sidecar files in level3 directory."""
    return sorted(
        [
            (html_file, html_file.with_suffix(".md"))
            for html_file in resources_dir.rglob("level3/*.html")
            if (html_file.with_suffix(".md")).exists()
        ]
    )
