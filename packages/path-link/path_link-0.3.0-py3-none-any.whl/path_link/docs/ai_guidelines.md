# Assistant Context — path-link v0.2.0

**Last Updated:** 2025-10-10
**Status:** Active (Production)
**Canonical Reference:** This document + CLAUDE.md

---

## Overview

`path-link` is a Python library for type-safe project path management using Pydantic models.

**Key Facts:**
- **Package:** `path-link` → imports as `project_paths`
- **Pattern:** Dynamic Pydantic model creation via factory methods (v2 API)
- **Tool:** `uv` for dependency management
- **Python:** 3.11+
- **Coverage Target:** ≥90% (enforced in CI)

**This project uses PTOOL v2 rules:**
- All paths managed through validated models
- Direct instantiation forbidden (raises `NotImplementedError`)
- Factory methods required

---

## Quick Start (5 Minutes)

### 1. Environment Setup

```bash
# Install dependencies (uv handles venv automatically)
uv pip install -e ".[test]"

# One-liner smoke test (verify installation)
uv run python -c "from path_link import ProjectPaths; p=ProjectPaths.from_pyproject(); print('✅ OK:', len(p.to_dict()), 'paths loaded')"
```

### 2. Basic Usage

```python
from path_link import ProjectPaths

# ✅ CORRECT: Use factory methods
paths = ProjectPaths.from_pyproject()         # Load from pyproject.toml
# OR
paths = ProjectPaths.from_config(".paths")    # Load from .paths file

# Access paths (all are pathlib.Path objects)
config_dir = paths.config_dir
settings = paths["settings_file"]  # Dict-style access

# ❌ FORBIDDEN: Direct instantiation
# paths = ProjectPaths()  # Raises NotImplementedError
```

### 3. Run Tests

```bash
uv run pytest                                    # All tests
uv run pytest --cov=src --cov-report=term       # With coverage
uv run pytest tests/test_validators.py          # Specific file
```

---

## Essential Commands

| Purpose | Command |
|---------|---------|
| **Install** | `uv pip install -e ".[test]"` |
| **Smoke test** | `uv run python -c "from path_link import ProjectPaths; p=ProjectPaths.from_pyproject(); print('✅ OK:', len(p.to_dict()))"` |
| **Run all tests** | `uv run pytest` |
| **Coverage check** | `uv run pytest --cov=src --cov-report=term-missing:skip-covered` |
| **Type check** | `uv run mypy src/` |
| **Lint** | `uv run ruff check .` |
| **Format** | `uv run ruff format .` |
| **Regenerate static model** | `uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"` |
| **Verify static sync** | `git diff --exit-code src/project_paths/project_paths_static.py` |
| **Access AI guidelines** | `uv run python -c "from path_link import get_ai_guidelines; print(get_ai_guidelines()[:200])"` |
| **Access dev guide** | `uv run python -c "from path_link import get_developer_guide; print(get_developer_guide()[:200])"` |
| **Access metadata** | `uv run python -c "import json; from path_link import get_metadata; print(json.loads(get_metadata())['version'])"` |
| **Run example** | `uv run python examples/minimal_project/src/main.py` |

---

## Critical Rules (PTOOL v2)

### ✅ Do

- **Use factory methods:**
  ```python
  paths = ProjectPaths.from_pyproject()      # For pyproject.toml
  paths = ProjectPaths.from_config(".paths") # For .paths files
  ```

- **Treat all values as `pathlib.Path` objects**

- **Create directories safely:**
  ```python
  path.mkdir(parents=True, exist_ok=True)
  ```

- **Validate paths:**
  ```python
  from path_link import validate_or_raise
  from path_link.builtin_validators import StrictPathValidator

  validator = StrictPathValidator(
      required=["config_dir", "data_dir"],
      must_be_dir=["config_dir"],
      allow_symlinks=False  # Default: blocks symlinks
  )
  validate_or_raise(paths, validator)
  ```

- **Keep `.paths` files simple:** key=value format only (no sections)

