from pathlib import Path
from repoplone import _types as t
from repoplone.utils.dependencies import constraints as const_utils

import pytest
import tomlkit


@pytest.fixture
def pyproject_path(test_public_project) -> Path:
    return test_public_project / "backend" / "pyproject.toml"


@pytest.fixture
def pyproject_toml(pyproject_path) -> tomlkit.TOMLDocument:
    return tomlkit.parse(pyproject_path.read_text())


@pytest.fixture
def existing_pins(pyproject_toml) -> t.Requirements:
    from repoplone.utils.dependencies import pyproject as utils

    return utils.get_all_pinned_dependencies(pyproject_toml)


@pytest.mark.parametrize(
    "core_package,core_package_version,constraint",
    [
        ["Products.CMFPlone", "6.1.0", "Products.CMFPlone==6.1.0"],
        ["Products.CMFPlone", "6.1.0", "pytest-plone>=1.0.0a1"],
        ["kitconcept.intranet", "1.0.0a17", "kitconcept.voltolighttheme==6.0.0a21"],
        ["kitconcept.intranet", "1.0.0a17", "pytest-plone>=1.0.0a1"],
    ],
)
@pytest.mark.vcr()
def test_get_package_constraints(
    existing_pins,
    core_package: str,
    core_package_version: str,
    constraint: str,
):
    func = const_utils.get_package_constraints
    result = func(core_package, core_package_version, existing_pins)
    assert constraint in result


@pytest.mark.parametrize(
    "core_package,raises",
    [
        ["Plone", False],
        ["Products.CMFPlone", False],
        ["kitconcept.core", False],
        ["kitconcept.intranet", False],
        ["kitconcept.site", False],
        ["kitconcept.website", False],
        ["portalbrasil.core", False],
        ["portalbrasil.devsite", False],
        ["portalbrasil.intranet", False],
        ["portalbrasil.legislativo", False],
        ["foo.bar", True],
    ],
)
def test_get_constraint_info(core_package: str, raises: bool):
    func = const_utils.get_constraint_info
    if raises:
        with pytest.raises(AttributeError) as exc:
            func(core_package)
        assert f"{core_package} is not supported at the moment." in str(exc)
    else:
        result = func(core_package)
        assert isinstance(result, dict)
