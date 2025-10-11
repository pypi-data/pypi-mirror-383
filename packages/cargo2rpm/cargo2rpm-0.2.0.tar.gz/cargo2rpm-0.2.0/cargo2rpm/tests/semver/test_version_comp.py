from cargo2rpm.semver import Version

import pytest


def test_version_comp_eq():
    values = [
        "1.2.3-dev",
        "1.0.0",
        "2.0.0",
        "0.1.0",
        "0.2.0",
        "0.0.1",
        "0.0.2",
        "1.0.0-beta.1",
        "1.0.0-beta.2",
        "2.1.0",
        "2.1.1",
        "1.0.0-alpha",
    ]

    for left in values:
        for right in values:
            if left == right:
                assert Version.parse(left) == Version.parse(right)
            else:
                assert not (Version.parse(left) == Version.parse(right))


def test_version_comp_ne():
    values = [
        "1.2.3-dev",
        "1.0.0",
        "2.0.0",
        "0.1.0",
        "0.2.0",
        "0.0.1",
        "0.0.2",
        "1.0.0-beta.1",
        "1.0.0-beta.2",
        "2.1.0",
        "2.1.1",
        "1.0.0-alpha",
    ]

    for left in values:
        for right in values:
            if left != right:
                assert Version.parse(left) != Version.parse(right)
            else:
                assert not (Version.parse(left) != Version.parse(right))


@pytest.mark.parametrize(
    "left,right,lt",
    [
        ("1.2.3-dev", "1.2.3-dev", False),
        ("2.0.0", "1.0.0", False),
        ("0.1.0", "0.2.0", True),
        ("0.2.0", "0.1.0", False),
        ("0.0.1", "0.0.2", True),
        ("0.0.2", "0.0.1", False),
        ("1.0.0-beta.1", "1.0.0-beta.2", True),
        ("1.0.0-beta.2", "1.0.0-beta.1", False),
        ("1.0.0", "2.0.0", True),
        ("2.0.0", "2.1.0", True),
        ("2.0.0", "1.3.0", False),
        ("2.1.0", "2.1.1", True),
        ("1.0.0-alpha", "1.0.0", True),
    ],
    ids=repr,
)
def test_version_comp_lt(left: str, right: str, lt: bool):
    assert (Version.parse(left) < Version.parse(right)) == lt


@pytest.mark.parametrize(
    "left,right,le",
    [
        ("1.2.3-dev", "1.2.3-dev", True),
        ("2.0.0", "1.0.0", False),
        ("0.1.0", "0.2.0", True),
        ("0.2.0", "0.1.0", False),
        ("0.0.1", "0.0.2", True),
        ("0.0.2", "0.0.1", False),
        ("1.0.0-beta.1", "1.0.0-beta.2", True),
        ("1.0.0-beta.2", "1.0.0-beta.1", False),
        ("1.0.0", "2.0.0", True),
        ("2.0.0", "2.1.0", True),
        ("2.1.0", "2.1.1", True),
        ("1.0.0-alpha", "1.0.0", True),
    ],
    ids=repr,
)
def test_version_comp_le(left: str, right: str, le: bool):
    assert (Version.parse(left) <= Version.parse(right)) == le


@pytest.mark.parametrize(
    "left,right,gt",
    [
        ("1.2.3-dev", "1.2.3-dev", False),
        ("2.0.0", "1.0.0", True),
        ("0.1.0", "0.2.0", False),
        ("0.2.0", "0.1.0", True),
        ("0.0.1", "0.0.2", False),
        ("0.0.2", "0.0.1", True),
        ("1.0.0-beta.1", "1.0.0-beta.2", False),
        ("1.0.0-beta.2", "1.0.0-beta.1", True),
        ("1.0.0", "2.0.0", False),
        ("2.0.0", "2.1.0", False),
        ("2.1.0", "2.1.1", False),
        ("1.0.0-alpha", "1.0.0", False),
    ],
    ids=repr,
)
def test_version_comp_gt(left: str, right: str, gt: bool):
    assert (Version.parse(left) > Version.parse(right)) == gt


@pytest.mark.parametrize(
    "left,right,ge",
    [
        ("1.2.3-dev", "1.2.3-dev", True),
        ("2.0.0", "1.0.0", True),
        ("0.1.0", "0.2.0", False),
        ("0.2.0", "0.1.0", True),
        ("0.0.1", "0.0.2", False),
        ("0.0.2", "0.0.1", True),
        ("1.0.0-beta.1", "1.0.0-beta.2", False),
        ("1.0.0-beta.2", "1.0.0-beta.1", True),
        ("1.0.0", "2.0.0", False),
        ("2.0.0", "2.1.0", False),
        ("2.1.0", "2.1.1", False),
        ("1.0.0-alpha", "1.0.0", False),
    ],
    ids=repr,
)
def test_version_comp_ge(left: str, right: str, ge: bool):
    assert (Version.parse(left) >= Version.parse(right)) == ge
