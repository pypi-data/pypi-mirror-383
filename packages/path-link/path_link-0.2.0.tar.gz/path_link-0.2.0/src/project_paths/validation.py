from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .model import _ProjectPathsBase


class Severity(Enum):
    """Defines the severity level of a validation finding."""

    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class Finding:
    """Represents a single, structured validation issue."""

    severity: Severity
    code: str
    message: str
    field: str | None = None
    path: str | None = None


@dataclass
class ValidationResult:
    """Aggregates findings from a validation run."""

    findings: list[Finding] = field(default_factory=list)

    def add(self, *items: Finding) -> None:
        """Adds one or more findings to the result."""
        self.findings.extend(items)

    def ok(self) -> bool:
        """Returns True if there are no findings with ERROR severity."""
        return not any(f.severity is Severity.ERROR for f in self.findings)

    def errors(self) -> list[Finding]:
        """Returns a list of all findings with ERROR severity."""
        return [f for f in self.findings if f.severity is Severity.ERROR]

    def warnings(self) -> list[Finding]:
        """Returns a list of all findings with WARNING severity."""
        return [f for f in self.findings if f.severity is Severity.WARNING]


class PathValidator(Protocol):
    """
    A protocol that all validator classes must implement.
    """

    def validate(self, p: "_ProjectPathsBase") -> ValidationResult: ...


@dataclass
class CompositeValidator:
    """Combines multiple validators and runs them in sequence."""

    parts: list[PathValidator]

    def validate(self, p: "_ProjectPathsBase") -> ValidationResult:
        out = ValidationResult()
        for v in self.parts:
            r = v.validate(p)
            out.add(*r.findings)
        return out


class PathValidationError(Exception):
    """Custom exception raised for validation failures."""

    def __init__(self, result: ValidationResult):
        errors = [f for f in result.findings if f.severity is Severity.ERROR]
        lines = [
            f"- [{f.severity.name}] {f.code} {f.field or ''} -> {f.path or ''}: {f.message}"
            for f in (errors or result.findings)
        ]
        super().__init__("\n".join(lines))
        self.result = result


def validate_or_raise(p: "_ProjectPathsBase", v: PathValidator) -> ValidationResult:
    """
    A helper function that runs a validator and raises an exception on failure.
    """
    res = v.validate(p)
    if not res.ok():
        raise PathValidationError(res)
    return res
