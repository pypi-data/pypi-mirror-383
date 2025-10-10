import dataclasses
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from project_paths.model import ProjectPaths as DynamicPaths
from project_paths.project_paths_static import ProjectPathsStatic as StaticPaths


def test_static_equals_dynamic_fields():
    dyn = DynamicPaths.from_pyproject()
    stat = StaticPaths()

    dyn_keys = set(dyn.model_dump().keys())
    stat_keys = {f.name for f in dataclasses.fields(stat)}
    # Only compare fields that exist in both
    overlap = dyn_keys & stat_keys

    assert overlap == dyn_keys


def test_static_equals_dynamic_values():
    dyn = DynamicPaths.from_pyproject()
    stat = StaticPaths()
    for k in dyn.model_dump().keys():
        assert getattr(dyn, k) == getattr(stat, k)


def test_properties_match():
    dyn = DynamicPaths.from_pyproject()
    stat = StaticPaths()

    skip_properties = {
        "model_fields_set",
        "model_fields",
        "model_dump",
        "model_post_init",
        "model_copy",
        "model_json_schema",
        "model_parametrized_name",
    }

    for name in dir(DynamicPaths):
        if name.startswith("_") or name in skip_properties:
            continue
        attr = getattr(DynamicPaths, name, None)
        if isinstance(attr, property):
            dyn_val = getattr(dyn, name)
            stat_val = getattr(stat, name, None)
            assert dyn_val == stat_val, f"Mismatch in property '{name}'"


def test_field_regression_static_matches_dynamic():
    dyn = DynamicPaths.from_pyproject()
    stat = StaticPaths()

    dyn_keys = set(dyn.model_dump().keys())

    # Collect property names from the dynamic model (to match static's fieldification)
    property_names = {
        name for name, val in vars(type(dyn)).items() if isinstance(val, property)
    }
    dyn_keys.update(property_names)

    stat_keys = {f.name for f in dataclasses.fields(stat)}

    if dyn_keys != stat_keys:
        only_in_dynamic = dyn_keys - stat_keys
        only_in_static = stat_keys - dyn_keys
        raise AssertionError(
            f"Static and dynamic fields differ:\n"
            f"Only in dynamic: {only_in_dynamic}\n"
            f"Only in static: {only_in_static}"
        )
