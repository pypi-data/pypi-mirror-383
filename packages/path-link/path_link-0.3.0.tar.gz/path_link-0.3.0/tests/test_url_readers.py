"""Tests for URL reading functions in builder.py."""

import os
import pytest
from pathlib import Path

from path_link.builder import (
    get_urls_from_pyproject,
    get_urls_from_dot_urls,
    get_urls_merged,
)


class TestGetUrlsFromPyproject:
    """Tests for get_urls_from_pyproject() function."""

    def test_loads_urls_from_pyproject(self, tmp_path):
        """Test loading URLs from [tool.path_link.urls] section."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "https://example.com"
admin_url = "http://192.168.1.1:5000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_from_pyproject()

            assert isinstance(urls, dict)
            assert len(urls) == 3
            assert urls["api_url"] == "http://localhost:8000"
            assert urls["web_url"] == "https://example.com"
            assert urls["admin_url"] == "http://192.168.1.1:5000"
        finally:
            os.chdir(original_cwd)

    def test_returns_empty_dict_if_no_pyproject(self, tmp_path):
        """Test returns empty dict when pyproject.toml doesn't exist."""
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_from_pyproject()

            assert urls == {}
        finally:
            os.chdir(original_cwd)

    def test_returns_empty_dict_if_no_tool_section(self, tmp_path):
        """Test returns empty dict when [tool.path_link] doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test-project"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_from_pyproject()

            assert urls == {}
        finally:
            os.chdir(original_cwd)

    def test_returns_empty_dict_if_no_urls_section(self, tmp_path):
        """Test returns empty dict when urls section doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
# No urls section
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_from_pyproject()

            assert urls == {}
        finally:
            os.chdir(original_cwd)

    def test_raises_error_if_urls_not_dict(self, tmp_path):
        """Test raises TypeError if urls section is not a dict."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
urls = "not-a-dict"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(TypeError) as exc_info:
                get_urls_from_pyproject()

            assert "must be a table" in str(exc_info.value)
        finally:
            os.chdir(original_cwd)

    def test_handles_empty_urls_section(self, tmp_path):
        """Test handles empty urls section."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
# Empty section
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_from_pyproject()

            assert urls == {}
        finally:
            os.chdir(original_cwd)


class TestGetUrlsFromDotUrls:
    """Tests for get_urls_from_dot_urls() function."""

    def test_loads_urls_from_dotenv_file(self, tmp_path):
        """Test loading URLs from .urls file in dotenv format."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
api_url=http://localhost:8000
web_url=https://example.com
admin_url=http://192.168.1.1:5000
""")

        urls = get_urls_from_dot_urls(urls_file)

        assert isinstance(urls, dict)
        assert len(urls) == 3
        assert urls["api_url"] == "http://localhost:8000"
        assert urls["web_url"] == "https://example.com"
        assert urls["admin_url"] == "http://192.168.1.1:5000"

    def test_raises_error_if_file_not_found(self, tmp_path):
        """Test raises FileNotFoundError if .urls file doesn't exist."""
        nonexistent = tmp_path / "missing.urls"

        with pytest.raises(FileNotFoundError):
            get_urls_from_dot_urls(nonexistent)

    def test_filters_out_none_values(self, tmp_path):
        """Test filters out None values from empty lines."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
api_url=http://localhost:8000

web_url=https://example.com

""")

        urls = get_urls_from_dot_urls(urls_file)

        # Should only have the two actual URLs
        assert len(urls) == 2
        assert "api_url" in urls
        assert "web_url" in urls

    def test_handles_comments(self, tmp_path):
        """Test handles comments in .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
# This is a comment
api_url=http://localhost:8000
# Another comment
web_url=https://example.com
""")

        urls = get_urls_from_dot_urls(urls_file)

        assert len(urls) == 2
        assert urls["api_url"] == "http://localhost:8000"
        assert urls["web_url"] == "https://example.com"

    def test_handles_quotes(self, tmp_path):
        """Test handles quoted values in .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
api_url="http://localhost:8000"
web_url='https://example.com'
""")

        urls = get_urls_from_dot_urls(urls_file)

        # dotenv should strip quotes
        assert "localhost" in urls["api_url"]
        assert "example.com" in urls["web_url"]

    def test_handles_empty_file(self, tmp_path):
        """Test handles empty .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("")

        urls = get_urls_from_dot_urls(urls_file)

        assert urls == {}

    def test_handles_whitespace_only_file(self, tmp_path):
        """Test handles .urls file with only whitespace."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("\n\n   \n\n")

        urls = get_urls_from_dot_urls(urls_file)

        assert urls == {}


