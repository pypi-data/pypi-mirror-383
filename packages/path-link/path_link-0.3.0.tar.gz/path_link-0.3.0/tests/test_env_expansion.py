"""Tests for environment variable and tilde expansion in path configuration."""

from pathlib import Path
from path_link import ProjectPaths


def test_env_var_expansion_in_paths_file(tmp_path, monkeypatch):
    """Test that environment variables are expanded in .paths files."""
    # Set an environment variable
    monkeypatch.setenv("DATA_ROOT", "/custom/data")

    # Create .paths file with environment variable
    paths_file = tmp_path / ".paths"
    paths_file.write_text("data_dir = ${DATA_ROOT}/files\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify environment variable was expanded
    assert str(paths.data_dir).startswith("/custom/data/files")


def test_home_expansion_in_paths_file(tmp_path):
    """Test that ~ is expanded to user's home directory in .paths files."""
    # Create .paths file with tilde
    paths_file = tmp_path / ".paths"
    paths_file.write_text("config_dir = ~/my_config\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify tilde was expanded to actual home directory
    # Note: ~ expands to the user's actual home, then joined with base_dir
    expected = Path.home() / "my_config"
    assert paths.config_dir == expected


def test_combined_env_and_tilde_expansion(tmp_path, monkeypatch):
    """Test that both environment variables and ~ can be used together."""
    monkeypatch.setenv("PROJECT_NAME", "myproject")

    # Create .paths file with both ~ and env var
    paths_file = tmp_path / ".paths"
    paths_file.write_text("project_dir = ~/projects/${PROJECT_NAME}\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify both were expanded - tilde goes to actual home, env var expanded
    expected = Path.home() / "projects/myproject"
    assert paths.project_dir == expected


def test_env_var_with_default_value(tmp_path, monkeypatch):
    """Test environment variable expansion when variable is not set."""
    # Ensure variable is NOT set
    monkeypatch.delenv("UNDEFINED_VAR", raising=False)

    # Create .paths file with undefined env var
    paths_file = tmp_path / ".paths"
    paths_file.write_text("data_dir = ${UNDEFINED_VAR}/data\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # On POSIX, os.path.expandvars() replaces undefined ${VAR} with empty string
    # So "${UNDEFINED_VAR}/data" becomes "/data"
    # This is standard Python behavior
    assert str(paths.data_dir).endswith("/data")
    # The undefined var was replaced with empty string
    assert "UNDEFINED_VAR" not in str(paths.data_dir)


def test_multiple_env_vars_in_single_path(tmp_path, monkeypatch):
    """Test multiple environment variables in a single path."""
    monkeypatch.setenv("BASE", "/opt")
    monkeypatch.setenv("APP", "myapp")
    monkeypatch.setenv("VERSION", "v1")

    # Create .paths file with multiple env vars
    paths_file = tmp_path / ".paths"
    paths_file.write_text("install_dir = ${BASE}/${APP}/${VERSION}\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify all variables were expanded
    assert str(paths.install_dir).startswith("/opt")
    assert "myapp" in str(paths.install_dir)
    assert "v1" in str(paths.install_dir)


def test_env_var_expansion_in_pyproject(tmp_path, monkeypatch):
    """Test that environment variables work in pyproject.toml as well."""
    monkeypatch.setenv("CONFIG_ROOT", "/etc/myapp")
    monkeypatch.chdir(tmp_path)

    # Create pyproject.toml with env var
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[tool.path_link.paths]
config_dir = "${CONFIG_ROOT}/config"
""")

    # Load paths
    paths = ProjectPaths.from_pyproject()

    # Verify expansion worked
    assert str(paths.config_dir).startswith("/etc/myapp/config")


def test_relative_path_with_env_var(tmp_path, monkeypatch):
    """Test relative paths combined with environment variables."""
    monkeypatch.setenv("SUBDIR", "subfolder")

    # Create .paths file with relative path + env var
    paths_file = tmp_path / ".paths"
    paths_file.write_text("nested_dir = data/${SUBDIR}\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify expansion worked
    assert "subfolder" in str(paths.nested_dir)
    assert str(paths.nested_dir).endswith("data/subfolder")


def test_tilde_expansion_portability(tmp_path):
    """Test that tilde expansion works consistently across platforms."""
    # Create .paths file
    paths_file = tmp_path / ".paths"
    paths_file.write_text("user_config = ~/.config/myapp\n")

    # Load paths
    paths = ProjectPaths.from_config(paths_file)

    # Verify expansion uses actual home directory
    home = Path.home()
    assert str(paths.user_config).startswith(str(home))
    assert ".config/myapp" in str(paths.user_config)
