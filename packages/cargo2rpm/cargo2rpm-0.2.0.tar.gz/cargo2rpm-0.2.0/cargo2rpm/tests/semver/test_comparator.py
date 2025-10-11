from cargo2rpm.semver import Comparator, Op, Version
from cargo2rpm.utils import short_repr

import pytest


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1", Comparator(Op.CARET, 1, None, None, None)),
        ("1.2", Comparator(Op.CARET, 1, 2, None, None)),
        ("1.2.3", Comparator(Op.CARET, 1, 2, 3, None)),
        ("1.2.3-alpha.1", Comparator(Op.CARET, 1, 2, 3, "alpha.1")),
        ("1.2.3-alpha2", Comparator(Op.CARET, 1, 2, 3, "alpha2")),
        ("=0", Comparator(Op.EXACT, 0, None, None, None)),
        ("=0.11", Comparator(Op.EXACT, 0, 11, None, None)),
        ("=0.1.17", Comparator(Op.EXACT, 0, 1, 17, None)),
        ("=0.2.37-alpha.1", Comparator(Op.EXACT, 0, 2, 37, "alpha.1")),
        ("=0.2.37-alpha2", Comparator(Op.EXACT, 0, 2, 37, "alpha2")),
        (">1", Comparator(Op.GREATER, 1, None, None, None)),
        (">1.2", Comparator(Op.GREATER, 1, 2, None, None)),
        (">1.2.3", Comparator(Op.GREATER, 1, 2, 3, None)),
        (">1.2.3-alpha.1", Comparator(Op.GREATER, 1, 2, 3, "alpha.1")),
        (">1.2.3-alpha2", Comparator(Op.GREATER, 1, 2, 3, "alpha2")),
        (">=0", Comparator(Op.GREATER_EQ, 0, None, None, None)),
        (">=0.11", Comparator(Op.GREATER_EQ, 0, 11, None, None)),
        (">=0.1.17", Comparator(Op.GREATER_EQ, 0, 1, 17, None)),
        (">=0.2.37-alpha.1", Comparator(Op.GREATER_EQ, 0, 2, 37, "alpha.1")),
        (">=0.2.37-alpha2", Comparator(Op.GREATER_EQ, 0, 2, 37, "alpha2")),
        ("<1", Comparator(Op.LESS, 1, None, None, None)),
        ("<1.2", Comparator(Op.LESS, 1, 2, None, None)),
        ("<1.2.3", Comparator(Op.LESS, 1, 2, 3, None)),
        ("<1.2.3-alpha.1", Comparator(Op.LESS, 1, 2, 3, "alpha.1")),
        ("<1.2.3-alpha2", Comparator(Op.LESS, 1, 2, 3, "alpha2")),
        ("<=0", Comparator(Op.LESS_EQ, 0, None, None, None)),
        ("<=0.11", Comparator(Op.LESS_EQ, 0, 11, None, None)),
        ("<=0.1.17", Comparator(Op.LESS_EQ, 0, 1, 17, None)),
        ("<=0.2.37-alpha.1", Comparator(Op.LESS_EQ, 0, 2, 37, "alpha.1")),
        ("<=0.2.37-alpha2", Comparator(Op.LESS_EQ, 0, 2, 37, "alpha2")),
        ("~1", Comparator(Op.TILDE, 1, None, None, None)),
        ("~1.2", Comparator(Op.TILDE, 1, 2, None, None)),
        ("~1.2.3", Comparator(Op.TILDE, 1, 2, 3, None)),
        ("~1.2.3-alpha.1", Comparator(Op.TILDE, 1, 2, 3, "alpha.1")),
        ("~1.2.3-alpha2", Comparator(Op.TILDE, 1, 2, 3, "alpha2")),
        ("^0", Comparator(Op.CARET, 0, None, None, None)),
        ("^0.11", Comparator(Op.CARET, 0, 11, None, None)),
        ("^0.1.17", Comparator(Op.CARET, 0, 1, 17, None)),
        ("^0.2.37-alpha.1", Comparator(Op.CARET, 0, 2, 37, "alpha.1")),
        ("^0.2.37-alpha2", Comparator(Op.CARET, 0, 2, 37, "alpha2")),
        ("1.*", Comparator(Op.WILDCARD, 1, None, None, None)),
        ("1.*.*", Comparator(Op.WILDCARD, 1, None, None, None)),
        ("1.2.*", Comparator(Op.WILDCARD, 1, 2, None, None)),
    ],
    ids=short_repr,
)
def test_parse_comparator(string: str, expected: Comparator):
    assert Comparator.parse(string) == expected


