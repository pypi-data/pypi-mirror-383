import textwrap

from cargo2rpm.utils import load_metadata_from_resource, short_repr

import pytest


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", "A non-cryptographic hash function using AES-NI for high performance."),
        ("aho-corasick-1.0.2.json", "Fast multiple substring searching."),
        ("assert_cmd-2.0.8.json", "Test CLI Applications."),
        ("assert_fs-1.0.10.json", "Filesystem fixtures and assertions for testing."),
        ("autocfg-1.1.0.json", "Automatic cfg for Rust compiler features."),
        ("bstr-1.2.0.json", "A string type that is not required to be valid UTF-8."),
        (
            "cfg-if-1.0.0.json",
            textwrap.dedent(
                """\
                A macro to ergonomically define an item depending on a large number of
                #[cfg] parameters. Structured like an if-else chain, the first matching
                branch is the item that gets emitted."""
            ),
        ),
        (
            "clap-4.1.4.json",
            textwrap.dedent(
                """\
                A simple to use, efficient, and full-featured Command Line Argument
                Parser."""
            ),
        ),
        ("gstreamer-0.19.7.json", "Rust bindings for GStreamer."),
        ("human-panic-1.1.0.json", "Panic messages for humans."),
        ("hyperfine-1.15.0.json", "A command-line benchmarking tool."),
        ("iri-string-0.7.0.json", "IRI as string types."),
        ("libc-0.2.139.json", "Raw FFI bindings to platform libraries like libc."),
        ("predicates-2.1.5.json", "An implementation of boolean-valued predicate functions."),
        (
            "proc-macro2-1.0.50.json",
            textwrap.dedent(
                """\
                A substitute implementation of the compiler's `proc_macro` API to
                decouple token-based libraries from the procedural macro use case."""
            ),
        ),
        ("quote-1.0.23.json", "Quasi-quoting macro quote!(...)."),
        ("rand-0.8.5.json", "Random number generators and other randomness functionality."),
        ("rand_core-0.6.4.json", "Core random number generator traits and tools for implementation."),
        (
            "regex-1.8.4.json",
            textwrap.dedent(
                """\
                An implementation of regular expressions for Rust. This implementation
                uses finite automata and guarantees linear time matching on all inputs."""
            ),
        ),
        ("regex-syntax-0.7.2.json", "A regular expression parser."),
        ("rpm-sequoia-1.2.0.json", "An implementation of the RPM PGP interface using Sequoia."),
        (
            "rust_decimal-1.28.0.json",
            textwrap.dedent(
                """\
                Decimal number implementation written in pure Rust suitable for
                financial and fixed-precision calculations."""
            ),
        ),
        ("rustix-0.36.8.json", "Safe Rust bindings to POSIX/Unix/Linux/Winsock2-like syscalls."),
        ("serde-1.0.152.json", "A generic serialization/deserialization framework."),
        ("serde_derive-1.0.152.json", "Macros 1.1 implementation of #[derive(Serialize, Deserialize)]."),
        ("sha1collisiondetection-0.3.1.json", "SHA-1 hash function with collision detection and mitigation."),
        ("syn-1.0.107.json", "Parser for Rust source code."),
        (
            "time-0.3.17.json",
            textwrap.dedent(
                """\
                Date and time library. Fully interoperable with the standard library.
                Mostly compatible with #![no_std]."""
            ),
        ),
        (
            "tokio-1.25.0.json",
            textwrap.dedent(
                """\
                An event-driven, non-blocking I/O platform for writing asynchronous I/O
                backed applications."""
            ),
        ),
        (
            "unicode-xid-0.2.4.json",
            textwrap.dedent(
                """\
                Determine whether characters have the XID_Start or XID_Continue
                properties according to Unicode Standard Annex #31."""
            ),
        ),
        ("zbus-3.8.0.json", "API for D-Bus communication."),
        ("zoxide-0.9.0.json", "A smarter cd command for your terminal."),
    ],
    ids=short_repr,
)
def test_metadata_get_description(filename: str, expected: str):
    metadata = load_metadata_from_resource(filename)
    assert metadata.packages[0].get_description() == expected


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("ahash-0.8.3.json", "Non-cryptographic hash function using AES-NI for high performance"),
        ("aho-corasick-1.0.2.json", "Fast multiple substring searching"),
        ("assert_cmd-2.0.8.json", "Test CLI Applications"),
        ("assert_fs-1.0.10.json", "Filesystem fixtures and assertions for testing"),
        ("autocfg-1.1.0.json", "Automatic cfg for Rust compiler features"),
        ("bstr-1.2.0.json", "String type that is not required to be valid UTF-8"),
        ("cfg-if-1.0.0.json", "Macro to ergonomically define an item depending on a large number of #[cfg] parameters"),
        ("clap-4.1.4.json", "Simple to use, efficient, and full-featured Command Line Argument Parser"),
        ("gstreamer-0.19.7.json", "Rust bindings for GStreamer"),
        ("human-panic-1.1.0.json", "Panic messages for humans"),
        ("hyperfine-1.15.0.json", "Command-line benchmarking tool"),
        ("iri-string-0.7.0.json", "IRI as string types"),
        ("libc-0.2.139.json", "Raw FFI bindings to platform libraries like libc"),
        ("predicates-2.1.5.json", "Implementation of boolean-valued predicate functions"),
        (
            "proc-macro2-1.0.50.json",
            "Substitute implementation of the compiler's proc_macro API to decouple token-based libraries from the procedural macro use case",
        ),
        ("quote-1.0.23.json", "Quasi-quoting macro quote!(...)"),
        ("rand-0.8.5.json", "Random number generators and other randomness functionality"),
        ("rand_core-0.6.4.json", "Core random number generator traits and tools for implementation"),
        ("regex-1.8.4.json", "Implementation of regular expressions for Rust"),
        ("regex-syntax-0.7.2.json", "Regular expression parser"),
        ("rpm-sequoia-1.2.0.json", "Implementation of the RPM PGP interface using Sequoia"),
        (
            "rust_decimal-1.28.0.json",
            "Decimal number implementation written in pure Rust suitable for financial and fixed-precision calculations",
        ),
        ("rustix-0.36.8.json", "Safe Rust bindings to POSIX/Unix/Linux/Winsock2-like syscalls"),
        ("serde-1.0.152.json", "Generic serialization/deserialization framework"),
        ("serde_derive-1.0.152.json", "Macros 1.1 implementation of #[derive(Serialize, Deserialize)]"),
        ("sha1collisiondetection-0.3.1.json", "SHA-1 hash function with collision detection and mitigation"),
        ("syn-1.0.107.json", "Parser for Rust source code"),
        ("time-0.3.17.json", "Date and time library"),
        ("tokio-1.25.0.json", "Event-driven, non-blocking I/O platform for writing asynchronous I/O backed applications"),
        (
            "unicode-xid-0.2.4.json",
            "Determine whether characters have the XID_Start or XID_Continue properties according to Unicode Standard Annex #31",
        ),
        ("zbus-3.8.0.json", "API for D-Bus communication"),
        ("zoxide-0.9.0.json", "Smarter cd command for your terminal"),
    ],
    ids=short_repr,
)
def test_metadata_get_summary(filename: str, expected: str):
    metadata = load_metadata_from_resource(filename)
    assert metadata.packages[0].get_summary() == expected
