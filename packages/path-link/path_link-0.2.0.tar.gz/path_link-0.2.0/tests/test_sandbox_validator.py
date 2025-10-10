"""Tests for the SandboxPathValidator."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from project_paths.model import _ProjectPathsBase
from project_paths.builtin_validators.sandbox import SandboxPathValidator


@pytest.fixture
def mock_paths_sandbox(tmp_path: Path) -> _ProjectPathsBase:
    """Provides a mock ProjectPaths instance with various path scenarios."""
    paths = MagicMock(spec=_ProjectPathsBase)
    base_dir = tmp_path / "project"
    base_dir.mkdir()

    # Create safe subdirectories
    (base_dir / "config").mkdir()
    (base_dir / "data").mkdir()
    (base_dir / "logs").mkdir()

    # Create a file outside base_dir for testing escapes
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.txt").touch()

    paths.to_dict.return_value = {
        "base_dir": base_dir,
        "config_dir": base_dir / "config",
        "data_dir": Path("data"),  # Relative path (safe)
        "logs_dir": Path("logs"),  # Relative path (safe)
        "absolute_safe": base_dir / "config" / "app.conf",  # Absolute within sandbox
        "absolute_unsafe": outside_dir / "secret.txt",  # Absolute outside sandbox
        "traversal_attempt": Path("../outside/secret.txt"),  # Path traversal attempt
        "nested_relative": Path("data/subdir"),  # Safe nested relative
    }
    return paths


class TestSandboxPathValidator:
    """Tests for the SandboxPathValidator."""

    def test_success_all_relative_paths_safe(self, mock_paths_sandbox):
        """Test validation succeeds when all paths are relative and within base_dir."""
        validator = SandboxPathValidator()
        result = validator.validate(mock_paths_sandbox)

        # Should only fail on absolute paths and traversal attempts
        errors = result.errors()
        error_codes = {e.code for e in errors}

        # We expect errors for absolute paths and traversal attempts
        assert (
            "ABSOLUTE_PATH_BLOCKED" in error_codes
            or "PATH_TRAVERSAL_ATTEMPT" in error_codes
        )

    def test_error_on_path_traversal_strict_mode(self, mock_paths_sandbox):
        """Test that '..' patterns are blocked in strict mode."""
        validator = SandboxPathValidator(strict_mode=True, allow_absolute=True)
        result = validator.validate(mock_paths_sandbox)

        errors = result.errors()
        traversal_errors = [e for e in errors if e.code == "PATH_TRAVERSAL_ATTEMPT"]

        assert len(traversal_errors) >= 1
        assert any(e.field == "traversal_attempt" for e in traversal_errors)

    def test_allow_path_traversal_non_strict_mode(self, mock_paths_sandbox):
        """Test that '..' patterns are allowed in non-strict mode if they resolve safely."""
        # Modify mock to have a safe '..' pattern
        paths_dict = mock_paths_sandbox.to_dict.return_value.copy()
        paths_dict["safe_traversal"] = Path(
            "data/../config"
        )  # Resolves to config (safe)
        mock_paths_sandbox.to_dict.return_value = paths_dict

        validator = SandboxPathValidator(strict_mode=False, allow_absolute=True)
        result = validator.validate(mock_paths_sandbox)

        # Should not have PATH_TRAVERSAL_ATTEMPT error for safe_traversal
        errors = result.errors()
        traversal_errors = [
            e
            for e in errors
            if e.code == "PATH_TRAVERSAL_ATTEMPT" and e.field == "safe_traversal"
        ]
        assert len(traversal_errors) == 0

    def test_error_on_absolute_path_outside_sandbox(self, mock_paths_sandbox):
        """Test that absolute paths outside base_dir are caught."""
        validator = SandboxPathValidator(allow_absolute=True, strict_mode=False)
        result = validator.validate(mock_paths_sandbox)

        errors = result.errors()
        escape_errors = [e for e in errors if e.code == "PATH_ESCAPES_SANDBOX"]

        assert len(escape_errors) >= 1
        assert any(e.field == "absolute_unsafe" for e in escape_errors)

    def test_success_on_absolute_path_within_sandbox(self, mock_paths_sandbox):
        """Test that absolute paths within base_dir are allowed when allow_absolute=True."""
        validator = SandboxPathValidator(
            allow_absolute=True, strict_mode=False, check_paths=["absolute_safe"]
        )
        result = validator.validate(mock_paths_sandbox)

        # absolute_safe should not have errors
        errors_for_field = [e for e in result.errors() if e.field == "absolute_safe"]
        assert len(errors_for_field) == 0

    def test_error_on_absolute_path_when_not_allowed(self, mock_paths_sandbox):
        """Test that absolute paths are blocked when allow_absolute=False."""
        validator = SandboxPathValidator(
            allow_absolute=False, check_paths=["absolute_safe"]
        )
        result = validator.validate(mock_paths_sandbox)

        errors = result.errors()
        absolute_errors = [e for e in errors if e.code == "ABSOLUTE_PATH_BLOCKED"]

        assert len(absolute_errors) >= 1
        assert any(e.field == "absolute_safe" for e in absolute_errors)

    def test_error_on_missing_base_dir(self):
        """Test that validation fails if base_dir key is missing."""
        paths = MagicMock(spec=_ProjectPathsBase)
        paths.to_dict.return_value = {"data_dir": Path("/tmp/data")}

        validator = SandboxPathValidator(base_dir_key="base_dir")
        result = validator.validate(paths)

        assert not result.ok()
        errors = result.errors()
        assert len(errors) == 1
        assert errors[0].code == "SANDBOX_BASE_MISSING"
        assert errors[0].field == "base_dir"

    def test_custom_base_dir_key(self, tmp_path):
        """Test that validator works with custom base_dir key name."""
        paths = MagicMock(spec=_ProjectPathsBase)
        custom_base = tmp_path / "custom_base"
        custom_base.mkdir()

        paths.to_dict.return_value = {
            "project_root": custom_base,
            "config": Path("config"),
        }

        validator = SandboxPathValidator(base_dir_key="project_root")
        result = validator.validate(paths)

        # Should succeed - no base_dir missing error
        base_errors = [e for e in result.errors() if e.code == "SANDBOX_BASE_MISSING"]
        assert len(base_errors) == 0

    def test_check_specific_paths_only(self, mock_paths_sandbox):
        """Test that check_paths parameter limits validation to specific keys."""
        validator = SandboxPathValidator(
            check_paths=["data_dir", "config_dir"],
            allow_absolute=False,
            strict_mode=False,
        )
        result = validator.validate(mock_paths_sandbox)

        # Only data_dir and config_dir should be checked
        # Other paths like traversal_attempt should not appear in findings
        fields_checked = {f.field for f in result.findings}

        # Should not check paths outside check_paths list
        assert "absolute_unsafe" not in fields_checked
        assert "traversal_attempt" not in fields_checked

    def test_relative_paths_resolve_to_base_dir(self, mock_paths_sandbox):
        """Test that relative paths are correctly resolved relative to base_dir."""
        validator = SandboxPathValidator(
            check_paths=["data_dir", "nested_relative"],
            allow_absolute=False,
            strict_mode=False,
        )
        result = validator.validate(mock_paths_sandbox)

        # Relative paths within base should be valid
        escape_errors = [
            e
            for e in result.errors()
            if e.code == "PATH_ESCAPES_SANDBOX"
            and e.field in ["data_dir", "nested_relative"]
        ]
        assert len(escape_errors) == 0

    def test_unresolvable_path_warning(self, tmp_path):
        """Test that unresolvable paths generate warnings."""
        paths = MagicMock(spec=_ProjectPathsBase)
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        # Create a path that can't be resolved (too many symlink levels, etc.)
        # For testing, we'll use a path with invalid characters if possible
        # On POSIX, most paths are valid, so we'll create a symlink loop
        link1 = base_dir / "link1"
        link2 = base_dir / "link2"
        link1.symlink_to(link2)
        link2.symlink_to(link1)

        paths.to_dict.return_value = {
            "base_dir": base_dir,
            "broken_link": Path("link1"),
        }

        validator = SandboxPathValidator(strict_mode=False)
        result = validator.validate(paths)

        # Should have a PATH_UNRESOLVABLE warning
        warnings = [f for f in result.findings if f.code == "PATH_UNRESOLVABLE"]
        assert len(warnings) >= 1

    def test_symlink_handling_in_base_dir(self, tmp_path):
        """Test that symlinks in base_dir path are resolved correctly."""
        # Create a real directory
        real_base = tmp_path / "real_base"
        real_base.mkdir()

        # Create a symlink to it
        link_base = tmp_path / "link_base"
        link_base.symlink_to(real_base)

        # Create subdirectory in real location
        (real_base / "data").mkdir()

        paths = MagicMock(spec=_ProjectPathsBase)
        paths.to_dict.return_value = {
            "base_dir": link_base,  # base_dir is a symlink
            "data_dir": Path("data"),
        }

        validator = SandboxPathValidator(strict_mode=False)
        result = validator.validate(paths)

        # Should succeed - symlink in base_dir should be resolved
        escape_errors = [e for e in result.errors() if e.code == "PATH_ESCAPES_SANDBOX"]
        assert len(escape_errors) == 0

    def test_all_error_codes_documented(self):
        """Test that all error codes used are properly documented."""
        expected_codes = {
            "SANDBOX_BASE_MISSING",
            "SANDBOX_BASE_UNRESOLVABLE",
            "PATH_TRAVERSAL_ATTEMPT",
            "ABSOLUTE_PATH_BLOCKED",
            "PATH_UNRESOLVABLE",
            "PATH_ESCAPES_SANDBOX",
        }

        # This is a documentation test - we just verify the codes exist in our implementation
        # Read the sandbox.py file to verify codes
        from pathlib import Path

        sandbox_file = (
            Path(__file__).parent.parent
            / "src"
            / "project_paths"
            / "builtin_validators"
            / "sandbox.py"
        )
        content = sandbox_file.read_text()

        for code in expected_codes:
            assert code in content, f"Error code {code} not found in sandbox.py"

    def test_empty_check_paths_validates_all(self, mock_paths_sandbox):
        """Test that empty check_paths validates all paths except base_dir."""
        validator = SandboxPathValidator(
            check_paths=[], allow_absolute=True, strict_mode=True
        )
        result = validator.validate(mock_paths_sandbox)

        # Should check all paths except base_dir
        fields_with_findings = {f.field for f in result.findings}

        # base_dir should not be in findings
        assert "base_dir" not in fields_with_findings

        # Other paths should be checked
        # At minimum, traversal_attempt should have a finding
        assert (
            "traversal_attempt" in fields_with_findings or len(fields_with_findings) > 0
        )

    def test_validator_is_idempotent(self, mock_paths_sandbox):
        """Test that running validator twice produces same results."""
        validator = SandboxPathValidator(allow_absolute=True, strict_mode=True)

        result1 = validator.validate(mock_paths_sandbox)
        result2 = validator.validate(mock_paths_sandbox)

        assert result1.findings == result2.findings
