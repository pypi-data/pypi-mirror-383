from __future__ import annotations
import os
from pathlib import Path
from tomllib import load as toml_load
from typing import Callable, Dict, Any, Optional

from dotenv import dotenv_values
from pydantic import Field


def get_paths_from_pyproject() -> Dict[str, str]:
    """Load path variables from pyproject.toml."""
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.is_file():
        return {}

    with pyproject_path.open("rb") as f:
        pyproject_data = toml_load(f)

    tool_config = pyproject_data.get("tool", {}).get("project_paths", {})
    if not tool_config:
        return {}

    paths = tool_config.get("paths", {})
    files = tool_config.get("files", {})

    if not isinstance(paths, dict) or not isinstance(files, dict):
        raise TypeError("`paths` and `files` must be tables in pyproject.toml")

    return {**paths, **files}


def get_paths_from_dot_paths(path_to_config: Path) -> Dict[str, str]:
    """Load path variables from a .paths file."""
    if not path_to_config.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path_to_config}")

    values = dotenv_values(path_to_config)

    # Filter out None values which can occur with empty lines
    return {k: v for k, v in values.items() if v is not None}


def make_path_factory(base: Path, rel_path: str):
    """Creates a lambda function to resolve a path relative to a base."""
    # Expand environment variables and user home directory
    expanded_path = os.path.expandvars(os.path.expanduser(rel_path))
    return lambda: base / expanded_path


def build_field_definitions(
    loader_func: Callable[..., Dict[str, str]] = get_paths_from_pyproject,
    config_path: Optional[Path] = None,
) -> dict[str, tuple[type[Path], Any]]:
    """
    Builds a dictionary of Pydantic field definitions from a configuration source.

    Args:
        loader_func: The function used to load the raw path strings.
        config_path: The optional path to the configuration file.

    Returns:
        A dictionary of field definitions for the dynamic Pydantic model.
    """
    if config_path:
        env_values = loader_func(config_path)
        base_dir = config_path.parent.resolve()
    else:
        env_values = loader_func()
        base_dir = Path.cwd()

    fields = {
        "root": (Path, Field(default_factory=Path.home)),
        "base_dir": (Path, Field(default_factory=lambda: base_dir)),
    }

    for key, val in env_values.items():
        if key not in fields:
            fields[key] = (
                Path,
                Field(default_factory=make_path_factory(base_dir, val)),
            )

    return fields
