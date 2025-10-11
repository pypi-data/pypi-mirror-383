from typing import Optional

from cargo2rpm.metadata import Package, FeatureFlags, Metadata
from cargo2rpm.semver import Version


class InvalidFeatureError(Exception):
    """
    Exception which is raised when calling a method on a crate with a feature
    name as argument that is not a feature of the crate.

    This is usually the result of a packager error, for example, when
    a spec file has not been properly regenerated for a new crate version
    (which has removed a previously included feature) or after patching the
    upstream `Cargo.toml` file to remove unwanted features or optional
    dependencies.
    """

    def __init__(self, error: str):
        self.error = error
        super().__init__(error)


def msrv_from_edition(edition: str) -> Optional[str]:
    match edition:
        case "2015":
            return None
        case "2018":
            return "1.31"
        case "2021":
            return "1.56"
        case "2024":
            return "1.85"
        case _:
            msg = f"Invalid Edition: {edition}"
            raise ValueError(msg)


def buildrequires(package: Package, flags: FeatureFlags, with_dev_deps: bool) -> set[str]:
    """
    Resolves and returns RPM `BuildRequires` of the `package` crate, taking into
    account feature flags passed in the `flags` argument (which represents the
    presence of the `--all-features`, `--no-default-features, or `--features`
    CLI flags of cargo), and only includes dev-dependencies if `with_dev_deps`
    is passed as `True`.

    This happens in two stages - first, the list of enabled features (and
    whether they are used with "default" features) is resolved for all
    dependencies; then this information is used to generate the actual set of
    dependencies in RPM format.
    """

    enabled, optional_enabled, other_enabled, other_conditional = package.get_enabled_features_transitive(flags)

    normal = package.get_normal_dependencies(False)
    normal_optional = package.get_normal_dependencies(True)
    build = package.get_build_dependencies(False)
    build_optional = package.get_build_dependencies(True)
    dev = package.get_dev_dependencies()

    # keep track of dependencies and which features are enabled for them:
    # - determine union of enabled features for all dependencies
    deps_enabled_features: dict[str, set[str]] = dict()
    # - determine whether default features are enabled for all dependencies
    deps_default_features: dict[str, bool] = dict()
    # - determine optional dependencies that need to be enabled as workarounds
    workarounds: dict[str, tuple[set[str], bool]] = dict()

    # unconditionally enabled features of normal dependencies
    for name, dep in normal.items():
        features = deps_enabled_features.get(name) or set()
        features.update(dep.features)
        deps_enabled_features[name] = features

        defaults = deps_default_features.get(name) or False
        defaults = defaults or dep.uses_default_features
        deps_default_features[name] = defaults

    # unconditionally enabled features of enabled, optional, normal dependencies
    for name, dep in normal_optional.items():
        if name in optional_enabled:
            features = deps_enabled_features.get(name) or set()
            features.update(dep.features)
            deps_enabled_features[name] = features

            defaults = deps_default_features.get(name) or False
            defaults = defaults or dep.uses_default_features
            deps_default_features[name] = defaults

    # unconditionally enabled features of build-dependencies
    for name, dep in build.items():
        features = deps_enabled_features.get(name) or set()
        features.update(dep.features)
        deps_enabled_features[name] = features

        defaults = deps_default_features.get(name) or False
        defaults = defaults or dep.uses_default_features
        deps_default_features[name] = defaults

    # unconditionally enabled features of enabled, optional, build-dependencies
    for name, dep in build_optional.items():
        if name in optional_enabled:
            features = deps_enabled_features.get(name) or set()
            features.update(dep.features)
            deps_enabled_features[name] = features

            defaults = deps_default_features.get(name) or False
            defaults = defaults or dep.uses_default_features
            deps_default_features[name] = defaults

    # unconditionally enabled features of enabled dev-dependencies
    if with_dev_deps:
        for name, dep in dev.items():
            features = deps_enabled_features.get(name) or set()
            features.update(dep.features)
            deps_enabled_features[name] = features

            defaults = deps_default_features.get(name) or False
            defaults = defaults or dep.uses_default_features
            deps_default_features[name] = defaults

    # features unconditionally enabled by feature dependencies
    for name, other_features in other_enabled.items():
        features = deps_enabled_features.get(name) or set()
        features.update(other_features)
        deps_enabled_features[name] = features

        if "default" in features:
            deps_default_features[name] = True

    # features conditionally enabled by feature dependencies
    for name, other_features in other_conditional.items():
        features = deps_enabled_features.get(name) or set()
        features.update(other_features)
        deps_enabled_features[name] = features

        if name not in enabled:
            defaults = deps_default_features.get(name) or False
            if odep := normal_optional.get(name):
                defaults = defaults or odep.uses_default_features
                additional_features = odep.features
            if odep := build_optional.get(name):
                defaults = defaults or odep.uses_default_features
                additional_features = odep.features
            workarounds[name] = (set.union(other_features, additional_features), defaults)

    # collect dependencies taking into account which features are enabled
    brs = set()

    # minimum supported Rust version
    if msrv := package.rust_version:
        brs.add(f"rust >= {msrv}")
    elif msrv := msrv_from_edition(package.edition):
        brs.add(f"rust >= {msrv}")

    # normal dependencies
    for name, dep in normal.items():
        if dep.is_path_or_git():
            continue

        if deps_default_features[name]:
            brs.add(dep.to_rpm("default"))
        else:
            brs.add(dep.to_rpm(None))
        for feature in deps_enabled_features[name]:
            brs.add(dep.to_rpm(feature))

    # optional normal dependencies
    for name, dep in normal_optional.items():
        if dep.is_path_or_git():
            continue

        if name in optional_enabled:
            if deps_default_features[name]:
                brs.add(dep.to_rpm("default"))
            else:
                brs.add(dep.to_rpm(None))
            for feature in deps_enabled_features[name]:
                brs.add(dep.to_rpm(feature))

    # build-dependencies
    for name, dep in build.items():
        if dep.is_path_or_git():
            continue

        if deps_default_features[name]:
            brs.add(dep.to_rpm("default"))
        else:
            brs.add(dep.to_rpm(None))
        for feature in deps_enabled_features[name]:
            brs.add(dep.to_rpm(feature))

    # optional build-dependencies
    for name, dep in build_optional.items():
        if dep.is_path_or_git():
            continue

        if name in optional_enabled:
            if deps_default_features[name]:
                brs.add(dep.to_rpm("default"))
            else:
                brs.add(dep.to_rpm(None))
            for feature in deps_enabled_features[name]:
                brs.add(dep.to_rpm(feature))

    # dev-dependencies
    if with_dev_deps:
        for name, dep in dev.items():
            if dep.is_path_or_git():
                continue

            if deps_default_features[name]:
                brs.add(dep.to_rpm("default"))
            else:
                brs.add(dep.to_rpm(None))
            for feature in deps_enabled_features[name]:
                brs.add(dep.to_rpm(feature))

    # workarounds
    for name, (features, defaults) in workarounds.items():
        if odep := normal_optional.get(name):
            if odep.is_path_or_git():
                continue
            if defaults:
                brs.add(odep.to_rpm("default"))
            else:
                brs.add(odep.to_rpm(None))
            for feature in features:
                brs.add(odep.to_rpm(feature))
        if odep := build_optional.get(name):
            if odep.is_path_or_git():
                continue
            if defaults:
                brs.add(odep.to_rpm("default"))
            else:
                brs.add(odep.to_rpm(None))
            for feature in features:
                brs.add(odep.to_rpm(feature))

    return brs