### ❌ Don't

- **Call `ProjectPaths()` directly** — v2 forbids direct instantiation (raises `NotImplementedError`)
- **Use `os.path` or raw `Path(...)` joins** in application code
- **Add INI sections** to `.paths` files (use dotenv format)
- **Edit `project_paths_static.py` manually** (auto-generated file)
- **Modify `PYTHONPATH`** (use editable install instead)

### 🛡️ Enforcement

**Compliance is automatically enforced by `tests/test_path_policy.py`**, which forbids:
- `os.path` usage in `src/**`
- Direct `Path(...)` calls in `src/**`
- Direct `ProjectPaths()` calls outside `src/project_paths/**` and `examples/**`

CI will fail if these patterns are detected.

---

## Instantiation Rules (v2)

**Factory methods only — direct instantiation is disabled.**

```python
# ✅ CORRECT: Load from pyproject.toml
paths = ProjectPaths.from_pyproject()

# ✅ CORRECT: Load from custom .paths file
paths = ProjectPaths.from_config(".paths")
paths = ProjectPaths.from_config("configs/custom.paths")

# ❌ FORBIDDEN: Direct instantiation
paths = ProjectPaths()  # Raises NotImplementedError by design
```

**Why:** V2 enforces factory pattern to ensure config is always loaded from a known source.

---

## Static Model Sync

**When to regenerate:** After any change to `[tool.path_link]` in `pyproject.toml`

```bash
# 1. Regenerate static model
uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"

# 2. Verify no drift (CI check)
git diff --exit-code src/project_paths/project_paths_static.py || \
    (echo "❌ Static model drift detected. Commit the regenerated file." && exit 1)
```

**Why:** Static model (`project_paths_static.py`) provides IDE autocomplete and type hints. Must match dynamic model or `tests/test_static_model_equivalence.py` fails.

**CI Enforcement:** `just check-regen` verifies static model is in sync.

---

## Security: TOCTOU Prevention

**TOCTOU** (Time-of-check to time-of-use) race conditions can create security vulnerabilities when filesystem state changes between checking a path and using it.

### Unsafe Pattern (Vulnerable)

```python
# ❌ VULNERABLE — filesystem can change between check and use
if not my_dir.exists():
    my_dir.mkdir()  # Race condition: symlink could be placed here

if not my_file.exists():
    my_file.write_text("data")  # Race condition: file could be created/linked
```

### Safe Pattern (Atomic)

```python
# ✅ SAFE — atomic directory creation
try:
    my_dir.mkdir(exist_ok=False)
except FileExistsError:
    if not my_dir.is_dir():  # Re-verify it's actually a directory
        raise

# ✅ SAFE — atomic file creation ('x' mode fails if exists)
try:
    with my_file.open("x") as f:
        f.write("data")
except FileExistsError:
    print("File already exists")
```

### Validator Protection

**`StrictPathValidator(allow_symlinks=False)` blocks both live and dangling symlinks by default.**

```python
from path_link.builtin_validators import StrictPathValidator

# Blocks symlinks (default behavior)
validator = StrictPathValidator(
    required=["config_dir"],
    allow_symlinks=False  # Default: False
)

# Allow symlinks only if explicitly needed
validator_permissive = StrictPathValidator(
    required=["config_dir"],
    allow_symlinks=True
)
```

**Security features:**
- Symlink detection: `path.is_symlink()` check before validation
- Dangling link detection: Catches broken symlinks
- Re-validation: Paths re-checked at use time, not cached

---

## Validation Framework

### Basic Validation

```python
from path_link import (
    ProjectPaths,
    validate_or_raise,
    ValidationResult,
    Finding,
    Severity
)
from path_link.builtin_validators import StrictPathValidator

# Load paths
paths = ProjectPaths.from_pyproject()

# Configure validator
validator = StrictPathValidator(
    required=["config_dir", "data_dir"],      # Must exist
    must_be_dir=["config_dir"],               # Must be directory
    must_be_file=["settings_file"],           # Must be file
    allow_symlinks=False                      # Block symlinks (default)
)

# Validate (raises PathValidationError on failure)
try:
    validate_or_raise(paths, validator)
    print("✅ All paths valid!")
except PathValidationError as e:
    print(f"❌ Validation failed:\n{e}")
```

