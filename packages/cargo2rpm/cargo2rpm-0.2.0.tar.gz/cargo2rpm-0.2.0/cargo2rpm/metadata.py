import json
import re
import subprocess
import sys
import textwrap
from typing import Optional

from cargo2rpm import CARGO
from cargo2rpm.semver import Comparator, Op, Version, VersionReq


class FeatureFlags:
    """
    Collection of flags that affect feature and dependency resolution
    (i.e. `--all-features`, `--no-default-features`, and `--features foo,bar`).

    Raises a `ValueError` during initialization if arguments that are
    incompatible with each other are passed.

    Passing no arguments is equivalent to passing no command-line flags to
    cargo, i.e. the "default" feature is enabled.
    """

    def __init__(self, all_features: bool = False, no_default_features: bool = False, features: Optional[list[str]] = None):
        if features is None:
            features = []

        if all_features and features:
            raise ValueError("Cannot specify both '--all-features' and '--features'.")

        if all_features and no_default_features:
            raise ValueError("Cannot specify both '--all-features' and '--no-default-features'.")

        self.all_features = all_features
        self.no_default_features = no_default_features
        self.features = features

    def __repr__(self):
        parts = []

        if self.all_features:
            parts.append("all_features")
        if self.no_default_features:
            parts.append("no_default_features")
        if self.features:
            parts.append(f"features=[{', '.join(self.features)}]")

        if parts:
            string = ", ".join(parts)
            return f"[{string}]"
        else:
            return "[]"

    def __eq__(self, other):
        if not isinstance(other, FeatureFlags):
            return False  # pragma nocover

        return (
            self.all_features == other.all_features
            and self.no_default_features == other.no_default_features
            and set(self.features) == set(other.features)
        )


class Dependency:
    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return repr(self._data)

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def req(self) -> str:
        return self._data["req"]

    @property
    def kind(self) -> Optional[str]:
        return self._data["kind"]

    @property
    def rename(self) -> Optional[str]:
        return self._data["rename"]

    @property
    def optional(self) -> bool:
        return self._data["optional"]

    @property
    def uses_default_features(self) -> bool:
        return self._data["uses_default_features"]

    @property
    def features(self) -> list[str]:
        return self._data["features"]

    @property
    def target(self) -> Optional[str]:
        return self._data["target"]

    @property
    def path(self) -> Optional[str]:
        return self._data.get("path")

    @property
    def source(self) -> Optional[str]:
        return self._data.get("source")

    def is_path_or_git(self) -> bool:
        if self.path:
            return True
        if source := self.source:
            if source.startswith("git+"):
                return True
        return False

    def to_rpm(self, feature: Optional[str]) -> str:
        """
        Formats this crate dependency as an RPM dependency string.
        """

        assert self.path is None, "Attempt to generate an RPM dependency for a path dependency!"

        req = VersionReq.parse(self.req)
        return req.to_rpm(self.name, feature)


class Target:
    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return repr(self._data)

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def kind(self) -> list[str]:
        return self._data["kind"]

    @property
    def crate_types(self) -> list[str]:
        return self._data["crate_types"]

    @property
    def required_features(self) -> list[str]:
        return self._data.get("required-features", None) or list()


