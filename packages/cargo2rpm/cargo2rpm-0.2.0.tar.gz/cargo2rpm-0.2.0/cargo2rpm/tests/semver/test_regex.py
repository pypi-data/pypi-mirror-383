from cargo2rpm.semver import VERSION_REGEX, VERSION_REQ_REGEX
from cargo2rpm.utils import short_repr

import pytest


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1.0.0-alpha", dict(major="1", minor="0", patch="0", pre="alpha", build=None)),
        ("1.0.0-alpha.1", dict(major="1", minor="0", patch="0", pre="alpha.1", build=None)),
        ("1.0.0-0.3.7", dict(major="1", minor="0", patch="0", pre="0.3.7", build=None)),
        ("1.0.0-x.7.z.92", dict(major="1", minor="0", patch="0", pre="x.7.z.92", build=None)),
        ("1.0.0-x-y-z.--", dict(major="1", minor="0", patch="0", pre="x-y-z.--", build=None)),
        ("1.0.0-alpha+001", dict(major="1", minor="0", patch="0", pre="alpha", build="001")),
        ("1.0.0+20130313144700", dict(major="1", minor="0", patch="0", pre=None, build="20130313144700")),
        ("1.0.0-beta+exp.sha.5114f85", dict(major="1", minor="0", patch="0", pre="beta", build="exp.sha.5114f85")),
        ("1.0.0+21AF26D3----117B344092BD", dict(major="1", minor="0", patch="0", pre=None, build="21AF26D3----117B344092BD")),
    ],
    ids=short_repr,
)
def test_version_regex(string: str, expected: dict):
    match = VERSION_REGEX.match(string)
    assert match is not None
    assert match.groupdict() == expected


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1", dict(op=None, major="1", minor=None, patch=None, pre=None)),
        ("1.2", dict(op=None, major="1", minor="2", patch=None, pre=None)),
        ("1.2.3", dict(op=None, major="1", minor="2", patch="3", pre=None)),
        ("1.2.3-alpha.1", dict(op=None, major="1", minor="2", patch="3", pre="alpha.1")),
        ("1.2.3-alpha2", dict(op=None, major="1", minor="2", patch="3", pre="alpha2")),
        ("=0", dict(op="=", major="0", minor=None, patch=None, pre=None)),
        ("=0.11", dict(op="=", major="0", minor="11", patch=None, pre=None)),
        ("=0.1.17", dict(op="=", major="0", minor="1", patch="17", pre=None)),
        ("=0.2.37-alpha.1", dict(op="=", major="0", minor="2", patch="37", pre="alpha.1")),
        ("=0.2.37-alpha2", dict(op="=", major="0", minor="2", patch="37", pre="alpha2")),
        (">1", dict(op=">", major="1", minor=None, patch=None, pre=None)),
        (">1.2", dict(op=">", major="1", minor="2", patch=None, pre=None)),
        (">1.2.3", dict(op=">", major="1", minor="2", patch="3", pre=None)),
        (">1.2.3-alpha.1", dict(op=">", major="1", minor="2", patch="3", pre="alpha.1")),
        (">1.2.3-alpha2", dict(op=">", major="1", minor="2", patch="3", pre="alpha2")),
        (">=0", dict(op=">=", major="0", minor=None, patch=None, pre=None)),
        (">=0.11", dict(op=">=", major="0", minor="11", patch=None, pre=None)),
        (">=0.1.17", dict(op=">=", major="0", minor="1", patch="17", pre=None)),
        (">=0.2.37-alpha.1", dict(op=">=", major="0", minor="2", patch="37", pre="alpha.1")),
        (">=0.2.37-alpha2", dict(op=">=", major="0", minor="2", patch="37", pre="alpha2")),
        ("<1", dict(op="<", major="1", minor=None, patch=None, pre=None)),
        ("<1.2", dict(op="<", major="1", minor="2", patch=None, pre=None)),
        ("<1.2.3", dict(op="<", major="1", minor="2", patch="3", pre=None)),
        ("<1.2.3-alpha.1", dict(op="<", major="1", minor="2", patch="3", pre="alpha.1")),
        ("<1.2.3-alpha2", dict(op="<", major="1", minor="2", patch="3", pre="alpha2")),
        ("<=0", dict(op="<=", major="0", minor=None, patch=None, pre=None)),
        ("<=0.11", dict(op="<=", major="0", minor="11", patch=None, pre=None)),
        ("<=0.1.17", dict(op="<=", major="0", minor="1", patch="17", pre=None)),
        ("<=0.2.37-alpha.1", dict(op="<=", major="0", minor="2", patch="37", pre="alpha.1")),
        ("<=0.2.37-alpha2", dict(op="<=", major="0", minor="2", patch="37", pre="alpha2")),
        ("~1", dict(op="~", major="1", minor=None, patch=None, pre=None)),
        ("~1.2", dict(op="~", major="1", minor="2", patch=None, pre=None)),
        ("~1.2.3", dict(op="~", major="1", minor="2", patch="3", pre=None)),
        ("~1.2.3-alpha.1", dict(op="~", major="1", minor="2", patch="3", pre="alpha.1")),
        ("~1.2.3-alpha2", dict(op="~", major="1", minor="2", patch="3", pre="alpha2")),
        ("^0", dict(op="^", major="0", minor=None, patch=None, pre=None)),
        ("^0.11", dict(op="^", major="0", minor="11", patch=None, pre=None)),
        ("^0.1.17", dict(op="^", major="0", minor="1", patch="17", pre=None)),
        ("^0.2.37-alpha.1", dict(op="^", major="0", minor="2", patch="37", pre="alpha.1")),
        ("^0.2.37-alpha2", dict(op="^", major="0", minor="2", patch="37", pre="alpha2")),
        ("1.*", dict(op=None, major="1", minor="*", patch=None, pre=None)),
        ("1.2.*", dict(op=None, major="1", minor="2", patch="*", pre=None)),
        ("1.*.*", dict(op=None, major="1", minor="*", patch="*", pre=None)),
    ],
    ids=short_repr,
)
def test_version_req_regex(string: str, expected: dict):
    match = VERSION_REQ_REGEX.match(string)
    assert match is not None
    assert match.groupdict() == expected
