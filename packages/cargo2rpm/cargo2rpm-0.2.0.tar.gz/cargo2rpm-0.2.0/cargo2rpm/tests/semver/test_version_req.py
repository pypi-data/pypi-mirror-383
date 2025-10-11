from typing import Optional

from cargo2rpm.semver import Comparator, Op, Version, VersionReq
from cargo2rpm.utils import short_repr

import pytest


@pytest.mark.parametrize(
    "string,expected",
    [
        ("^0.1", VersionReq([Comparator(Op.CARET, 0, 1, None, None)])),
        ("~0.1", VersionReq([Comparator(Op.TILDE, 0, 1, None, None)])),
        ("^1.2", VersionReq([Comparator(Op.CARET, 1, 2, None, None)])),
        ("~1.2", VersionReq([Comparator(Op.TILDE, 1, 2, None, None)])),
        (">=1.2.3, <2.0.0", VersionReq([Comparator(Op.GREATER_EQ, 1, 2, 3, None), Comparator(Op.LESS, 2, 0, 0, None)])),
        (">=0.1.7, <0.2.0", VersionReq([Comparator(Op.GREATER_EQ, 0, 1, 7, None), Comparator(Op.LESS, 0, 2, 0, None)])),
        ("*", VersionReq([])),
    ],
    ids=short_repr,
)
def test_parse_version_req(string: str, expected: VersionReq):
    assert VersionReq.parse(string) == expected


def test_parse_version_req_fail():
    with pytest.raises(ValueError) as exc:
        VersionReq.parse("")
    assert "Invalid version requirement (empty string)" in str(exc.value)


