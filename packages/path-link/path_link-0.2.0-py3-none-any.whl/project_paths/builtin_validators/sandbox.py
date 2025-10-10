from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

from ..validation import Finding, Severity, ValidationResult

if TYPE_CHECKING:
    from ..model import _ProjectPathsBase


@dataclass
class SandboxPathValidator:
    """
    Validates that paths stay within a base directory sandbox.

    This is a security-focused validator that prevents path traversal attacks
    and ensures all paths remain within the project's base directory.

    Features:
    - Detects '..' path escape attempts
    - Validates paths stay within base_dir
    - Optionally allows absolute paths (with validation)
    - Configurable strict mode for maximum security
    """

    base_dir_key: str = "base_dir"
    """The key in ProjectPaths that represents the base directory."""

    check_paths: Iterable[str] = ()
    """Specific path keys to check. If empty, checks all paths."""

    allow_absolute: bool = False
    """Allow absolute paths that are within base_dir."""

    strict_mode: bool = True
    """In strict mode, block all attempts at path traversal, even if they resolve safely."""

    def validate(self, p: "_ProjectPathsBase") -> ValidationResult:
        """
        Validates that all paths stay within the base directory sandbox.

        Args:
            p: The ProjectPaths instance to validate.

        Returns:
            A ValidationResult containing all findings.
        """
        vr = ValidationResult()
        all_paths = p.to_dict()

        # Get base directory
        if self.base_dir_key not in all_paths:
            vr.add(
                Finding(
                    severity=Severity.ERROR,
                    code="SANDBOX_BASE_MISSING",
                    field=self.base_dir_key,
                    message=f"Sandbox base directory key '{self.base_dir_key}' not found in ProjectPaths.",
                )
            )
            return vr

        base_dir = Path(all_paths[self.base_dir_key])

        # Resolve base_dir to handle symlinks and get absolute path
        try:
            base_dir_resolved = base_dir.resolve()
        except (OSError, RuntimeError) as e:
            vr.add(
                Finding(
                    severity=Severity.ERROR,
                    code="SANDBOX_BASE_UNRESOLVABLE",
                    field=self.base_dir_key,
                    path=str(base_dir),
                    message=f"Cannot resolve base directory: {e}",
                )
            )
            return vr

        # Determine which paths to check
        if self.check_paths:
            keys_to_check = set(self.check_paths)
        else:
            # Check all paths except base_dir itself
            keys_to_check = set(all_paths.keys()) - {self.base_dir_key}

        for key in sorted(keys_to_check):
            if key not in all_paths:
                continue  # Skip missing keys - that's StrictPathValidator's job

            path = Path(all_paths[key])
            path_str = str(path)

            # Check 1: Detect suspicious '..' patterns in strict mode
            if self.strict_mode:
                parts = path.parts
                if ".." in parts:
                    vr.add(
                        Finding(
                            severity=Severity.ERROR,
                            code="PATH_TRAVERSAL_ATTEMPT",
                            field=key,
                            path=path_str,
                            message="Path contains '..' traversal pattern (blocked in strict mode)",
                        )
                    )
                    continue  # Don't proceed with further checks for this path

            # Check 2: Validate absolute paths if not allowed
            if path.is_absolute() and not self.allow_absolute:
                vr.add(
                    Finding(
                        severity=Severity.ERROR,
                        code="ABSOLUTE_PATH_BLOCKED",
                        field=key,
                        path=path_str,
                        message="Absolute paths not allowed (set allow_absolute=True to permit)",
                    )
                )
                continue

            # Check 3: Resolve path and verify it's within base_dir
            try:
                # For relative paths, resolve relative to base_dir
                if not path.is_absolute():
                    full_path = base_dir / path
                else:
                    full_path = path

                path_resolved = full_path.resolve()
            except (OSError, RuntimeError) as e:
                vr.add(
                    Finding(
                        severity=Severity.WARNING,
                        code="PATH_UNRESOLVABLE",
                        field=key,
                        path=path_str,
                        message=f"Cannot resolve path: {e}",
                    )
                )
                continue

            # Check if resolved path is within base_dir
            try:
                # relative_to() raises ValueError if path is not relative to base
                path_resolved.relative_to(base_dir_resolved)
            except ValueError:
                vr.add(
                    Finding(
                        severity=Severity.ERROR,
                        code="PATH_ESCAPES_SANDBOX",
                        field=key,
                        path=path_str,
                        message=f"Path escapes sandbox (resolves outside {base_dir_resolved})",
                    )
                )

        return vr
