# path-link

Type-safe path and URL configuration for Python projects with validation, static models, and IDE autocompletion.

**Features:**
- ✅ Local path management
- ✅ URL configuration with lenient/strict validation
- ✅ Static model generation for both paths and URLs
- ✅ CLI tools for validation and inspection

## 🚀 Features

### Path Management
- **Dynamic Path Management**: Load paths from `pyproject.toml` or custom `.paths` files
- **Type-Safe Static Models**: Generate static dataclasses for IDE autocomplete and type checking
- **Environment Variable Expansion**: Support for `$VAR`, `${VAR}`, and `~` expansion
- **Cross-Platform**: Works on Linux, Windows, and macOS

### URL Management
- **Dual Validation Modes**: Lenient (dev/localhost) and strict (production) URL validation
- **Multiple Sources**: Load from `pyproject.toml`, `.urls` files, or merge both
- **Static URL Models**: Generate dataclasses for type-safe URL access
- **CLI Tools**: Validate, print, and generate static models from command line

### General
- **Extensible Validation**: Protocol-based validator system with built-in and custom validators
- **Security Features**: Path traversal protection, sandbox validation
- **Minimal Dependencies**: Only requires `pydantic` and `python-dotenv`
- **Developer Friendly**: Full type hints, comprehensive testing (212 tests), and clear error messages

## 📦 Installation

### Using pip
```bash
pip install path-link
```

### Using uv (recommended)
```bash
uv add path-link
```

### From source
```bash
git clone https://github.com/jaahdytyspalvelu/path-link.git
cd path-link
uv sync
```

## 🎯 Quick Start

### Basic Usage

```python
from path_link import ProjectPaths

# Load paths from pyproject.toml
paths = ProjectPaths.from_pyproject()

# Access paths
print(paths.base_dir)  # Project root directory
print(paths.config)    # config directory path
print(paths.icons)     # icons directory path

# Dictionary-style access
config_path = paths["config"]

# Get all paths as dictionary
all_paths = paths.to_dict()
```

### Configuration in pyproject.toml

```toml
[tool.path_link.paths]
config = "config"
icons = "icons"
data = "data"
cache = ".cache"
logs = "logs"

[tool.path_link.files]
settings = "config/settings.json"
database = "data/app.db"
```

### Using Custom Configuration Files

```python
# Load from custom .paths file
paths = ProjectPaths.from_config(".paths")

# Load from specific location
paths = ProjectPaths.from_config("configs/my.paths")
```

### Environment Variable Expansion

Path configurations support environment variable expansion and home directory expansion (`~`). This is useful for creating portable configurations that adapt to different environments.

```python
# .paths file
# data_dir = ${DATA_ROOT}/files
# cache_dir = ~/my_app/cache
# config = ${APP_CONFIG:-/etc/myapp}

# Environment variables are expanded automatically
import os
os.environ["DATA_ROOT"] = "/custom/data"

paths = ProjectPaths.from_config(".paths")
print(paths.data_dir)   # /custom/data/files
print(paths.cache_dir)  # /home/username/my_app/cache
```

**Supported patterns:**
- `${VAR}` - Expands to environment variable value (empty string if undefined)
- `$VAR` - Alternative syntax for environment variables
- `~` - Expands to user's home directory
- `~/path` - Expands to path under user's home directory

**Example `.paths` file:**
```bash
# Production paths
data_dir = ${DATA_ROOT}/app_data
logs_dir = ${LOG_DIR:-/var/log/myapp}
cache_dir = /tmp/${USER}_cache

# User-specific paths
config_dir = ~/.config/myapp
```

**Example `pyproject.toml`:**
```toml
[tool.path_link.paths]
data_dir = "${DATA_ROOT}/files"
config_dir = "~/.config/myapp"
```

## 🌐 URL Management

path-link includes powerful URL configuration management with validation modes for different environments.

### Basic URL Usage