@pytest.mark.parametrize(
    "string,expected_exc,expected_err",
    [
        ("foo", ValueError, "Invalid version requirement"),
        ("0.*.0", ValueError, "Invalid wildcard requirement"),
        ("0-alpha.1", ValueError, "Invalid pre-release requirement"),
        ("01.2.3", ValueError, "Invalid version requirement"),
        ("1.02.3", ValueError, "Invalid version requirement"),
        ("1.2.03", ValueError, "Invalid version requirement"),
    ],
    ids=short_repr,
)
def test_parse_comparator_fail(string: str, expected_exc, expected_err: str):
    with pytest.raises(expected_exc) as exc:
        Comparator.parse(string)
    assert expected_err in str(exc.value)


@pytest.mark.parametrize(
    "comparator,version,expected",
    [
        # =
        (Comparator(Op.EXACT, 1, 2, 3, None), Version(1, 2, 3), True),
        (Comparator(Op.EXACT, 1, 2, 3, None), Version(0, 1, 2), False),
        # >
        (Comparator(Op.GREATER, 1, 2, 3, None), Version(1, 2, 4), True),
        (Comparator(Op.GREATER, 1, 2, 3, None), Version(1, 2, 2), False),
        # >=
        (Comparator(Op.GREATER_EQ, 1, 2, 3, None), Version(1, 2, 3), True),
        (Comparator(Op.GREATER_EQ, 1, 2, 3, None), Version(1, 2, 4), True),
        (Comparator(Op.GREATER_EQ, 1, 2, 3, None), Version(1, 2, 2), False),
        # <
        (Comparator(Op.LESS, 1, 2, 3, None), Version(1, 2, 2), True),
        (Comparator(Op.LESS, 1, 2, 3, None), Version(1, 2, 4), False),
        # <=
        (Comparator(Op.LESS_EQ, 1, 2, 3, None), Version(1, 2, 3), True),
        (Comparator(Op.LESS_EQ, 1, 2, 3, None), Version(1, 2, 2), True),
        (Comparator(Op.LESS_EQ, 1, 2, 3, None), Version(1, 2, 4), False),
        # ~
        (Comparator(Op.TILDE, 1, 2, 3, None), Version(1, 2, 3), True),
        (Comparator(Op.TILDE, 1, 2, 3, None), Version(1, 2, 4), True),
        (Comparator(Op.TILDE, 1, 2, 3, None), Version(1, 2, 2), False),
        (Comparator(Op.TILDE, 1, 2, 3, None), Version(1, 3, 0), False),
        # ^
        (Comparator(Op.CARET, 1, 2, 3, None), Version(1, 2, 3), True),
        (Comparator(Op.CARET, 1, 2, 3, None), Version(1, 2, 4), True),
        (Comparator(Op.CARET, 1, 2, 3, None), Version(1, 3, 0), True),
        (Comparator(Op.CARET, 1, 2, 3, None), Version(1, 2, 2), False),
        (Comparator(Op.CARET, 1, 2, 3, None), Version(2, 0, 0), False),
        # *
        (Comparator(Op.WILDCARD, 1, None, None, None), Version(1, 0, 0), True),
        (Comparator(Op.WILDCARD, 1, None, None, None), Version(2, 0, 0), False),
        (Comparator(Op.WILDCARD, 1, 2, None, None), Version(1, 2, 0), True),
        (Comparator(Op.WILDCARD, 1, 2, None, None), Version(1, 1, 0), False),
    ],
    ids=repr,
)
def test_comparator_contains(comparator: Comparator, version: Version, expected: bool):
    assert (version in comparator) == expected