class Package:
    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return repr(self._data)

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def version(self) -> str:
        return self._data["version"]

    @property
    def license(self) -> Optional[str]:
        return self._data["license"]

    @property
    def license_file(self) -> Optional[str]:
        return self._data["license_file"]

    @property
    def description(self) -> Optional[str]:
        return self._data["description"]

    @property
    def dependencies(self) -> list[Dependency]:
        return [Dependency(dependency) for dependency in self._data["dependencies"]]

    @property
    def targets(self) -> list[Target]:
        return [Target(target) for target in self._data["targets"]]

    @property
    def features(self) -> dict[str, list[str]]:
        return self._data["features"]

    @property
    def manifest_path(self) -> str:
        return self._data["manifest_path"]

    @property
    def rust_version(self) -> Optional[str]:
        return self._data["rust_version"]

    @property
    def edition(self) -> str:
        return self._data["edition"]

    @property
    def homepage(self) -> Optional[str]:
        return self._data["homepage"]

    @property
    def repository(self) -> Optional[str]:
        return self._data["repository"]

    def get_feature_names(self) -> set[str]:
        return set(self.features.keys())

    def get_normal_dependencies(self, optional: bool) -> dict[str, Dependency]:
        """
        Returns a dictionary that maps "normal" dependencies (i.e. not build- or
        dev-dependencies) from their possibly renamed name (i.e. how they can be
        referenced in feature dependencies) to the dependency objects
        themselves.
        """

        normal = filter(lambda d: d.kind is None and d.optional == optional, self.dependencies)
        return {d.rename if d.rename else d.name: d for d in normal}

    def get_build_dependencies(self, optional: bool) -> dict[str, Dependency]:
        """
        Returns a dictionary that maps build-dependencies from their possibly
        renamed name (i.e. how they can be referenced in feature dependencies)
        to the dependency objects themselves.
        """

        build = filter(lambda d: d.kind == "build" and d.optional == optional, self.dependencies)
        return {d.rename if d.rename else d.name: d for d in build}

    def get_dev_dependencies(self) -> dict[str, Dependency]:
        """
        Returns a dictionary that maps dev-dependencies from their possibly
        renamed name (i.e. how they can be referenced in feature dependencies)
        to the dependency objects themselves.
        """

        dev = filter(lambda d: d.kind == "dev", self.dependencies)
        return {d.rename if d.rename else d.name: d for d in dev}

    def to_rpm_dependency(self, feature: Optional[str]) -> str:
        """
        Returns an RPM dependency string that represents a dependency on this
        crate with an exact requirement on its current version.
        """

        ver = Version.parse(self.version)
        req = VersionReq([Comparator(Op.EXACT, ver.major, ver.minor, ver.patch, ver.pre)])
        return req.to_rpm(self.name, feature)

    def get_description(self) -> Optional[str]:
        """
        Returns a reformatted version of the package description with lines
        wrapped to 72 characters.
        """

        if self.description is None:
            return None

        # reformat contents so paragraphs become lines
        paragraphs = self.description.replace("\n\n", "\r").replace("\n", " ").replace("\r", "\n").strip()

        # ensure description starts with a capital letter
        if not paragraphs[0].isupper():
            paragraphs = paragraphs[0].upper() + paragraphs[1:]

        # ensure description ends with a full stop
        if not paragraphs.endswith("."):
            paragraphs += "."

        # return contents wrapped to 72 columns
        return "\n".join(textwrap.wrap(paragraphs, 72))

    def get_summary(self) -> Optional[str]:
        """
        Returns a shortened version of the package description based on a few
        heuristics.
        """

        if not self.description:
            return None

        # replace markdown markup (i.e. code fences)
        description = self.description.replace("`", "")

        # replace common phrases like "this is a" or "this {crate} provides an"
        stripped = re.sub(
            r"^((a|an|this)\s+)?(crate\s+)?((is|provides)\s+)?((a|an|the)\s+)?",
            "",
            description,
            flags=re.IGNORECASE,
        )

        # if stripped description still contains multiple lines, merge them
        stripped = re.sub(r"(\n+)", " ", stripped).strip()

        # ensure summary starts with a capital letter
        if not stripped[0].isupper():
            stripped = stripped[0].upper() + stripped[1:]

        # if length is already short enough, reformat as one line and return
        if len(stripped) <= 72:
            return stripped.removesuffix(".")

        # use some heuristics to determine phrase boundaries
        if (brace := stripped.find(" (")) != -1:
            return stripped[0:brace].removesuffix(".")
        if (period := stripped.find(". ")) != -1:
            return stripped[0:period].removesuffix(".")
        if (semicolon := stripped.find("; ")) != -1:
            return stripped[0:semicolon].removesuffix(".")

        # none of the heuristics matched:
        # fall back to returning the stripped description even if it's too long
        return stripped.removesuffix(".")

    def is_bin(self) -> bool:
        """
        Returns `True` if any of the build targets of this crate are a "proper"
        binary target (i.e. crate type is `bin`, but not `example`, `test`, or
        `bench`).
        """

        for target in self.targets:
            if "bin" in target.kind:
                return True
        return False

    def is_lib(self) -> bool:
        """
        Returns `True` if any of the build targets of this crate are either a
        `(r)lib` target with `(r)lib` crate type, or a `proc-macro` target with
        `proc-macro` crate type.
        """

        for target in self.targets:
            if "lib" in target.kind and "lib" in target.crate_types:
                return True
            if "rlib" in target.kind and "rlib" in target.crate_types:
                return True
            if "proc-macro" in target.kind and "proc-macro" in target.crate_types:
                return True
        return False

    def is_cdylib(self) -> bool:
        """
        Returns `True` if any of the build targets of this crate are a `lib`
        target with `cdylib` crate type.
        """

        for target in self.targets:
            if "cdylib" in target.kind and "cdylib" in target.crate_types:
                return True
        return False

    def get_binaries(self) -> set[str]:
        """
        Returns the set of "proper" binary build targets of this crate (i.e.
        the crate type is `bin`, but not `example`, `test`, or `bench`).
        """

        bins = set()
        for target in self.targets:
            if "bin" in target.kind:
                bins.add(target.name)
        return bins

    def get_enabled_features_transitive(self, flags: FeatureFlags) -> tuple[set[str], set[str], dict[str, set[str]], dict[str, set[str]]]:
        """
        Resolves the transitive closure of enabled features, enabled optional
        dependencies, enabled features of (optional or non-optional)
        dependencies, and conditionally enabled features of optional
        dependencies, taking feature flags into account.
        """

        # get names of all optional dependencies
        optional_names = set(self.get_normal_dependencies(True).keys()).union(set(self.get_build_dependencies(True).keys()))

        # collect enabled features of this crate
        enabled: set[str] = set()
        # collect enabled optional dependencies
        optional_enabled: set[str] = set()
        # collect enabled features of other crates
        other_enabled: dict[str, set[str]] = dict()
        # collect conditionally enabled features of other crates
        other_conditional: dict[str, set[str]] = dict()

        # process arguments
        feature_names = self.get_feature_names()

        if not flags.no_default_features and "default" not in flags.features and "default" in feature_names:
            enabled.add("default")

        if flags.all_features:
            for feature in feature_names:
                enabled.add(feature)

        for feature in flags.features:
            enabled.add(feature)

        # calculate transitive closure of enabled features
        while True:
            new = set()

            for feature in enabled:
                deps = self.features[feature]

                for dep in deps:
                    # named optional dependency
                    if dep.startswith("dep:"):
                        name = dep.removeprefix("dep:")
                        optional_enabled.add(name)
                        continue

                    # dependency/feature
                    if "/" in dep and "?/" not in dep:
                        name, feat = dep.split("/")

                        # using "foo/bar" in feature dependencies implicitly
                        # also enables the optional dependency "foo":
                        if name in optional_names:
                            optional_enabled.add(name)

                        if name in other_enabled.keys():
                            other_enabled[name].add(feat)
                        else:
                            other_enabled[name] = {feat}
                        continue

                    # dependency?/feature
                    if "?/" in dep:
                        name, feat = dep.split("?/")
                        if name in other_conditional.keys():
                            other_conditional[name].add(feat)
                        else:
                            other_conditional[name] = {feat}
                        continue

                    # feature name
                    if dep not in enabled:
                        new.add(dep)

            # continue until set of enabled "proper" features no longer changes
            if new:
                enabled.update(new)
            else:
                break

        return enabled, optional_enabled, other_enabled, other_conditional


