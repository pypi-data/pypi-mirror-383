"""Tests for url_factory.py - ProjectUrls factory methods and mode determination."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from path_link.url_factory import (
    ProjectUrls,
    _get_validation_mode_from_env,
    _make_url_field,
    _build_url_field_definitions,
)
from path_link.url_model import ValidationMode
from pydantic import ValidationError


class TestProjectUrlsDirectInstantiation:
    """Test that direct instantiation is blocked."""

    def test_direct_instantiation_raises_error(self):
        """Test that ProjectUrls() raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            ProjectUrls()

        assert "Direct instantiation" in str(exc_info.value)
        assert "from_pyproject()" in str(exc_info.value)


class TestGetValidationModeFromEnv:
    """Tests for _get_validation_mode_from_env()."""

    def test_default_is_lenient(self):
        """Test default mode is lenient when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            mode = _get_validation_mode_from_env()
            assert mode == ValidationMode.LENIENT

    def test_explicit_lenient(self):
        """Test PTOOL_URL_MODE=lenient."""
        with patch.dict(os.environ, {"PTOOL_URL_MODE": "lenient"}):
            mode = _get_validation_mode_from_env()
            assert mode == ValidationMode.LENIENT

    def test_explicit_strict(self):
        """Test PTOOL_URL_MODE=strict."""
        with patch.dict(os.environ, {"PTOOL_URL_MODE": "strict"}):
            mode = _get_validation_mode_from_env()
            assert mode == ValidationMode.STRICT

    def test_case_insensitive(self):
        """Test env var is case-insensitive."""
        with patch.dict(os.environ, {"PTOOL_URL_MODE": "STRICT"}):
            mode = _get_validation_mode_from_env()
            assert mode == ValidationMode.STRICT

    def test_invalid_value_defaults_to_lenient(self):
        """Test invalid value defaults to lenient."""
        with patch.dict(os.environ, {"PTOOL_URL_MODE": "invalid"}):
            mode = _get_validation_mode_from_env()
            assert mode == ValidationMode.LENIENT


class TestMakeUrlField:
    """Tests for _make_url_field() function."""

    def test_lenient_field_localhost(self):
        """Test creating lenient field with localhost."""
        field_type, field_info = _make_url_field("http://localhost:8000", ValidationMode.LENIENT)
        assert field_type is str
        assert "localhost" in field_info.default

    def test_strict_field_public_url(self):
        """Test creating strict field with public URL."""
        field_type, field_info = _make_url_field("https://example.com", ValidationMode.STRICT)
        assert field_type is str
        assert "example.com" in field_info.default

    def test_strict_field_rejects_localhost(self):
        """Test strict field rejects localhost."""
        with pytest.raises(ValidationError):
            _make_url_field("http://localhost", ValidationMode.STRICT)

    def test_lenient_field_private_ip(self):
        """Test lenient field accepts private IP."""
        field_type, field_info = _make_url_field("http://192.168.1.1:5000", ValidationMode.LENIENT)
        assert field_type is str
        assert "192.168.1.1" in field_info.default


class TestBuildUrlFieldDefinitions:
    """Tests for _build_url_field_definitions() function."""

    def test_empty_dict_lenient(self):
        """Test building fields from empty dict."""
        fields = _build_url_field_definitions({}, ValidationMode.LENIENT)
        assert fields == {}

    def test_single_url_lenient(self):
        """Test building field from single URL in lenient mode."""
        url_dict = {"api_url": "http://localhost:8000/api"}
        fields = _build_url_field_definitions(url_dict, ValidationMode.LENIENT)

        assert "api_url" in fields
        field_type, field_info = fields["api_url"]
        assert field_type is str
        assert "localhost" in field_info.default

    def test_multiple_urls_strict(self):
        """Test building fields from multiple URLs in strict mode."""
        url_dict = {
            "api_url": "https://api.example.com",
            "web_url": "https://www.example.com",
        }
        fields = _build_url_field_definitions(url_dict, ValidationMode.STRICT)

        assert len(fields) == 2
        assert "api_url" in fields
        assert "web_url" in fields

    def test_invalid_url_raises_error(self):
        """Test that invalid URL raises ValidationError during field building."""
        url_dict = {"bad_url": "not-a-url"}

        with pytest.raises(ValidationError):
            _build_url_field_definitions(url_dict, ValidationMode.LENIENT)


class TestProjectUrlsFromPyproject:
    """Tests for ProjectUrls.from_pyproject() factory method."""

    def test_from_pyproject_with_urls(self, tmp_path):
        """Test loading URLs from pyproject.toml."""
        # Create pyproject.toml with URLs
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        # Change to tmp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_pyproject(mode=ValidationMode.LENIENT)

            # Check URLs are loaded
            assert hasattr(urls, "api_url")
            assert hasattr(urls, "web_url")
            assert "localhost" in urls.api_url
            assert "8000" in urls.api_url
        finally:
            os.chdir(original_cwd)

    def test_from_pyproject_empty(self, tmp_path):
        """Test loading from pyproject.toml with no URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
