# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`path-link` is a Python library for type-safe project path management with built-in validation. It uses Pydantic models to dynamically create path configurations from `pyproject.toml` or custom `.paths` files, and can generate static dataclass models for enhanced IDE support.

## Development Setup

### Environment

Uses `uv` for dependency management:

```bash
# Setup environment
uv venv
source .venv/bin/activate  # macOS/Linux
uv pip install -e ".[test]"
```

The project must be installed in editable mode. Never modify `PYTHONPATH` - all imports resolve through the editable install.

### Common Commands

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_validators.py

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy src/

# Regenerate static model (required after pyproject.toml changes)
uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"

# Or use justfile commands
just test
just lint
just format
just regen
```

### Smoke Test

Verify setup is working:
```bash
uv run python scripts/smoke_import.py
# Or one-liner:
uv run python -c "from path_link import ProjectPaths; p = ProjectPaths.from_pyproject(); print('✅ OK:', len(p.to_dict()), 'paths loaded')"
```

## Architecture

### Core Components

1. **ProjectPaths Model** (`src/project_paths/model.py`)
   - Main API for path management
   - Uses Pydantic dynamic model creation via `create_model()`
   - Direct instantiation is disabled - use factory methods only:
     - `ProjectPaths.from_pyproject()` - loads from `[tool.path_link]` in pyproject.toml
     - `ProjectPaths.from_config(".paths")` - loads from dotenv-style files
   - All path access returns `pathlib.Path` objects
   - Supports dict-style access via `__getitem__`

2. **Builder System** (`src/project_paths/builder.py`)
   - `build_field_definitions()` - constructs Pydantic field definitions from config
   - `make_path_factory()` - creates lazy path resolvers with environment variable expansion
   - `get_paths_from_pyproject()` - TOML parser for pyproject.toml
   - `get_paths_from_dot_paths()` - dotenv parser for .paths files

3. **Validation Framework** (`src/project_paths/validation.py`)
   - Protocol-based system using `PathValidator` protocol
   - `ValidationResult` aggregates `Finding` objects with severity levels (INFO, WARNING, ERROR)
   - `validate_or_raise()` helper throws `PathValidationError` on failure
   - `CompositeValidator` chains multiple validators

4. **Built-in Validators** (`src/project_paths/builtin_validators/`)
   - `StrictPathValidator` - enforces path existence, type (file/dir), and symlink rules
     - Configurable via `required`, `must_be_dir`, `must_be_file`, `allow_symlinks` parameters
   - `SandboxPathValidator` - prevents path traversal attacks and enforces base directory sandbox
     - Configurable via `base_dir_key`, `allow_absolute`, `strict_mode`, `check_paths` parameters
     - Error codes: `PATH_TRAVERSAL_ATTEMPT`, `ABSOLUTE_PATH_BLOCKED`, `PATH_ESCAPES_SANDBOX`

5. **Static Model Generation** (`src/project_paths/get_paths.py`)
   - `write_dataclass_file()` generates `project_paths_static.py` from current config
   - Uses atomic file replacement via temp file to avoid TOCTOU issues
   - Must be regenerated after modifying `[tool.path_link]` in pyproject.toml

6. **Documentation Access** (`src/project_paths/__init__.py`)
   - `get_ai_guidelines()` - Returns AI assistant usage patterns (bundled assistant_context.md)
   - `get_developer_guide()` - Returns architecture and development guide (bundled CLAUDE.md)
   - `get_metadata()` - Returns machine-readable project metadata (bundled assistant_handoff.json)
   - Documentation bundled via `[tool.setuptools.package-data]` for offline access

### Configuration Format

In `pyproject.toml`:
```toml
[tool.path_link.paths]
config_dir = "config"
data_dir = "data"

[tool.path_link.files]
settings_file = "config/settings.json"
```

In `.paths` files (dotenv format, no sections):
```
config_dir=config
data_dir=data
settings_file=config/settings.json
```

### Import Structure

The project uses `src` layout. All imports should be absolute from package name:
```python
from path_link import ProjectPaths, ValidationResult, StrictPathValidator
from path_link.model import _ProjectPathsBase
from path_link.validation import Finding, Severity
```

## Critical Rules

### ProjectPaths Usage

**Correct:**
```python
from path_link import ProjectPaths

# Load from pyproject.toml
paths = ProjectPaths.from_pyproject()

# Load from custom config
paths = ProjectPaths.from_config(".paths")

# Access paths
config = paths.config_dir
settings = paths["settings_file"]
```

**Incorrect:**
```python
# NEVER do this - direct instantiation is disabled
paths = ProjectPaths()  # Raises NotImplementedError
```

### Static Model Sync

After any change to `[tool.path_link]` in pyproject.toml, you MUST regenerate the static model:
```bash
uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"
```

The CI check `just check-regen` verifies this file is in sync.

### TOCTOU Prevention

Avoid time-of-check-time-of-use vulnerabilities in filesystem operations:

**Unsafe:**
```python
if not path.exists():
    path.mkdir()  # Race condition possible
```

**Safe:**
```python
try:
    path.mkdir(exist_ok=False)
except FileExistsError:
    if not path.is_dir():
        raise
```

The `StrictPathValidator` includes `allow_symlinks` parameter to mitigate symlink-based attacks.

### Path Traversal Protection

Use `SandboxPathValidator` to prevent path traversal attacks and ensure paths stay within the project sandbox:

**Maximum Security (Recommended):**
```python
from path_link import ProjectPaths, SandboxPathValidator

paths = ProjectPaths.from_pyproject()
validator = SandboxPathValidator(
    base_dir_key="base_dir",
    allow_absolute=False,  # Block all absolute paths
    strict_mode=True,      # Block '..' patterns
    check_paths=[]         # Check all paths
)

