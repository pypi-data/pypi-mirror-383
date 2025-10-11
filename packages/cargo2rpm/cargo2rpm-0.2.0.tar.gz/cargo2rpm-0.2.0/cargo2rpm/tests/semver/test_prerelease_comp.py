from cargo2rpm.semver import PreRelease

import pytest


def test_prerelease_comp_eq():
    values = [
        "alpha",
        "alpha.1",
        "alpha.beta",
        "beta",
        "beta.2",
        "beta.11",
        "rc.1",
    ]

    for left in values:
        for right in values:
            if left == right:
                assert PreRelease.parse(left) == PreRelease.parse(right)
            else:
                assert not (PreRelease.parse(left) == PreRelease.parse(right))


def test_prerelease_comp_ne():
    values = [
        "alpha",
        "alpha.1",
        "alpha.beta",
        "beta",
        "beta.2",
        "beta.11",
        "rc.1",
    ]

    for left in values:
        for right in values:
            if left != right:
                assert PreRelease.parse(left) != PreRelease.parse(right)
            else:
                assert not (PreRelease.parse(left) != PreRelease.parse(right))


@pytest.mark.parametrize(
    "left,right,lt",
    [
        ("alpha", "alpha.1", True),
        ("alpha.1", "alpha", False),
        ("alpha.1", "alpha.beta", True),
        ("alpha.beta", "alpha.1", False),
        ("alpha.beta", "beta", True),
        ("beta", "alpha.beta", False),
        ("beta", "beta.2", True),
        ("beta.2", "beta", False),
        ("beta.2", "beta.11", True),
        ("beta.11", "beta.2", False),
        ("beta.11", "rc.1", True),
        ("rc.1", "beta.11", False),
        ("alpha.1.1", "alpha.1.2", True),
    ],
    ids=repr,
)
def test_prerelease_comp_lt(left: str, right: str, lt: bool):
    assert (PreRelease.parse(left) < PreRelease.parse(right)) == lt


@pytest.mark.parametrize(
    "left,right,le",
    [
        ("alpha", "alpha", True),
        ("alpha", "alpha.1", True),
        ("alpha.1", "alpha", False),
        ("alpha.1", "alpha.1", True),
        ("alpha.1", "alpha.beta", True),
        ("alpha.beta", "alpha.1", False),
        ("alpha.beta", "alpha.beta", True),
        ("alpha.beta", "beta", True),
        ("beta", "alpha.beta", False),
        ("beta", "beta", True),
        ("beta", "beta.2", True),
        ("beta.2", "beta", False),
        ("beta.2", "beta.2", True),
        ("beta.2", "beta.11", True),
        ("beta.11", "beta.2", False),
        ("beta.11", "beta.11", True),
        ("beta.11", "rc.1", True),
        ("rc.1", "beta.11", False),
        ("rc.1", "rc.1", True),
    ],
    ids=repr,
)
def test_prerelease_comp_le(left: str, right: str, le: bool):
    assert (PreRelease.parse(left) <= PreRelease.parse(right)) == le


@pytest.mark.parametrize(
    "left,right,gt",
    [
        ("alpha", "alpha.1", False),
        ("alpha.1", "alpha", True),
        ("alpha.1", "alpha.beta", False),
        ("alpha.beta", "alpha.1", True),
        ("alpha.beta", "beta", False),
        ("beta", "alpha.beta", True),
        ("beta", "beta.2", False),
        ("beta.2", "beta", True),
        ("beta.2", "beta.11", False),
        ("beta.11", "beta.2", True),
        ("beta.11", "rc.1", False),
        ("rc.1", "beta.11", True),
    ],
    ids=repr,
)
def test_prerelease_comp_gt(left: str, right: str, gt: bool):
    assert (PreRelease.parse(left) > PreRelease.parse(right)) == gt


@pytest.mark.parametrize(
    "left,right,ge",
    [
        ("alpha", "alpha", True),
        ("alpha", "alpha.1", False),
        ("alpha.1", "alpha", True),
        ("alpha.1", "alpha.1", True),
        ("alpha.1", "alpha.beta", False),
        ("alpha.beta", "alpha.1", True),
        ("alpha.beta", "alpha.beta", True),
        ("alpha.beta", "beta", False),
        ("beta", "alpha.beta", True),
        ("beta", "beta", True),
        ("beta", "beta.2", False),
        ("beta.2", "beta", True),
        ("beta.2", "beta.2", True),
        ("beta.2", "beta.11", False),
        ("beta.11", "beta.2", True),
        ("beta.11", "beta.11", True),
        ("beta.11", "rc.1", False),
        ("rc.1", "beta.11", True),
        ("rc.1", "rc.1", True),
    ],
    ids=repr,
)
def test_prerelease_comp_ge(left: str, right: str, ge: bool):
    assert (PreRelease.parse(left) >= PreRelease.parse(right)) == ge
