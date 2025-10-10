from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

from ..validation import Finding, Severity, ValidationResult

if TYPE_CHECKING:
    from ..model import _ProjectPathsBase


@dataclass
class StrictPathValidator:
    """
    Validates path existence, type (file/directory), and symlinks based on configured rules.
    """

    required: Iterable[str]
    must_be_dir: Iterable[str] = ()
    must_be_file: Iterable[str] = ()
    allow_symlinks: bool = False

    def validate(self, p: "_ProjectPathsBase") -> ValidationResult:
        """
        Validates paths against the configured rules.

        Args:
            p: The ProjectPaths instance to validate.

        Returns:
            A ValidationResult containing all findings.
        """
        vr = ValidationResult()
        all_paths = p.to_dict()

        req_set = set(self.required)
        dir_set = set(self.must_be_dir)
        file_set = set(self.must_be_file)

        # Configuration conflict guard
        conflict = dir_set & file_set
        if conflict:
            for k in sorted(conflict):
                vr.add(
                    Finding(
                        severity=Severity.ERROR,
                        code="CONFLICTING_KIND_RULES",
                        field=k,
                        message="Field listed as both must_be_dir and must_be_file",
                    )
                )
            return vr

        keys_to_check = req_set | dir_set | file_set

        for k in keys_to_check:
            if k not in all_paths:
                is_required = k in req_set
                vr.add(
                    Finding(
                        severity=Severity.ERROR if is_required else Severity.WARNING,
                        code="KEY_NOT_FOUND",
                        field=k,
                        message=f"Path key '{k}' not found in ProjectPaths model.",
                    )
                )
                continue

            path = Path(all_paths[k])

            if not self.allow_symlinks and path.is_symlink():
                vr.add(
                    Finding(
                        severity=Severity.ERROR,
                        code="SYMLINK_BLOCKED",
                        field=k,
                        path=str(path),
                        message="Symlinks not permitted",
                    )
                )

            exists = path.exists()

            if k in req_set and not exists:
                vr.add(
                    Finding(
                        severity=Severity.ERROR,
                        code="MISSING_REQUIRED",
                        field=k,
                        path=str(path),
                        message="Required path missing",
                    )
                )
            elif not exists and k in (dir_set | file_set):
                vr.add(
                    Finding(
                        severity=Severity.WARNING,
                        code="MISSING_OPTIONAL",
                        field=k,
                        path=str(path),
                        message="Optional path missing",
                    )
                )

            if exists:
                if k in dir_set and not path.is_dir():
                    vr.add(
                        Finding(
                            severity=Severity.ERROR,
                            code="NOT_A_DIRECTORY",
                            field=k,
                            path=str(path),
                            message="Expected directory",
                        )
                    )
                if k in file_set and not path.is_file():
                    vr.add(
                        Finding(
                            severity=Severity.ERROR,
                            code="NOT_A_FILE",
                            field=k,
                            path=str(path),
                            message="Expected file",
                        )
                    )
        return vr