def workspace_buildrequires(metadata: Metadata, flags: FeatureFlags, with_dev_deps: bool) -> set[str]:
    """
    Resolves and returns RPM `BuildRequires` for an entire cargo workspace.

    Prior to generating `BuildRequires` for every individual workspace member,
    intra-workspace dependencies are resolved (i.e. which features of which
    workspace member are enabled).

    This takes into account "required features" of binary targets (i.e. crates
    with "bin" or "cdylib" targets).
    """

    all_brs = set()

    member_flags = metadata.get_feature_flags_for_workspace_members(flags)
    for package in metadata.packages:
        all_brs.update(buildrequires(package, member_flags[package.name], with_dev_deps))

    return all_brs


def devel_subpackage_names(package: Package) -> set[str]:
    """
    Returns the set of subpackage names for a crate.

    If the crate does not provide a "lib" target, the set will be empty.
    Otherwise, the set of "features" of the crate is returned, with the
    implicitly defined "default" feature explicitly included.
    """

    # no feature subpackages are generated for binary-only crates
    if not package.is_lib():
        return set()

    names = package.get_feature_names()

    # the "default" feature is always implicitly defined
    if "default" not in names:
        names.add("default")

    return names


def _requires_crate(package: Package) -> set[str]:
    """
    Resolves install-time dependencies of the given crate. Used for
    automatically generating dependencies of crate packages with RPM generators.

    This only includes non-optional "normal" and "build-dependencies" of the
    crate (i.e. no enabled features or enabled optional dependencies), and
    a dependency on "cargo".
    """

    normal = package.get_normal_dependencies(False)
    build = package.get_build_dependencies(False)

    deps = set()

    # dependency on cargo is mandatory
    deps.add("cargo")

    # minimum supported Rust version
    if msrv := package.rust_version:
        deps.add(f"rust >= {msrv}")

    # normal dependencies
    for dep in normal.values():
        if dep.uses_default_features:
            deps.add(dep.to_rpm("default"))
        else:
            deps.add(dep.to_rpm(None))
        for depf in dep.features:
            deps.add(dep.to_rpm(depf))

    # build-dependencies
    for dep in build.values():
        if dep.uses_default_features:
            deps.add(dep.to_rpm("default"))
        else:
            deps.add(dep.to_rpm(None))
        for depf in dep.features:
            deps.add(dep.to_rpm(depf))

    return deps