@pytest.mark.parametrize(
    "string,expected",
    [
        ("=1.2.3", [Comparator(Op.EXACT, 1, 2, 3, None)]),
        ("=1.2", [Comparator(Op.GREATER_EQ, 1, 2, 0, None), Comparator(Op.LESS, 1, 3, 0, None)]),
        ("=1", [Comparator(Op.GREATER_EQ, 1, 0, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        (">1.2.3", [Comparator(Op.GREATER, 1, 2, 3, None)]),
        (">1.2", [Comparator(Op.GREATER_EQ, 1, 3, 0, None)]),
        (">1", [Comparator(Op.GREATER_EQ, 2, 0, 0, None)]),
        (">=1.2.3", [Comparator(Op.GREATER_EQ, 1, 2, 3, None)]),
        (">=1.2", [Comparator(Op.GREATER_EQ, 1, 2, 0, None)]),
        (">=1", [Comparator(Op.GREATER_EQ, 1, 0, 0, None)]),
        ("<1.2.3", [Comparator(Op.LESS, 1, 2, 3, None)]),
        ("<1.2", [Comparator(Op.LESS, 1, 2, 0, None)]),
        ("<1", [Comparator(Op.LESS, 1, 0, 0, None)]),
        ("<=1.2.3", [Comparator(Op.LESS_EQ, 1, 2, 3, None)]),
        ("<=1.2", [Comparator(Op.LESS, 1, 3, 0, None)]),
        ("<=1", [Comparator(Op.LESS, 2, 0, 0, None)]),
        ("~1.2.3", [Comparator(Op.GREATER_EQ, 1, 2, 3, None), Comparator(Op.LESS, 1, 3, 0, None)]),
        ("~1.2", [Comparator(Op.GREATER_EQ, 1, 2, 0, None), Comparator(Op.LESS, 1, 3, 0, None)]),
        ("~1", [Comparator(Op.GREATER_EQ, 1, 0, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        ("^1.2.3", [Comparator(Op.GREATER_EQ, 1, 2, 3, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        ("^0.1.2", [Comparator(Op.GREATER_EQ, 0, 1, 2, None), Comparator(Op.LESS, 0, 2, 0, None)]),
        ("^0.0.1", [Comparator(Op.EXACT, 0, 0, 1, None)]),
        ("^1.2", [Comparator(Op.GREATER_EQ, 1, 2, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        ("^0.1", [Comparator(Op.GREATER_EQ, 0, 1, 0, None), Comparator(Op.LESS, 0, 2, 0, None)]),
        ("^0.0", [Comparator(Op.GREATER_EQ, 0, 0, 0, None), Comparator(Op.LESS, 0, 1, 0, None)]),
        ("^1", [Comparator(Op.GREATER_EQ, 1, 0, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        ("1.2.*", [Comparator(Op.GREATER_EQ, 1, 2, 0, None), Comparator(Op.LESS, 1, 3, 0, None)]),
        ("1.*", [Comparator(Op.GREATER_EQ, 1, 0, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
        ("1.*.*", [Comparator(Op.GREATER_EQ, 1, 0, 0, None), Comparator(Op.LESS, 2, 0, 0, None)]),
    ],
    ids=short_repr,
)
def test_normalize_comparator(string: str, expected: list[Comparator]):
    assert Comparator.parse(string).normalize() == expected


@pytest.mark.parametrize(
    "comparator,feature,expected",
    [
        ("=1.2.3", None, "crate(foo) = 1.2.3"),
        ("=1.2.3", "default", "crate(foo/default) = 1.2.3"),
        (">1.2.3", None, "crate(foo) > 1.2.3"),
        (">1.2.3", "default", "crate(foo/default) > 1.2.3"),
        (">=1.2.3", None, "crate(foo) >= 1.2.3"),
        (">=1.2.3", "default", "crate(foo/default) >= 1.2.3"),
        ("<1.2.3", None, "crate(foo) < 1.2.3~"),
        ("<1.2.3", "default", "crate(foo/default) < 1.2.3~"),
        ("<=1.2.3", None, "crate(foo) <= 1.2.3"),
        ("<=1.2.3", "default", "crate(foo/default) <= 1.2.3"),
    ],
    ids=short_repr,
)
def test_comparator_to_rpm(comparator: str, feature: Optional[str], expected: str):
    assert Comparator.parse(comparator).to_rpm("foo", feature) == expected


@pytest.mark.parametrize(
    "req,feature,expected",
    [
        ("*", None, "crate(foo)"),
        ("*", "default", "crate(foo/default)"),
        ("=1.2.3", None, "crate(foo) = 1.2.3"),
        ("=1.2.3", "default", "crate(foo/default) = 1.2.3"),
        ("=1.2", None, "(crate(foo) >= 1.2.0 with crate(foo) < 1.3.0~)"),
        ("=1.2", "default", "(crate(foo/default) >= 1.2.0 with crate(foo/default) < 1.3.0~)"),
        ("=1", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("=1", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        (">1.2.3", None, "crate(foo) > 1.2.3"),
        (">1.2.3", "default", "crate(foo/default) > 1.2.3"),
        (">1.2", None, "crate(foo) >= 1.3.0"),
        (">1.2", "default", "crate(foo/default) >= 1.3.0"),
        (">1", None, "crate(foo) >= 2.0.0"),
        (">1", "default", "crate(foo/default) >= 2.0.0"),
        (">=1.2.3", None, "crate(foo) >= 1.2.3"),
        (">=1.2.3", "default", "crate(foo/default) >= 1.2.3"),
        (">=1.2", None, "crate(foo) >= 1.2.0"),
        (">=1.2", "default", "crate(foo/default) >= 1.2.0"),
        (">=1", None, "crate(foo) >= 1.0.0"),
        (">=1", "default", "crate(foo/default) >= 1.0.0"),
        ("<1.2.3", None, "crate(foo) < 1.2.3~"),
        ("<1.2.3", "default", "crate(foo/default) < 1.2.3~"),
        ("<1.2", None, "crate(foo) < 1.2.0~"),
        ("<1.2", "default", "crate(foo/default) < 1.2.0~"),
        ("<1", None, "crate(foo) < 1.0.0~"),
        ("<1", "default", "crate(foo/default) < 1.0.0~"),
        ("<=1.2.3", None, "crate(foo) <= 1.2.3"),
        ("<=1.2.3", "default", "crate(foo/default) <= 1.2.3"),
        ("<=1.2", None, "crate(foo) < 1.3.0~"),
        ("<=1.2", "default", "crate(foo/default) < 1.3.0~"),
        ("<=1", None, "crate(foo) < 2.0.0~"),
        ("<=1", "default", "crate(foo/default) < 2.0.0~"),
        ("~1.2.3", None, "(crate(foo) >= 1.2.3 with crate(foo) < 1.3.0~)"),
        ("~1.2.3", "default", "(crate(foo/default) >= 1.2.3 with crate(foo/default) < 1.3.0~)"),
        ("~1.2", None, "(crate(foo) >= 1.2.0 with crate(foo) < 1.3.0~)"),
        ("~1.2", "default", "(crate(foo/default) >= 1.2.0 with crate(foo/default) < 1.3.0~)"),
        ("~1", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("~1", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        ("^1.2.3", None, "(crate(foo) >= 1.2.3 with crate(foo) < 2.0.0~)"),
        ("^1.2.3", "default", "(crate(foo/default) >= 1.2.3 with crate(foo/default) < 2.0.0~)"),
        ("^0.1.2", None, "(crate(foo) >= 0.1.2 with crate(foo) < 0.2.0~)"),
        ("^0.1.2", "default", "(crate(foo/default) >= 0.1.2 with crate(foo/default) < 0.2.0~)"),
        ("^0.0.1", None, "crate(foo) = 0.0.1"),
        ("^0.0.1", "default", "crate(foo/default) = 0.0.1"),
        ("^1.2", None, "(crate(foo) >= 1.2.0 with crate(foo) < 2.0.0~)"),
        ("^1.2", "default", "(crate(foo/default) >= 1.2.0 with crate(foo/default) < 2.0.0~)"),
        ("^0.1", None, "(crate(foo) >= 0.1.0 with crate(foo) < 0.2.0~)"),
        ("^0.1", "default", "(crate(foo/default) >= 0.1.0 with crate(foo/default) < 0.2.0~)"),
        ("^0.0", None, "(crate(foo) >= 0.0.0 with crate(foo) < 0.1.0~)"),
        ("^0.0", "default", "(crate(foo/default) >= 0.0.0 with crate(foo/default) < 0.1.0~)"),
        ("^1", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("^1", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        ("1.2.3", None, "(crate(foo) >= 1.2.3 with crate(foo) < 2.0.0~)"),
        ("1.2.3", "default", "(crate(foo/default) >= 1.2.3 with crate(foo/default) < 2.0.0~)"),
        ("0.1.2", None, "(crate(foo) >= 0.1.2 with crate(foo) < 0.2.0~)"),
        ("0.1.2", "default", "(crate(foo/default) >= 0.1.2 with crate(foo/default) < 0.2.0~)"),
        ("0.0.1", None, "crate(foo) = 0.0.1"),
        ("0.0.1", "default", "crate(foo/default) = 0.0.1"),
        ("1.2", None, "(crate(foo) >= 1.2.0 with crate(foo) < 2.0.0~)"),
        ("1.2", "default", "(crate(foo/default) >= 1.2.0 with crate(foo/default) < 2.0.0~)"),
        ("0.1", None, "(crate(foo) >= 0.1.0 with crate(foo) < 0.2.0~)"),
        ("0.1", "default", "(crate(foo/default) >= 0.1.0 with crate(foo/default) < 0.2.0~)"),
        ("0.0", None, "(crate(foo) >= 0.0.0 with crate(foo) < 0.1.0~)"),
        ("0.0", "default", "(crate(foo/default) >= 0.0.0 with crate(foo/default) < 0.1.0~)"),
        ("1", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("1", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        ("1.2.*", None, "(crate(foo) >= 1.2.0 with crate(foo) < 1.3.0~)"),
        ("1.2.*", "default", "(crate(foo/default) >= 1.2.0 with crate(foo/default) < 1.3.0~)"),
        ("1.*", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("1.*", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        ("1.*.*", None, "(crate(foo) >= 1.0.0 with crate(foo) < 2.0.0~)"),
        ("1.*.*", "default", "(crate(foo/default) >= 1.0.0 with crate(foo/default) < 2.0.0~)"),
        # some real-world test cases with pre-releases
        ("^0.1.0-alpha.4", "default", "(crate(foo/default) >= 0.1.0~alpha.4 with crate(foo/default) < 0.2.0~)"),
        ("=1.0.0-alpha.5", "default", "crate(foo/default) = 1.0.0~alpha.5"),
    ],
    ids=short_repr,
)
def test_version_req_to_rpm(req: str, feature: Optional[str], expected: str):
    assert VersionReq.parse(req).to_rpm("foo", feature) == expected


def test_version_req_to_rpm_fail():
    with pytest.raises(ValueError) as exc:
        VersionReq.parse(">=0.1.0, <0.2.0, >=0.3.0, <1.0.0").to_rpm("foo", None)
    assert "Using more than 2 comparators is not supported by RPM." in str(exc.value)


@pytest.mark.parametrize(
    "req,version,expected",
    [
        # =
        (VersionReq.parse("=0.1.2"), Version(0, 1, 2), True),
        (VersionReq.parse("=0.1.2"), Version(0, 1, 1), False),
        (VersionReq.parse("=0.1.2"), Version(0, 1, 3), False),
        # >=, <
        (VersionReq.parse(">=0.13, <0.22"), Version(0, 13, 0), True),
        (VersionReq.parse(">=0.13, <0.22"), Version(0, 21, 42), True),
        (VersionReq.parse(">=0.13, <0.22"), Version(0, 12, 0), False),
        (VersionReq.parse(">=0.13, <0.22"), Version(0, 22, 0), False),
        # ~
        (VersionReq.parse("~1.2.3"), Version(1, 2, 3), True),
        (VersionReq.parse("~1.2.3"), Version(1, 2, 2), False),
        (VersionReq.parse("~1.2.3"), Version(1, 3, 0), False),
        (VersionReq.parse("~1.2.3"), Version(2, 0, 0), False),
        # ^
        (VersionReq.parse("^1.2.3"), Version(1, 2, 3), True),
        (VersionReq.parse("^1.2.3"), Version(1, 2, 2), False),
        (VersionReq.parse("^1.2.3"), Version(2, 0, 0), False),
    ],
    ids=repr,
)
def test_version_req_contains(req: VersionReq, version: Version, expected: bool):
    print(req.comparators)
    print(req.normalize().comparators)
    assert (version in req) == expected
