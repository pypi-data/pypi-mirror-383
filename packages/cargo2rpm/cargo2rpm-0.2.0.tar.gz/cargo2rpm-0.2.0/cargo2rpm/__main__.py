import subprocess
import sys

from cargo2rpm.cli import get_args, get_feature_from_subpackage, get_cargo_toml_paths_from_stdin, get_cargo_vendor_txt_paths_from_stdin
from cargo2rpm.license import license_breakdown, license_summary
from cargo2rpm.metadata import Metadata, FeatureFlags
from cargo2rpm.rpm import buildrequires, workspace_buildrequires, requires, provides, InvalidFeatureError
from cargo2rpm.semver import Version


def break_the_build(error: str):
    """
    This function writes a string that is an invalid RPM dependency specifier,
    which causes dependency generators to fail and break the build. The
    additional error message is printed to stderr.
    """

    print("*** FATAL ERROR ***")
    print(error, file=sys.stderr)


def pretty_called_process_error(exc: subprocess.CalledProcessError) -> str:
    """
    This function extracts stdout and stderr from failed subprocesses and
    returns a string that contains both a representation of the exception
    (i.e. the command that failed and the non-zero return code) *and* the
    actual stdout and stderr.

    When `subprocess.CalledProcessError` exceptions are not caught, only the
    failed command and return code are printed, but stdout and stderr are lost.
    """

    try:
        return str(exc) + "\n" + exc.stdout.decode() + exc.stderr.decode()
    except UnicodeDecodeError:
        return str(exc) + "\n" + str(exc.stdout) + str(exc.stderr)


def feature_flags_from_args(args) -> FeatureFlags:
    features = args.features.split(",") if args.features else None
    return FeatureFlags(
        all_features=args.all_features,
        no_default_features=args.no_default_features,
        features=features,
    )


def action_buildrequires(args):
    metadata = Metadata.from_cargo(args.path)
    flags = feature_flags_from_args(args)

    if metadata.is_workspace():
        brs = workspace_buildrequires(metadata, flags, args.with_check)
    else:
        brs = buildrequires(metadata.packages[0], flags, args.with_check)

    for item in sorted(brs):
        print(item)


def action_requires(args):
    paths = {args.path} if args.path else get_cargo_toml_paths_from_stdin()

    for path in paths:
        metadata = Metadata.from_cargo(path)
        if metadata.is_workspace():
            print(f"Skipping generation of Requires for cargo workspace: {path}", file=sys.stderr)
            continue

        feature = get_feature_from_subpackage(args.feature) if args.subpackage else args.feature

        items = requires(metadata.packages[0], feature)
        for item in sorted(items):
            print(item)


def action_provides(args):
    paths = {args.path} if args.path else get_cargo_toml_paths_from_stdin()

    for path in paths:
        metadata = Metadata.from_cargo(path)
        if metadata.is_workspace():
            print(f"Skipping generation of Provides for cargo workspace: {path}", file=sys.stderr)
            continue

        feature = get_feature_from_subpackage(args.feature) if args.subpackage else args.feature

        print(provides(metadata.packages[0], feature))


def action_parse_vendor_manifest(args):
    paths = {args.path} if args.path else get_cargo_vendor_txt_paths_from_stdin()

    for path in paths:
        with open(path) as file:
            manifest = file.read()

        for line in manifest.strip().splitlines():
            crate, version = line.split(" v")
            print(f"bundled(crate({crate})) = {Version.parse(version).to_rpm()}")


def action_license_breakdown(args):
    flags = feature_flags_from_args(args)

    items = license_breakdown(flags, args.package)

    for item in sorted(items):
        print(item)


def action_license_summary(args):
    flags = feature_flags_from_args(args)

    items = license_summary(flags, args.package)

    print("### BEGIN LICENSE SUMMARY ###")
    for item in sorted(items):
        print(item)
    print("###  END LICENSE SUMMARY  ###")


def main():
    args = get_args()

    if args.action is None:
        print("No action specified.")
        exit(0)

    # check if path argument is present when required
    if not args.path and args.action in {"buildrequires", "name", "version", "is-lib", "is-bin"}:
        print("Missing '--path' argument.")
        exit(1)

    match args.action:
        case "buildrequires":
            try:
                action_buildrequires(args)
                exit(0)

            # print an error message that is not a valid RPM dependency
            # to cause the generator to break the build

            except subprocess.CalledProcessError as exc:
                # "cargo metadata" subprocess failed
                break_the_build(pretty_called_process_error(exc))
                exit(1)

            except AssertionError as exc:
                # errors because assumptions are not upheld
                break_the_build(str(exc))
                exit(1)

        case "requires":
            try:
                action_requires(args)
                exit(0)

            # print an error message that is not a valid RPM dependency
            # to cause the generator to break the build

            except subprocess.CalledProcessError as exc:
                # "cargo metadata" subprocess failed
                break_the_build(pretty_called_process_error(exc))
                exit(1)

            except InvalidFeatureError as exc:
                # dependency generator called for unknown feature name
                break_the_build(exc.error)
                exit(1)

            except AssertionError as exc:
                # errors because assumptions are not upheld
                break_the_build(str(exc))
                exit(1)

        case "provides":
            try:
                action_provides(args)
                exit(0)

            # print an error message that is not a valid RPM dependency
            # to cause the generator to break the build

            except subprocess.CalledProcessError as exc:
                # "cargo metadata" subprocess failed
                break_the_build(pretty_called_process_error(exc))
                exit(1)

            except InvalidFeatureError as exc:
                # dependency generator called for unknown feature name
                break_the_build(exc.error)
                exit(1)

            except AssertionError as exc:
                # errors because assumptions are not upheld
                break_the_build(str(exc))
                exit(1)

        case "parse-vendor-manifest":
            try:
                action_parse_vendor_manifest(args)
                exit(0)

            # print an error message that is not a valid RPM dependency
            # to cause the generator to break the build
            except (IOError, ValueError) as exc:
                break_the_build(str(exc))
                exit(1)

        case "license-breakdown":
            try:
                action_license_breakdown(args)
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "license-summary":
            try:
                action_license_summary(args)
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "name":
            try:
                metadata = Metadata.from_cargo(args.path)

                if metadata.is_workspace():
                    print("Cannot determine crate name from a cargo workspace.", file=sys.stderr)
                    # exit code 1 will fail package scriptlets
                    exit(1)

                print(metadata.packages[0].name)
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "version":
            try:
                metadata = Metadata.from_cargo(args.path)
                if metadata.is_workspace():
                    print("Cannot determine crate version from a cargo workspace.", file=sys.stderr)
                    # exit code 1 will fail package scriptlets
                    exit(1)

                print(metadata.packages[0].version)
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "is-lib":
            try:
                metadata = Metadata.from_cargo(args.path)
                if metadata.is_lib():
                    print("1", end="")
                else:
                    print("0", end="")
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "is-bin":
            try:
                metadata = Metadata.from_cargo(args.path)
                if metadata.is_bin():
                    print("1", end="")
                else:
                    print("0", end="")
                exit(0)

            except subprocess.CalledProcessError as exc:
                # catch the exception to ensure stdout and stderr are printed
                print(pretty_called_process_error(exc), file=sys.stderr)
                exit(1)

        case "semver2rpm":
            print(Version.parse(args.version).to_rpm())
            exit(0)

        case "rpm2semver":
            print(str(Version.from_rpm(args.version)))
            exit(0)

        case _:
            print("Unknown action.")
            exit(1)

    break_the_build("Uncaught exception: This should not happen, please report a bug.")
    exit(1)


if __name__ == "__main__":
    main()