# No urls section
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_pyproject(mode=ValidationMode.LENIENT)

            # Should return empty model
            assert len(urls.to_dict()) == 0
        finally:
            os.chdir(original_cwd)

    def test_from_pyproject_strict_mode(self, tmp_path):
        """Test from_pyproject with strict mode."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_pyproject(mode=ValidationMode.STRICT)

            assert hasattr(urls, "api_url")
            assert "example.com" in urls.api_url
        finally:
            os.chdir(original_cwd)

    def test_from_pyproject_strict_rejects_localhost(self, tmp_path):
        """Test from_pyproject strict mode rejects localhost."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(ValidationError):
                ProjectUrls.from_pyproject(mode=ValidationMode.STRICT)
        finally:
            os.chdir(original_cwd)

    def test_from_pyproject_mode_from_env(self, tmp_path):
        """Test from_pyproject reads mode from PTOOL_URL_MODE env var."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Default env (lenient) should accept localhost
            with patch.dict(os.environ, {}, clear=True):
                urls = ProjectUrls.from_pyproject()
                assert "localhost" in urls.api_url
        finally:
            os.chdir(original_cwd)

    def test_from_pyproject_string_mode(self, tmp_path):
        """Test from_pyproject accepts mode as string."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://example.com"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            urls = ProjectUrls.from_pyproject(mode="strict")
            assert hasattr(urls, "api_url")
        finally:
            os.chdir(original_cwd)


class TestProjectUrlsFromConfig:
    """Tests for ProjectUrls.from_config() factory method."""

    def test_from_config_dotenv_file(self, tmp_path):
        """Test loading URLs from .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
api_url=http://localhost:8000/api
web_url=http://localhost:3000
""")

        urls = ProjectUrls.from_config(urls_file, mode=ValidationMode.LENIENT)

        assert hasattr(urls, "api_url")
        assert hasattr(urls, "web_url")
        assert "localhost" in urls.api_url
        assert "8000" in urls.api_url

    def test_from_config_strict_mode(self, tmp_path):
        """Test from_config with strict mode."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=https://api.example.com\n")

        urls = ProjectUrls.from_config(urls_file, mode=ValidationMode.STRICT)
        assert "example.com" in urls.api_url

    def test_from_config_file_not_found(self, tmp_path):
        """Test from_config raises error if file doesn't exist."""
        nonexistent = tmp_path / "missing.urls"

        with pytest.raises(FileNotFoundError):
            ProjectUrls.from_config(nonexistent, mode=ValidationMode.LENIENT)

    def test_from_config_string_path(self, tmp_path):
        """Test from_config accepts string path."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8000\n")

        urls = ProjectUrls.from_config(str(urls_file), mode=ValidationMode.LENIENT)
        assert hasattr(urls, "api_url")


class TestProjectUrlsFromMerged:
    """Tests for ProjectUrls.from_merged() factory method."""

    def test_from_merged_both_sources(self, tmp_path):
        """Test merging URLs from both pyproject.toml and .urls."""
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
            urls = ProjectUrls.from_merged(mode=ValidationMode.LENIENT)

            # Both URLs should be present
            assert hasattr(urls, "api_url")
            assert hasattr(urls, "web_url")
            assert "8000" in urls.api_url
            assert "3000" in urls.web_url
        finally:
            os.chdir(original_cwd)

    def test_from_merged_precedence(self, tmp_path):
        """Test that pyproject.toml takes precedence over .urls."""
        # Both define api_url
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
            urls = ProjectUrls.from_merged(mode=ValidationMode.LENIENT)

            # pyproject.toml value should win
            assert "9999" in urls.api_url
            assert "8888" not in urls.api_url
        finally:
            os.chdir(original_cwd)

    def test_from_merged_only_pyproject(self, tmp_path):
        """Test from_merged with only pyproject.toml."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_merged(mode=ValidationMode.LENIENT)

            assert hasattr(urls, "api_url")
        finally:
            os.chdir(original_cwd)

    def test_from_merged_only_dotenv(self, tmp_path):
        """Test from_merged with only .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8000\n")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_merged(mode=ValidationMode.LENIENT)

            assert hasattr(urls, "api_url")
        finally:
            os.chdir(original_cwd)

    def test_from_merged_custom_dotenv_path(self, tmp_path):
        """Test from_merged with custom .urls file path."""
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
            urls = ProjectUrls.from_merged(dotenv_path=custom_urls, mode=ValidationMode.LENIENT)

            assert hasattr(urls, "api_url")
            assert hasattr(urls, "web_url")
        finally:
            os.chdir(original_cwd)

    def test_from_merged_no_sources(self, tmp_path):
        """Test from_merged with no configuration sources."""
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            urls = ProjectUrls.from_merged(mode=ValidationMode.LENIENT)

            # Should return empty model
            assert len(urls.to_dict()) == 0
        finally:
            os.chdir(original_cwd)


class TestToDictMethod:
    """Tests for the to_dict() method on ProjectUrls instances."""

    def test_to_dict_returns_strings(self, tmp_path):
        """Test to_dict() returns string values."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8000\n")

        urls = ProjectUrls.from_config(urls_file, mode=ValidationMode.LENIENT)
        urls_dict = urls.to_dict()

        assert isinstance(urls_dict, dict)
        assert isinstance(urls_dict["api_url"], str)

    def test_to_dict_multiple_urls(self, tmp_path):
        """Test to_dict() with multiple URLs."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("""
api_url=http://localhost:8000
web_url=http://localhost:3000
admin_url=http://localhost:9000
""")

        urls = ProjectUrls.from_config(urls_file, mode=ValidationMode.LENIENT)
        urls_dict = urls.to_dict()

        assert len(urls_dict) == 3
        assert "api_url" in urls_dict
        assert "web_url" in urls_dict
        assert "admin_url" in urls_dict
