from typing import Optional

from cargo2rpm.cli import get_args, get_feature_from_subpackage
from cargo2rpm.rpm import InvalidFeatureError
from cargo2rpm.utils import short_repr

import pytest


@pytest.mark.parametrize(
    "args,expected",
    [
        (
            [],
            {
                "action": None,
                "path": None,
            },
        ),
        (
            ["buildrequires"],
            {
                "action": "buildrequires",
                "all_features": False,
                "features": None,
                "no_default_features": False,
                "path": None,
                "with_check": False,
            },
        ),
        (
            ["buildrequires", "-t", "-a"],
            {
                "action": "buildrequires",
                "all_features": True,
                "features": None,
                "no_default_features": False,
                "path": None,
                "with_check": True,
            },
        ),
        (
            ["requires"],
            {
                "action": "requires",
                "feature": None,
                "path": None,
                "subpackage": False,
            },
        ),
        (
            ["requires", "-f", "default"],
            {
                "action": "requires",
                "feature": "default",
                "path": None,
                "subpackage": False,
            },
        ),
        (
            ["requires", "-s", "-f", "rust-ahash+default-devel"],
            {
                "action": "requires",
                "feature": "rust-ahash+default-devel",
                "path": None,
                "subpackage": True,
            },
        ),
        (
            ["provides"],
            {
                "action": "provides",
                "feature": None,
                "path": None,
                "subpackage": False,
            },
        ),
        (
            ["provides", "-f", "default"],
            {
                "action": "provides",
                "feature": "default",
                "path": None,
                "subpackage": False,
            },
        ),
        (
            ["provides", "-s", "-f", "rust-ahash+default-devel"],
            {
                "action": "provides",
                "feature": "rust-ahash+default-devel",
                "path": None,
                "subpackage": True,
            },
        ),
    ],
    ids=short_repr,
)
def test_get_args(args, expected):
    assert vars(get_args(args)) == expected


@pytest.mark.parametrize(
    "subpackage,expected",
    [
        ("rust-ahash-devel", None),
        ("rust-ahash+default-devel", "default"),
        ("rust-cxx-devel", None),
        ("rust-cxx+c++14-devel", "c++14"),
        ("rust-cxx+c++17-devel", "c++17"),
        ("rust-cxx+c++20-devel", "c++20"),
    ],
    ids=short_repr,
)
def test_get_feature_from_subpackage(subpackage: str, expected: Optional[str]):
    assert get_feature_from_subpackage(subpackage) == expected


@pytest.mark.parametrize(
    "invalid,expected",
    [
        ("firefox", "Invalid subpackage name (missing 'rust-' prefix)"),
        ("rust-packaging", "Invalid subpackage name (missing '-devel' suffix)"),
        ("rust-+invalid-devel", "Invalid subpackage name (crate name cannot be empty or contain '+' characters)"),
        ("rust-+foo+invalid-devel", "Invalid subpackage name (crate name cannot be empty or contain '+' characters)"),
    ],
    ids=short_repr,
)
def test_get_feature_from_subpackage_fail(invalid: str, expected: str):
    with pytest.raises(InvalidFeatureError) as exc:
        get_feature_from_subpackage(invalid)
    assert expected in str(exc.value)
