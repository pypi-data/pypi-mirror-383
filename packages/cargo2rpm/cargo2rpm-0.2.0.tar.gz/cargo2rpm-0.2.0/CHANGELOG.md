## Release 0.2.0

Bug fixes and improvements!

- New subcommands for `license-breakdown` and `license-summary` which
  are intended to replace the Bash implementations in rust-packaging.
- When determining the minimum required Rust version (MSRV) for RPM
  package dependencies, use a conservative estimate based on the `edition`
  setting when the `rust-version` setting is not present in metadata.
- Heuristics for RPM Summary generation from crate description text were
  slightly tweaked, hopefully with better results for a few common cases.

## Release 0.1.18

This release fixes a crash when running `cargo2rpm` without arguments.

## Release 0.1.17

This release contains a fix for a logic bug that prevented stderr output from 
`cargo metadata` calls with a non-zero exit status from being written to actual
stderr.

## Release 0.1.16

This release addresses an edge case in `BuildRequires` generation for cargo
workspaces which could previously lead to crashes for path- or git-based
dependencies in some circumstances.

## Release 0.1.15

This release contains a follow-up fix for the changes that were introduced
in v0.1.13 and v0.1.14. The previous fixes were incomplete, and did not cause
any features that were enabled for those additional dependencies to be included
in the generated `Requires`.

## Release 0.1.14

This release includes a fix for another subtle bug in the resolution of
`Requires` for crate subpackages. Similarly to the change in v0.1.13, the
"default" features of a dependency also need to pulled in for dependencies
that are conditionally enabled optional dependencies.

## Release 0.1.13

This release includes a fix for a subtle bug in the resolution of `Requires` for
crate subpackages. Previosly, the "default" feature set of dependencies was
mistakenly not added to dependencies of an optional dependency with "default"
features enabled was implicitly enabled because of a feature dependency.

## Release 0.1.12

This release exposes two more attributes from the JSON output from
"cargo metadata" as properties - `package.homepage` and `package.repository`.

## Release 0.1.11

This release includes a fix for a bug that could lead to errors not
being reported properly and for RPM builds to succeed despite assertion
failures. In earlier versions, some exceptions were not caught in
the cargo2rpm script entry point, causing tracebacks and errors to be
printed to stderr, where they do not cause RPM builds to abort.

The code for the script entry point has been reorganized for this release
to ensure that any uncaught exception also causes RPM to abort builds, in
addition to properly catching previously ignored `AssertionErrors`.

Additionally, some type annotations were fixed and minor issues with
mismatched types and variable names that are reused for values of a different
type were addressed. With these changes in place, cargo2rpm now passes the
checks run by mypy.

## Release 0.1.10

This release contains some additions, fixes, and improvements:

- Fixed a bug in the implementation of `Version` comparisons. Earlier
  versions reported `2.0.0` to be smaller than `1.1.0` due to a flaw in
  the comparison logic.
- Added APIs for checking whether a `Version` is contained in version
  requirements (i.e. `VersionReq` or `Comparator`). Together with
  comparisons on `Version`, this should allow doing something like
  determining the greatest version that is compatible with a given
  requirement.
- Added the `py.typed` marker file to the package so that tools like
  mypy actually read the type annotations.

## Release 0.1.9

This release includes a bugfix in the support for cargo workspaces and a
small (backwards compatible) improvement for the RPM dependency generators:

- Required features of any binary targets in workspace members are now
  resolved correctly and no longer cause crashes.
- If crates set a minimum supported Rust version (MSRV) by using the
  `package.rust-version` setting in `Cargo.toml`, an equivalent dependency
  on `rust >= MSRV` is now automatically generated for crate `Requires` and
  `BuildRequires`. This allows builds to fail fast during dependency
  resolution instead of only failing late during the actual build stage.

## Release 0.1.8

This release adds another subcommand for the cargo2rpm script, which can be
used by RPM generators for bundled / vendored crate dependencies.

## Release 0.1.7

This is a fixup release for version 0.1.6. It accidentally did not include
test sources.

## Release 0.1.6

This release adds implementations of all comparison operators for the `Version`
class from the `semver` submodule, and introduces a new `PreRelease` class in
the same module for parsing and comparing version substrings that denote a
pre-release version.

This functionality was previously present in the SemVer implementation in
`rust2rpm` but was dropped because `rust2rpm` did not use it. However, other
applications relied on this functionality, so it was restored in `cargo2rpm`
to make porting from old `rust2rpm` versions to `cargo2rpm` easier.

## Release 0.1.5

This release fixes some subtle bugs in the calculation of enabled features
when resolving `BuildRequires`.

## Release 0.1.4

This release fixes a typo in the CLI argument parser which prevented the
`-n` flag ("`--no-default-features`") of some RPM macros from working.

## Release 0.1.3

This release fixes an edge case when determining whether default features
are enabled for a member of a cargo workspace.

## Release 0.1.2

This release fixes an edge cases in the "is this crate a library" heuristics:
Some crates explicitly set their crate type to "rlib", which is equivalent
to "lib", but which was not recognised as such prior to v0.1.2.

Additionally, two methods have been added: `Metadata.is_cdylib` and
`Package.cdylib`, which can be used to detect whether a crate (or any crate in a
cargo workspace) provides a `cdylib` binary target.

## Release 0.1.1

This release adds two methods on `Metadata` for processing crate description
into usable "Summary" and "description" texts for use in RPM specs based on
a few simple heuristics.

It is now also possible to override which "cargo" binary is used for generating
crate metadata by defining the `CARGO` environment variable. The now redundant
`cargo` argument was dropped from the `Metadata.from_cargo` method.

## Release 0.1.0

Initial release.