### Manual Validation (No Exception)

```python
# Get ValidationResult without raising
result = validator.validate(paths)

if result.ok():
    print("✅ Validation passed")
else:
    # Inspect errors
    for error in result.errors():
        print(f"ERROR [{error.code}] {error.field}: {error.message}")

    # Inspect warnings
    for warning in result.warnings():
        print(f"WARN [{warning.code}] {warning.field}: {warning.message}")
```

### Custom Validators

```python
from dataclasses import dataclass
from path_link import ValidationResult, Finding, Severity

@dataclass
class MyValidator:
    """Custom validator example."""
    required_file: str

    def validate(self, paths) -> ValidationResult:
        result = ValidationResult()

        # Check custom condition
        config_path = paths.to_dict().get("config_dir")
        if config_path and not (config_path / self.required_file).exists():
            result.add(Finding(
                severity=Severity.ERROR,
                code="CUSTOM_FILE_MISSING",
                field="config_dir",
                message=f"Required file '{self.required_file}' not found"
            ))

        return result

# Use custom validator
validator = MyValidator(required_file="app.conf")
validate_or_raise(paths, validator)
```

---

## Accessing Documentation Programmatically

**New in v0.2.0:** Documentation is bundled in the package and accessible offline.

The package includes three functions to access documentation programmatically, even in airgapped or offline environments. This is especially useful for AI assistants helping users with the package.

```python
from path_link import get_ai_guidelines, get_developer_guide, get_metadata
import json

# Get AI assistant guidelines (this file - comprehensive usage patterns)
ai_docs = get_ai_guidelines()
print(f"AI Guidelines: {len(ai_docs):,} characters")

# Get developer guide (CLAUDE.md - architecture, development setup)
dev_docs = get_developer_guide()
print(f"Developer Guide: {len(dev_docs):,} characters")

# Get machine-readable metadata (assistant_handoff.json)
metadata_json = get_metadata()
metadata = json.loads(metadata_json)
print(f"Version: {metadata['version']}")
print(f"Public APIs: {metadata['public_api']}")
print(f"CLI Commands: {len(metadata['cli_commands'])} available")
```

**Use Cases:**
- **AI Assistants**: Provide context to AI agents helping users
- **Offline Environments**: Access docs without internet connection
- **Enterprise/Airgapped**: Full documentation in restricted environments
- **Automation**: Build tools that need package metadata programmatically

**Location:** Documentation is stored in `src/project_paths/docs/` and bundled via `[tool.setuptools.package-data]` in `pyproject.toml`.

---

## Troubleshooting

### Import Errors

```bash
# 1. Check Python version (must be 3.11+)
uv run python -c "import sys; print(sys.version)"

# 2. Verify editable install
uv pip list | grep path-link  # Should show editable install

# 3. Reinstall if needed
uv pip install -e ".[test]"

# 4. Test import
uv run python -c "import path_link; print('✅ Import OK')"
```

### Test Failures

```bash
# 1. Check if static model is out of sync
uv run pytest tests/test_static_model_equivalence.py -v

# 2. If failing, regenerate static model
uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"

# 3. Re-run all tests
uv run pytest -v
```

### "NotImplementedError" When Creating ProjectPaths

**This is expected behavior!** Direct instantiation is forbidden in v2.

```python
# ❌ This will fail
paths = ProjectPaths()  # NotImplementedError

# ✅ Use factory methods instead
paths = ProjectPaths.from_pyproject()
```

### Static Model Base Path Mismatch

**Symptom:** `test_static_equals_dynamic_values` fails with base_dir mismatch

**Cause:** Static model was generated in different environment (e.g., Docker `/app`)