class Metadata:
    """
    Representation of top-level crate metadata, i.e. the entire JSON dump
    produced by calling `cargo metadata --format-version 1`. The format of this
    data is guaranteed to be stable.

    The format of the data is the same whether run against `Cargo.toml` from an
    isolated crate or against a `Cargo.toml` manifest that defines a cargo
    workspace. The only difference is that for a single crate, the list of
    packages will be of length one, and for a workspace, the list of packages
    will (in general) be two or larger.
    """

    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return repr(self._data)

    @staticmethod
    def from_json(data: str) -> "Metadata":
        """
        Loads JSON dump from input data and returns a `Metadata` object.

        This method is used for loading JSON dumps for test input, as it does
        not require any other files (i.e. crate sources) to be present.
        """

        return Metadata(json.loads(data))

    @staticmethod
    def from_cargo(path: str) -> "Metadata":  # pragma nocover
        """
        Runs `cargo metadata` with the appropriate flags against the
        `Cargo.toml` manifest at `path`.

        This method only returns correct results when run against `Cargo.toml`
        files included in complete crate sources. Otherwise, automatic target
        discovery (i.e. the default behaviour of `autobins`, `autoexamples`,
        `autotests`, and `autobenches`) will result in missing build targets,
        and missing source files for explicitly specified `bin`, `example`,
        `test`, or `bench` targets will cause errors.
        """

        ret = subprocess.run(
            [
                CARGO,
                "metadata",
                "--quiet",
                "--format-version",
                "1",
                "--offline",
                "--no-deps",
                "--manifest-path",
                path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            ret.check_returncode()
            stdout = ret.stdout.decode()
            stderr = ret.stderr.decode()

            if stderr:
                print(stderr, file=sys.stderr)

            return Metadata.from_json(stdout)

        except subprocess.CalledProcessError as exc:
            if exc.stdout:
                print(exc.stdout.decode(), file=sys.stdout)
            if exc.stderr:
                print(exc.stderr.decode(), file=sys.stderr)
            raise

    @property
    def packages(self) -> list[Package]:
        return [Package(package) for package in self._data["packages"]]

    @property
    def target_directory(self) -> str:
        return self._data["target_directory"]

    def is_workspace(self) -> bool:
        """
        Returns `True` if the metadata looks like a cargo workspace.

        A workspace with a single member is equivalent to no workspace (since
        no path dependencies are possible with only one workspace member), so
        the naive check for "at least two workspace members" is enough.
        """

        return len(self.packages) >= 2

    def is_bin(self) -> bool:
        """
        Returns `True` if there are any "proper" binary targets.
        """

        for package in self.packages:
            if package.is_bin():
                return True
        return False

    def is_lib(self) -> bool:
        """
        Returns `True` if the crate has a `lib` or `proc-macro` build target.
        Always returns `False` for cargo workspaces.
        """

        packages = self.packages

        # do not report libs from workspaces until this is actually supported
        if len(packages) >= 2:
            return False

        for package in packages:
            if package.is_lib():
                return True
        return False

    def is_cdylib(self) -> bool:
        """
        Returns `True` if there are any `cdylib` (C shared library) targets.
        """

        for package in self.packages:
            if package.is_cdylib():
                return True
        return False

    def get_binaries(self) -> set[str]:
        """
        Returns the union of all sets of "proper" binary build targets of all
        crates in this workspace (or of the single crate for non-workspace
        crates).
        """

        bins = set()
        for package in self.packages:
            bins.update(package.get_binaries())
        return bins

    def get_feature_flags_for_workspace_members(self, flags: FeatureFlags) -> dict[str, FeatureFlags]:
        """
        Resolves the transitive closure of enabled features for intra-workspace
        crate dependencies, taking `required-features` for binary targets and
        passed feature flags into account.
        """

        members = {package.name for package in self.packages}

        # keep track of workspace members and which features are enabled for them:
        # - determine union of enabled features for all workspace members
        member_features: dict[str, set[str]] = dict()
        # - determine whether default features are enabled for workspace members
        member_defaults: dict[str, bool] = dict()

        # collect required features of "bin" and "cdylib" targets
        required_features: dict[str, set[str]] = dict()

        # apply feature flags to all packages
        for package in self.packages:
            if flags.all_features:
                features = member_features.get(package.name) or set()
                features.update(package.get_feature_names())
                member_features[package.name] = features

            if flags.features:
                features = member_features.get(package.name) or set()
                for feature in flags.features:
                    if feature in package.get_feature_names():
                        features.add(feature)
                member_features[package.name] = features

            if flags.no_default_features:
                member_defaults[package.name] = False

            # ensure that the mapping includes data for all packages
            features = member_features.get(package.name) or set()
            member_features[package.name] = features

        # enable required and default features of binary targets
        for package in self.packages:
            for target in package.targets:
                if ("bin" in target.kind and "bin" in target.crate_types) or ("cdylib" in target.kind and "cdylib" in target.crate_types):
                    if reqs := target.required_features:
                        if package.name not in required_features.keys():
                            required_features[package.name] = set(reqs)
                        else:
                            required_features[package.name].update(reqs)
                    if not flags.no_default_features:
                        member_defaults[package.name] = True

        for package in self.packages:
            for dep in filter(lambda pkg: pkg.path is not None, package.dependencies):
                features = member_features.get(dep.name) or set()
                features.update(dep.features)
                member_features[dep.name] = features

                defaults = member_defaults.get(dep.name) or False
                defaults = defaults or dep.uses_default_features
                member_defaults[dep.name] = defaults

        # unconditionally add required features to resolved features:
        # "cargo build" skips building targets for which required features are
        # not enabled, but for package builds this behaviour doesn't make sense
        for name, required in required_features.items():
            member_features[name].update(required)

        # turn on default features for all workspace members that are not
        # explicitly referenced by other workspace members
        for package in self.packages:
            if package.name not in member_defaults.keys():
                member_defaults[package.name] = True

        # enable features pulled in by feature dependencies of enabled features
        for package in self.packages:
            deps_real_names = {dep.rename or dep.name: dep.name for dep in package.dependencies}

            enabled = member_features[package.name].copy()
            if member_defaults[package.name] and "default" in package.get_feature_names():
                enabled.add("default")

            while True:
                new: set[str] = set()

                for feature_name, deps in package.features.items():
                    if feature_name not in enabled:
                        continue

                    for fdep in deps:
                        # named optional dependency
                        if fdep.startswith("dep:"):
                            # cargo builds all workspace members even if they are optional
                            continue

                        # dependency/feature
                        if "/" in fdep and "?/" not in fdep:
                            name, feat = fdep.split("/")

                            if deps_real_names[name] in members:
                                real_name = deps_real_names[name]
                                member_features[real_name].add(feat)
                            continue

                        # dependency?/feature
                        if "?/" in fdep:
                            name, feat = fdep.split("?/")

                            if deps_real_names[name] in members:
                                real_name = deps_real_names[name]
                                member_features[real_name].add(feat)
                            continue

                        # feature name
                        if fdep not in enabled:
                            new.add(fdep)
                            continue

                # continue until set of enabled "proper" features no longer changes
                if new:
                    enabled.update(new)
                else:
                    break

        # construct feature flags from collected settings
        member_flags: dict[str, FeatureFlags] = dict()
        for package in self.packages:
            if member_features[package.name] == package.get_feature_names() and flags.all_features:
                flag_no_default_features = False
                flag_all_features = True
                flag_features = list()
            else:
                flag_no_default_features = not member_defaults[package.name]
                flag_all_features = False
                flag_features = list(sorted(member_features[package.name]))

            flags = FeatureFlags(all_features=flag_all_features, no_default_features=flag_no_default_features, features=flag_features)
            member_flags[package.name] = flags

        return member_flags