result = validator.validate(paths)
if not result.ok():
    for error in result.errors():
        print(f"Security issue: {error.code} in {error.field}")
```

**Permissive Mode (Allow absolute paths within sandbox):**
```python
validator = SandboxPathValidator(
    allow_absolute=True,   # Allow absolute paths if within base_dir
    strict_mode=False      # Allow '..' if it resolves safely
)
```

**Security Features:**
- Detects `..` path traversal patterns in strict mode
- Validates all paths resolve within `base_dir` after symlink resolution
- Configurable absolute path handling
- Clear error codes for security violations

**Error Codes:**
- `PATH_TRAVERSAL_ATTEMPT` - Path contains `..` pattern (strict mode only)
- `ABSOLUTE_PATH_BLOCKED` - Absolute path not allowed (when `allow_absolute=False`)
- `PATH_ESCAPES_SANDBOX` - Resolved path is outside `base_dir`
- `SANDBOX_BASE_MISSING` - Base directory key not found
- `SANDBOX_BASE_UNRESOLVABLE` - Cannot resolve base directory
- `PATH_UNRESOLVABLE` - Cannot resolve path (warning level)

## Testing

### Test Structure

- Tests mirror source structure: `src/project_paths/model.py` → `tests/test_model.py`
- Tests use pytest fixtures and `tmp_path` for isolated filesystem operations
- Mock `_ProjectPathsBase` instances in tests using `MagicMock(spec=_ProjectPathsBase)`

### Running Tests

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_validators.py

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Single test
uv run pytest tests/test_validators.py::test_strict_validator_required
```

## Validation Patterns

### Basic Validation
```python
from path_link import ProjectPaths, validate_or_raise, StrictPathValidator

paths = ProjectPaths.from_pyproject()
validator = StrictPathValidator(
    required=["config_dir", "data_dir"],
    must_be_dir=["config_dir"],
    must_be_file=["settings_file"]
)

# Raises PathValidationError on failure
validate_or_raise(paths, validator)
```

### Composite Validation
```python
from path_link import CompositeValidator

validator = CompositeValidator(parts=[
    StrictPathValidator(required=["config_dir"]),
    CustomValidator()
])

result = validator.validate(paths)
if not result.ok():
    for error in result.errors():
        print(f"{error.code}: {error.message}")
```

### Custom Validators

Implement the `PathValidator` protocol:
```python
from dataclasses import dataclass
from path_link import ValidationResult, Finding, Severity

@dataclass
class CustomValidator:
    def validate(self, paths) -> ValidationResult:
        result = ValidationResult()
        # Add validation logic
        if some_condition:
            result.add(Finding(
                severity=Severity.ERROR,
                code="CUSTOM_ERROR",
                field="field_name",
                message="Error description"
            ))
        return result
```

## Accessing Documentation Programmatically

The package includes bundled documentation accessible via three helper functions. This enables offline access and is especially useful for AI assistants helping users.

```python
from path_link import get_ai_guidelines, get_developer_guide, get_metadata
import json

# Access AI assistant guidelines (assistant_context.md)
ai_docs = get_ai_guidelines()

# Access developer guide (this file - CLAUDE.md)
dev_docs = get_developer_guide()

# Access machine-readable metadata (assistant_handoff.json)
metadata = json.loads(get_metadata())
print(f"Version: {metadata['version']}")
print(f"Public APIs: {len(metadata['public_api'])}")
```

**Location:** Documentation files are stored in `src/project_paths/docs/` and bundled with the package via `[tool.setuptools.package-data]` in `pyproject.toml`.

**Use Cases:**
- AI assistants helping users with the package
- Offline/airgapped environments
- Programmatic access to package metadata

## Package Structure

```
src/project_paths/
├── __init__.py          # Public API exports + documentation access functions
├── model.py             # ProjectPaths class and factory methods
├── builder.py           # Config loading and field building
├── get_paths.py         # Static model generation
├── validation.py        # Validation framework
├── project_paths_static.py  # Auto-generated static model
├── cli.py               # CLI tool (ptool command)
├── builtin_validators/
│   ├── __init__.py
│   ├── strict.py        # StrictPathValidator
│   └── sandbox.py       # SandboxPathValidator
└── docs/                # Bundled documentation (accessible offline)
    ├── ai_guidelines.md       # AI assistant usage patterns (assistant_context.md)
    ├── developer_guide.md     # Architecture & development (CLAUDE.md)
    └── metadata.json          # Machine-readable metadata (assistant_handoff.json)

tests/
├── test_validators.py
├── test_sandbox_validator.py
├── test_static_model_equivalence.py
├── test_path_policy.py
├── test_env_expansion.py
├── test_cli.py
└── test_example_project.py

scripts/
├── smoke_import.py      # Quick verification script
└── test_coverage_tool.py  # Test coverage analysis
```

## Dependencies

**Runtime:**
- `pydantic>=2.11.0` - Dynamic model creation and validation
- `python-dotenv>=1.0.1` - Parsing .paths files

**Development:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `mypy` - Type checking
- `ruff` - Linting and formatting

## Troubleshooting

### Import errors
- Ensure virtual environment is activated
- Verify editable install: `uv pip install -e ".[test]"`
- Check import uses package name: `from path_link import ...`

### Static model out of sync
- Run: `just check-regen` to detect
- Fix with: `just regen`

### Test failures
- Use `tmp_path` fixture for filesystem tests
- Mock `_ProjectPathsBase` when testing validators
- Ensure tests are isolated and don't depend on cwd state