**Fix:**
```bash
# Regenerate in current environment
uv run python -c "from path_link import write_dataclass_file; write_dataclass_file()"

# Verify fix
uv run pytest tests/test_static_model_equivalence.py -v
```

### Coverage Too Low

**Current target:** ≥90%

```bash
# Check current coverage
uv run pytest --cov=src --cov-report=term-missing:skip-covered

# Focus on uncovered lines
uv run pytest --cov=src --cov-report=term-missing | grep -A 5 "Missing"

# Add tests for uncovered code (priority: model.py, builder.py)
```

---

## Architecture Quick Reference

**Pattern:** Dynamic Pydantic model creation via factory methods

```
User Code
   ↓
ProjectPaths.from_pyproject()    ← Factory method
   ↓
builder.build_field_definitions() ← Loads config, builds Pydantic fields
   ↓
model.create_model()              ← Generates dynamic Pydantic class
   ↓
Returns: ProjectPathsDynamic      ← Instance inheriting _ProjectPathsBase
```

### Core Components

1. **model.py** - Factory methods (`from_pyproject()`, `from_config()`), `_ProjectPathsBase` class
2. **builder.py** - Config parsing (`get_paths_from_pyproject`, `get_paths_from_dot_paths`), field generation
3. **validation.py** - `ValidationResult`, `Finding`, `Severity`, `validate_or_raise()`
4. **builtin_validators/strict.py** - `StrictPathValidator` implementation
5. **builtin_validators/sandbox.py** - `SandboxPathValidator` implementation
6. **get_paths.py** - Static model generator (`write_dataclass_file()`)
7. **__init__.py** - Public API exports, documentation access functions (`get_ai_guidelines`, `get_developer_guide`, `get_metadata`)
8. **docs/** - Bundled documentation (ai_guidelines.md, developer_guide.md, metadata.json)

**See CLAUDE.md for detailed architecture explanation.**

---

## Assistant Behavior Guidelines

When working with this codebase, AI assistants MUST:

1. **Always use factory methods** — Never call `ProjectPaths()` directly
2. **Keep static model in sync** — Regenerate after `pyproject.toml` changes
3. **Follow `src` layout** — Use absolute imports: `from path_link.model import ...`
4. **Refer to this document first** — Before any path-related task
5. **Verify changes** — Run tests after modifications: `uv run pytest`
6. **Use atomic operations** — Follow TOCTOU prevention patterns
7. **Validate before writing** — Use `validate_or_raise()` before filesystem operations

### Example Pattern

```python
from path_link import ProjectPaths, validate_or_raise
from path_link.builtin_validators import StrictPathValidator

# 1. Load paths
paths = ProjectPaths.from_pyproject()

# 2. Validate
validator = StrictPathValidator(
    required=["config_dir", "data_dir"],
    must_be_dir=["config_dir", "data_dir"],
    allow_symlinks=False
)
validate_or_raise(paths, validator)

# 3. Use paths safely
config_dir = paths.config_dir
config_dir.mkdir(parents=True, exist_ok=True)

config_file = config_dir / "app.conf"
try:
    with config_file.open("x") as f:
        f.write("# Configuration\n")
except FileExistsError:
    print("Config already exists")
```

---

## Non-Negotiables

- **Do not modify `PYTHONPATH`** — All imports must resolve through editable install
- **Always work within activated virtual environment** — Use `uv` for consistency
- **Never edit auto-generated files** — `project_paths_static.py` is generated by tooling
- **Follow policy enforcement** — `tests/test_path_policy.py` will catch violations
- **Maintain test coverage** — Target ≥90%, enforced in CI

---

## Configuration Formats

### pyproject.toml

```toml
[tool.path_link.paths]
config_dir = "config"
data_dir = "data"
logs_dir = "logs"

[tool.path_link.files]
settings_file = "config/settings.json"
log_file = "logs/app.log"
```

### .paths (dotenv format)

```bash
# Simple key=value format (NO SECTIONS)
config_dir=config
data_dir=data
logs_dir=logs
settings_file=config/settings.json
log_file=logs/app.log
```

**Important:** `.paths` files use dotenv syntax (key=value) with **no `[section]` headers**.

### Environment Variable Expansion

**Both pyproject.toml and .paths files support environment variable and home directory expansion.**

```python
# Expansion happens automatically via os.path.expandvars() and os.path.expanduser()
```

**Supported patterns:**
- `${VAR}` - Expands to environment variable (empty string if undefined)
- `$VAR` - Alternative syntax
- `~` - Expands to user's home directory (`Path.home()`)
- `~/path` - Path under home directory

**Example .paths file:**
```bash
# Environment variables
data_dir=${DATA_ROOT}/files
cache_dir=/tmp/${USER}_cache

# Home directory expansion
config_dir=~/.config/myapp

# Combined
user_data=~/projects/${PROJECT_NAME}/data
```

**Example pyproject.toml:**
```toml
[tool.path_link.paths]
data_dir = "${DATA_ROOT}/app_data"
config_dir = "~/.config/myapp"
```

**Behavior:**
- Undefined environment variables expand to empty string (standard Python behavior)
- `~` always expands to actual user home directory
- Expansion occurs at load time in `builder.py:make_path_factory()`
- All paths are then resolved relative to `base_dir` unless absolute

---

## Documentation Index

**Primary References:**
- **CLAUDE.md** — Comprehensive development guide (architecture, patterns, testing)
- **README.md** — User-facing documentation and API reference
- **assistant_context.md** — This file (quick start + troubleshooting)

**Project Status:**
- **REFACTOR_PLAN_1.md** — Latest refactoring plan (evidence-based, YAGNI analysis)
- **REFACTOR_STATUS.md** — Execution status, metrics, and results
- **assistant_handoff.json** — Machine-readable project snapshot

**Policy & Standards:**
- **CODE_QUALITY.json** — Development policy (SOLID, KISS, YAGNI principles)
- **CHAIN_OF_THOUGHT_GOLDEN_ALL_IN_ONE.json** — Reasoning framework for changes

---

## Diagnostic Checklist

If you encounter issues, run these commands in order:

```bash
# 1. Check Python version
uv run python -c "import sys; print('Python:', sys.version)"  # Should be 3.11+

# 2. Check editable install
uv pip list | grep path-link  # Should show path with "(editable)"

# 3. Test import
uv run python -c "import path_link; print('✅ Import OK')"

# 4. Run smoke test
uv run python -c "from path_link import ProjectPaths; p=ProjectPaths.from_pyproject(); print('✅ OK:', len(p.to_dict()), 'paths loaded')"

# 5. Check config files
ls -l pyproject.toml .paths 2>/dev/null

# 6. Run full test suite
uv run pytest -v

# 7. Check coverage
uv run pytest --cov=src --cov-report=term

# 8. Verify static model sync
git diff src/project_paths/project_paths_static.py
```

---

## Known Issues & Recent Fixes

### ✅ Recently Resolved (2025-10-10)

1. **main.py policy violation** — Fixed direct `ProjectPaths()` call → `ProjectPaths.from_pyproject()`
2. **Static model base_dir hardcoding** — Fixed to use `Path.cwd` for portability (was hardcoded `/app`)
3. **Pytest collection warning** — Renamed `TestCoverageAnalyzer` → `CoverageAnalyzer`

### 🎯 Active Work

1. **Coverage improvement** — Current state meets project standards; target ≥90% enforced in CI
2. **Documentation consolidation** — Ongoing effort to reduce duplication between docs

---

## Summary

**path-link (v0.2.0)** provides type-safe, validated path management for Python projects.

**Core Principles:**
- Factory methods only (v2 API)
- Protocol-based validation
- Atomic filesystem operations
- Test-enforced policy compliance

**If code touches the filesystem, it must use PTOOL.**

---

**Project:** path-link v0.2.0
**Python:** 3.11+
**License:** MIT
**Package Manager:** uv
**Last Verified:** 2025-10-10 (all commands tested against current codebase)
