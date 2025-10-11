from cargo2rpm.rpm import _requires_crate, _requires_feature
from cargo2rpm.utils import load_metadata_from_resource, short_repr

import pytest


@pytest.mark.parametrize(
    "filename,expected",
    [
        (
            "ahash-0.8.3.json",
            {
                "cargo",
                "(crate(cfg-if/default) >= 1.0.0 with crate(cfg-if/default) < 2.0.0~)",
                "(crate(once_cell) >= 1.13.1 with crate(once_cell) < 2.0.0~)",
                "(crate(once_cell/unstable) >= 1.13.1 with crate(once_cell/unstable) < 2.0.0~)",
                "(crate(once_cell/alloc) >= 1.13.1 with crate(once_cell/alloc) < 2.0.0~)",
                "(crate(version_check/default) >= 0.9.4 with crate(version_check/default) < 0.10.0~)",
            },
        ),
        (
            "assert_cmd-2.0.8.json",
            {
                "cargo",
                "rust >= 1.60.0",
                "(crate(bstr/default) >= 1.0.1 with crate(bstr/default) < 2.0.0~)",
                "(crate(doc-comment/default) >= 0.3.0 with crate(doc-comment/default) < 0.4.0~)",
                "(crate(predicates) >= 2.1.0 with crate(predicates) < 3.0.0~)",
                "(crate(predicates/diff) >= 2.1.0 with crate(predicates/diff) < 3.0.0~)",
                "(crate(predicates-core/default) >= 1.0.0 with crate(predicates-core/default) < 2.0.0~)",
                "(crate(predicates-tree/default) >= 1.0.0 with crate(predicates-tree/default) < 2.0.0~)",
                "(crate(wait-timeout/default) >= 0.2.0 with crate(wait-timeout/default) < 0.3.0~)",
            },
        ),
        (
            "assert_fs-1.0.10.json",
            {
                "cargo",
                "rust >= 1.60.0",
                "(crate(doc-comment/default) >= 0.3.0 with crate(doc-comment/default) < 0.4.0~)",
                "(crate(globwalk/default) >= 0.8.0 with crate(globwalk/default) < 0.9.0~)",
                "(crate(predicates) >= 2.0.3 with crate(predicates) < 3.0.0~)",
                "(crate(predicates/diff) >= 2.0.3 with crate(predicates/diff) < 3.0.0~)",
                "(crate(predicates-core/default) >= 1.0.0 with crate(predicates-core/default) < 2.0.0~)",
                "(crate(predicates-tree/default) >= 1.0.0 with crate(predicates-tree/default) < 2.0.0~)",
                "(crate(tempfile/default) >= 3.0.0 with crate(tempfile/default) < 4.0.0~)",
            },
        ),
        (
            "autocfg-1.1.0.json",
            {
                "cargo",
            },
        ),
        (
            "bstr-1.2.0.json",
            {
                "cargo",
                "rust >= 1.60",
                "(crate(memchr) >= 2.4.0 with crate(memchr) < 3.0.0~)",
            },
        ),
        (
            "cfg-if-1.0.0.json",
            {
                "cargo",
            },
        ),
        (
            "clap-4.1.4.json",
            {
                "cargo",
                "rust >= 1.64.0",
                "(crate(bitflags/default) >= 1.2.0 with crate(bitflags/default) < 2.0.0~)",
                "(crate(clap_lex/default) >= 0.3.0 with crate(clap_lex/default) < 0.4.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            {
                "cargo",
                "rust >= 1.63",
                "(crate(bitflags/default) >= 1.0.0 with crate(bitflags/default) < 2.0.0~)",
                "(crate(cfg-if/default) >= 1.0.0 with crate(cfg-if/default) < 2.0.0~)",
                "(crate(gstreamer-sys/default) >= 0.19.0 with crate(gstreamer-sys/default) < 0.20.0~)",
                "(crate(futures-channel/default) >= 0.3.0 with crate(futures-channel/default) < 0.4.0~)",
                "(crate(futures-core/default) >= 0.3.0 with crate(futures-core/default) < 0.4.0~)",
                "(crate(futures-util) >= 0.3.0 with crate(futures-util) < 0.4.0~)",
                "(crate(glib/default) >= 0.16.2 with crate(glib/default) < 0.17.0~)",
                "(crate(libc/default) >= 0.2.0 with crate(libc/default) < 0.3.0~)",
                "(crate(muldiv/default) >= 1.0.0 with crate(muldiv/default) < 2.0.0~)",
                "(crate(num-integer) >= 0.1.0 with crate(num-integer) < 0.2.0~)",
                "(crate(num-rational) >= 0.4.0 with crate(num-rational) < 0.5.0~)",
                "(crate(once_cell/default) >= 1.0.0 with crate(once_cell/default) < 2.0.0~)",
                "(crate(option-operations/default) >= 0.5.0 with crate(option-operations/default) < 0.6.0~)",
                "(crate(paste/default) >= 1.0.0 with crate(paste/default) < 2.0.0~)",
                "(crate(pretty-hex/default) >= 0.3.0 with crate(pretty-hex/default) < 0.4.0~)",
                "(crate(thiserror/default) >= 1.0.0 with crate(thiserror/default) < 2.0.0~)",
            },
        ),
        (
            "human-panic-1.1.0.json",
            {
                "cargo",
                "rust >= 1.60.0",
                "(crate(backtrace/default) >= 0.3.9 with crate(backtrace/default) < 0.4.0~)",
                "(crate(os_info/default) >= 2.0.6 with crate(os_info/default) < 3.0.0~)",
                "(crate(serde/default) >= 1.0.79 with crate(serde/default) < 2.0.0~)",
                "(crate(serde_derive/default) >= 1.0.79 with crate(serde_derive/default) < 2.0.0~)",
                "(crate(toml/default) >= 0.5.0 with crate(toml/default) < 0.6.0~)",
                "(crate(uuid) >= 0.8.0 with crate(uuid) < 0.9.0~)",
                "(crate(uuid/v4) >= 0.8.0 with crate(uuid/v4) < 0.9.0~)",
            },
        ),
        (
            "libc-0.2.139.json",
            {
                "cargo",
            },
        ),
        (
            "predicates-2.1.5.json",
            {
                "cargo",
                "rust >= 1.60.0",
                "(crate(itertools/default) >= 0.10.0 with crate(itertools/default) < 0.11.0~)",
                "(crate(predicates-core/default) >= 1.0.0 with crate(predicates-core/default) < 2.0.0~)",
            },
        ),
        (
            "proc-macro2-1.0.50.json",
            {
                "cargo",
                "rust >= 1.31",
                "(crate(unicode-ident/default) >= 1.0.0 with crate(unicode-ident/default) < 2.0.0~)",
            },
        ),
        (
            "quote-1.0.23.json",
            {
                "cargo",
                "rust >= 1.31",
                "(crate(proc-macro2) >= 1.0.40 with crate(proc-macro2) < 2.0.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            {
                "cargo",
                "(crate(rand_core/default) >= 0.6.0 with crate(rand_core/default) < 0.7.0~)",
            },
        ),
        (
            "rand_core-0.6.4.json",
            {
                "cargo",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            {
                "cargo",
                "rust >= 1.60",
                "(crate(arrayvec) >= 0.7.0 with crate(arrayvec) < 0.8.0~)",
                "(crate(num-traits) >= 0.2.0 with crate(num-traits) < 0.3.0~)",
                "(crate(num-traits/i128) >= 0.2.0 with crate(num-traits/i128) < 0.3.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            {
                "cargo",
                "rust >= 1.48",
                "(crate(bitflags/default) >= 1.2.1 with crate(bitflags/default) < 2.0.0~)",
                "(crate(linux-raw-sys) >= 0.1.2 with crate(linux-raw-sys) < 0.2.0~)",
                "(crate(linux-raw-sys/errno) >= 0.1.2 with crate(linux-raw-sys/errno) < 0.2.0~)",
                "(crate(linux-raw-sys/general) >= 0.1.2 with crate(linux-raw-sys/general) < 0.2.0~)",
                "(crate(linux-raw-sys/ioctl) >= 0.1.2 with crate(linux-raw-sys/ioctl) < 0.2.0~)",
                "(crate(linux-raw-sys/no_std) >= 0.1.2 with crate(linux-raw-sys/no_std) < 0.2.0~)",
                "(crate(libc/default) >= 0.2.133 with crate(libc/default) < 0.3.0~)",
                "(crate(libc/extra_traits) >= 0.2.133 with crate(libc/extra_traits) < 0.3.0~)",
                "(crate(errno) >= 0.2.8 with crate(errno) < 0.3.0~)",
                "(crate(windows-sys/default) >= 0.45.0 with crate(windows-sys/default) < 0.46.0~)",
                "(crate(windows-sys/Win32_Foundation) >= 0.45.0 with crate(windows-sys/Win32_Foundation) < 0.46.0~)",
                "(crate(windows-sys/Win32_Networking_WinSock) >= 0.45.0 with crate(windows-sys/Win32_Networking_WinSock) < 0.46.0~)",
                "(crate(windows-sys/Win32_NetworkManagement_IpHelper) >= 0.45.0 with crate(windows-sys/Win32_NetworkManagement_IpHelper) < 0.46.0~)",
                "(crate(windows-sys/Win32_System_Threading) >= 0.45.0 with crate(windows-sys/Win32_System_Threading) < 0.46.0~)",
            },
        ),
        (
            "serde-1.0.152.json",
            {
                "cargo",
                "rust >= 1.13",
            },
        ),
        (
            "serde_derive-1.0.152.json",
            {
                "cargo",
                "rust >= 1.31",
                "(crate(proc-macro2/default) >= 1.0.0 with crate(proc-macro2/default) < 2.0.0~)",
                "(crate(quote/default) >= 1.0.0 with crate(quote/default) < 2.0.0~)",
                "(crate(syn/default) >= 1.0.104 with crate(syn/default) < 2.0.0~)",
            },
        ),
        (
            "sha1collisiondetection-0.3.1.json",
            {
                "cargo",
                "rust >= 1.60",
                "(crate(generic-array/default) >= 0.12.0 with crate(generic-array/default) < 0.15.0~)",
            },
        ),
        (
            "syn-1.0.107.json",
            {
                "cargo",
                "rust >= 1.31",
                "(crate(proc-macro2) >= 1.0.46 with crate(proc-macro2) < 2.0.0~)",
                "(crate(unicode-ident/default) >= 1.0.0 with crate(unicode-ident/default) < 2.0.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            {
                "cargo",
                "rust >= 1.60.0",
                "crate(time-core/default) = 0.1.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            {
                "cargo",
                "rust >= 1.49",
                "(crate(pin-project-lite/default) >= 0.2.0 with crate(pin-project-lite/default) < 0.3.0~)",
                "(crate(autocfg/default) >= 1.1.0 with crate(autocfg/default) < 2.0.0~)",
                "(crate(windows-sys/default) >= 0.42.0 with crate(windows-sys/default) < 0.43.0~)",
                "(crate(windows-sys/Win32_Foundation) >= 0.42.0 with crate(windows-sys/Win32_Foundation) < 0.43.0~)",
                "(crate(windows-sys/Win32_Security_Authorization) >= 0.42.0 with crate(windows-sys/Win32_Security_Authorization) < 0.43.0~)",
            },
        ),
        (
            "unicode-xid-0.2.4.json",
            {
                "cargo",
                "rust >= 1.17",
            },
        ),
        (
            "zbus-3.8.0.json",
            {
                "cargo",
                "rust >= 1.60",
                "(crate(async-broadcast/default) >= 0.5.0 with crate(async-broadcast/default) < 0.6.0~)",
                "(crate(async-recursion/default) >= 1.0.0 with crate(async-recursion/default) < 2.0.0~)",
                "(crate(async-trait/default) >= 0.1.58 with crate(async-trait/default) < 0.2.0~)",
                "(crate(byteorder/default) >= 1.4.3 with crate(byteorder/default) < 2.0.0~)",
                "(crate(derivative/default) >= 2.2.0 with crate(derivative/default) < 3.0.0~)",
                "(crate(dirs/default) >= 4.0.0 with crate(dirs/default) < 5.0.0~)",
                "(crate(enumflags2/default) >= 0.7.5 with crate(enumflags2/default) < 0.8.0~)",
                "(crate(enumflags2/serde) >= 0.7.5 with crate(enumflags2/serde) < 0.8.0~)",
                "(crate(event-listener/default) >= 2.5.3 with crate(event-listener/default) < 3.0.0~)",
                "(crate(futures-core/default) >= 0.3.25 with crate(futures-core/default) < 0.4.0~)",
                "(crate(futures-sink/default) >= 0.3.25 with crate(futures-sink/default) < 0.4.0~)",
                "(crate(futures-util) >= 0.3.25 with crate(futures-util) < 0.4.0~)",
                "(crate(futures-util/sink) >= 0.3.25 with crate(futures-util/sink) < 0.4.0~)",
                "(crate(futures-util/std) >= 0.3.25 with crate(futures-util/std) < 0.4.0~)",
                "(crate(hex/default) >= 0.4.3 with crate(hex/default) < 0.5.0~)",
                "(crate(nix/default) >= 0.25.0 with crate(nix/default) < 0.26.0~)",
                "(crate(once_cell/default) >= 1.4.0 with crate(once_cell/default) < 2.0.0~)",
                "(crate(ordered-stream/default) >= 0.1.4 with crate(ordered-stream/default) < 0.2.0~)",
                "(crate(rand/default) >= 0.8.5 with crate(rand/default) < 0.9.0~)",
                "(crate(serde/default) >= 1.0.0 with crate(serde/default) < 2.0.0~)",
                "(crate(serde/derive) >= 1.0.0 with crate(serde/derive) < 2.0.0~)",
                "(crate(serde_repr/default) >= 0.1.9 with crate(serde_repr/default) < 0.2.0~)",
                "(crate(sha1/default) >= 0.10.5 with crate(sha1/default) < 0.11.0~)",
                "(crate(sha1/std) >= 0.10.5 with crate(sha1/std) < 0.11.0~)",
                "(crate(static_assertions/default) >= 1.1.0 with crate(static_assertions/default) < 2.0.0~)",
                "(crate(tracing/default) >= 0.1.37 with crate(tracing/default) < 0.2.0~)",
                "crate(zbus_macros/default) = 3.8.0",
                "(crate(zbus_names/default) >= 2.5.0 with crate(zbus_names/default) < 3.0.0~)",
                "(crate(zvariant) >= 3.10.0 with crate(zvariant) < 4.0.0~)",
                "(crate(zvariant/enumflags2) >= 3.10.0 with crate(zvariant/enumflags2) < 4.0.0~)",
                "(crate(uds_windows/default) >= 1.0.2 with crate(uds_windows/default) < 2.0.0~)",
                "(crate(winapi/default) >= 0.3.0 with crate(winapi/default) < 0.4.0~)",
                "(crate(winapi/handleapi) >= 0.3.0 with crate(winapi/handleapi) < 0.4.0~)",
                "(crate(winapi/iphlpapi) >= 0.3.0 with crate(winapi/iphlpapi) < 0.4.0~)",
                "(crate(winapi/memoryapi) >= 0.3.0 with crate(winapi/memoryapi) < 0.4.0~)",
                "(crate(winapi/processthreadsapi) >= 0.3.0 with crate(winapi/processthreadsapi) < 0.4.0~)",
                "(crate(winapi/sddl) >= 0.3.0 with crate(winapi/sddl) < 0.4.0~)",
                "(crate(winapi/securitybaseapi) >= 0.3.0 with crate(winapi/securitybaseapi) < 0.4.0~)",
                "(crate(winapi/synchapi) >= 0.3.0 with crate(winapi/synchapi) < 0.4.0~)",
                "(crate(winapi/tcpmib) >= 0.3.0 with crate(winapi/tcpmib) < 0.4.0~)",
                "(crate(winapi/winbase) >= 0.3.0 with crate(winapi/winbase) < 0.4.0~)",
                "(crate(winapi/winerror) >= 0.3.0 with crate(winapi/winerror) < 0.4.0~)",
                "(crate(winapi/winsock2) >= 0.3.0 with crate(winapi/winsock2) < 0.4.0~)",
            },
        ),
    ],
    ids=short_repr,
)
def test_requires_crate(filename: str, expected: set[str]):
    metadata = load_metadata_from_resource(filename)
    assert _requires_crate(metadata.packages[0]) == expected


@pytest.mark.parametrize(
    "filename,feature,expected",
    [
        (
            "ahash-0.8.3.json",
            "default",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "crate(ahash/std) = 0.8.3",
                "crate(ahash/runtime-rng) = 0.8.3",
            },
        ),
        (
            "ahash-0.8.3.json",
            "atomic-polyfill",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "(crate(atomic-polyfill/default) >= 1.0.1 with crate(atomic-polyfill/default) < 2.0.0~)",
                "(crate(once_cell/atomic-polyfill) >= 1.13.1 with crate(once_cell/atomic-polyfill) < 2.0.0~)",
            },
        ),
        (
            "ahash-0.8.3.json",
            "compile-time-rng",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "crate(ahash/const-random) = 0.8.3",
            },
        ),
        (
            "ahash-0.8.3.json",
            "const-random",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "(crate(const-random/default) >= 0.1.12 with crate(const-random/default) < 0.2.0~)",
            },
        ),
        (
            "ahash-0.8.3.json",
            "getrandom",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "(crate(getrandom/default) >= 0.2.7 with crate(getrandom/default) < 0.3.0~)",
            },
        ),
        (
            "ahash-0.8.3.json",
            "no-rng",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
            },
        ),
        (
            "ahash-0.8.3.json",
            "runtime-rng",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "crate(ahash/getrandom) = 0.8.3",
            },
        ),
        (
            "ahash-0.8.3.json",
            "serde",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
                "(crate(serde/default) >= 1.0.117 with crate(serde/default) < 2.0.0~)",
            },
        ),
        (
            "ahash-0.8.3.json",
            "std",
            {
                "cargo",
                "crate(ahash) = 0.8.3",
            },
        ),
        (
            "assert_cmd-2.0.8.json",
            "default",
            {
                "cargo",
                "crate(assert_cmd) = 2.0.8",
            },
        ),
        (
            "assert_cmd-2.0.8.json",
            "color",
            {
                "cargo",
                "crate(assert_cmd) = 2.0.8",
                "crate(concolor/default) = 0.0.11",
                "crate(concolor/std) = 0.0.11",
                "(crate(yansi/default) >= 0.5.1 with crate(yansi/default) < 0.6.0~)",
                "(crate(predicates/color) >= 2.1.0 with crate(predicates/color) < 3.0.0~)",
            },
        ),
        (
            "assert_cmd-2.0.8.json",
            "color-auto",
            {
                "cargo",
                "crate(assert_cmd) = 2.0.8",
                "crate(assert_cmd/color) = 2.0.8",
                "crate(concolor/auto) = 0.0.11",
                "crate(concolor/default) = 0.0.11",
            },
        ),
        (
            "assert_fs-1.0.10.json",
            "default",
            {
                "cargo",
                "crate(assert_fs) = 1.0.10",
            },
        ),
        (
            "assert_fs-1.0.10.json",
            "color",
            {
                "cargo",
                "crate(assert_fs) = 1.0.10",
                "crate(concolor/default) = 0.0.11",
                "(crate(yansi/default) >= 0.5.0 with crate(yansi/default) < 0.6.0~)",
                "(crate(predicates/color) >= 2.0.3 with crate(predicates/color) < 3.0.0~)",
            },
        ),
        (
            "assert_fs-1.0.10.json",
            "color-auto",
            {
                "cargo",
                "crate(assert_fs) = 1.0.10",
                "crate(assert_fs/color) = 1.0.10",
                "crate(concolor/auto) = 0.0.11",
                "crate(concolor/default) = 0.0.11",
            },
        ),
        (
            "autocfg-1.1.0.json",
            "default",
            {
                "cargo",
                "crate(autocfg) = 1.1.0",
            },
        ),
        (
            "bstr-1.2.0.json",
            "default",
            {
                "cargo",
                "crate(bstr) = 1.2.0",
                "crate(bstr/std) = 1.2.0",
                "crate(bstr/unicode) = 1.2.0",
            },
        ),
        (
            "bstr-1.2.0.json",
            "alloc",
            {
                "cargo",
                "crate(bstr) = 1.2.0",
                "(crate(serde) >= 1.0.85 with crate(serde) < 2.0.0~)",
                "(crate(serde/alloc) >= 1.0.85 with crate(serde/alloc) < 2.0.0~)",
            },
        ),
        (
            "bstr-1.2.0.json",
            "serde",
            {
                "cargo",
                "crate(bstr) = 1.2.0",
                "(crate(serde) >= 1.0.85 with crate(serde) < 2.0.0~)",
            },
        ),
        (
            "bstr-1.2.0.json",
            "std",
            {
                "cargo",
                "crate(bstr) = 1.2.0",
                "crate(bstr/alloc) = 1.2.0",
                "(crate(memchr/std) >= 2.4.0 with crate(memchr/std) < 3.0.0~)",
                "(crate(serde) >= 1.0.85 with crate(serde) < 2.0.0~)",
                "(crate(serde/std) >= 1.0.85 with crate(serde/std) < 2.0.0~)",
            },
        ),
        (
            "bstr-1.2.0.json",
            "unicode",
            {
                "cargo",
                "crate(bstr) = 1.2.0",
                "(crate(once_cell/default) >= 1.14.0 with crate(once_cell/default) < 2.0.0~)",
                "(crate(regex-automata) >= 0.1.5 with crate(regex-automata) < 0.2.0~)",
            },
        ),
        (
            "cfg-if-1.0.0.json",
            "default",
            {
                "cargo",
                "crate(cfg-if) = 1.0.0",
            },
        ),
        (
            "cfg-if-1.0.0.json",
            "compiler_builtins",
            {
                "cargo",
                "crate(cfg-if) = 1.0.0",
                "(crate(compiler_builtins/default) >= 0.1.2 with crate(compiler_builtins/default) < 0.2.0~)",
            },
        ),
        (
            "cfg-if-1.0.0.json",
            "core",
            {
                "cargo",
                "crate(cfg-if) = 1.0.0",
                "(crate(rustc-std-workspace-core/default) >= 1.0.0 with crate(rustc-std-workspace-core/default) < 2.0.0~)",
            },
        ),
        (
            "cfg-if-1.0.0.json",
            "rustc-dep-of-std",
            {
                "cargo",
                "crate(cfg-if) = 1.0.0",
                "crate(cfg-if/core) = 1.0.0",
                "crate(cfg-if/compiler_builtins) = 1.0.0",
            },
        ),
        (
            "clap-4.1.4.json",
            "default",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap/std) = 4.1.4",
                "crate(clap/color) = 4.1.4",
                "crate(clap/help) = 4.1.4",
                "crate(clap/usage) = 4.1.4",
                "crate(clap/error-context) = 4.1.4",
                "crate(clap/suggestions) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "cargo",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "(crate(once_cell/default) >= 1.12.0 with crate(once_cell/default) < 2.0.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "color",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "(crate(is-terminal/default) >= 0.4.1 with crate(is-terminal/default) < 0.5.0~)",
                "(crate(termcolor/default) >= 1.1.1 with crate(termcolor/default) < 2.0.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "debug",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap_derive/debug) = 4.1.0",
                "crate(clap_derive/default) = 4.1.0",
                "(crate(backtrace/default) >= 0.3.0 with crate(backtrace/default) < 0.4.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "deprecated",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap_derive/default) = 4.1.0",
                "crate(clap_derive/deprecated) = 4.1.0",
            },
        ),
        (
            "clap-4.1.4.json",
            "derive",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap_derive/default) = 4.1.0",
                "(crate(once_cell/default) >= 1.12.0 with crate(once_cell/default) < 2.0.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "env",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "error-context",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "help",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "std",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "string",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "suggestions",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap/error-context) = 4.1.4",
                "(crate(strsim/default) >= 0.10.0 with crate(strsim/default) < 0.11.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "unicode",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "(crate(unicode-width/default) >= 0.1.9 with crate(unicode-width/default) < 0.2.0~)",
                "(crate(unicase/default) >= 2.6.0 with crate(unicase/default) < 3.0.0~)",
            },
        ),
        (
            "clap-4.1.4.json",
            "unstable-doc",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap/derive) = 4.1.4",
                "crate(clap/cargo) = 4.1.4",
                "crate(clap/wrap_help) = 4.1.4",
                "crate(clap/env) = 4.1.4",
                "crate(clap/unicode) = 4.1.4",
                "crate(clap/string) = 4.1.4",
                "crate(clap/unstable-replace) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "unstable-grouped",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "unstable-replace",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "unstable-v5",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap/deprecated) = 4.1.4",
                "crate(clap_derive/default) = 4.1.0",
                "crate(clap_derive/unstable-v5) = 4.1.0",
            },
        ),
        (
            "clap-4.1.4.json",
            "usage",
            {
                "cargo",
                "crate(clap) = 4.1.4",
            },
        ),
        (
            "clap-4.1.4.json",
            "wrap_help",
            {
                "cargo",
                "crate(clap) = 4.1.4",
                "crate(clap/help) = 4.1.4",
                "(crate(terminal_size/default) >= 0.2.1 with crate(terminal_size/default) < 0.3.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "default",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "dox",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "crate(gstreamer/serde) = 0.19.7",
                "(crate(glib/dox) >= 0.16.2 with crate(glib/dox) < 0.17.0~)",
                "(crate(gstreamer-sys/dox) >= 0.19.0 with crate(gstreamer-sys/dox) < 0.20.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "serde",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "crate(gstreamer/serde_bytes) = 0.19.7",
                "(crate(num-rational/serde) >= 0.4.0 with crate(num-rational/serde) < 0.5.0~)",
                "(crate(serde/default) >= 1.0.0 with crate(serde/default) < 2.0.0~)",
                "(crate(serde/derive) >= 1.0.0 with crate(serde/derive) < 2.0.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "serde_bytes",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "(crate(serde_bytes/default) >= 0.11.0 with crate(serde_bytes/default) < 0.12.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "v1_16",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "(crate(gstreamer-sys/v1_16) >= 0.19.0 with crate(gstreamer-sys/v1_16) < 0.20.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "v1_18",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "crate(gstreamer/v1_16) = 0.19.7",
                "(crate(gstreamer-sys/v1_18) >= 0.19.0 with crate(gstreamer-sys/v1_18) < 0.20.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "v1_20",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "crate(gstreamer/v1_18) = 0.19.7",
                "(crate(gstreamer-sys/v1_20) >= 0.19.0 with crate(gstreamer-sys/v1_20) < 0.20.0~)",
            },
        ),
        (
            "gstreamer-0.19.7.json",
            "v1_22",
            {
                "cargo",
                "crate(gstreamer) = 0.19.7",
                "crate(gstreamer/v1_20) = 0.19.7",
                "(crate(gstreamer-sys/v1_22) >= 0.19.0 with crate(gstreamer-sys/v1_22) < 0.20.0~)",
            },
        ),
        (
            "human-panic-1.1.0.json",
            "default",
            {
                "cargo",
                "crate(human-panic) = 1.1.0",
                "crate(human-panic/color) = 1.1.0",
            },
        ),
        (
            "human-panic-1.1.0.json",
            "color",
            {
                "cargo",
                "crate(human-panic) = 1.1.0",
                "crate(concolor/default) = 0.0.11",
                "crate(concolor/auto) = 0.0.11",
                "(crate(termcolor/default) >= 1.0.4 with crate(termcolor/default) < 2.0.0~)",
            },
        ),
        (
            "human-panic-1.1.0.json",
            "nightly",
            {
                "cargo",
                "crate(human-panic) = 1.1.0",
            },
        ),
        (
            "libc-0.2.139.json",
            "default",
            {
                "cargo",
                "crate(libc) = 0.2.139",
                "crate(libc/std) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "align",
            {
                "cargo",
                "crate(libc) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "const-extern-fn",
            {
                "cargo",
                "crate(libc) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "extra_traits",
            {
                "cargo",
                "crate(libc) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "rustc-dep-of-std",
            {
                "cargo",
                "crate(libc) = 0.2.139",
                "crate(libc/align) = 0.2.139",
                "crate(libc/rustc-std-workspace-core) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "rustc-std-workspace-core",
            {
                "cargo",
                "crate(libc) = 0.2.139",
                "(crate(rustc-std-workspace-core/default) >= 1.0.0 with crate(rustc-std-workspace-core/default) < 2.0.0~)",
            },
        ),
        (
            "libc-0.2.139.json",
            "std",
            {
                "cargo",
                "crate(libc) = 0.2.139",
            },
        ),
        (
            "libc-0.2.139.json",
            "use_std",
            {
                "cargo",
                "crate(libc) = 0.2.139",
                "crate(libc/std) = 0.2.139",
            },
        ),
        (
            "predicates-2.1.5.json",
            "default",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "crate(predicates/diff) = 2.1.5",
                "crate(predicates/regex) = 2.1.5",
                "crate(predicates/float-cmp) = 2.1.5",
                "crate(predicates/normalize-line-endings) = 2.1.5",
            },
        ),
        (
            "predicates-2.1.5.json",
            "color",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "crate(concolor/default) = 0.0.11",
                "crate(concolor/std) = 0.0.11",
                "(crate(yansi/default) >= 0.5.1 with crate(yansi/default) < 0.6.0~)",
            },
        ),
        (
            "predicates-2.1.5.json",
            "color-auto",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "crate(predicates/color) = 2.1.5",
                "crate(concolor/auto) = 0.0.11",
                "crate(concolor/default) = 0.0.11",
            },
        ),
        (
            "predicates-2.1.5.json",
            "diff",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "(crate(difflib/default) >= 0.4.0 with crate(difflib/default) < 0.5.0~)",
            },
        ),
        (
            "predicates-2.1.5.json",
            "float-cmp",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "(crate(float-cmp/default) >= 0.9.0 with crate(float-cmp/default) < 0.10.0~)",
            },
        ),
        (
            "predicates-2.1.5.json",
            "normalize-line-endings",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "(crate(normalize-line-endings/default) >= 0.3.0 with crate(normalize-line-endings/default) < 0.4.0~)",
            },
        ),
        (
            "predicates-2.1.5.json",
            "regex",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
                "(crate(regex/default) >= 1.0.0 with crate(regex/default) < 2.0.0~)",
            },
        ),
        (
            "predicates-2.1.5.json",
            "unstable",
            {
                "cargo",
                "crate(predicates) = 2.1.5",
            },
        ),
        (
            "proc-macro2-1.0.50.json",
            "default",
            {
                "cargo",
                "crate(proc-macro2) = 1.0.50",
                "crate(proc-macro2/proc-macro) = 1.0.50",
            },
        ),
        (
            "proc-macro2-1.0.50.json",
            "nightly",
            {
                "cargo",
                "crate(proc-macro2) = 1.0.50",
            },
        ),
        (
            "proc-macro2-1.0.50.json",
            "proc-macro",
            {
                "cargo",
                "crate(proc-macro2) = 1.0.50",
            },
        ),
        (
            "proc-macro2-1.0.50.json",
            "span-locations",
            {
                "cargo",
                "crate(proc-macro2) = 1.0.50",
            },
        ),
        (
            "quote-1.0.23.json",
            "default",
            {
                "cargo",
                "crate(quote) = 1.0.23",
                "crate(quote/proc-macro) = 1.0.23",
            },
        ),
        (
            "quote-1.0.23.json",
            "proc-macro",
            {
                "cargo",
                "crate(quote) = 1.0.23",
                "(crate(proc-macro2/proc-macro) >= 1.0.40 with crate(proc-macro2/proc-macro) < 2.0.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "default",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "crate(rand/std) = 0.8.5",
                "crate(rand/std_rng) = 0.8.5",
            },
        ),
        (
            "rand-0.8.5.json",
            "alloc",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(rand_core/alloc) >= 0.6.0 with crate(rand_core/alloc) < 0.7.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "getrandom",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(rand_core/getrandom) >= 0.6.0 with crate(rand_core/getrandom) < 0.7.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "libc",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(libc) >= 0.2.22 with crate(libc) < 0.3.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "log",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(log/default) >= 0.4.4 with crate(log/default) < 0.5.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "min_const_gen",
            {
                "cargo",
                "crate(rand) = 0.8.5",
            },
        ),
        (
            "rand-0.8.5.json",
            "nightly",
            {
                "cargo",
                "crate(rand) = 0.8.5",
            },
        ),
        (
            "rand-0.8.5.json",
            "packed_simd",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(packed_simd_2/default) >= 0.3.7 with crate(packed_simd_2/default) < 0.4.0~)",
                "(crate(packed_simd_2/into_bits) >= 0.3.7 with crate(packed_simd_2/into_bits) < 0.4.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "rand_chacha",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(rand_chacha) >= 0.3.0 with crate(rand_chacha) < 0.4.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "serde",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "(crate(serde/default) >= 1.0.103 with crate(serde/default) < 2.0.0~)",
                "(crate(serde/derive) >= 1.0.103 with crate(serde/derive) < 2.0.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "serde1",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "crate(rand/serde) = 0.8.5",
                "(crate(rand_core/serde1) >= 0.6.0 with crate(rand_core/serde1) < 0.7.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "simd_support",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "crate(rand/packed_simd) = 0.8.5",
            },
        ),
        (
            "rand-0.8.5.json",
            "small_rng",
            {
                "cargo",
                "crate(rand) = 0.8.5",
            },
        ),
        (
            "rand-0.8.5.json",
            "std",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "crate(rand/alloc) = 0.8.5",
                "crate(rand/getrandom) = 0.8.5",
                "crate(rand/libc) = 0.8.5",
                "(crate(rand_core/std) >= 0.6.0 with crate(rand_core/std) < 0.7.0~)",
                "(crate(rand_chacha) >= 0.3.0 with crate(rand_chacha) < 0.4.0~)",
                "(crate(rand_chacha/std) >= 0.3.0 with crate(rand_chacha/std) < 0.4.0~)",
            },
        ),
        (
            "rand-0.8.5.json",
            "std_rng",
            {
                "cargo",
                "crate(rand) = 0.8.5",
                "crate(rand/rand_chacha) = 0.8.5",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "default",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "alloc",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "getrandom",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
                "(crate(getrandom/default) >= 0.2.0 with crate(getrandom/default) < 0.3.0~)",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "serde",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
                "(crate(serde/default) >= 1.0.0 with crate(serde/default) < 2.0.0~)",
                "(crate(serde/derive) >= 1.0.0 with crate(serde/derive) < 2.0.0~)",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "serde1",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
                "crate(rand_core/serde) = 0.6.4",
            },
        ),
        (
            "rand_core-0.6.4.json",
            "std",
            {
                "cargo",
                "crate(rand_core) = 0.6.4",
                "crate(rand_core/alloc) = 0.6.4",
                "crate(rand_core/getrandom) = 0.6.4",
                "(crate(getrandom/default) >= 0.2.0 with crate(getrandom/default) < 0.3.0~)",
                "(crate(getrandom/std) >= 0.2.0 with crate(getrandom/std) < 0.3.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "default",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "arbitrary",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(arbitrary) >= 1.0.0 with crate(arbitrary) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "borsh",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(borsh) >= 0.9.0 with crate(borsh) < 0.10.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "bytecheck",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(bytecheck) >= 0.6.0 with crate(bytecheck) < 0.7.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "byteorder",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(byteorder) >= 1.0.0 with crate(byteorder) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "bytes",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(bytes) >= 1.0.0 with crate(bytes) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "c-repr",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel-mysql",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/db-diesel1-mysql) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/db-diesel1-postgres) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel1-mysql",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
                "(crate(diesel) >= 1.0.0 with crate(diesel) < 2.0.0~)",
                "(crate(diesel/mysql) >= 1.0.0 with crate(diesel/mysql) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel1-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
                "(crate(diesel) >= 1.0.0 with crate(diesel) < 2.0.0~)",
                "(crate(diesel/postgres) >= 1.0.0 with crate(diesel/postgres) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel2-mysql",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
                "(crate(diesel) >= 2.0.0 with crate(diesel) < 3.0.0~)",
                "(crate(diesel/mysql) >= 2.0.0 with crate(diesel/mysql) < 3.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-diesel2-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
                "(crate(diesel) >= 2.0.0 with crate(diesel) < 3.0.0~)",
                "(crate(diesel/postgres) >= 2.0.0 with crate(diesel/postgres) < 3.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/byteorder) = 1.28.0",
                "crate(rust_decimal/bytes) = 1.28.0",
                "crate(rust_decimal/postgres) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "db-tokio-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/byteorder) = 1.28.0",
                "crate(rust_decimal/bytes) = 1.28.0",
                "crate(rust_decimal/postgres) = 1.28.0",
                "crate(rust_decimal/std) = 1.28.0",
                "crate(rust_decimal/tokio-postgres) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "diesel1",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(diesel) >= 1.0.0 with crate(diesel) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "diesel2",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(diesel) >= 2.0.0 with crate(diesel) < 3.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "legacy-ops",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "maths",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "maths-nopanic",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/maths) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(postgres) >= 0.19.0 with crate(postgres) < 0.20.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rand",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(rand) >= 0.8.0 with crate(rand) < 0.9.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rkyv",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(rkyv) >= 0.7.0 with crate(rkyv) < 0.8.0~)",
                "(crate(rkyv/size_32) >= 0.7.0 with crate(rkyv/size_32) < 0.8.0~)",
                "(crate(rkyv/std) >= 0.7.0 with crate(rkyv/std) < 0.8.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rkyv-safe",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/bytecheck) = 1.28.0",
                "(crate(rkyv) >= 0.7.0 with crate(rkyv) < 0.8.0~)",
                "(crate(rkyv/size_32) >= 0.7.0 with crate(rkyv/size_32) < 0.8.0~)",
                "(crate(rkyv/std) >= 0.7.0 with crate(rkyv/std) < 0.8.0~)",
                "(crate(rkyv/validation) >= 0.7.0 with crate(rkyv/validation) < 0.8.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rocket",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(rocket) >= 0.5.0~rc.1 with crate(rocket) < 0.6.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rocket-traits",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/rocket) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "rust-fuzz",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/arbitrary) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-arbitrary-precision",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde-with-arbitrary-precision) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-bincode",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde-str) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-float",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde-with-float) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-str",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde-with-str) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-with-arbitrary-precision",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde) = 1.28.0",
                "(crate(serde_json) >= 1.0.0 with crate(serde_json) < 2.0.0~)",
                "(crate(serde_json/arbitrary_precision) >= 1.0.0 with crate(serde_json/arbitrary_precision) < 2.0.0~)",
                "(crate(serde_json/std) >= 1.0.0 with crate(serde_json/std) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-with-float",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde-with-str",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/serde) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "serde_json",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(serde_json) >= 1.0.0 with crate(serde_json) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "std",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(arrayvec/std) >= 0.7.0 with crate(arrayvec/std) < 0.8.0~)",
                "(crate(borsh) >= 0.9.0 with crate(borsh) < 0.10.0~)",
                "(crate(borsh/std) >= 0.9.0 with crate(borsh/std) < 0.10.0~)",
                "(crate(bytecheck) >= 0.6.0 with crate(bytecheck) < 0.7.0~)",
                "(crate(bytecheck/std) >= 0.6.0 with crate(bytecheck/std) < 0.7.0~)",
                "(crate(byteorder) >= 1.0.0 with crate(byteorder) < 2.0.0~)",
                "(crate(byteorder/std) >= 1.0.0 with crate(byteorder/std) < 2.0.0~)",
                "(crate(bytes) >= 1.0.0 with crate(bytes) < 2.0.0~)",
                "(crate(bytes/std) >= 1.0.0 with crate(bytes/std) < 2.0.0~)",
                "(crate(rand) >= 0.8.0 with crate(rand) < 0.9.0~)",
                "(crate(rand/std) >= 0.8.0 with crate(rand/std) < 0.9.0~)",
                "(crate(rkyv) >= 0.7.0 with crate(rkyv) < 0.8.0~)",
                "(crate(rkyv/size_32) >= 0.7.0 with crate(rkyv/size_32) < 0.8.0~)",
                "(crate(rkyv/std) >= 0.7.0 with crate(rkyv/std) < 0.8.0~)",
                "(crate(serde) >= 1.0.0 with crate(serde) < 2.0.0~)",
                "(crate(serde/std) >= 1.0.0 with crate(serde/std) < 2.0.0~)",
                "(crate(serde_json) >= 1.0.0 with crate(serde_json) < 2.0.0~)",
                "(crate(serde_json/std) >= 1.0.0 with crate(serde_json/std) < 2.0.0~)",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "tokio-pg",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "crate(rust_decimal/db-tokio-postgres) = 1.28.0",
            },
        ),
        (
            "rust_decimal-1.28.0.json",
            "tokio-postgres",
            {
                "cargo",
                "crate(rust_decimal) = 1.28.0",
                "(crate(tokio-postgres) >= 0.7.0 with crate(tokio-postgres) < 0.8.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "default",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/std) = 0.36.8",
                "crate(rustix/use-libc-auxv) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "all-apis",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/fs) = 0.36.8",
                "crate(rustix/io_uring) = 0.36.8",
                "crate(rustix/mm) = 0.36.8",
                "crate(rustix/net) = 0.36.8",
                "crate(rustix/param) = 0.36.8",
                "crate(rustix/process) = 0.36.8",
                "crate(rustix/procfs) = 0.36.8",
                "crate(rustix/rand) = 0.36.8",
                "crate(rustix/runtime) = 0.36.8",
                "crate(rustix/termios) = 0.36.8",
                "crate(rustix/thread) = 0.36.8",
                "crate(rustix/time) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "all-impls",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/fs-err) = 0.36.8",
                "crate(rustix/os_pipe) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "alloc",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(rustc-std-workspace-alloc/default) >= 1.0.0 with crate(rustc-std-workspace-alloc/default) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "cc",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(cc/default) >= 1.0.68 with crate(cc/default) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "compiler_builtins",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(compiler_builtins/default) >= 0.1.49 with crate(compiler_builtins/default) < 0.2.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "core",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(rustc-std-workspace-core/default) >= 1.0.0 with crate(rustc-std-workspace-core/default) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "fs",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "fs-err",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(io-lifetimes) >= 1.0.0 with crate(io-lifetimes) < 2.0.0~)",
                "(crate(io-lifetimes/close) >= 1.0.0 with crate(io-lifetimes/close) < 2.0.0~)",
                "(crate(io-lifetimes/fs-err) >= 1.0.0 with crate(io-lifetimes/fs-err) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "io-lifetimes",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(io-lifetimes) >= 1.0.0 with crate(io-lifetimes) < 2.0.0~)",
                "(crate(io-lifetimes/close) >= 1.0.0 with crate(io-lifetimes/close) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "io_uring",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/fs) = 0.36.8",
                "crate(rustix/net) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "itoa",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(itoa) >= 1.0.1 with crate(itoa) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "libc",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(libc/default) >= 0.2.133 with crate(libc/default) < 0.3.0~)",
                "(crate(libc/extra_traits) >= 0.2.133 with crate(libc/extra_traits) < 0.3.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "libc_errno",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(errno) >= 0.2.8 with crate(errno) < 0.3.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "mm",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "net",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "once_cell",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(once_cell/default) >= 1.5.2 with crate(once_cell/default) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "os_pipe",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "(crate(io-lifetimes) >= 1.0.0 with crate(io-lifetimes) < 2.0.0~)",
                "(crate(io-lifetimes/close) >= 1.0.0 with crate(io-lifetimes/close) < 2.0.0~)",
                "(crate(io-lifetimes/os_pipe) >= 1.0.0 with crate(io-lifetimes/os_pipe) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "param",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/fs) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "process",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "procfs",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/once_cell) = 0.36.8",
                "crate(rustix/itoa) = 0.36.8",
                "crate(rustix/fs) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "rand",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "runtime",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "rustc-dep-of-std",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/core) = 0.36.8",
                "crate(rustix/alloc) = 0.36.8",
                "crate(rustix/compiler_builtins) = 0.36.8",
                "(crate(linux-raw-sys/rustc-dep-of-std) >= 0.1.2 with crate(linux-raw-sys/rustc-dep-of-std) < 0.2.0~)",
                "(crate(bitflags/rustc-dep-of-std) >= 1.2.1 with crate(bitflags/rustc-dep-of-std) < 2.0.0~)",
            },
        ),
        (
            "rustix-0.36.8.json",
            "std",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/io-lifetimes) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "termios",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "thread",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "time",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "use-libc",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/libc) = 0.36.8",
                "crate(rustix/libc_errno) = 0.36.8",
            },
        ),
        (
            "rustix-0.36.8.json",
            "use-libc-auxv",
            {
                "cargo",
                "crate(rustix) = 0.36.8",
                "crate(rustix/libc) = 0.36.8",
            },
        ),
        (
            "serde-1.0.152.json",
            "default",
            {
                "cargo",
                "crate(serde) = 1.0.152",
                "crate(serde/std) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "alloc",
            {
                "cargo",
                "crate(serde) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "derive",
            {
                "cargo",
                "crate(serde) = 1.0.152",
                "crate(serde/serde_derive) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "rc",
            {
                "cargo",
                "crate(serde) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "serde_derive",
            {
                "cargo",
                "crate(serde) = 1.0.152",
                "crate(serde_derive/default) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "std",
            {
                "cargo",
                "crate(serde) = 1.0.152",
            },
        ),
        (
            "serde-1.0.152.json",
            "unstable",
            {
                "cargo",
                "crate(serde) = 1.0.152",
            },
        ),
        (
            "serde_derive-1.0.152.json",
            "default",
            {
                "cargo",
                "crate(serde_derive) = 1.0.152",
            },
        ),
        (
            "serde_derive-1.0.152.json",
            "deserialize_in_place",
            {
                "cargo",
                "crate(serde_derive) = 1.0.152",
            },
        ),
        (
            "sha1collisiondetection-0.3.1.json",
            "default",
            {
                "cargo",
                "crate(sha1collisiondetection) = 0.3.1",
                "crate(sha1collisiondetection/std) = 0.3.1",
                "crate(sha1collisiondetection/digest-trait) = 0.3.1",
            },
        ),
        (
            "sha1collisiondetection-0.3.1.json",
            "digest-trait",
            {
                "cargo",
                "crate(sha1collisiondetection) = 0.3.1",
                "crate(sha1collisiondetection/digest) = 0.3.1",
            },
        ),
        (
            "sha1collisiondetection-0.3.1.json",
            "oid",
            {
                "cargo",
                "crate(sha1collisiondetection) = 0.3.1",
                "crate(sha1collisiondetection/const-oid) = 0.3.1",
            },
        ),
        (
            "sha1collisiondetection-0.3.1.json",
            "std",
            {
                "cargo",
                "crate(sha1collisiondetection) = 0.3.1",
                "(crate(digest/default) >= 0.10.0 with crate(digest/default) < 0.11.0~)",
                "(crate(digest/std) >= 0.10.0 with crate(digest/std) < 0.11.0~)",
            },
        ),
        (
            "syn-1.0.107.json",
            "default",
            {
                "cargo",
                "crate(syn) = 1.0.107",
                "crate(syn/derive) = 1.0.107",
                "crate(syn/parsing) = 1.0.107",
                "crate(syn/printing) = 1.0.107",
                "crate(syn/clone-impls) = 1.0.107",
                "crate(syn/proc-macro) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "clone-impls",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "derive",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "extra-traits",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "fold",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "full",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "parsing",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "printing",
            {
                "cargo",
                "crate(syn) = 1.0.107",
                "crate(syn/quote) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "proc-macro",
            {
                "cargo",
                "crate(syn) = 1.0.107",
                "(crate(proc-macro2/proc-macro) >= 1.0.46 with crate(proc-macro2/proc-macro) < 2.0.0~)",
                "(crate(quote) >= 1.0.0 with crate(quote) < 2.0.0~)",
                "(crate(quote/proc-macro) >= 1.0.0 with crate(quote/proc-macro) < 2.0.0~)",
            },
        ),
        (
            "syn-1.0.107.json",
            "quote",
            {
                "cargo",
                "crate(syn) = 1.0.107",
                "(crate(quote) >= 1.0.0 with crate(quote) < 2.0.0~)",
            },
        ),
        (
            "syn-1.0.107.json",
            "test",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "visit",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "syn-1.0.107.json",
            "visit-mut",
            {
                "cargo",
                "crate(syn) = 1.0.107",
            },
        ),
        (
            "time-0.3.17.json",
            "default",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/std) = 0.3.17",
            },
        ),
        (
            "time-0.3.17.json",
            "default",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/std) = 0.3.17",
            },
        ),
        (
            "time-0.3.17.json",
            "alloc",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "(crate(serde) >= 1.0.126 with crate(serde) < 2.0.0~)",
                "(crate(serde/alloc) >= 1.0.126 with crate(serde/alloc) < 2.0.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            "formatting",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/std) = 0.3.17",
                "crate(time-macros/default) = 0.2.6",
                "crate(time-macros/formatting) = 0.2.6",
                "(crate(itoa/default) >= 1.0.1 with crate(itoa/default) < 2.0.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            "large-dates",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time-macros/default) = 0.2.6",
                "crate(time-macros/large-dates) = 0.2.6",
            },
        ),
        (
            "time-0.3.17.json",
            "local-offset",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/std) = 0.3.17",
                "(crate(libc/default) >= 0.2.98 with crate(libc/default) < 0.3.0~)",
                "(crate(num_threads/default) >= 0.1.2 with crate(num_threads/default) < 0.2.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            "macros",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time-macros/default) = 0.2.6",
            },
        ),
        (
            "time-0.3.17.json",
            "parsing",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time-macros/default) = 0.2.6",
                "crate(time-macros/parsing) = 0.2.6",
            },
        ),
        (
            "time-0.3.17.json",
            "rand",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "(crate(rand) >= 0.8.4 with crate(rand) < 0.9.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            "serde",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time-macros/default) = 0.2.6",
                "crate(time-macros/serde) = 0.2.6",
                "(crate(serde) >= 1.0.126 with crate(serde) < 2.0.0~)",
            },
        ),
        (
            "time-0.3.17.json",
            "serde-human-readable",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/serde) = 0.3.17",
                "crate(time/formatting) = 0.3.17",
                "crate(time/parsing) = 0.3.17",
            },
        ),
        (
            "time-0.3.17.json",
            "serde-well-known",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/serde) = 0.3.17",
                "crate(time/formatting) = 0.3.17",
                "crate(time/parsing) = 0.3.17",
            },
        ),
        (
            "time-0.3.17.json",
            "std",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "crate(time/alloc) = 0.3.17",
            },
        ),
        (
            "time-0.3.17.json",
            "wasm-bindgen",
            {
                "cargo",
                "crate(time) = 0.3.17",
                "(crate(js-sys/default) >= 0.3.58 with crate(js-sys/default) < 0.4.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "default",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "bytes",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(bytes/default) >= 1.0.0 with crate(bytes/default) < 2.0.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "fs",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "full",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/fs) = 1.25.0",
                "crate(tokio/io-util) = 1.25.0",
                "crate(tokio/io-std) = 1.25.0",
                "crate(tokio/macros) = 1.25.0",
                "crate(tokio/net) = 1.25.0",
                "crate(tokio/parking_lot) = 1.25.0",
                "crate(tokio/process) = 1.25.0",
                "crate(tokio/rt) = 1.25.0",
                "crate(tokio/rt-multi-thread) = 1.25.0",
                "crate(tokio/signal) = 1.25.0",
                "crate(tokio/sync) = 1.25.0",
                "crate(tokio/time) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "io-std",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "io-util",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/memchr) = 1.25.0",
                "crate(tokio/bytes) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "libc",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(libc/default) >= 0.2.42 with crate(libc/default) < 0.3.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "macros",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/tokio-macros) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "memchr",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(memchr/default) >= 2.2.0 with crate(memchr/default) < 3.0.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "mio",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(mio/default) >= 0.8.4 with crate(mio/default) < 0.9.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "net",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/libc) = 1.25.0",
                "crate(tokio/socket2) = 1.25.0",
                "(crate(mio/default) >= 0.8.4 with crate(mio/default) < 0.9.0~)",
                "(crate(mio/os-poll) >= 0.8.4 with crate(mio/os-poll) < 0.9.0~)",
                "(crate(mio/os-ext) >= 0.8.4 with crate(mio/os-ext) < 0.9.0~)",
                "(crate(mio/net) >= 0.8.4 with crate(mio/net) < 0.9.0~)",
                "(crate(windows-sys/default) >= 0.42.0 with crate(windows-sys/default) < 0.43.0~)",
                "(crate(windows-sys/Win32_Foundation) >= 0.42.0 with crate(windows-sys/Win32_Foundation) < 0.43.0~)",
                "(crate(windows-sys/Win32_Security) >= 0.42.0 with crate(windows-sys/Win32_Security) < 0.43.0~)",
                "(crate(windows-sys/Win32_Storage_FileSystem) >= 0.42.0 with crate(windows-sys/Win32_Storage_FileSystem) < 0.43.0~)",
                "(crate(windows-sys/Win32_System_Pipes) >= 0.42.0 with crate(windows-sys/Win32_System_Pipes) < 0.43.0~)",
                "(crate(windows-sys/Win32_System_SystemServices) >= 0.42.0 with crate(windows-sys/Win32_System_SystemServices) < 0.43.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "num_cpus",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(num_cpus/default) >= 1.8.0 with crate(num_cpus/default) < 2.0.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "parking_lot",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(parking_lot/default) >= 0.12.0 with crate(parking_lot/default) < 0.13.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "process",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/bytes) = 1.25.0",
                "crate(tokio/libc) = 1.25.0",
                "crate(tokio/signal-hook-registry) = 1.25.0",
                "(crate(mio/default) >= 0.8.4 with crate(mio/default) < 0.9.0~)",
                "(crate(mio/os-poll) >= 0.8.4 with crate(mio/os-poll) < 0.9.0~)",
                "(crate(mio/os-ext) >= 0.8.4 with crate(mio/os-ext) < 0.9.0~)",
                "(crate(mio/net) >= 0.8.4 with crate(mio/net) < 0.9.0~)",
                "(crate(windows-sys/default) >= 0.42.0 with crate(windows-sys/default) < 0.43.0~)",
                "(crate(windows-sys/Win32_Foundation) >= 0.42.0 with crate(windows-sys/Win32_Foundation) < 0.43.0~)",
                "(crate(windows-sys/Win32_System_Threading) >= 0.42.0 with crate(windows-sys/Win32_System_Threading) < 0.43.0~)",
                "(crate(windows-sys/Win32_System_WindowsProgramming) >= 0.42.0 with crate(windows-sys/Win32_System_WindowsProgramming) < 0.43.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "rt",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "rt-multi-thread",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/rt) = 1.25.0",
                "crate(tokio/num_cpus) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "signal",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/libc) = 1.25.0",
                "crate(tokio/signal-hook-registry) = 1.25.0",
                "(crate(mio/default) >= 0.8.4 with crate(mio/default) < 0.9.0~)",
                "(crate(mio/os-poll) >= 0.8.4 with crate(mio/os-poll) < 0.9.0~)",
                "(crate(mio/os-ext) >= 0.8.4 with crate(mio/os-ext) < 0.9.0~)",
                "(crate(mio/net) >= 0.8.4 with crate(mio/net) < 0.9.0~)",
                "(crate(windows-sys/default) >= 0.42.0 with crate(windows-sys/default) < 0.43.0~)",
                "(crate(windows-sys/Win32_Foundation) >= 0.42.0 with crate(windows-sys/Win32_Foundation) < 0.43.0~)",
                "(crate(windows-sys/Win32_System_Console) >= 0.42.0 with crate(windows-sys/Win32_System_Console) < 0.43.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "signal-hook-registry",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(signal-hook-registry/default) >= 1.1.1 with crate(signal-hook-registry/default) < 2.0.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "socket2",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(socket2/default) >= 0.4.4 with crate(socket2/default) < 0.5.0~)",
                "(crate(socket2/all) >= 0.4.4 with crate(socket2/all) < 0.5.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "stats",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "sync",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "test-util",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "crate(tokio/rt) = 1.25.0",
                "crate(tokio/sync) = 1.25.0",
                "crate(tokio/time) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "time",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
            },
        ),
        (
            "tokio-1.25.0.json",
            "tokio-macros",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(tokio-macros/default) >= 1.7.0 with crate(tokio-macros/default) < 2.0.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "tracing",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(tracing) >= 0.1.25 with crate(tracing) < 0.2.0~)",
                "(crate(tracing/std) >= 0.1.25 with crate(tracing/std) < 0.2.0~)",
            },
        ),
        (
            "tokio-1.25.0.json",
            "windows-sys",
            {
                "cargo",
                "crate(tokio) = 1.25.0",
                "(crate(windows-sys/default) >= 0.42.0 with crate(windows-sys/default) < 0.43.0~)",
            },
        ),
        (
            "unicode-xid-0.2.4.json",
            "default",
            {
                "cargo",
                "crate(unicode-xid) = 0.2.4",
            },
        ),
        (
            "unicode-xid-0.2.4.json",
            "bench",
            {
                "cargo",
                "crate(unicode-xid) = 0.2.4",
            },
        ),
        (
            "unicode-xid-0.2.4.json",
            "no_std",
            {
                "cargo",
                "crate(unicode-xid) = 0.2.4",
            },
        ),
        (
            "zbus-3.8.0.json",
            "default",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "crate(zbus/async-io) = 3.8.0",
            },
        ),
        (
            "zbus-3.8.0.json",
            "async-executor",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(async-executor/default) >= 1.5.0 with crate(async-executor/default) < 2.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "async-io",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "crate(zbus/async-executor) = 3.8.0",
                "crate(zbus/async-task) = 3.8.0",
                "crate(zbus/async-lock) = 3.8.0",
                "(crate(async-io/default) >= 1.12.0 with crate(async-io/default) < 2.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "async-lock",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(async-lock/default) >= 2.6.0 with crate(async-lock/default) < 3.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "async-task",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(async-task/default) >= 4.3.0 with crate(async-task/default) < 5.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "chrono",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(zvariant/chrono) >= 3.10.0 with crate(zvariant/chrono) < 4.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "gvariant",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(zvariant/gvariant) >= 3.10.0 with crate(zvariant/gvariant) < 4.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "lazy_static",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(lazy_static/default) >= 1.4.0 with crate(lazy_static/default) < 2.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "quick-xml",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(quick-xml/default) >= 0.27.1 with crate(quick-xml/default) < 0.28.0~)",
                "(crate(quick-xml/serialize) >= 0.27.1 with crate(quick-xml/serialize) < 0.28.0~)",
                "(crate(quick-xml/overlapped-lists) >= 0.27.1 with crate(quick-xml/overlapped-lists) < 0.28.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "serde-xml-rs",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(serde-xml-rs/default) >= 0.4.1 with crate(serde-xml-rs/default) < 0.5.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "time",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(zvariant/time) >= 3.10.0 with crate(zvariant/time) < 4.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "tokio",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "crate(zbus/lazy_static) = 3.8.0",
                "(crate(tokio/default) >= 1.21.2 with crate(tokio/default) < 2.0.0~)",
                "(crate(tokio/rt) >= 1.21.2 with crate(tokio/rt) < 2.0.0~)",
                "(crate(tokio/net) >= 1.21.2 with crate(tokio/net) < 2.0.0~)",
                "(crate(tokio/time) >= 1.21.2 with crate(tokio/time) < 2.0.0~)",
                "(crate(tokio/fs) >= 1.21.2 with crate(tokio/fs) < 2.0.0~)",
                "(crate(tokio/io-util) >= 1.21.2 with crate(tokio/io-util) < 2.0.0~)",
                "(crate(tokio/sync) >= 1.21.2 with crate(tokio/sync) < 2.0.0~)",
                "(crate(tokio/tracing) >= 1.21.2 with crate(tokio/tracing) < 2.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "tokio-vsock",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "crate(zbus/tokio) = 3.8.0",
                "(crate(tokio-vsock/default) >= 0.3.3 with crate(tokio-vsock/default) < 0.4.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "url",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(zvariant/url) >= 3.10.0 with crate(zvariant/url) < 4.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "uuid",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(zvariant/uuid) >= 3.10.0 with crate(zvariant/uuid) < 4.0.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "vsock",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "(crate(async-io/default) >= 1.12.0 with crate(async-io/default) < 2.0.0~)",
                "(crate(vsock/default) >= 0.3.0 with crate(vsock/default) < 0.4.0~)",
            },
        ),
        (
            "zbus-3.8.0.json",
            "windows-gdbus",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
            },
        ),
        (
            "zbus-3.8.0.json",
            "xml",
            {
                "cargo",
                "crate(zbus) = 3.8.0",
                "crate(zbus/serde-xml-rs) = 3.8.0",
            },
        ),
    ],
    ids=short_repr,
)
def test_requires_feature(filename: str, feature: str, expected: set[str]):
    metadata = load_metadata_from_resource(filename)
    assert _requires_feature(metadata.packages[0], feature) == expected