```python
from path_link import ProjectUrls, ValidationMode

# Load URLs from pyproject.toml (lenient mode by default)
urls = ProjectUrls.from_pyproject()

# Access URLs
print(urls.api_base)      # API base URL
print(urls.webhook_url)   # Webhook endpoint

# Dictionary-style access
api_url = urls["api_base"]

# Get all URLs as dictionary
all_urls = urls.to_dict()
```

### URL Configuration

**In `pyproject.toml`:**
```toml
[tool.path_link.urls]
api_base = "https://api.example.com"
webhook_url = "https://example.com/webhooks/callback"
docs_url = "https://docs.example.com"

# Development URLs (use lenient mode)
dev_api = "http://localhost:8000"
dev_db = "http://127.0.0.1:5432"
```

**In `.urls` file (dotenv format):**
```bash
# Production URLs
api_base=https://api.example.com
webhook_url=https://example.com/webhooks/callback

# Development URLs
dev_api=http://localhost:8000
dev_db=http://127.0.0.1:5432
```

### Validation Modes

**Lenient Mode (Development):**
- Accepts `localhost` and `127.0.0.1`
- Allows private IP addresses (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- Permits custom ports
- Suitable for development and testing

**Strict Mode (Production):**
- Only accepts public HTTP(S) URLs
- Rejects localhost and private IPs
- RFC-compliant validation
- Suitable for production deployments

```python
from path_link import ProjectUrls, ValidationMode

# Lenient mode (default) - allows localhost
dev_urls = ProjectUrls.from_pyproject(mode=ValidationMode.LENIENT)
# ✅ http://localhost:8000 is valid

# Strict mode - only public URLs
prod_urls = ProjectUrls.from_pyproject(mode=ValidationMode.STRICT)
# ❌ http://localhost:8000 raises ValidationError
# ✅ https://api.example.com is valid
```

### Loading from Multiple Sources

```python
# Load from .urls file only
urls = ProjectUrls.from_config(".urls")

# Merge pyproject.toml and .urls (pyproject takes precedence)
urls = ProjectUrls.from_merged()

# Merge with custom .urls file
urls = ProjectUrls.from_merged(dotenv_path="config/.urls.prod")
```

### Environment-Based Mode Selection

Set the validation mode via environment variable:

```bash
# Development
export PTOOL_URL_MODE=lenient
python your_app.py

# Production
export PTOOL_URL_MODE=strict
python your_app.py
```

```python
# Automatically uses environment variable
urls = ProjectUrls.from_pyproject()  # Respects PTOOL_URL_MODE
```

### Static URL Model Generation

Generate a static dataclass for IDE autocomplete:

```python
from path_link import write_url_dataclass_file, ValidationMode

# Generate with lenient validation (default)
write_url_dataclass_file()

# Generate with strict validation for production
write_url_dataclass_file(mode=ValidationMode.STRICT)

# Custom output location
write_url_dataclass_file(
    output_path="config/urls_static.py",
    mode=ValidationMode.LENIENT
)
```

Then import and use:

```python
from path_link.project_urls_static import ProjectUrlsStatic

urls = ProjectUrlsStatic()
# Full IDE autocomplete for all configured URLs!
print(urls.api_base)
```

### URL CLI Commands

```bash
# Print all URLs as JSON
pathlink print-urls

# Print in table format
pathlink print-urls --format table

# Validate URLs (lenient mode)
pathlink validate-urls

# Validate with strict mode
pathlink validate-urls --mode strict

# Generate static URL model
pathlink gen-static-urls

# Generate with strict mode
pathlink gen-static-urls --mode strict
```

## 🖥️ Command Line Interface

path-link includes a `pathlink` CLI for quick operations without writing Python code.

### Available Commands

```bash
# Print all configured paths as JSON
pathlink print

# Validate project structure
pathlink validate

# Generate static dataclass model
pathlink gen-static

# Show help
pathlink --help
```

### Command Reference

#### `pathlink print` - Display Paths

Prints all configured paths as formatted JSON.

```bash
# Print from pyproject.toml (default)
pathlink print

# Print from custom .paths file
pathlink print --source config --config my.paths

# Output example:
# {
#   "base_dir": "/home/user/project",
#   "config_dir": "/home/user/project/config",
#   "data_dir": "/home/user/project/data",
#   ...
# }
```

**Options:**
- `--source {pyproject,config}` - Configuration source (default: pyproject)
- `--config PATH` - Path to .paths file (default: .paths)

#### `pathlink validate` - Validate Paths

Validates that your project structure matches the configuration.

```bash
# Basic validation (check paths can be loaded)
pathlink validate

# Strict validation (check paths exist, no symlinks)
pathlink validate --strict

# Raise exception on validation failure
pathlink validate --strict --raise

# Validate from custom config
pathlink validate --source config --config production.paths
```

**Options:**
- `--source {pyproject,config}` - Configuration source (default: pyproject)
- `--config PATH` - Path to .paths file (default: .paths)
- `--strict` - Enable strict validation (paths must exist, correct types)
- `--raise` - Raise exception on validation failure (for CI/scripts)

**Exit codes:**
- `0` - Validation passed
- `1` - Validation failed or error occurred

#### `pathlink gen-static` - Generate Static Model

Generates a static dataclass for IDE autocomplete and type checking.

```bash
# Generate at default location (src/path_link/project_paths_static.py)
pathlink gen-static

# Generate at custom location
pathlink gen-static --out custom/path/static_paths.py
```

**Options:**
- `--out PATH` - Output path for static model

**When to use:** After modifying `[tool.path_link]` in `pyproject.toml` to keep static model in sync.

### CLI Usage Examples

**Quick project validation:**
```bash
cd your-project/
pathlink validate --strict
# ✅ All paths valid (strict mode)
```

**View all configured paths:**
```bash
pathlink print
# Outputs JSON with all resolved paths
```

**Generate static model for IDE support:**
```bash
pathlink gen-static
# ✅ Static model generated successfully
```

**CI/CD integration:**
```bash
# In your CI script
pathlink validate --strict --raise || exit 1
```

**Multiple environments:**
```bash
# Development
pathlink validate --source config --config .paths.dev

# Production
pathlink validate --source config --config .paths.prod
```

### With Validation

You can validate your project's structure by using one of the built-in validators.

```python
from path_link import ProjectPaths, validate_or_raise, PathValidationError
from path_link.builtin_validators import StrictPathValidator

# 1. Load your paths
paths = ProjectPaths.from_pyproject()

# 2. Configure a validator
# This example ensures a 'config' directory and a 'database' file exist.
validator = StrictPathValidator(
    required=["config", "database"],
    must_be_dir=["config"],
    must_be_file=["database"]
)

# 3. Validate and raise an exception on failure
try:
    validate_or_raise(paths, validator)
    print("✅ Project structure is valid.")
except PathValidationError as e:
    print(f"❌ Invalid project structure:\n{e}")

# Or, to handle results manually without raising an exception:
result = validator.validate(paths)
if not result.ok():
    for error in result.errors():
        print(f"Error: {error.message} (Code: {error.code})")
```

### Security: Sandbox Validation

The `SandboxPathValidator` prevents path traversal attacks by ensuring all paths stay within your project's base directory. This is crucial for applications that handle user input or load paths from external sources.

```python
from path_link import ProjectPaths
from path_link.builtin_validators import SandboxPathValidator

paths = ProjectPaths.from_pyproject()

# Create sandbox validator with security settings
validator = SandboxPathValidator(
    base_dir_key="base_dir",        # Key representing the base directory
    allow_absolute=False,            # Block absolute paths (recommended)
    strict_mode=True,                # Block '..' patterns (recommended)
    check_paths=[]                   # Empty = check all paths
)

result = validator.validate(paths)
if not result.ok():
    for error in result.errors():
        print(f"🔒 Security issue: {error.message}")
        print(f"   Field: {error.field}, Code: {error.code}")
```

**Security Features:**

- **Path Traversal Protection**: Detects and blocks `..` patterns in strict mode
- **Absolute Path Control**: Can block or allow absolute paths
- **Sandbox Verification**: Ensures resolved paths stay within base directory
- **Symlink Resolution**: Properly resolves symlinks before validation

**Error Codes:**

- `PATH_TRAVERSAL_ATTEMPT`: Path contains `..` pattern (strict mode)
- `ABSOLUTE_PATH_BLOCKED`: Absolute path not allowed
- `PATH_ESCAPES_SANDBOX`: Path resolves outside base directory
- `SANDBOX_BASE_MISSING`: Base directory key not found
- `SANDBOX_BASE_UNRESOLVABLE`: Cannot resolve base directory
- `PATH_UNRESOLVABLE`: Cannot resolve path (warning)

**Example Use Cases:**

```python
# 1. Maximum security - block everything suspicious
strict_sandbox = SandboxPathValidator(
    allow_absolute=False,
    strict_mode=True
)

# 2. Allow absolute paths within sandbox
permissive_sandbox = SandboxPathValidator(
    allow_absolute=True,
    strict_mode=False
)

# 3. Check specific paths only
targeted_sandbox = SandboxPathValidator(
    check_paths=["user_uploads", "temp_files"],
    strict_mode=True
)
```

## 🛠️ Advanced Features

### Static Model Generation

Generate a static dataclass for better IDE support:

```python
from path_link import write_dataclass_file

# Generate src/project_paths/project_paths_static.py
write_dataclass_file()
```

This creates a fully typed dataclass that can be imported:

```python
from path_link.project_paths_static import ProjectPathsStatic

paths = ProjectPathsStatic()
# Now you get full IDE autocomplete!
```

### Custom Validators

Create your own validators by creating a class with a `validate` method that returns a `ValidationResult`.

```python
from dataclasses import dataclass
from path_link import Finding, Severity, ValidationResult, ProjectPaths

@dataclass
class MyCustomValidator:
    """A custom validator to check for a specific file."""
    required_file: str

    def validate(self, paths: ProjectPaths) -> ValidationResult:
        result = ValidationResult()
        # Assume 'config_dir' is a defined path in your ProjectPaths
        config_path = paths.to_dict().get("config_dir")

        if not config_path or not (config_path / self.required_file).exists():
            result.add(Finding(
                severity=Severity.ERROR,
                code="CUSTOM_FILE_MISSING",
                field="config_dir",
                message=f"Required file '{self.required_file}' not found in config directory."
            ))
        return result

# Use the custom validator
paths = ProjectPaths.from_pyproject()
custom_validator = MyCustomValidator(required_file="user_settings.json")
validation_result = custom_validator.validate(paths)

if not validation_result.ok():
    print("Custom validation failed!")
```

### Composite Validators

Combine multiple validators to run them as a single pipeline.

```python
# Assuming MyCustomValidator is defined as in the previous example
from path_link.builtin_validators import CompositeValidator, StrictPathValidator

# 1. Load paths
paths = ProjectPaths.from_pyproject()

# 2. Configure validators
strict_check = StrictPathValidator(required=["config_dir"])
custom_check = MyCustomValidator(required_file="user_settings.json")

# 3. Combine them
composite_validator = CompositeValidator(parts=[strict_check, custom_check])

# 4. Run all checks at once
final_result = composite_validator.validate(paths)

if not final_result.ok():
    print("Composite validation failed!")
    for error in final_result.errors():
        print(f"- {error.message}")
```

### Programmatic Documentation Access

The package includes bundled documentation that can be accessed programmatically, even in offline or airgapped environments. This is especially useful for AI assistants helping users with the package.

```python
from path_link import get_ai_guidelines, get_developer_guide, get_metadata
import json

# Get AI assistant guidelines (comprehensive usage patterns and best practices)
ai_docs = get_ai_guidelines()
print(f"AI Guidelines: {len(ai_docs)} characters")

# Get developer guide (architecture, development setup, contribution guidelines)
dev_docs = get_developer_guide()
print(f"Developer Guide: {len(dev_docs)} characters")

# Get machine-readable metadata (version, APIs, validators, CLI commands)
metadata_json = get_metadata()
metadata = json.loads(metadata_json)
print(f"Version: {metadata['version']}")
print(f"Public APIs: {metadata['public_api']}")
```

**Use Cases:**
- **AI Assistants**: Provide context to AI agents helping users with the package
- **Offline Environments**: Access documentation without internet connection
- **Enterprise/Airgapped**: Full documentation in restricted environments
- **Automation**: Build tools that need package metadata programmatically

**Available Functions:**
- `get_ai_guidelines()` → Comprehensive AI assistant usage guide
- `get_developer_guide()` → Architecture and development documentation
- `get_metadata()` → Machine-readable project metadata (JSON)

## 📁 Project Structure

```
project_root/
├── pyproject.toml          # Configuration file
├── src/
│   └── project_paths/      # Main package
│       ├── model.py        # Core ProjectPaths class
│       ├── factory.py      # Factory functions
│       ├── validators.py   # Built-in validators
│       └── ...
└── tests/                  # Test suite
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test
uv run pytest tests/test_validators.py
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/jaahdytyspalvelu/path-link.git
cd path-link

# Install with uv
uv sync

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy src/
```

### Code Quality Standards

This project follows strict quality standards defined in `CLAUDE.md`:

- **Minimal Compliance**: For prototypes and quick fixes
- **Standard Compliance**: For production code (80% test coverage)
- **Strict Compliance**: For critical systems (90% test coverage)

## 📚 API Reference

### ProjectPaths

Main class for path management.

#### Methods

- `from_config(config_path: str | Path) -> ProjectPaths`: Load from custom config
- `to_dict() -> dict[str, Path]`: Get all paths as dictionary
- `get_paths() -> dict[str, Path]`: Get only Path fields

### Factory Functions

- `create_project_paths(validator=None, raise_on_error=False)`: Create with validation

### Documentation Functions

- `get_ai_guidelines() -> str`: Return AI assistant guidelines for working with this package
- `get_developer_guide() -> str`: Return developer guide for contributing to this package
- `get_metadata() -> str`: Return machine-readable project metadata (JSON)

### Validators

#### Built-in Validators

- `StrictPathValidator`: Ensures all paths exist and match expected types (file/directory)
- `SandboxPathValidator`: Prevents path traversal attacks and enforces base directory sandbox
- `CompositeValidator`: Combines multiple validators into a single validation pipeline

#### Validator Protocol

```python
class PathValidatorProtocol(Protocol):
    def validate(self, paths: Any) -> None: ...
    def add_error(self, message: str) -> None: ...
    def add_warning(self, message: str) -> None: ...
    def add_info(self, key: str, value: Any) -> None: ...
    @property
    def has_errors(self) -> bool: ...
    def clear(self) -> None: ...
```

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and follow the code style defined in `CLAUDE.md`.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Documentation](https://github.com/jaahdytyspalvelu/path-link/docs)
- [Issue Tracker](https://github.com/jaahdytyspalvelu/path-link/issues)
- [Changelog](CHANGELOG.md)

## 💡 Examples

Check out the `tests/examples/` directory for more usage examples:

- Basic configuration loading
- Custom validator implementation
- Static model generation
- Integration with existing projects

## 🛟 Support

- Open an issue for bug reports
- Start a discussion for feature requests
- Check existing issues before creating new ones

---

Made with ❤️ for Python developers who value type safety and clean configuration management.# path-link
