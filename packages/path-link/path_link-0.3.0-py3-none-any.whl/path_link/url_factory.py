"""Factory for creating ProjectUrls instances with validation mode support.

This module provides factory methods to create ProjectUrls instances from
various configuration sources (pyproject.toml, .urls files) with configurable
validation modes (lenient or strict).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union, Any

from pydantic import create_model, Field

from path_link.url_model import _ProjectUrlsBase, ValidationMode, validate_url
from path_link.builder import (
    get_urls_from_pyproject,
    get_urls_from_dot_urls,
    get_urls_merged,
)


def _get_validation_mode_from_env() -> ValidationMode:
    """
    Determine validation mode from environment variable.

    Checks PTOOL_URL_MODE environment variable:
    - "strict" -> ValidationMode.STRICT
    - anything else -> ValidationMode.LENIENT (default)

    Returns:
        ValidationMode enum value
    """
    mode_str = os.getenv("PTOOL_URL_MODE", "lenient").lower()
    if mode_str == "strict":
        return ValidationMode.STRICT
    return ValidationMode.LENIENT


def _make_url_field(url_value: str, mode: ValidationMode) -> tuple[type[str], Any]:
    """
    Create a Pydantic field definition for a URL with validation.

    Args:
        url_value: The URL string to validate
        mode: Validation mode (lenient or strict)

    Returns:
        Tuple of (type, Field) for Pydantic model definition
    """
    # Validate the URL according to the mode
    validated_url = validate_url(url_value, mode)

    # Return a field with the validated URL as default
    return (str, Field(default=validated_url))


def _build_url_field_definitions(
    url_dict: dict[str, str], mode: ValidationMode
) -> dict[str, tuple[type[str], Any]]:
    """
    Build Pydantic field definitions from URL dictionary.

    Args:
        url_dict: Dictionary of URL key-value pairs
        mode: Validation mode to use for all URLs

    Returns:
        Dictionary of field definitions for dynamic Pydantic model
    """
    fields = {}

    for key, url_value in url_dict.items():
        fields[key] = _make_url_field(url_value, mode)

    return fields


class ProjectUrls:
    """
    Main URL management class.

    Do not instantiate this class directly. Use the factory methods:
    - `ProjectUrls.from_pyproject(mode=ValidationMode.LENIENT)`
    - `ProjectUrls.from_config("path/to/.urls", mode=ValidationMode.LENIENT)`
    - `ProjectUrls.from_merged(mode=ValidationMode.LENIENT)`
    """

    def __init__(self, **kwargs: Any):
        raise NotImplementedError(
            "Direct instantiation of ProjectUrls is not supported. "
            "Use a factory method: `from_pyproject()`, `from_config()`, or `from_merged()`."
        )

    @classmethod
    def from_pyproject(
        cls, mode: Union[ValidationMode, str, None] = None
    ) -> _ProjectUrlsBase:
        """
        Creates a ProjectUrls instance from pyproject.toml [tool.path_link.urls].

        Args:
            mode: Validation mode (lenient or strict). If None, reads from
                  PTOOL_URL_MODE environment variable (default: lenient)

        Returns:
            Dynamic Pydantic model instance with validated URLs

        Raises:
            ValidationError: If any URL fails validation for the given mode
            TypeError: If urls section is not a dict in pyproject.toml
        """
        # Determine validation mode
        if mode is None:
            validation_mode = _get_validation_mode_from_env()
        elif isinstance(mode, str):
            validation_mode = ValidationMode(mode.lower())
        else:
            validation_mode = mode

        # Load URLs from pyproject.toml
        url_dict = get_urls_from_pyproject()

        # Build field definitions with validation
        field_defs = _build_url_field_definitions(url_dict, validation_mode)

        # Create dynamic model
        DynamicModel = create_model(  # type: ignore[call-overload]
            "ProjectUrlsDynamic",
            __base__=(_ProjectUrlsBase,),
            **field_defs,
        )

        return DynamicModel()  # type: ignore[no-any-return]

    @classmethod
    def from_config(
        cls, config_path: Union[str, Path], mode: Union[ValidationMode, str, None] = None
    ) -> _ProjectUrlsBase:
        """
        Creates a ProjectUrls instance from a .urls file.

        Args:
            config_path: Path to .urls configuration file
            mode: Validation mode (lenient or strict). If None, reads from
                  PTOOL_URL_MODE environment variable (default: lenient)

        Returns:
            Dynamic Pydantic model instance with validated URLs

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If any URL fails validation for the given mode
        """
        # Determine validation mode
        if mode is None:
            validation_mode = _get_validation_mode_from_env()
        elif isinstance(mode, str):
            validation_mode = ValidationMode(mode.lower())
        else:
            validation_mode = mode

        # Load URLs from .urls file
        resolved_path = Path(config_path)
        url_dict = get_urls_from_dot_urls(resolved_path)

        # Build field definitions with validation
        field_defs = _build_url_field_definitions(url_dict, validation_mode)

        # Create dynamic model
        DynamicModel = create_model(  # type: ignore[call-overload]
            "ProjectUrlsDynamic",
            __base__=(_ProjectUrlsBase,),
            **field_defs,
        )

        return DynamicModel()  # type: ignore[no-any-return]

    @classmethod
    def from_merged(
        cls,
        dotenv_path: Union[str, Path, None] = None,
        mode: Union[ValidationMode, str, None] = None,
    ) -> _ProjectUrlsBase:
        """
        Creates a ProjectUrls instance from merged pyproject.toml and .urls sources.

        Precedence: pyproject.toml > .urls file
        Missing keys are merged; duplicates resolved by pyproject.toml.

        Args:
            dotenv_path: Optional path to .urls file (default: ./.urls)
            mode: Validation mode (lenient or strict). If None, reads from
                  PTOOL_URL_MODE environment variable (default: lenient)

        Returns:
            Dynamic Pydantic model instance with validated URLs

        Raises:
            ValidationError: If any URL fails validation for the given mode
        """
        # Determine validation mode
        if mode is None:
            validation_mode = _get_validation_mode_from_env()
        elif isinstance(mode, str):
            validation_mode = ValidationMode(mode.lower())
        else:
            validation_mode = mode

        # Load merged URLs
        resolved_dotenv = Path(dotenv_path) if dotenv_path else None
        url_dict = get_urls_merged(resolved_dotenv)

        # Build field definitions with validation
        field_defs = _build_url_field_definitions(url_dict, validation_mode)

        # Create dynamic model
        DynamicModel = create_model(  # type: ignore[call-overload]
            "ProjectUrlsDynamic",
            __base__=(_ProjectUrlsBase,),
            **field_defs,
        )

        return DynamicModel()  # type: ignore[no-any-return]
