from __future__ import annotations
from pathlib import Path
from typing import Union, Any

from pydantic import BaseModel, ConfigDict, create_model

from .builder import (
    build_field_definitions,
    get_paths_from_dot_paths,
    get_paths_from_pyproject,
)


class _ProjectPathsBase(BaseModel):
    """
    Internal base class for ProjectPaths.
    This class has a functional __init__ and provides the core logic.
    It should not be used directly by end-users.
    """

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    def to_dict(self) -> dict[str, Path]:
        """Returns a dictionary of all resolved path attributes."""
        return self.model_dump(include=set(self.model_fields.keys()))  # type: ignore[no-any-return]

    def get_paths(self) -> list[Path]:
        """Returns a list of all resolved Path objects."""
        return [v for v in self.to_dict().values() if isinstance(v, Path)]

    def __getitem__(self, key: str) -> Path:
        """Enables dictionary-style access to path attributes."""
        if key not in self.model_fields:
            raise KeyError(f"'{key}' is not a configured path.")
        return getattr(self, key)  # type: ignore[no-any-return]


class ProjectPaths:
    """
    Main path management class.

    Do not instantiate this class directly. Use the factory methods:
    - `ProjectPaths.from_pyproject()`
    - `ProjectPaths.from_config("path/to/.paths")`
    """

    def __init__(self, **kwargs: Any):
        raise NotImplementedError(
            "Direct instantiation of ProjectPaths is not supported. "
            "Use a factory method: `from_pyproject()` or `from_config()`."
        )

    @classmethod
    def from_pyproject(cls) -> _ProjectPathsBase:
        """Creates a ProjectPaths instance from pyproject.toml."""
        field_defs = build_field_definitions(loader_func=get_paths_from_pyproject)
        DynamicModel = create_model(  # type: ignore[call-overload]
            "ProjectPathsDynamic",
            __base__=(_ProjectPathsBase,),  # Config inherited from base class
            **field_defs,
        )
        return DynamicModel()  # type: ignore[no-any-return]

    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> _ProjectPathsBase:
        """Creates a ProjectPaths instance from a custom .paths file."""
        resolved_path = Path(config_path)
        field_defs = build_field_definitions(
            loader_func=get_paths_from_dot_paths, config_path=resolved_path
        )
        DynamicModel = create_model(  # type: ignore[call-overload]
            "ProjectPathsDynamic",
            __base__=(_ProjectPathsBase,),  # Config inherited from base class
            **field_defs,
        )
        return DynamicModel()  # type: ignore[no-any-return]
