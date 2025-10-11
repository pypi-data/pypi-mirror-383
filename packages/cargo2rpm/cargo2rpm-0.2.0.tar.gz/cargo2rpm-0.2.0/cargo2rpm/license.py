import os
import subprocess
from typing import Optional

from cargo2rpm import CARGO
from cargo2rpm.metadata import FeatureFlags


def license_breakdown(flags: FeatureFlags, package: Optional[str] = None) -> set[str]:
    cmd = [
        CARGO,
        "tree",
        "-Zavoid-dev-deps",
        "--package={package}" if package else "--workspace",
        "--offline",
        "--edges=no-build,no-dev,no-proc-macro",
        "--no-dedupe",
        "--target=all",
        "--prefix=none",
        "--format",
        "{l}: {p}",
    ]
    if flags.all_features:
        cmd.append("--all-features")
    if flags.no_default_features:
        cmd.append("--no-default-features")
    if flags.features:
        cmd.append("--features={}".format(",".join(flags.features)))

    ret = subprocess.run(cmd, capture_output=True)
    ret.check_returncode()

    cwd = os.getcwd()
    lines = ret.stdout.decode().splitlines()
    items = {line.replace(f" ({cwd})", "").replace(" / ", "/").replace("/", " OR ") for line in lines}

    return items


def license_summary(flags: FeatureFlags, package: Optional[str] = None) -> set[str]:
    cmd = [
        CARGO,
        "tree",
        "-Zavoid-dev-deps",
        "--package={package}" if package else "--workspace",
        "--offline",
        "--edges=no-build,no-dev,no-proc-macro",
        "--no-dedupe",
        "--target=all",
        "--prefix=none",
        "--format",
        "# {l}",
    ]
    if flags.all_features:
        cmd.append("--all-features")
    if flags.no_default_features:
        cmd.append("--no-default-features")
    if flags.features:
        cmd.append("--features={}".format(",".join(flags.features)))

    ret = subprocess.run(cmd, capture_output=True)
    ret.check_returncode()

    lines = ret.stdout.decode().splitlines()
    items = {line.replace(" / ", "/").replace("/", " OR ") for line in lines}

    return items