def _requires_feature(package: Package, feature: str) -> set[str]:
    """
    Resolves install-time dependencies of the given crate feature.

    This includes optional "normal" and "build-dependencies" of the
    crate that are specified as dependencies of the given feature, a
    dependency on the "main" crate package, and a dependency on "cargo".

    Raises an `InvalidFeatureError` if the given feature is not a feature
    of the crate.
    """

    if feature != "default" and feature not in package.get_feature_names():
        raise InvalidFeatureError(f"Unknown feature: {feature}")

    deps = set()

    # dependency on cargo is mandatory
    deps.add("cargo")

    if feature == "default" and "default" not in package.get_feature_names():
        # default feature is implicitly defined but empty
        deps.add(package.to_rpm_dependency(None))
        return deps

    feature_deps = package.features[feature]

    normal = package.get_normal_dependencies(False)
    normal_optional = package.get_normal_dependencies(True)
    build_optional = package.get_build_dependencies(True)

    # always add a dependency on the main crate
    deps.add(package.to_rpm_dependency(None))

    for fdep in feature_deps:
        if fdep.startswith("dep:"):
            # optional dependency
            name = fdep.removeprefix("dep:")

            found = False
            if dep := normal_optional.get(name):
                # optional normal dependency
                found = True
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

            if dep := build_optional.get(name):
                # optional build-dependency
                found = True
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

            if not found:  # pragma nocover
                raise InvalidFeatureError(f"No optional dependency found with name {name!r}.")

        elif "/" in fdep and "?/" not in fdep:
            # dependency with specified feature
            name, feat = fdep.split("/")

            # implicitly enabled optional dependency
            if dep := normal_optional.get(name):
                deps.add(dep.to_rpm(feat))
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

            if dep := build_optional.get(name):
                deps.add(dep.to_rpm(feat))
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

            # normal dependency
            if dep := normal.get(name):
                deps.add(dep.to_rpm(feat))

        elif "?/" in fdep:
            # conditionally enabled dependency feature
            name, feat = fdep.split("?/")

            if dep := normal_optional.get(name):
                deps.add(f"{dep.to_rpm(feat)}")
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

            if dep := build_optional.get(name):
                deps.add(f"{dep.to_rpm(feat)}")
                if dep.uses_default_features:
                    deps.add(dep.to_rpm("default"))
                else:
                    deps.add(dep.to_rpm(None))
                for depf in dep.features:
                    deps.add(dep.to_rpm(depf))

        else:
            # dependency on a feature of the current crate
            if fdep not in package.get_feature_names():  # pragma nocover
                raise InvalidFeatureError(f"Invalid feature dependency (not a feature name): {fdep!r}")

            deps.add(package.to_rpm_dependency(fdep))

    return deps


def requires(package: Package, feature: Optional[str]) -> set[str]:  # pragma nocover
    if feature is None:
        return _requires_crate(package)
    else:
        return _requires_feature(package, feature)


def _provides_crate(package: Package) -> str:
    """
    Returns the standardized identifier for the "main" crate subpackage
    (i.e. `crate(foo) = x.y.z`), which is used for the automatic generation of
    "virtual Provides".
    """

    rpm_version = Version.parse(package.version).to_rpm()
    return f"crate({package.name}) = {rpm_version}"


def _provides_feature(package: Package, feature: str) -> str:
    """
    Returns a standardized identifier for the "feature" crate subpackages
    (i.e. `crate(foo/bar) = x.y.z`), which is used for the automatic generation
    of "virtual Provides".
    """

    if feature != "default" and feature not in package.get_feature_names():
        raise InvalidFeatureError(f"Unknown feature: {feature}")

    rpm_version = Version.parse(package.version).to_rpm()
    return f"crate({package.name}/{feature}) = {rpm_version}"


def provides(package: Package, feature: Optional[str]) -> str:  # pragma nocover
    if feature is None:
        return _provides_crate(package)
    else:
        return _provides_feature(package, feature)
