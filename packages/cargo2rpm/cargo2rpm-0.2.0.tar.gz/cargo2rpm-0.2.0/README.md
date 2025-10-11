# cargo2rpm

cargo2rpm implements a translation layer between cargo and RPM. It provides a
CLI interface (for implementing [RPM macros and generators][rust-packaging]) and
a Python API (which [rust2rpm] is built upon).

The project serves as a dependency-free, pure-Python replacement for the old
backend code in rust2rpm, which was no longer maintainable and could not be
adapted to support the latest cargo features (i.e. "namespaced dependencies" and
"weak dependency features", which were introduced in Rust 1.60.0).

To decouple the release cycles of the different components involved in packaging
Rust projects (and prevent possible bootstrap problems), the code originally
developed under the "rust2rpm" umbrella was split into three projects:

- [cargo2rpm]: low-level functionality for translating between cargo and RPM
- [rust-packaging]: RPM macros and generators built on top of the cargo2rpm CLI
- [rust2rpm]: RPM spec file generator built on top of cargo2rpm 

[cargo2rpm]: https://pagure.io/fedora-rust/cargo2rpm
[rust-packaging]: https://pagure.io/fedora-rust/rust-packaging
[rust2rpm]: https://pagure.io/fedora-rust/rust2rpm
