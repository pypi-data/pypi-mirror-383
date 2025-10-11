from typing import Optional

from cargo2rpm.utils import load_metadata_from_resource, short_repr

import pytest


@pytest.mark.parametrize(
    "filename",
    [
        "ahash-0.8.3.json",
        "aho-corasick-1.0.2.json",
        "assert_cmd-2.0.8.json",
        "assert_fs-1.0.10.json",
        "autocfg-1.1.0.json",
        "bstr-1.2.0.json",
        "cfg-if-1.0.0.json",
        "clap-4.1.4.json",
        "espanso-2.1.8.json",
        "fapolicy-analyzer-0.6.8.json",
        "gstreamer-0.19.7.json",
        "human-panic-1.1.0.json",
        "hyperfine-1.15.0.json",
        "iri-string-0.7.0.json",
        "libblkio-1.2.2.json",
        "libc-0.2.139.json",
        "predicates-2.1.5.json",
        "proc-macro2-1.0.50.json",
        "quote-1.0.23.json",
        "rand-0.8.5.json",
        "rand_core-0.6.4.json",
        "regex-1.8.4.json",
        "regex-syntax-0.7.2.json",
        "rpm-sequoia-1.2.0.json",
        "rust_decimal-1.28.0.json",
        "rustix-0.36.8.json",
        "serde-1.0.152.json",
        "serde_derive-1.0.152.json",
        "sha1collisiondetection-0.3.1.json",
        "syn-1.0.107.json",
        "time-0.3.17.json",
        "tokio-1.25.0.json",
        "unicode-xid-0.2.4.json",
        "zbus-3.8.0.json",
        "zola-0.16.1.json",
        "zoxide-0.9.0.json",
    ],
    ids=short_repr,
)
def test_metadata_smoke(filename: str):
    metadata = load_metadata_from_resource(filename)
    packages = metadata.packages
    assert len(packages) >= 1


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", False),
        ("aho-corasick-1.0.2.json", False),
        ("assert_cmd-2.0.8.json", True),
        ("assert_fs-1.0.10.json", False),
        ("autocfg-1.1.0.json", False),
        ("bstr-1.2.0.json", False),
        ("cfg-if-1.0.0.json", False),
        ("clap-4.1.4.json", True),
        ("espanso-2.1.8.json", True),
        ("fapolicy-analyzer-0.6.8.json", True),
        ("gstreamer-0.19.7.json", False),
        ("human-panic-1.1.0.json", False),
        ("hyperfine-1.15.0.json", True),
        ("iri-string-0.7.0.json", False),
        ("libblkio-1.2.2.json", False),
        ("libc-0.2.139.json", False),
        ("predicates-2.1.5.json", False),
        ("proc-macro2-1.0.50.json", False),
        ("quote-1.0.23.json", False),
        ("rand-0.8.5.json", False),
        ("rand_core-0.6.4.json", False),
        ("regex-1.8.4.json", False),
        ("regex-syntax-0.7.2.json", False),
        ("rpm-sequoia-1.2.0.json", False),
        ("rust_decimal-1.28.0.json", False),
        ("rustix-0.36.8.json", False),
        ("serde-1.0.152.json", False),
        ("serde_derive-1.0.152.json", False),
        ("sha1collisiondetection-0.3.1.json", True),
        ("syn-1.0.107.json", False),
        ("time-0.3.17.json", False),
        ("tokio-1.25.0.json", False),
        ("unicode-xid-0.2.4.json", False),
        ("zbus-3.8.0.json", False),
        ("zola-0.16.1.json", True),
        ("zoxide-0.9.0.json", True),
    ],
    ids=short_repr,
)
def test_metadata_is_bin(filename: str, expected):
    metadata = load_metadata_from_resource(filename)
    assert metadata.is_bin() == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", True),
        ("aho-corasick-1.0.2.json", True),
        ("assert_cmd-2.0.8.json", True),
        ("assert_fs-1.0.10.json", True),
        ("autocfg-1.1.0.json", True),
        ("bstr-1.2.0.json", True),
        ("cfg-if-1.0.0.json", True),
        ("clap-4.1.4.json", True),
        ("espanso-2.1.8.json", False),
        ("fapolicy-analyzer-0.6.8.json", False),
        ("gstreamer-0.19.7.json", True),
        ("human-panic-1.1.0.json", True),
        ("hyperfine-1.15.0.json", False),
        ("iri-string-0.7.0.json", True),
        ("libblkio-1.2.2.json", False),
        ("libc-0.2.139.json", True),
        ("predicates-2.1.5.json", True),
        ("proc-macro2-1.0.50.json", True),
        ("quote-1.0.23.json", True),
        ("rand-0.8.5.json", True),
        ("rand_core-0.6.4.json", True),
        ("regex-1.8.4.json", True),
        ("regex-syntax-0.7.2.json", True),
        ("rpm-sequoia-1.2.0.json", False),
        ("rust_decimal-1.28.0.json", True),
        ("rustix-0.36.8.json", True),
        ("serde-1.0.152.json", True),
        ("serde_derive-1.0.152.json", True),
        ("sha1collisiondetection-0.3.1.json", True),
        ("syn-1.0.107.json", True),
        ("time-0.3.17.json", True),
        ("tokio-1.25.0.json", True),
        ("unicode-xid-0.2.4.json", True),
        ("zbus-3.8.0.json", True),
        ("zola-0.16.1.json", False),
        ("zoxide-0.9.0.json", False),
    ],
    ids=short_repr,
)
def test_metadata_is_lib(filename: str, expected: bool):
    metadata = load_metadata_from_resource(filename)
    assert metadata.is_lib() == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", False),
        ("aho-corasick-1.0.2.json", False),
        ("assert_cmd-2.0.8.json", False),
        ("assert_fs-1.0.10.json", False),
        ("autocfg-1.1.0.json", False),
        ("bstr-1.2.0.json", False),
        ("cfg-if-1.0.0.json", False),
        ("clap-4.1.4.json", False),
        ("espanso-2.1.8.json", True),
        ("fapolicy-analyzer-0.6.8.json", True),
        ("gstreamer-0.19.7.json", False),
        ("human-panic-1.1.0.json", False),
        ("hyperfine-1.15.0.json", False),
        ("iri-string-0.7.0.json", False),
        ("libblkio-1.2.2.json", True),
        ("libc-0.2.139.json", False),
        ("predicates-2.1.5.json", False),
        ("proc-macro2-1.0.50.json", False),
        ("quote-1.0.23.json", False),
        ("rand-0.8.5.json", False),
        ("rand_core-0.6.4.json", False),
        ("regex-1.8.4.json", False),
        ("regex-syntax-0.7.2.json", False),
        ("rpm-sequoia-1.2.0.json", False),
        ("rust_decimal-1.28.0.json", False),
        ("rustix-0.36.8.json", False),
        ("serde-1.0.152.json", False),
        ("serde_derive-1.0.152.json", False),
        ("sha1collisiondetection-0.3.1.json", False),
        ("syn-1.0.107.json", False),
        ("time-0.3.17.json", False),
        ("tokio-1.25.0.json", False),
        ("unicode-xid-0.2.4.json", False),
        ("zbus-3.8.0.json", False),
        ("zola-0.16.1.json", True),
        ("zoxide-0.9.0.json", False),
    ],
    ids=short_repr,
)
def test_metadata_is_workspace(filename: str, expected: bool):
    metadata = load_metadata_from_resource(filename)
    assert metadata.is_workspace() == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", set()),
        ("aho-corasick-1.0.2.json", set()),
        ("assert_cmd-2.0.8.json", {"bin_fixture"}),
        ("assert_fs-1.0.10.json", set()),
        ("autocfg-1.1.0.json", set()),
        ("bstr-1.2.0.json", set()),
        ("cfg-if-1.0.0.json", set()),
        ("clap-4.1.4.json", {"stdio-fixture"}),
        ("espanso-2.1.8.json", {"espanso"}),
        ("fapolicy-analyzer-0.6.8.json", {"tdb", "rulec"}),
        ("gstreamer-0.19.7.json", set()),
        ("human-panic-1.1.0.json", set()),
        ("hyperfine-1.15.0.json", {"hyperfine"}),
        ("iri-string-0.7.0.json", set()),
        ("libblkio-1.2.2.json", set()),
        ("libc-0.2.139.json", set()),
        ("predicates-2.1.5.json", set()),
        ("proc-macro2-1.0.50.json", set()),
        ("quote-1.0.23.json", set()),
        ("rand-0.8.5.json", set()),
        ("rand_core-0.6.4.json", set()),
        ("regex-1.8.4.json", set()),
        ("regex-syntax-0.7.2.json", set()),
        ("rpm-sequoia-1.2.0.json", set()),
        ("rust_decimal-1.28.0.json", set()),
        ("rustix-0.36.8.json", set()),
        ("serde-1.0.152.json", set()),
        ("serde_derive-1.0.152.json", set()),
        ("sha1collisiondetection-0.3.1.json", {"sha1cdsum"}),
        ("syn-1.0.107.json", set()),
        ("time-0.3.17.json", set()),
        ("tokio-1.25.0.json", set()),
        ("unicode-xid-0.2.4.json", set()),
        ("zbus-3.8.0.json", set()),
        ("zola-0.16.1.json", {"zola"}),
        ("zoxide-0.9.0.json", {"zoxide"}),
    ],
    ids=short_repr,
)
def test_metadata_get_binaries(filename: str, expected: set[str]):
    metadata = load_metadata_from_resource(filename)
    assert metadata.get_binaries() == expected


@pytest.mark.parametrize(
    "filename,feature,expected",
    [
        ("ahash-0.8.3.json", None, "crate(ahash) = 0.8.3"),
        ("ahash-0.8.3.json", "default", "crate(ahash/default) = 0.8.3"),
        ("assert_cmd-2.0.8.json", None, "crate(assert_cmd) = 2.0.8"),
        ("assert_cmd-2.0.8.json", "default", "crate(assert_cmd/default) = 2.0.8"),
    ],
    ids=short_repr,
)
def test_package_to_rpm_dependency(filename: str, feature: Optional[str], expected: str):
    data = load_metadata_from_resource(filename)
    assert data.packages[0].to_rpm_dependency(feature) == expected
