"""Tests for url_static.py - static URL model generation."""

import os
import sys
import pytest
from pathlib import Path

from path_link.url_static import (
    generate_static_url_model_text,
    write_url_dataclass_file,
)
from path_link.url_model import ValidationMode


class TestGenerateStaticUrlModelText:
    """Tests for generate_static_url_model_text() function."""

    def test_generates_valid_python_code(self, tmp_path):
        """Test generates valid Python code."""
        # Create pyproject.toml with URLs
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            # Check basic structure
            assert "from dataclasses import dataclass" in code
            assert "class ProjectUrlsStatic" in code
            assert "api_url:" in code
            assert "web_url:" in code
            assert "localhost:8000" in code
            assert "localhost:3000" in code
        finally:
            os.chdir(original_cwd)

    def test_generates_sorted_fields(self, tmp_path):
        """Test generates fields in sorted order for stable diffs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
zebra_url = "http://localhost:9000"
alpha_url = "http://localhost:8000"
beta_url = "http://localhost:7000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            # Find positions of field names
            alpha_pos = code.find("alpha_url:")
            beta_pos = code.find("beta_url:")
            zebra_pos = code.find("zebra_url:")

            # Check sorted order
            assert alpha_pos < beta_pos < zebra_pos
        finally:
            os.chdir(original_cwd)

    def test_lenient_mode_accepts_localhost(self, tmp_path):
        """Test lenient mode generates code with localhost URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            assert "localhost:8000" in code
        finally:
            os.chdir(original_cwd)

    def test_strict_mode_accepts_public_urls(self, tmp_path):
        """Test strict mode generates code with public URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.STRICT)

            assert "api.example.com" in code
        finally:
            os.chdir(original_cwd)

    def test_handles_no_urls(self, tmp_path):
        """Test handles case with no URLs configured."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
# No urls section
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            # Should generate empty model with comment
            assert "class ProjectUrlsStatic" in code
            assert ("# No URLs configured" in code or "pass" in code)
        finally:
            os.chdir(original_cwd)

    def test_includes_auto_generated_comment(self, tmp_path):
        """Test includes auto-generated warning comment."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            assert "# This file is auto-generated" in code
            assert "Do not edit manually" in code
            assert "pathlink gen-static-urls" in code
        finally:
            os.chdir(original_cwd)

    def test_uses_frozen_dataclass(self, tmp_path):
        """Test uses frozen=True for immutability."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            code = generate_static_url_model_text(ValidationMode.LENIENT)

            assert "@dataclass(frozen=True)" in code
        finally:
            os.chdir(original_cwd)


class TestWriteUrlDataclassFile:
    """Tests for write_url_dataclass_file() function."""

    def test_writes_file_successfully(self, tmp_path):
        """Test writes static file successfully."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            # Check file exists
            assert output_file.exists()

            # Check file contents
            content = output_file.read_text()
            assert "class ProjectUrlsStatic" in content
            assert "api_url" in content
            assert "web_url" in content
            assert "localhost:8000" in content
        finally:
            os.chdir(original_cwd)

    def test_creates_parent_directories(self, tmp_path):
        """Test creates parent directories if they don't exist."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        output_file = tmp_path / "nested" / "dir" / "urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            assert output_file.exists()
            assert output_file.parent.exists()
        finally:
            os.chdir(original_cwd)

    def test_overwrites_existing_file(self, tmp_path):
        """Test overwrites existing file."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        output_file = tmp_path / "test_urls_static.py"

        # Create existing file with different content
        output_file.write_text("# Old content")

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            # Check file was overwritten
            content = output_file.read_text()
            assert "# Old content" not in content
            assert "class ProjectUrlsStatic" in content
        finally:
            os.chdir(original_cwd)

    def test_idempotent(self, tmp_path):
        """Test writing same config twice produces identical content."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Write twice
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)
            content1 = output_file.read_text()

            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)
            content2 = output_file.read_text()

            # Content should be identical
            assert content1 == content2
        finally:
            os.chdir(original_cwd)

    def test_generated_file_is_importable(self, tmp_path):
        """Test generated file can be imported as Python module."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            # Try to import and use the generated module
            sys.path.insert(0, str(tmp_path))
            try:
                import test_urls_static

                # Check class exists
                assert hasattr(test_urls_static, "ProjectUrlsStatic")

                # Instantiate the dataclass
                urls = test_urls_static.ProjectUrlsStatic()

                # Check attributes
                assert hasattr(urls, "api_url")
                assert hasattr(urls, "web_url")
                assert "localhost:8000" in urls.api_url
                assert "localhost:3000" in urls.web_url

                # Check frozen (immutable)
                with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
                    urls.api_url = "changed"

            finally:
                sys.path.remove(str(tmp_path))
                # Clean up imported module
                if "test_urls_static" in sys.modules:
                    del sys.modules["test_urls_static"]
        finally:
            os.chdir(original_cwd)

    def test_accepts_string_mode(self, tmp_path):
        """Test accepts mode as string."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode="strict")

            assert output_file.exists()
            content = output_file.read_text()
            assert "api_url" in content
        finally:
            os.chdir(original_cwd)

    def test_defaults_to_lenient_mode(self, tmp_path):
        """Test defaults to lenient mode when mode is None."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            # Don't specify mode
            write_url_dataclass_file(output_path=output_file, mode=None)

            # Should accept localhost (lenient mode)
            content = output_file.read_text()
            assert "localhost:8000" in content
        finally:
            os.chdir(original_cwd)

    def test_atomic_write_with_temp_file(self, tmp_path):
        """Test uses atomic write with temp file."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            # Temp file should be cleaned up
            temp_file = output_file.with_suffix(".tmp")
            assert not temp_file.exists()

            # Final file should exist
            assert output_file.exists()
        finally:
            os.chdir(original_cwd)


class TestStaticModelEquivalence:
    """Tests that static model matches dynamic model behavior."""

    def test_static_matches_dynamic(self, tmp_path):
        """Test static model fields match dynamic ProjectUrls fields."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
admin_url = "http://localhost:9000"
""")

        output_file = tmp_path / "test_urls_static.py"

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            # Generate static model
            write_url_dataclass_file(output_path=output_file, mode=ValidationMode.LENIENT)

            # Import static model
            sys.path.insert(0, str(tmp_path))
            try:
                import test_urls_static
                from path_link.url_factory import ProjectUrls

                # Get dynamic URLs
                dynamic_urls = ProjectUrls.from_pyproject(mode=ValidationMode.LENIENT)
                dynamic_dict = dynamic_urls.to_dict()

                # Get static URLs
                static_urls = test_urls_static.ProjectUrlsStatic()

                # Compare all fields
                for key, value in dynamic_dict.items():
                    assert hasattr(static_urls, key)
                    static_value = getattr(static_urls, key)
                    # Values should be identical
                    assert static_value == value

            finally:
                sys.path.remove(str(tmp_path))
                if "test_urls_static" in sys.modules:
                    del sys.modules["test_urls_static"]
        finally:
            os.chdir(original_cwd)
