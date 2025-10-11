from cargo2rpm.semver import Version
from cargo2rpm.utils import short_repr

import pytest


@pytest.mark.parametrize(
    "string,expected",
    [
        ("1.0.0-alpha", Version(1, 0, 0, "alpha")),
        ("1.0.0-alpha.1", Version(1, 0, 0, "alpha.1")),
        ("1.0.0-0.3.7", Version(1, 0, 0, "0.3.7")),
        ("1.0.0-x.7.z.92", Version(1, 0, 0, "x.7.z.92")),
        ("1.0.0-x-y-z.--", Version(1, 0, 0, "x-y-z.--")),
        ("1.0.0-alpha+001", Version(1, 0, 0, "alpha", "001")),
        ("1.0.0+20130313144700", Version(1, 0, 0, None, "20130313144700")),
        ("1.0.0-beta+exp.sha.5114f85", Version(1, 0, 0, "beta", "exp.sha.5114f85")),
        ("1.0.0+21AF26D3----117B344092BD", Version(1, 0, 0, None, "21AF26D3----117B344092BD")),
        # valid versions from semver.org regular expression:
        # https://regex101.com/r/Ly7O1x/3/
        ("0.0.4", Version(0, 0, 4)),
        ("1.2.3", Version(1, 2, 3)),
        ("10.20.30", Version(10, 20, 30)),
        ("1.1.2+meta", Version(1, 1, 2, None, "meta")),
        ("1.1.2+meta-valid", Version(1, 1, 2, None, "meta-valid")),
        ("1.0.0-alpha", Version(1, 0, 0, "alpha")),
        ("1.0.0-alpha.beta", Version(1, 0, 0, "alpha.beta")),
        ("1.0.0-alpha.beta.1", Version(1, 0, 0, "alpha.beta.1")),
        ("1.0.0-alpha.1", Version(1, 0, 0, "alpha.1")),
        ("1.0.0-alpha0.valid", Version(1, 0, 0, "alpha0.valid")),
        ("1.0.0-alpha.0valid", Version(1, 0, 0, "alpha.0valid")),
        ("1.0.0-alpha-a.b-c-somethinglong+build.1-aef.1-its-okay", Version(1, 0, 0, "alpha-a.b-c-somethinglong", "build.1-aef.1-its-okay")),
        ("1.0.0-rc.1+build.1", Version(1, 0, 0, "rc.1", "build.1")),
        ("2.0.0-rc.1+build.123", Version(2, 0, 0, "rc.1", "build.123")),
        ("10.2.3-DEV-SNAPSHOT", Version(10, 2, 3, "DEV-SNAPSHOT")),
        ("1.2.3-SNAPSHOT-123", Version(1, 2, 3, "SNAPSHOT-123")),
        ("1.0.0", Version(1, 0, 0)),
        ("2.0.0", Version(2, 0, 0)),
        ("1.1.7", Version(1, 1, 7)),
        ("2.0.0+build.1848", Version(2, 0, 0, None, "build.1848")),
        ("2.0.1-alpha.1227", Version(2, 0, 1, "alpha.1227")),
        ("1.0.0-alpha+beta", Version(1, 0, 0, "alpha", "beta")),
        ("1.2.3----RC-SNAPSHOT.12.9.1--.12+788", Version(1, 2, 3, "---RC-SNAPSHOT.12.9.1--.12", "788")),
        ("1.2.3----R-S.12.9.1--.12+meta", Version(1, 2, 3, "---R-S.12.9.1--.12", "meta")),
        ("1.2.3----RC-SNAPSHOT.12.9.1--.12", Version(1, 2, 3, "---RC-SNAPSHOT.12.9.1--.12")),
        ("1.0.0+0.build.1-rc.10000aaa-kk-0.1", Version(1, 0, 0, None, "0.build.1-rc.10000aaa-kk-0.1")),
        (
            "99999999999999999999999.999999999999999999.99999999999999999",
            Version(99999999999999999999999, 999999999999999999, 99999999999999999),
        ),
        ("1.0.0-0A.is.legal", Version(1, 0, 0, "0A.is.legal")),
    ],
    ids=short_repr,
)
def test_parse_version(string: str, expected: Version):
    assert Version.parse(string) == expected


@pytest.mark.parametrize(
    "string",
    [
        "foo",
        "0.0",
        "0-alpha.1",
        "01.2.3",
        "1.02.3",
        "1.2.03",
        # invalid versions from semver.org regular expression:
        # https://regex101.com/r/Ly7O1x/3/
        "1",
        "1.2",
        "1.2.3-0123",
        "1.2.3-0123.0123",
        "1.1.2+.123",
        "+invalid",
        "-invalid",
        "-invalid+invalid",
        "-invalid.01",
        "alpha",
        "alpha.beta",
        "alpha.beta.1",
        "alpha.1",
        "alpha+beta",
        "alpha_beta",
        "alpha.",
        "alpha..",
        "beta",
        "1.0.0-alpha_beta",
        "-alpha.",
        "1.0.0-alpha..",
        "1.0.0-alpha..1",
        "1.0.0-alpha...1",
        "1.0.0-alpha....1",
        "1.0.0-alpha.....1",
        "1.0.0-alpha......1",
        "1.0.0-alpha.......1",
        "01.1.1",
        "1.01.1",
        "1.1.01",
        "1.2",
        "1.2.3.DEV",
        "1.2-SNAPSHOT",
        "1.2.31.2.3----RC-SNAPSHOT.12.09.1--..12+788",
        "1.2-RC-SNAPSHOT",
        "-1.0.3-gamma+b7718",
        "+justmeta",
        "9.8.7+meta+meta",
        "9.8.7-whatever+meta+meta",
        "99999999999999999999999.999999999999999999.99999999999999999----RC-SNAPSHOT.12.09.1--------------------------------..12",
    ],
    ids=short_repr,
)
def test_parse_version_fail(string: str):
    with pytest.raises(ValueError) as exc:
        Version.parse(string)
    assert "Invalid version" in str(exc.value)


@pytest.mark.parametrize(
    "string,version",
    [
        ("0.0.4", Version(0, 0, 4)),
        ("1.2.3", Version(1, 2, 3)),
        ("10.20.30", Version(10, 20, 30)),
        ("1.0.0~alpha", Version(1, 0, 0, "alpha")),
        ("1.0.0~alpha.1", Version(1, 0, 0, "alpha.1")),
        ("1.0.0~0.3.7", Version(1, 0, 0, "0.3.7")),
        ("1.0.0~x.7.z.92", Version(1, 0, 0, "x.7.z.92")),
        ("1.0.0~x_y_z.__", Version(1, 0, 0, "x-y-z.--")),
    ],
    ids=short_repr,
)
def test_version_to_from_rpm(string: str, version: Version):
    parsed = Version.from_rpm(string)
    assert parsed == version
    assert parsed.to_rpm() == string
