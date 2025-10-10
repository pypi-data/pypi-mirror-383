import pytest
from pathlib import Path
from unittest.mock import MagicMock

from project_paths.model import _ProjectPathsBase
from project_paths.validation import (
    Severity,
    PathValidationError,
    validate_or_raise,
    CompositeValidator,
)
from project_paths.builtin_validators.strict import StrictPathValidator


@pytest.fixture
def mock_paths(tmp_path: Path) -> _ProjectPathsBase:
    """Provides a mock ProjectPaths instance with a temporary file structure."""
    paths = MagicMock(spec=_ProjectPathsBase)
    tmpdir = tmp_path

    # Create some files and directories
    (tmpdir / "config").mkdir()
    (tmpdir / "data").mkdir()
    (tmpdir / "app.log").touch()

    # Create a symlink for testing
    target_file = tmpdir / "real.txt"
    target_file.touch()
    symlink_path = tmpdir / "link.txt"
    symlink_path.symlink_to(target_file)

    paths.to_dict.return_value = {
        "config_dir": tmpdir / "config",
        "data_dir": tmpdir / "data",
        "log_file": tmpdir / "app.log",
        "symlink": symlink_path,
        "temp_file": tmpdir / "temp.tmp",  # Intentionally does not exist
    }
    return paths


class TestStrictPathValidator:
    """Tests for the StrictPathValidator."""

    def test_success_all_paths_exist(self, mock_paths):
        """Test validation succeeds when all required paths exist."""
        validator = StrictPathValidator(
            required=["config_dir", "log_file"],
            must_be_dir=["config_dir", "data_dir"],
            must_be_file=["log_file"],
            allow_symlinks=True,
        )
        result = validator.validate(mock_paths)
        assert result.ok()
        assert not result.findings

    def test_error_on_missing_required_path(self, mock_paths):
        """Test an error is reported for a missing required path."""
        validator = StrictPathValidator(required=["temp_file"])
        result = validator.validate(mock_paths)
        assert not result.ok()
        assert len(result.errors()) == 1
        error = result.errors()[0]
        assert error.severity == Severity.ERROR
        assert error.code == "MISSING_REQUIRED"
        assert error.field == "temp_file"

    def test_warning_on_missing_optional_path(self, mock_paths):
        """Test a warning is reported for a missing optional path."""
        validator = StrictPathValidator(required=[], must_be_file=["temp_file"])
        result = validator.validate(mock_paths)
        assert result.ok()
        warnings = [
            f
            for f in result.findings
            if f.severity == Severity.WARNING and f.code == "MISSING_OPTIONAL"
        ]
        assert len(warnings) == 1
        assert warnings[0].field == "temp_file"

    def test_error_on_wrong_path_type(self, mock_paths):
        """Test an error is reported when a path is not the expected type."""
        validator = StrictPathValidator(required=[], must_be_dir=["log_file"])
        result = validator.validate(mock_paths)
        assert not result.ok()
        error = result.errors()[0]
        assert error.code == "NOT_A_DIRECTORY"
        assert error.field == "log_file"

    def test_error_on_disallowed_symlink(self, mock_paths):
        """Test an error is reported for a disallowed symbolic link."""
        validator = StrictPathValidator(required=["symlink"], allow_symlinks=False)
        result = validator.validate(mock_paths)
        assert not result.ok()
        error = result.errors()[0]
        assert error.code == "SYMLINK_BLOCKED"
        assert error.field == "symlink"

    def test_key_not_found_is_error_when_required(self):
        """Test KEY_NOT_FOUND is an ERROR for a required key."""
        paths = MagicMock(spec=_ProjectPathsBase)
        paths.to_dict.return_value = {"existing_key": Path("/fake")}
        validator = StrictPathValidator(required=["missing_key"])
        result = validator.validate(paths)
        assert not result.ok()
        assert len(result.errors()) == 1
        error = result.errors()[0]
        assert error.code == "KEY_NOT_FOUND"
        assert error.severity == Severity.ERROR
        assert error.field == "missing_key"

    def test_dangling_symlink_is_blocked(self, tmp_path):
        """Test that a dangling symlink is correctly identified as blocked."""
        dangling_link = tmp_path / "dangling_link"
        dangling_link.symlink_to("non_existent_target")

        paths = MagicMock(spec=_ProjectPathsBase)
        paths.to_dict.return_value = {"dangling": dangling_link}

        validator = StrictPathValidator(
            required=[], must_be_file=["dangling"], allow_symlinks=False
        )
        result = validator.validate(paths)
        assert not result.ok()
        assert len(result.errors()) == 1
        error = result.errors()[0]
        assert error.code == "SYMLINK_BLOCKED"

    def test_config_conflict_is_error(self, mock_paths):
        """Test that a config conflict (dir and file) is an ERROR."""
        validator = StrictPathValidator(
            required=[], must_be_dir=["log_file"], must_be_file=["log_file"]
        )
        result = validator.validate(mock_paths)
        assert not result.ok()
        assert len(result.errors()) == 1
        error = result.errors()[0]
        assert error.code == "CONFLICTING_KIND_RULES"
        assert error.field == "log_file"


class TestCompositeValidator:
    """Tests for the CompositeValidator."""

    def test_aggregates_findings_and_preserves_order(self, mock_paths):
        """Test that it runs all validators and combines their findings in order."""
        validator1 = StrictPathValidator(required=["temp_file"])
        validator2 = StrictPathValidator(required=[], must_be_dir=["log_file"])

        composite = CompositeValidator(parts=[validator1, validator2])
        result = composite.validate(mock_paths)

        assert not result.ok()
        assert len(result.errors()) == 2
        # Check that findings are in the expected order from the validators
        assert result.errors()[0].code == "MISSING_REQUIRED"
        assert result.errors()[1].code == "NOT_A_DIRECTORY"

    def test_idempotence(self, mock_paths):
        """Test that running the same validator twice yields identical results."""
        validator = CompositeValidator(
            parts=[
                StrictPathValidator(required=["temp_file"]),
                StrictPathValidator(required=[], must_be_dir=["log_file"]),
            ]
        )
        result1 = validator.validate(mock_paths)
        result2 = validator.validate(mock_paths)
        assert result1.findings == result2.findings


class TestValidationHelpers:
    """Tests for helper functions in validation.py."""

    def test_validate_or_raise_success(self, mock_paths):
        """Test that validate_or_raise does not raise on a successful validation."""
        validator = StrictPathValidator(required=["config_dir"], allow_symlinks=True)
        try:
            validate_or_raise(mock_paths, validator)
        except PathValidationError:
            pytest.fail("validate_or_raise should not have raised an exception.")

    def test_validate_or_raise_failure(self, mock_paths):
        """Test that validate_or_raise raises PathValidationError on failure."""
        validator = StrictPathValidator(required=["temp_file"])

        with pytest.raises(PathValidationError) as exc_info:
            validate_or_raise(mock_paths, validator)

        assert not exc_info.value.result.ok()
        assert len(exc_info.value.result.errors()) == 1
        assert exc_info.value.result.errors()[0].code == "MISSING_REQUIRED"
        assert "MISSING_REQUIRED" in str(exc_info.value)
