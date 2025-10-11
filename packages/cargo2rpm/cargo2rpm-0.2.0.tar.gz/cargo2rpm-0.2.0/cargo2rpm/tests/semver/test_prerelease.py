from cargo2rpm.semver import PreRelease

import pytest


@pytest.mark.parametrize(
    "string,expected",
    [
        ("alpha", PreRelease(["alpha"])),
        ("alpha.beta", PreRelease(["alpha", "beta"])),
        ("alpha.beta.1", PreRelease(["alpha", "beta", 1])),
        ("alpha.1", PreRelease(["alpha", 1])),
        ("alpha0.valid", PreRelease(["alpha0", "valid"])),
        ("alpha.0valid", PreRelease(["alpha", "0valid"])),
        ("alpha-a.b-c-somethinglong", PreRelease(["alpha-a", "b-c-somethinglong"])),
        ("rc.1", PreRelease(["rc", 1])),
        ("DEV-SNAPSHOT", PreRelease(["DEV-SNAPSHOT"])),
        ("SNAPSHOT-123", PreRelease(["SNAPSHOT-123"])),
        ("alpha.1227", PreRelease(["alpha", 1227])),
        ("---RC-SNAPSHOT.12.9.1--.12", PreRelease(["---RC-SNAPSHOT", 12, 9, "1--", 12])),
        ("---R-S.12.9.1--.12", PreRelease(["---R-S", 12, 9, "1--", 12])),
        ("---RC-SNAPSHOT.12.9.1--.12", PreRelease(["---RC-SNAPSHOT", 12, 9, "1--", 12])),
        ("0A.is.legal", PreRelease(["0A", "is", "legal"])),
    ],
    ids=repr,
)
def test_parse_prerelease(string: str, expected: PreRelease):
    assert PreRelease.parse(string) == expected