class TestGetUrlsMerged:
    """Tests for get_urls_merged() function - precedence and merging."""

    def test_merges_both_sources(self, tmp_path):
        """Test merges URLs from both pyproject.toml and .urls."""
        # Create pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        # Create .urls file
        urls_file = tmp_path / ".urls"
        urls_file.write_text("web_url=http://localhost:3000\n")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            # Both URLs should be present
            assert len(urls) == 2
            assert urls["api_url"] == "http://localhost:8000"
            assert urls["web_url"] == "http://localhost:3000"
        finally:
            os.chdir(original_cwd)

    def test_pyproject_takes_precedence(self, tmp_path):
        """Test that pyproject.toml values override .urls file."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:9999"
""")

        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8888\n")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            # pyproject.toml should win
            assert urls["api_url"] == "http://localhost:9999"
        finally:
            os.chdir(original_cwd)

    def test_missing_keys_are_merged(self, tmp_path):
        """Test that missing keys from either source are included."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
admin_url = "http://localhost:9000"
""")

        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
web_url=http://localhost:3000
db_url=http://localhost:5432
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            # All 4 URLs should be present
            assert len(urls) == 4
            assert "api_url" in urls
            assert "admin_url" in urls
            assert "web_url" in urls
            assert "db_url" in urls
        finally:
            os.chdir(original_cwd)

    def test_only_pyproject(self, tmp_path):
        """Test with only pyproject.toml (no .urls file)."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            assert len(urls) == 1
            assert urls["api_url"] == "http://localhost:8000"
        finally:
            os.chdir(original_cwd)

    def test_only_dotenv(self, tmp_path):
        """Test with only .urls file (no pyproject.toml)."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8000\n")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            assert len(urls) == 1
            assert urls["api_url"] == "http://localhost:8000"
        finally:
            os.chdir(original_cwd)

    def test_no_sources(self, tmp_path):
        """Test with no configuration sources."""
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            assert urls == {}
        finally:
            os.chdir(original_cwd)

    def test_custom_dotenv_path(self, tmp_path):
        """Test with custom .urls file path."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        custom_urls = tmp_path / "custom.urls"
        custom_urls.write_text("web_url=http://localhost:3000\n")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged(dotenv_path=custom_urls)

            assert len(urls) == 2
            assert "api_url" in urls
            assert "web_url" in urls
        finally:
            os.chdir(original_cwd)

    def test_custom_dotenv_path_not_exists(self, tmp_path):
        """Test with custom .urls file path that doesn't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        nonexistent = tmp_path / "missing.urls"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            # Should only load from pyproject, ignore missing .urls
            urls = get_urls_merged(dotenv_path=nonexistent)

            assert len(urls) == 1
            assert urls["api_url"] == "http://localhost:8000"
        finally:
            os.chdir(original_cwd)

    def test_complex_precedence_scenario(self, tmp_path):
        """Test complex scenario with multiple overlapping keys."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
admin_url = "http://localhost:9000"
shared_url = "http://pyproject-wins.com"
""")

        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
web_url=http://localhost:3000
db_url=http://localhost:5432
shared_url=http://dotenv-loses.com
another_url=http://localhost:7000
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = get_urls_merged()

            # Check all keys present
            assert len(urls) == 6
            assert "api_url" in urls
            assert "admin_url" in urls
            assert "web_url" in urls
            assert "db_url" in urls
            assert "shared_url" in urls
            assert "another_url" in urls

            # Check pyproject precedence
            assert urls["shared_url"] == "http://pyproject-wins.com"
            assert urls["shared_url"] != "http://dotenv-loses.com"
        finally:
            os.chdir(original_cwd)
