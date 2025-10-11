from cargo2rpm.metadata import FeatureFlags
from cargo2rpm.utils import load_metadata_from_resource, short_repr

import pytest


@pytest.mark.parametrize(
    "filename,flags,expected_enabled,expected_optional,expected_other,expected_conditional",
    [
        # default features
        ("ahash-0.8.3.json", FeatureFlags(), {"default", "std", "runtime-rng", "getrandom"}, {"getrandom"}, dict(), dict()),
        # all features
        (
            "ahash-0.8.3.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "std",
                "runtime-rng",
                "getrandom",
                "atomic-polyfill",
                "compile-time-rng",
                "const-random",
                "no-rng",
                "serde",
            },
            {
                "atomic-polyfill",
                "const-random",
                "getrandom",
                "serde",
            },
            {"once_cell": {"atomic-polyfill"}},
            dict(),
        ),
        # no default features
        ("ahash-0.8.3.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + compile-time-rng
        (
            "ahash-0.8.3.json",
            FeatureFlags(features=["compile-time-rng"]),
            {"default", "std", "runtime-rng", "getrandom", "compile-time-rng", "const-random"},
            {"const-random", "getrandom"},
            dict(),
            dict(),
        ),
        # no default features + compile-time-rng
        (
            "ahash-0.8.3.json",
            FeatureFlags(no_default_features=True, features=["compile-time-rng"]),
            {"compile-time-rng", "const-random"},
            {"const-random"},
            dict(),
            dict(),
        ),
        # default features
        ("aho-corasick-1.0.2.json", FeatureFlags(), {"default", "std", "perf-literal"}, {"memchr"}, dict(), {"memchr": {"std"}}),
        # all features
        (
            "aho-corasick-1.0.2.json",
            FeatureFlags(all_features=True),
            {"default", "logging", "perf-literal", "std"},
            {"memchr", "log"},
            dict(),
            {"memchr": {"std"}},
        ),
        # no default features
        ("aho-corasick-1.0.2.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + logging
        (
            "aho-corasick-1.0.2.json",
            FeatureFlags(features=["logging"]),
            {"default", "std", "perf-literal", "logging"},
            {"memchr", "log"},
            dict(),
            {"memchr": {"std"}},
        ),
        # no default features + logging
        ("aho-corasick-1.0.2.json", FeatureFlags(no_default_features=True, features=["logging"]), {"logging"}, {"log"}, dict(), dict()),
        # default features
        ("assert_cmd-2.0.8.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        (
            "assert_cmd-2.0.8.json",
            FeatureFlags(all_features=True),
            {"color", "color-auto"},
            {"concolor", "yansi"},
            {"predicates": {"color"}},
            {"concolor": {"std", "auto"}},
        ),
        # no default features
        ("assert_cmd-2.0.8.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + color
        (
            "assert_cmd-2.0.8.json",
            FeatureFlags(features=["color"]),
            {"color"},
            {"concolor", "yansi"},
            {"predicates": {"color"}},
            {"concolor": {"std"}},
        ),
        # no default features + color
        (
            "assert_cmd-2.0.8.json",
            FeatureFlags(no_default_features=True, features=["color"]),
            {"color"},
            {"concolor", "yansi"},
            {"predicates": {"color"}},
            {"concolor": {"std"}},
        ),
        # default features
        ("assert_fs-1.0.10.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        (
            "assert_fs-1.0.10.json",
            FeatureFlags(all_features=True),
            {"color", "color-auto"},
            {"concolor", "yansi"},
            {"predicates": {"color"}},
            {"concolor": {"auto"}},
        ),
        # no default features
        ("assert_fs-1.0.10.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + color
        ("assert_fs-1.0.10.json", FeatureFlags(features=["color"]), {"color"}, {"concolor", "yansi"}, {"predicates": {"color"}}, dict()),
        # no default features + color
        (
            "assert_fs-1.0.10.json",
            FeatureFlags(no_default_features=True, features=["color"]),
            {"color"},
            {"concolor", "yansi"},
            {"predicates": {"color"}},
            dict(),
        ),
        # default features
        ("autocfg-1.1.0.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        ("autocfg-1.1.0.json", FeatureFlags(all_features=True), set(), set(), dict(), dict()),
        # no default features
        ("autocfg-1.1.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "bstr-1.2.0.json",
            FeatureFlags(),
            {"default", "std", "unicode", "alloc"},
            {"once_cell", "regex-automata"},
            {"memchr": {"std"}},
            {"serde": {"alloc", "std"}},
        ),
        # all features
        (
            "bstr-1.2.0.json",
            FeatureFlags(all_features=True),
            {"default", "alloc", "serde", "std", "unicode"},
            {"serde", "once_cell", "regex-automata"},
            {"memchr": {"std"}},
            {"serde": {"alloc", "std"}},
        ),
        # no default features
        ("bstr-1.2.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + serde
        (
            "bstr-1.2.0.json",
            FeatureFlags(features=["serde"]),
            {"default", "std", "unicode", "alloc", "serde"},
            {"once_cell", "regex-automata", "serde"},
            {"memchr": {"std"}},
            {"serde": {"alloc", "std"}},
        ),
        # no default features + serde
        (
            "bstr-1.2.0.json",
            FeatureFlags(no_default_features=True, features=["serde"]),
            {"serde"},
            {"serde"},
            dict(),
            dict(),
        ),
        # default features
        ("cfg-if-1.0.0.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        (
            "cfg-if-1.0.0.json",
            FeatureFlags(all_features=True),
            {"compiler_builtins", "core", "rustc-dep-of-std"},
            {"compiler_builtins", "core"},
            dict(),
            dict(),
        ),
        # no default features
        ("cfg-if-1.0.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "clap-4.1.4.json",
            FeatureFlags(),
            {"default", "std", "color", "help", "usage", "error-context", "suggestions"},
            {"is-terminal", "termcolor", "strsim"},
            dict(),
            dict(),
        ),
        # all features
        (
            "clap-4.1.4.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "cargo",
                "color",
                "debug",
                "deprecated",
                "derive",
                "env",
                "error-context",
                "help",
                "std",
                "string",
                "suggestions",
                "unicode",
                "unstable-doc",
                "unstable-grouped",
                "unstable-replace",
                "unstable-v5",
                "usage",
                "wrap_help",
            },
            {"once_cell", "is-terminal", "termcolor", "backtrace", "clap_derive", "strsim", "unicode-width", "unicase", "terminal_size"},
            dict(),
            {"clap_derive": {"debug", "deprecated", "unstable-v5"}},
        ),
        # no default features
        ("clap-4.1.4.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + wrap_help
        (
            "clap-4.1.4.json",
            FeatureFlags(features=["wrap_help"]),
            {"default", "std", "color", "help", "usage", "error-context", "suggestions", "wrap_help"},
            {"is-terminal", "termcolor", "strsim", "terminal_size"},
            dict(),
            dict(),
        ),
        # no default features + wrap_help
        (
            "clap-4.1.4.json",
            FeatureFlags(no_default_features=True, features=["wrap_help"]),
            {"wrap_help", "help"},
            {"terminal_size"},
            dict(),
            dict(),
        ),
        # default features
        (
            "gstreamer-0.19.7.json",
            FeatureFlags(),
            {"default"},
            set(),
            dict(),
            dict(),
        ),
        # all features
        (
            "gstreamer-0.19.7.json",
            FeatureFlags(all_features=True),
            {"default", "dox", "serde", "serde_bytes", "v1_16", "v1_18", "v1_20", "v1_22"},
            {"serde", "serde_bytes"},
            {"ffi": {"dox", "v1_16", "v1_18", "v1_20", "v1_22"}, "glib": {"dox"}, "num-rational": {"serde"}},
            dict(),
        ),
        # no default features
        ("gstreamer-0.19.7.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + serde
        (
            "gstreamer-0.19.7.json",
            FeatureFlags(features=["serde"]),
            {"default", "serde", "serde_bytes"},
            {"serde", "serde_bytes"},
            {"num-rational": {"serde"}},
            dict(),
        ),
        # no default features + serde
        (
            "gstreamer-0.19.7.json",
            FeatureFlags(no_default_features=True, features=["serde"]),
            {"serde", "serde_bytes"},
            {"serde", "serde_bytes"},
            {"num-rational": {"serde"}},
            dict(),
        ),
        # default features
        (
            "human-panic-1.1.0.json",
            FeatureFlags(),
            {"default", "color"},
            {"concolor", "termcolor"},
            dict(),
            dict(),
        ),
        # all features
        (
            "human-panic-1.1.0.json",
            FeatureFlags(all_features=True),
            {"default", "color", "nightly"},
            {"concolor", "termcolor"},
            dict(),
            dict(),
        ),
        # no default features
        ("human-panic-1.1.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + nightly
        (
            "human-panic-1.1.0.json",
            FeatureFlags(features=["nightly"]),
            {"default", "color", "nightly"},
            {"concolor", "termcolor"},
            dict(),
            dict(),
        ),
        # no default features + nightly
        (
            "human-panic-1.1.0.json",
            FeatureFlags(no_default_features=True, features=["nightly"]),
            {"nightly"},
            set(),
            dict(),
            dict(),
        ),
        # default features
        ("hyperfine-1.15.0.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        (
            "hyperfine-1.15.0.json",
            FeatureFlags(all_features=True),
            {"windows_process_extensions_main_thread_handle"},
            set(),
            dict(),
            dict(),
        ),
        # no default features
        ("hyperfine-1.15.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "iri-string-0.7.0.json",
            FeatureFlags(),
            {"default", "std", "alloc"},
            set(),
            dict(),
            {"memchr": {"std"}, "serde": {"std", "alloc"}},
        ),
        # all features
        (
            "iri-string-0.7.0.json",
            FeatureFlags(all_features=True),
            {"default", "alloc", "default", "memchr", "serde", "std"},
            {"memchr", "serde"},
            dict(),
            {"serde": {"alloc", "std"}, "memchr": {"std"}},
        ),
        # no default features
        ("iri-string-0.7.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + serde
        (
            "iri-string-0.7.0.json",
            FeatureFlags(features=["serde"]),
            {"default", "std", "alloc", "serde"},
            {"serde"},
            dict(),
            {"serde": {"alloc", "std"}, "memchr": {"std"}},
        ),
        # no default features + serde
        ("iri-string-0.7.0.json", FeatureFlags(no_default_features=True, features=["serde"]), {"serde"}, {"serde"}, dict(), dict()),
        # default features
        ("libc-0.2.139.json", FeatureFlags(), {"default", "std"}, set(), dict(), dict()),
        # all features
        (
            "libc-0.2.139.json",
            FeatureFlags(all_features=True),
            {"default", "align", "const-extern-fn", "extra_traits", "rustc-dep-of-std", "rustc-std-workspace-core", "std", "use_std"},
            {"rustc-std-workspace-core"},
            dict(),
            dict(),
        ),
        # no default features
        ("libc-0.2.139.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + align
        (
            "libc-0.2.139.json",
            FeatureFlags(features=["align"]),
            {"default", "std", "align"},
            set(),
            dict(),
            dict(),
        ),
        # no default features + align
        ("libc-0.2.139.json", FeatureFlags(no_default_features=True, features=["align"]), {"align"}, set(), dict(), dict()),
        # default features
        (
            "predicates-2.1.5.json",
            FeatureFlags(),
            {"default", "diff", "regex", "float-cmp", "normalize-line-endings"},
            {"difflib", "regex", "float-cmp", "normalize-line-endings"},
            dict(),
            dict(),
        ),
        # all features
        (
            "predicates-2.1.5.json",
            FeatureFlags(all_features=True),
            {"default", "color", "color-auto", "diff", "float-cmp", "normalize-line-endings", "regex", "unstable"},
            {"yansi", "concolor", "difflib", "float-cmp", "normalize-line-endings", "regex"},
            dict(),
            {"concolor": {"auto", "std"}},
        ),
        # no default features
        ("predicates-2.1.5.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + color
        (
            "predicates-2.1.5.json",
            FeatureFlags(features=["color"]),
            {"default", "diff", "regex", "float-cmp", "normalize-line-endings", "color"},
            {"difflib", "regex", "float-cmp", "normalize-line-endings", "yansi", "concolor"},
            dict(),
            {"concolor": {"std"}},
        ),
        # no default features + color
        (
            "predicates-2.1.5.json",
            FeatureFlags(no_default_features=True, features=["color"]),
            {"color"},
            {"yansi", "concolor"},
            dict(),
            {"concolor": {"std"}},
        ),
        # default features
        ("proc-macro2-1.0.50.json", FeatureFlags(), {"default", "proc-macro"}, set(), dict(), dict()),
        # all features
        (
            "proc-macro2-1.0.50.json",
            FeatureFlags(all_features=True),
            {"default", "nightly", "proc-macro", "span-locations"},
            set(),
            dict(),
            dict(),
        ),
        # no default features
        ("proc-macro2-1.0.50.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + span-locations
        (
            "proc-macro2-1.0.50.json",
            FeatureFlags(features=["span-locations"]),
            {"default", "proc-macro", "span-locations"},
            set(),
            dict(),
            dict(),
        ),
        # no default features + span-locations
        (
            "proc-macro2-1.0.50.json",
            FeatureFlags(no_default_features=True, features=["span-locations"]),
            {"span-locations"},
            set(),
            dict(),
            dict(),
        ),
        # default features
        ("quote-1.0.23.json", FeatureFlags(), {"default", "proc-macro"}, set(), {"proc-macro2": {"proc-macro"}}, dict()),
        # all features
        (
            "quote-1.0.23.json",
            FeatureFlags(all_features=True),
            {"default", "proc-macro"},
            set(),
            {"proc-macro2": {"proc-macro"}},
            dict(),
        ),
        # no default features
        ("quote-1.0.23.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "rand-0.8.5.json",
            FeatureFlags(),
            {"default", "std", "std_rng", "alloc", "getrandom", "libc", "rand_chacha"},
            {"libc", "rand_chacha"},
            {"rand_core": {"alloc", "getrandom", "std"}, "rand_chacha": {"std"}},
            dict(),
        ),
        # all features
        (
            "rand-0.8.5.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "alloc",
                "getrandom",
                "libc",
                "log",
                "min_const_gen",
                "nightly",
                "packed_simd",
                "rand_chacha",
                "serde",
                "serde1",
                "simd_support",
                "small_rng",
                "std",
                "std_rng",
            },
            {"libc", "log", "packed_simd", "rand_chacha", "serde"},
            {"rand_core": {"alloc", "getrandom", "serde1", "std"}, "rand_chacha": {"std"}},
            dict(),
        ),
        # no default features
        ("rand-0.8.5.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + serde1
        (
            "rand-0.8.5.json",
            FeatureFlags(features=["serde1"]),
            {"default", "std", "std_rng", "alloc", "getrandom", "libc", "rand_chacha", "serde1", "serde"},
            {"libc", "rand_chacha", "serde"},
            {"rand_core": {"alloc", "getrandom", "std", "serde1"}, "rand_chacha": {"std"}},
            dict(),
        ),
        # no default features + serde1
        (
            "rand-0.8.5.json",
            FeatureFlags(no_default_features=True, features=["serde1"]),
            {"serde1", "serde"},
            {"serde"},
            {"rand_core": {"serde1"}},
            dict(),
        ),
        # default features
        ("rand_core-0.6.4.json", FeatureFlags(), set(), set(), dict(), dict()),
        # all features
        (
            "rand_core-0.6.4.json",
            FeatureFlags(all_features=True),
            {"alloc", "getrandom", "serde", "serde1", "std"},
            {"getrandom", "serde"},
            {"getrandom": {"std"}},
            dict(),
        ),
        # no default features
        ("rand_core-0.6.4.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "regex-1.8.4.json",
            FeatureFlags(),
            {
                "default",
                "std",
                "perf",
                "unicode",
                "perf-cache",
                "perf-dfa",
                "perf-inline",
                "perf-literal",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
                "aho-corasick",
                "memchr",
            },
            {"aho-corasick", "memchr"},
            {
                "regex-syntax": {
                    "default",
                    "unicode",
                    "unicode-age",
                    "unicode-bool",
                    "unicode-case",
                    "unicode-gencat",
                    "unicode-perl",
                    "unicode-script",
                    "unicode-segment",
                }
            },
            dict(),
        ),
        # all features
        (
            "regex-1.8.4.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "aho-corasick",
                "memchr",
                "pattern",
                "perf",
                "perf-cache",
                "perf-dfa",
                "perf-inline",
                "perf-literal",
                "std",
                "unicode",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
                "unstable",
                "use_std",
            },
            {"aho-corasick", "memchr"},
            {
                "regex-syntax": {
                    "default",
                    "unicode",
                    "unicode-age",
                    "unicode-bool",
                    "unicode-case",
                    "unicode-gencat",
                    "unicode-perl",
                    "unicode-script",
                    "unicode-segment",
                }
            },
            dict(),
        ),
        # no default features
        ("regex-1.8.4.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + unstable
        (
            "regex-1.8.4.json",
            FeatureFlags(features=["unstable"]),
            {
                "default",
                "std",
                "perf",
                "unicode",
                "perf-cache",
                "perf-dfa",
                "perf-inline",
                "perf-literal",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
                "aho-corasick",
                "memchr",
                "unstable",
                "pattern",
            },
            {"aho-corasick", "memchr"},
            {
                "regex-syntax": {
                    "default",
                    "unicode",
                    "unicode-age",
                    "unicode-bool",
                    "unicode-case",
                    "unicode-gencat",
                    "unicode-perl",
                    "unicode-script",
                    "unicode-segment",
                }
            },
            dict(),
        ),
        # no default features + unstable
        ("regex-1.8.4.json", FeatureFlags(no_default_features=True, features=["unstable"]), {"unstable", "pattern"}, set(), dict(), dict()),
        # default features
        (
            "regex-syntax-0.7.2.json",
            FeatureFlags(),
            {
                "default",
                "std",
                "unicode",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
            },
            set(),
            dict(),
            dict(),
        ),
        # all features
        (
            "regex-syntax-0.7.2.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "std",
                "unicode",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
            },
            set(),
            dict(),
            dict(),
        ),
        # no default features
        ("regex-syntax-0.7.2.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # no default features + unicode
        (
            "regex-syntax-0.7.2.json",
            FeatureFlags(no_default_features=True, features=["unicode"]),
            {
                "unicode",
                "unicode-age",
                "unicode-bool",
                "unicode-case",
                "unicode-gencat",
                "unicode-perl",
                "unicode-script",
                "unicode-segment",
            },
            set(),
            dict(),
            dict(),
        ),
        # default features
        (
            "rust_decimal-1.28.0.json",
            FeatureFlags(),
            {"default", "serde", "std"},
            {"serde"},
            {"arrayvec": {"std"}},
            {
                "borsh": {"std"},
                "bytecheck": {"std"},
                "byteorder": {"std"},
                "bytes": {"std"},
                "rand": {"std"},
                "rkyv": {"std"},
                "serde": {"std"},
                "serde_json": {"std"},
            },
        ),
        # all features
        (
            "rust_decimal-1.28.0.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "arbitrary",
                "borsh",
                "bytecheck",
                "byteorder",
                "bytes",
                "c-repr",
                "db-diesel-mysql",
                "db-diesel-postgres",
                "db-diesel1-mysql",
                "db-diesel1-postgres",
                "db-diesel2-mysql",
                "db-diesel2-postgres",
                "db-postgres",
                "db-tokio-postgres",
                "diesel1",
                "diesel2",
                "legacy-ops",
                "maths",
                "maths-nopanic",
                "postgres",
                "rand",
                "rkyv",
                "rkyv-safe",
                "rocket",
                "rocket-traits",
                "rust-fuzz",
                "serde",
                "serde-arbitrary-precision",
                "serde-bincode",
                "serde-float",
                "serde-str",
                "serde-with-arbitrary-precision",
                "serde-with-float",
                "serde-with-str",
                "serde_json",
                "std",
                "tokio-pg",
                "tokio-postgres",
            },
            {
                "arbitrary",
                "borsh",
                "bytecheck",
                "byteorder",
                "bytes",
                "diesel1",
                "diesel2",
                "postgres",
                "rand",
                "rkyv",
                "rocket",
                "serde",
                "serde_json",
                "tokio-postgres",
            },
            {
                "diesel1": {"mysql", "postgres"},
                "diesel2": {"mysql", "postgres"},
                "rkyv": {"validation"},
                "serde_json": {"arbitrary_precision", "std"},
                "arrayvec": {"std"},
            },
            {
                "borsh": {"std"},
                "bytecheck": {"std"},
                "byteorder": {"std"},
                "bytes": {"std"},
                "rand": {"std"},
                "rkyv": {"std"},
                "serde": {"std"},
                "serde_json": {"std"},
            },
        ),
        # no default features
        ("rust_decimal-1.28.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "rustix-0.36.8.json",
            FeatureFlags(),
            {"default", "std", "use-libc-auxv", "io-lifetimes", "libc"},
            {"io-lifetimes", "libc"},
            dict(),
            dict(),
        ),
        # all features
        (
            "rustix-0.36.8.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "all-apis",
                "all-impls",
                "alloc",
                "cc",
                "compiler_builtins",
                "core",
                "fs",
                "fs-err",
                "io-lifetimes",
                "io_uring",
                "itoa",
                "libc",
                "libc_errno",
                "mm",
                "net",
                "once_cell",
                "os_pipe",
                "param",
                "process",
                "procfs",
                "rand",
                "runtime",
                "rustc-dep-of-std",
                "std",
                "termios",
                "thread",
                "time",
                "use-libc",
                "use-libc-auxv",
            },
            {"alloc", "cc", "compiler_builtins", "core", "io-lifetimes", "itoa", "libc", "libc_errno", "once_cell"},
            {"bitflags": {"rustc-dep-of-std"}, "io-lifetimes": {"fs-err", "os_pipe"}, "linux-raw-sys": {"rustc-dep-of-std"}},
            dict(),
        ),
        # no default features
        ("rustix-0.36.8.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + all-impls
        (
            "rustix-0.36.8.json",
            FeatureFlags(features=["all-impls"]),
            {"default", "std", "use-libc-auxv", "io-lifetimes", "libc", "all-impls", "os_pipe", "fs-err"},
            {"io-lifetimes", "libc"},
            {"io-lifetimes": {"fs-err", "os_pipe"}},
            dict(),
        ),
        # no default features + all-impls
        (
            "rustix-0.36.8.json",
            FeatureFlags(no_default_features=True, features=["all-impls"]),
            {"all-impls", "fs-err", "os_pipe"},
            {"io-lifetimes"},
            {"io-lifetimes": {"fs-err", "os_pipe"}},
            dict(),
        ),
        # default features
        ("serde-1.0.152.json", FeatureFlags(), {"default", "std"}, set(), dict(), dict()),
        # all features
        (
            "serde-1.0.152.json",
            FeatureFlags(all_features=True),
            {"default", "alloc", "derive", "serde_derive", "rc", "std", "unstable"},
            {"serde_derive"},
            dict(),
            dict(),
        ),
        # no default features
        ("serde-1.0.152.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + derive
        (
            "serde-1.0.152.json",
            FeatureFlags(features=["derive"]),
            {"default", "std", "derive", "serde_derive"},
            {"serde_derive"},
            dict(),
            dict(),
        ),
        # default features
        ("serde_derive-1.0.152.json", FeatureFlags(), {"default"}, set(), dict(), dict()),
        # all features
        ("serde_derive-1.0.152.json", FeatureFlags(all_features=True), {"default", "deserialize_in_place"}, set(), dict(), dict()),
        # no default features
        ("serde_derive-1.0.152.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "sha1collisiondetection-0.3.1.json",
            FeatureFlags(),
            {"default", "std", "digest", "digest-trait"},
            {"digest"},
            {"digest": {"std"}},
            dict(),
        ),
        # all features
        (
            "sha1collisiondetection-0.3.1.json",
            FeatureFlags(all_features=True),
            {"default", "digest-trait", "oid", "std", "clap", "clap_mangen", "const-oid", "digest"},
            {"clap", "clap_mangen", "const-oid", "digest"},
            {"digest": {"std"}},
            dict(),
        ),
        # no default features
        ("sha1collisiondetection-0.3.1.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # no default features + std
        (
            "sha1collisiondetection-0.3.1.json",
            FeatureFlags(no_default_features=True, features=["std"]),
            {"std"},
            {"digest"},
            {"digest": {"std"}},
            dict(),
        ),
        # default features
        (
            "syn-1.0.107.json",
            FeatureFlags(),
            {"default", "derive", "parsing", "printing", "clone-impls", "proc-macro", "quote"},
            {"quote"},
            {"proc-macro2": {"proc-macro"}, "quote": {"proc-macro"}},
            dict(),
        ),
        # all features
        (
            "syn-1.0.107.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "clone-impls",
                "derive",
                "extra-traits",
                "fold",
                "full",
                "parsing",
                "printing",
                "proc-macro",
                "quote",
                "test",
                "visit",
                "visit-mut",
            },
            {"quote"},
            {"proc-macro2": {"proc-macro"}, "quote": {"proc-macro"}, "syn-test-suite": {"all-features"}},
            dict(),
        ),
        # no default features
        ("syn-1.0.107.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "time-0.3.17.json",
            FeatureFlags(),
            {"default", "std", "alloc"},
            set(),
            dict(),
            {"serde": {"alloc"}},
        ),
        # all features
        (
            "time-0.3.17.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "alloc",
                "formatting",
                "large-dates",
                "local-offset",
                "macros",
                "parsing",
                "quickcheck",
                "rand",
                "serde",
                "serde-human-readable",
                "serde-well-known",
                "std",
                "wasm-bindgen",
            },
            {"itoa", "libc", "num_threads", "time-macros", "quickcheck", "rand", "serde", "js-sys"},
            dict(),
            {"serde": {"alloc"}, "time-macros": {"formatting", "large-dates", "parsing", "serde"}},
        ),
        # no default features
        ("time-0.3.17.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + serde
        (
            "time-0.3.17.json",
            FeatureFlags(features=["serde"]),
            {"default", "std", "alloc", "serde"},
            {"serde"},
            dict(),
            {"serde": {"alloc"}, "time-macros": {"serde"}},
        ),
        # no default features + serde
        (
            "time-0.3.17.json",
            FeatureFlags(no_default_features=True, features=["serde"]),
            {"serde"},
            {"serde"},
            dict(),
            {"time-macros": {"serde"}},
        ),
        # default features
        (
            "tokio-1.25.0.json",
            FeatureFlags(),
            {"default"},
            set(),
            dict(),
            dict(),
        ),
        # all features
        (
            "tokio-1.25.0.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "bytes",
                "fs",
                "full",
                "io-std",
                "io-util",
                "libc",
                "macros",
                "memchr",
                "mio",
                "net",
                "num_cpus",
                "parking_lot",
                "process",
                "rt",
                "rt-multi-thread",
                "signal",
                "signal-hook-registry",
                "socket2",
                "stats",
                "sync",
                "test-util",
                "time",
                "tokio-macros",
                "tracing",
                "windows-sys",
            },
            {
                "bytes",
                "libc",
                "memchr",
                "mio",
                "num_cpus",
                "parking_lot",
                "signal-hook-registry",
                "socket2",
                "tokio-macros",
                "tracing",
                "windows-sys",
            },
            {
                "mio": {"os-poll", "os-ext", "net"},
                "windows-sys": {
                    "Win32_Foundation",
                    "Win32_Security",
                    "Win32_Storage_FileSystem",
                    "Win32_System_Console",
                    "Win32_System_Pipes",
                    "Win32_System_Threading",
                    "Win32_System_SystemServices",
                    "Win32_System_WindowsProgramming",
                },
            },
            dict(),
        ),
        # default features + signal
        (
            "tokio-1.25.0.json",
            FeatureFlags(features=["signal"]),
            {"default", "signal", "libc", "signal-hook-registry"},
            {"libc", "mio", "signal-hook-registry", "windows-sys"},
            {
                "mio": {"os-poll", "os-ext", "net"},
                "windows-sys": {"Win32_Foundation", "Win32_System_Console"},
            },
            dict(),
        ),
        # no default features + signal
        (
            "tokio-1.25.0.json",
            FeatureFlags(no_default_features=True, features=["signal"]),
            {"signal", "libc", "signal-hook-registry"},
            {"libc", "mio", "signal-hook-registry", "windows-sys"},
            {
                "mio": {"os-poll", "os-ext", "net"},
                "windows-sys": {"Win32_Foundation", "Win32_System_Console"},
            },
            dict(),
        ),
        # no default features
        (
            "tokio-1.25.0.json",
            FeatureFlags(no_default_features=True),
            set(),
            set(),
            dict(),
            dict(),
        ),
        # default features
        ("unicode-xid-0.2.4.json", FeatureFlags(), {"default"}, set(), dict(), dict()),
        # all features
        ("unicode-xid-0.2.4.json", FeatureFlags(all_features=True), {"default", "bench", "no_std"}, set(), dict(), dict()),
        # no default features
        ("unicode-xid-0.2.4.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features
        (
            "zbus-3.8.0.json",
            FeatureFlags(),
            {"default", "async-io", "async-executor", "async-task", "async-lock"},
            {"async-io", "async-executor", "async-task", "async-lock"},
            dict(),
            dict(),
        ),
        # all features
        (
            "zbus-3.8.0.json",
            FeatureFlags(all_features=True),
            {
                "default",
                "async-executor",
                "async-io",
                "async-lock",
                "async-task",
                "chrono",
                "gvariant",
                "lazy_static",
                "quick-xml",
                "serde-xml-rs",
                "time",
                "tokio",
                "tokio-vsock",
                "url",
                "uuid",
                "vsock",
                "windows-gdbus",
                "xml",
            },
            {
                "async-executor",
                "async-io",
                "async-lock",
                "async-task",
                "lazy_static",
                "quick-xml",
                "serde-xml-rs",
                "tokio",
                "tokio-vsock",
                "vsock",
            },
            {"zvariant": {"chrono", "gvariant", "time", "url", "uuid"}},
            dict(),
        ),
        # no default features
        ("zbus-3.8.0.json", FeatureFlags(no_default_features=True), set(), set(), dict(), dict()),
        # default features + tokio
        (
            "zbus-3.8.0.json",
            FeatureFlags(features=["tokio"]),
            {"default", "async-io", "async-executor", "async-task", "async-lock", "tokio", "lazy_static"},
            {"async-io", "async-executor", "async-task", "async-lock", "tokio", "lazy_static"},
            dict(),
            dict(),
        ),
        # no default features + tokio
        (
            "zbus-3.8.0.json",
            FeatureFlags(no_default_features=True, features=["tokio"]),
            {"tokio", "lazy_static"},
            {"tokio", "lazy_static"},
            dict(),
            dict(),
        ),
        # default features
        (
            "zoxide-0.9.0.json",
            FeatureFlags(),
            {"default"},
            set(),
            dict(),
            dict(),
        ),
        # all features
        (
            "zoxide-0.9.0.json",
            FeatureFlags(all_features=True),
            {"default", "nix-dev"},
            set(),
            dict(),
            dict(),
        ),
        # no default features
        (
            "zoxide-0.9.0.json",
            FeatureFlags(no_default_features=True),
            set(),
            set(),
            dict(),
            dict(),
        ),
    ],
    ids=short_repr,
)
def test_package_get_enabled_features_transitive(
    filename: str,
    flags: FeatureFlags,
    expected_enabled: set[str],
    expected_optional: set[str],
    expected_other: dict[str, set[str]],
    expected_conditional: dict[str, set[str]],
):
    metadata = load_metadata_from_resource(filename)
    enabled, optional_enabled, other_enabled, other_conditional = metadata.packages[0].get_enabled_features_transitive(flags)

    assert enabled == expected_enabled
    assert optional_enabled == expected_optional
    assert other_enabled == expected_other
    assert other_conditional == expected_conditional
