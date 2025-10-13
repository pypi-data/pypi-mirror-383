"""
path-link: Type-safe path configuration for Python projects

A powerful library for managing project paths with built-in validation,
static model generation, and comprehensive security features.

Quick Start
-----------
    >>> from path_link import ProjectPaths
    >>>
    >>> # Load paths from pyproject.toml
    >>> paths = ProjectPaths.from_pyproject()
    >>>
    >>> # Access paths (all are pathlib.Path objects)
    >>> config_dir = paths.config_dir
    >>> settings = paths["settings_file"]

Key Features
------------
- Dynamic path management from pyproject.toml or .paths files
- Type-safe static model generation for IDE support
- Built-in validators: StrictPathValidator, SandboxPathValidator
- Path traversal attack prevention
- CLI tool for validation and inspection
- Offline-accessible documentation

Documentation Access (Offline)
-------------------------------
Access comprehensive documentation programmatically, even in airgapped environments:

    >>> from path_link import get_ai_guidelines, get_developer_guide, get_metadata
    >>> import json
    >>>
    >>> # Get AI assistant usage patterns and best practices
    >>> ai_docs = get_ai_guidelines()
    >>> print(f"AI Guidelines: {len(ai_docs):,} characters")
    >>>
    >>> # Get architecture and development guide
    >>> dev_docs = get_developer_guide()
    >>>
    >>> # Get machine-readable metadata
    >>> metadata = json.loads(get_metadata())
    >>> print(f"Version: {metadata['version']}")
    >>> print(f"Public APIs: {len(metadata['public_api'])}")

Validation Example
------------------
    >>> from path_link import validate_or_raise, StrictPathValidator
    >>>
    >>> paths = ProjectPaths.from_pyproject()
    >>> validator = StrictPathValidator(
    ...     required=["config_dir", "data_dir"],
    ...     must_be_dir=["config_dir"],
    ...     allow_symlinks=False  # Security: block symlinks
    ... )
    >>> validate_or_raise(paths, validator)

CLI Commands
------------
    $ ptool print                    # Show all configured paths
    $ ptool validate --strict        # Validate project structure
    $ ptool gen-static               # Generate static model
    $ ptool --help                   # Full CLI reference

Critical Rules
--------------
- NEVER instantiate ProjectPaths() directly (raises NotImplementedError)
- ALWAYS use factory methods: from_pyproject() or from_config()
- Regenerate static model after pyproject.toml changes
- Use validators before filesystem operations

See Also
--------
- Full documentation: README.md in package root
- AI guidelines: get_ai_guidelines()
- Developer guide: get_developer_guide()
- Package metadata: get_metadata()
- GitHub: https://github.com/yourusername/path-link
"""

from importlib.resources import files

from path_link.model import ProjectPaths
from path_link.get_paths import write_dataclass_file
from path_link.validation import (
    Severity,
    Finding,
    ValidationResult,
    PathValidator,
    PathValidationError,
    validate_or_raise,
    CompositeValidator,
)
from path_link.builtin_validators.strict import StrictPathValidator
from path_link.builtin_validators.sandbox import SandboxPathValidator
from path_link.url_factory import ProjectUrls
from path_link.url_model import ValidationMode
from path_link.url_static import write_url_dataclass_file


def get_ai_guidelines() -> str:
    """
    Return AI assistant guidelines for working with this package.

    This provides comprehensive guidance for AI agents helping users with path-link,
    including usage patterns, critical rules, validation patterns, and troubleshooting.

    Returns:
        str: Full content of AI guidelines (formerly assistant_context.md)

    Example:
        >>> guidelines = get_ai_guidelines()
        >>> print(guidelines[:100])
    """
    return files("path_link.docs").joinpath("ai_guidelines.md").read_text()


def get_developer_guide() -> str:
    """
    Return developer guide for contributing to this package.

    This provides architecture details, development setup, testing patterns,
    and contribution guidelines for developers working on path-link.

    Returns:
        str: Full content of developer guide (formerly CLAUDE.md)

    Example:
        >>> guide = get_developer_guide()
        >>> print(guide[:100])
    """
    return files("path_link.docs").joinpath("developer_guide.md").read_text()


def get_metadata() -> str:
    """
    Return machine-readable project metadata.

    This provides structured information about the package including version,
    public API, validators, CLI commands, and architecture notes.

    Returns:
        str: JSON content of project metadata (formerly assistant_handoff.json)

    Example:
        >>> import json
        >>> metadata = json.loads(get_metadata())
        >>> print(metadata['version'])
    """
    return files("path_link.docs").joinpath("metadata.json").read_text()


__all__ = [
    "ProjectPaths",
    "write_dataclass_file",
    "Severity",
    "Finding",
    "ValidationResult",
    "PathValidator",
    "PathValidationError",
    "validate_or_raise",
    "CompositeValidator",
    "StrictPathValidator",
    "SandboxPathValidator",
    "ProjectUrls",
    "ValidationMode",
    "write_url_dataclass_file",
    "get_ai_guidelines",
    "get_developer_guide",
    "get_metadata",
]
