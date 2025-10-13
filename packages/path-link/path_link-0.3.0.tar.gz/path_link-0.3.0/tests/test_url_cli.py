"""Tests for URL CLI commands."""

import json
import subprocess


class TestPrintUrlsCommand:
    """Tests for 'ptool print-urls' command."""

    def test_print_urls_json_format(self, tmp_path):
        """Test print-urls outputs valid JSON."""
        # Create pyproject.toml with URLs
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        # Run command using python -m
        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Parse JSON output
        output = json.loads(result.stdout)
        assert isinstance(output, dict)
        assert "api_url" in output
        assert "web_url" in output
        assert "localhost" in output["api_url"]

    def test_print_urls_table_format(self, tmp_path):
        """Test print-urls with table format."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--src", "pyproject", "--format", "table"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "api_url" in result.stdout
        assert "localhost" in result.stdout

    def test_print_urls_from_dotenv(self, tmp_path):
        """Test print-urls loading from .urls file."""
        urls_file = tmp_path / ".urls"
        urls_file.write_text("api_url=http://localhost:8000\n")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--src", "dotenv"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "api_url" in output

    def test_print_urls_merged_sources(self, tmp_path):
        """Test print-urls with merged sources."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        urls_file = tmp_path / ".urls"
        urls_file.write_text("web_url=http://localhost:3000\n")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--src", "all"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "api_url" in output
        assert "web_url" in output

    def test_print_urls_lenient_mode(self, tmp_path):
        """Test print-urls in lenient mode accepts localhost."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--mode", "lenient", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "localhost" in output["api_url"]

    def test_print_urls_strict_mode_rejects_localhost(self, tmp_path):
        """Test print-urls in strict mode rejects localhost."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--mode", "strict", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Should fail validation
        assert result.returncode == 1
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_print_urls_no_urls_configured(self, tmp_path):
        """Test print-urls with no URLs configured."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
# No urls section
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output == {}


class TestValidateUrlsCommand:
    """Tests for 'ptool validate-urls' command."""

    def test_validate_urls_success(self, tmp_path):
        """Test validate-urls succeeds with valid URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "validate-urls", "--mode", "lenient", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "✅" in result.stdout or "valid" in result.stdout.lower()

    def test_validate_urls_failure(self, tmp_path):
        """Test validate-urls fails with invalid URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "validate-urls", "--mode", "strict", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Strict mode should reject localhost
        assert result.returncode == 1
        assert "❌" in result.stderr or "fail" in result.stderr.lower()

    def test_validate_urls_merged_sources(self, tmp_path):
        """Test validate-urls with merged sources."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
""")

        urls_file = tmp_path / ".urls"
        urls_file.write_text("web_url=https://www.example.com\n")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "validate-urls", "--mode", "strict", "--src", "all"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_validate_urls_strict_mode_public_urls(self, tmp_path):
        """Test validate-urls strict mode accepts public URLs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
web_url = "https://www.example.com"
""")

        result = subprocess.run(
            ["python", "-m", "path_link.cli", "validate-urls", "--mode", "strict", "--src", "pyproject"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "valid" in result.stdout.lower()


class TestGenStaticUrlsCommand:
    """Tests for 'ptool gen-static-urls' command."""

    def test_gen_static_urls_creates_file(self, tmp_path):
        """Test gen-static-urls creates static file."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
web_url = "http://localhost:3000"
""")

        output_file = tmp_path / "test_urls_static.py"

        result = subprocess.run(
            [
                "python",
                "-m",
                "path_link.cli",
                "gen-static-urls",
                "--mode",
                "lenient",
                "--output",
                str(output_file),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_file.exists()

        # Check file contents
        content = output_file.read_text()
        assert "class ProjectUrlsStatic" in content
        assert "api_url" in content
        assert "web_url" in content
        assert "localhost:8000" in content
        assert "localhost:3000" in content

    def test_gen_static_urls_strict_mode(self, tmp_path):
        """Test gen-static-urls with strict mode."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "https://api.example.com"
""")

        output_file = tmp_path / "test_urls_static.py"

        result = subprocess.run(
            [
                "python",
                "-m",
                "path_link.cli",
                "gen-static-urls",
                "--mode",
                "strict",
                "--output",
                str(output_file),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "api_url" in content
        assert "example.com" in content

    def test_gen_static_urls_idempotent(self, tmp_path):
        """Test gen-static-urls is idempotent."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
api_url = "http://localhost:8000"
""")

        output_file = tmp_path / "test_urls_static.py"

        # Generate twice
        for _ in range(2):
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "path_link.cli",
                    "gen-static-urls",
                    "--mode",
                    "lenient",
                    "--output",
                    str(output_file),
                ],
                cwd=tmp_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0

        # File should exist and be valid
        assert output_file.exists()
        content = output_file.read_text()
        assert "class ProjectUrlsStatic" in content

    def test_gen_static_urls_sorted_fields(self, tmp_path):
        """Test gen-static-urls generates sorted fields for stable diffs."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link.urls]
zebra_url = "http://localhost:9000"
alpha_url = "http://localhost:8000"
beta_url = "http://localhost:7000"
""")

        output_file = tmp_path / "test_urls_static.py"

        result = subprocess.run(
            [
                "python",
                "-m",
                "path_link.cli",
                "gen-static-urls",
                "--mode",
                "lenient",
                "--output",
                str(output_file),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Check fields are sorted
        content = output_file.read_text()
        alpha_pos = content.find("alpha_url")
        beta_pos = content.find("beta_url")
        zebra_pos = content.find("zebra_url")

        assert alpha_pos < beta_pos < zebra_pos

    def test_gen_static_urls_no_urls_configured(self, tmp_path):
        """Test gen-static-urls with no URLs configured."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.path_link]
# No urls section
""")

        output_file = tmp_path / "test_urls_static.py"

        result = subprocess.run(
            [
                "python",
                "-m",
                "path_link.cli",
                "gen-static-urls",
                "--mode",
                "lenient",
                "--output",
                str(output_file),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        # Should still succeed with empty model
        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "class ProjectUrlsStatic" in content
        assert "pass" in content or "# No URLs configured" in content


class TestCliIntegration:
    """Integration tests for CLI commands."""

    def test_help_shows_url_commands(self):
        """Test that ptool --help shows URL commands."""
        result = subprocess.run(
            ["python", "-m", "path_link.cli", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "print-urls" in result.stdout
        assert "validate-urls" in result.stdout
        assert "gen-static-urls" in result.stdout

    def test_print_urls_help(self):
        """Test print-urls --help."""
        result = subprocess.run(
            ["python", "-m", "path_link.cli", "print-urls", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--mode" in result.stdout
        assert "--format" in result.stdout
        assert "--src" in result.stdout

    def test_validate_urls_help(self):
        """Test validate-urls --help."""
        result = subprocess.run(
            ["python", "-m", "path_link.cli", "validate-urls", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--mode" in result.stdout
        assert "--src" in result.stdout

    def test_gen_static_urls_help(self):
        """Test gen-static-urls --help."""
        result = subprocess.run(
            ["python", "-m", "path_link.cli", "gen-static-urls", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "--mode" in result.stdout
        assert "--output" in result.stdout
