"""
This module is a partial Python port of the "semver" crate:
<https://docs.rs/semver>
"""

from enum import Enum
import itertools
import re
from typing import Optional


VERSION_REGEX = re.compile(
    r"""
    ^
    (?P<major>0|[1-9]\d*)
    \.(?P<minor>0|[1-9]\d*)
    \.(?P<patch>0|[1-9]\d*)
    (?:-(?P<pre>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
    (?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$
    """,
    re.VERBOSE,
)


VERSION_REQ_REGEX = re.compile(
    r"""
    ^
    (?P<op>=|>|>=|<|<=|~|\^)?
    (?P<major>0|[1-9]\d*)
    (\.(?P<minor>\*|0|[1-9]\d*))?
    (\.(?P<patch>\*|0|[1-9]\d*))?
    (-(?P<pre>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?
    $
    """,
    re.VERBOSE,
)


class PreRelease:
    """
    Pre-release part of a Version.
    """

    def __init__(self, parts: list[str | int]):
        self.parts: list[str | int] = parts

    @staticmethod
    def parse(prerelease: str) -> "PreRelease":
        parts: list[str | int] = [int(part) if part.isdecimal() else part for part in prerelease.split(".")]

        return PreRelease(parts)

    def __str__(self):
        return ".".join([str(part) for part in self.parts])

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        if not isinstance(other, PreRelease):
            return False  # pragma nocover

        return self.parts == other.parts

    def __lt__(self, other):
        """
        Algorithm for determining precedence between pre-releases based on the semver.org spec.
        """

        if not isinstance(other, PreRelease):
            return False  # pragma nocover

        for lpart, rpart in itertools.zip_longest(self.parts, other.parts):
            match lpart, rpart:
                # all previous parts were equal and the left pre-release has more parts
                case l, None:
                    return False

                # all previous parts were equal and the right pre-release has more parts
                case None, r:
                    return True

                # compare nonempty parts depending on value type
                case l, r:
                    match isinstance(l, int), isinstance(r, int):
                        # both parts are numbers: compare numerically
                        case True, True:
                            if l < r:
                                return True
                            elif l == r:
                                continue
                            else:
                                return False

                        # both parts are strings: compare lexicographically
                        case False, False:
                            if l < r:
                                return True
                            elif l == r:
                                continue
                            else:
                                return False

                        # number and string: string takes precedence
                        case True, False:
                            return True

                        # string and number: string takes precedence
                        case False, True:
                            return False

                        case _:  # pragma nocover
                            raise RuntimeError("Unreachable: This should never happen.")

                case _:  # pragma nocover
                    raise RuntimeError("Unreachable: This should never happen.")

        # both pre-releases have equal numbers of parts and all pairs of parts are equal
        else:
            return False

    def __le__(self, other):
        if not isinstance(other, PreRelease):
            return False  # pragma nocover

        return (self == other) or (self < other)

    def __gt__(self, other):
        if not isinstance(other, PreRelease):
            return False  # pragma nocover

        return other < self

    def __ge__(self, other):
        if not isinstance(other, PreRelease):
            return False  # pragma nocover

        return (self == other) or (self > other)


class Version:
    """
    Version that adheres to the "semantic versioning" format.
    """

    def __init__(self, major: int, minor: int, patch: int, pre: Optional[str] = None, build: Optional[str] = None):
        self.major: int = major
        self.minor: int = minor
        self.patch: int = patch
        self.pre: Optional[str] = pre
        self.build: Optional[str] = build

    @staticmethod
    def parse(version: str) -> "Version":
        """
        Parses a version string and return a `Version` object.
        Raises a `ValueError` if the string does not match the expected format.
        """

        match = VERSION_REGEX.match(version)
        if not match:
            raise ValueError(f"Invalid version: {version!r}")

        matches = match.groupdict()

        major_str = matches["major"]
        minor_str = matches["minor"]
        patch_str = matches["patch"]
        pre = matches["pre"]
        build = matches["build"]

        major = int(major_str)
        minor = int(minor_str)
        patch = int(patch_str)

        return Version(major, minor, patch, pre, build)

    def __str__(self):
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            s += f"-{self.pre}"
        if self.build:
            s += f"+{self.build}"
        return s

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        if not isinstance(other, Version):
            return False  # pragma nocover

        return (self.major == other.major) and (self.minor == other.minor) and (self.patch == other.patch) and (self.pre == other.pre)

    def __lt__(self, other):
        """
        Algorithm for determining precedence between versions based on the semver.org spec.
        """

        if not isinstance(other, Version):
            return False  # pragma nocover

        if self.major < other.major:
            return True
        if self.major > other.major:
            return False

        # major versions match
        if self.minor < other.minor:
            return True
        if self.minor > other.minor:
            return False

        # minor versions match
        if self.patch < other.patch:
            return True
        if self.patch > other.patch:
            return False

        # patch versions match
        match self.pre, other.pre:
            case None, None:
                return False
            case spre, None:
                return True
            case None, opre:
                return False
            case spre, opre:
                return PreRelease.parse(spre) < PreRelease.parse(opre)
            case _:  # pragma nocover
                raise RuntimeError("Unreachable: This should never happen.")

    def __le__(self, other):
        if not isinstance(other, Version):
            return False  # pragma nocover

        return (self == other) or (self < other)

    def __gt__(self, other):
        if not isinstance(other, Version):
            return False  # pragma nocover

        return other < self

    def __ge__(self, other):
        if not isinstance(other, Version):
            return False  # pragma nocover

        return (self == other) or (self > other)

    def to_rpm(self) -> str:
        """
        Formats the `Version` object as an equivalent RPM version string.
        Characters that are invalid in RPM versions are replaced ("-" -> "_")

        Build metadata (the optional `Version.build` attribute) is dropped, so
        the conversion is not lossless for versions where this attribute is not
        `None`. However, build metadata is not intended to be part of the
        version (and is not even considered when doing version comparison), so
        dropping it when converting to the RPM version format is correct.
        """

        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            s += f"~{self.pre.replace('-', '_')}"
        return s

    @staticmethod
    def from_rpm(version: str) -> "Version":
        """
        Parses an RPM version string and return the equivalent `Version`.
        Characters that are invalid in SemVer format are replaced ("_" -> "-").

        This method performs the inverse of `Version.to_rpm`.
        """

        return Version.parse(version.replace("~", "-").replace("_", "-"))


class Op(Enum):
    """
    Version requirement operator.

    This class enumerates all operators that are considered valid for specifying
    the required version of a dependency in cargo.
    """

    EXACT = "="
    GREATER = ">"
    GREATER_EQ = ">="
    LESS = "<"
    LESS_EQ = "<="
    TILDE = "~"
    CARET = "^"
    WILDCARD = "*"

    def __repr__(self):
        return self.value  # pragma nocover


class Comparator:
    """
    Partial version requirement.

    A `Comparator` consists of an operator (`Op`) and a (partial) semantic
    version and is used to define a requirement that a version can be matched
    against.
    """

    def __init__(self, op: Op, major: int, minor: Optional[int], patch: Optional[int], pre: Optional[str]):
        self.op: Op = op
        self.major: int = major
        self.minor: Optional[int] = minor
        self.patch: Optional[int] = patch
        self.pre: Optional[str] = pre

    def __str__(self):
        if self.op == Op.WILDCARD:
            if self.minor is not None:
                return f"{self.major}.{self.minor}.*"
            else:
                return f"{self.major}.*"

        op = self.op.value
        if self.pre is not None:
            return f"{op}{self.major}.{self.minor}.{self.patch}-{self.pre}"
        if self.patch is not None:
            return f"{op}{self.major}.{self.minor}.{self.patch}"
        if self.minor is not None:
            return f"{op}{self.major}.{self.minor}"
        return f"{op}{self.major}"

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        if not isinstance(other, Comparator):
            return False  # pragma nocover

        # naive equality check: does not take equivalence into account
        return (
            self.op == other.op
            and self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.pre == other.pre
        )

    def __contains__(self, item):
        if not isinstance(item, Version):
            return False  # pragma nocover

        match self.op:
            case Op.EXACT:
                return item == self._as_version()
            case Op.GREATER:
                return item > self._as_version()
            case Op.GREATER_EQ:
                return item >= self._as_version()
            case Op.LESS:
                return item < self._as_version()
            case Op.LESS_EQ:
                return item <= self._as_version()
            case Op.TILDE:
                return item in VersionReq(self.normalize())
            case Op.CARET:
                return item in VersionReq(self.normalize())
            case Op.WILDCARD:
                return item in VersionReq(self.normalize())
            case _:  # pragma nocover
                raise ValueError(f"Unknown operator: {self.op} (this should never happen)")

    def _as_version(self) -> Version:
        return Version(self.major, self.minor or 0, self.patch or 0, self.pre)

    @staticmethod
    def parse(comparator: str) -> "Comparator":
        """
        Parses a single version requirement string and return a `Comparator`.
        Raises a `ValueError` if the string does not match the expected format.
        """

        match = VERSION_REQ_REGEX.match(comparator)
        if not match:
            raise ValueError(f"Invalid version requirement: {comparator!r}")

        matches = match.groupdict()

        op_str = matches["op"]
        major_str = matches["major"]
        minor_str = matches["minor"]
        patch_str = matches["patch"]
        pre = matches["pre"]

        # if patch is present, minor needs to be present as well
        if minor_str is None and patch_str is not None:
            raise ValueError(f"Invalid version requirement: {comparator!r}")  # pragma nocover

        # if patch is not wildcard, then minor cannot be wildcard
        if minor_str is not None and patch_str is not None and minor_str == "*" and patch_str != "*":
            raise ValueError(f"Invalid wildcard requirement: {comparator!r}.")

        # if pre-release is specified, then minor and patch must be present
        if pre and (minor_str is None or patch_str is None):
            raise ValueError(f"Invalid pre-release requirement (minor / patch version missing): {comparator!r}")

        # normalize wildcard specifiers
        if minor_str is not None and minor_str == "*":
            op_str = "*"
            minor_str = None
        if patch_str is not None and patch_str == "*":
            op_str = "*"
            patch_str = None

        # fall back to default CARET ("^") operator if not specified
        op = Op(op_str) if op_str is not None else Op.CARET
        major = int(major_str)
        minor = int(minor_str) if minor_str is not None else None
        patch = int(patch_str) if patch_str is not None else None

        return Comparator(op, major, minor, patch, pre)

    def normalize(self) -> list["Comparator"]:
        """
        Normalizes this comparator into a list of equivalent comparators which
        only use the ">=", ">", "<", "<=", and "=" operators.

        This is based on the documentation of the semver crate, which is used
        by cargo: <https://docs.rs/semver/1.0.16/semver/enum.Op.html>

        This normalized version requirement can be formatted as a valid RPM
        dependency string. Other operators (i.e. "^", "~", and "*") are not
        supported by RPM.
        """

        comparators = []

        match self.op:
            case Op.EXACT:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, 0, 0, None))
                        comparators.append(Comparator(Op.LESS, self.major + 1, 0, 0, None))
                    case (minor, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, minor, 0, None))
                        comparators.append(Comparator(Op.LESS, self.major, minor + 1, 0, None))  # type: ignore
                    case (minor, patch):
                        comparators.append(Comparator(Op.EXACT, self.major, minor, patch, self.pre))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.GREATER:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major + 1, 0, 0, None))
                    case (minor, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, minor + 1, 0, None))  # type: ignore
                    case (minor, patch):
                        comparators.append(Comparator(Op.GREATER, self.major, minor, patch, self.pre))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.GREATER_EQ:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, 0, 0, None))
                    case (minor, None):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, minor, 0, None))
                    case (minor, patch):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, minor, patch, self.pre))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.LESS:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.append(Comparator(Op.LESS, self.major, 0, 0, None))
                    case (minor, None):
                        comparators.append(Comparator(Op.LESS, self.major, minor, 0, None))
                    case (minor, patch):
                        comparators.append(Comparator(Op.LESS, self.major, minor, patch, self.pre))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.LESS_EQ:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.append(Comparator(Op.LESS, self.major + 1, 0, 0, None))
                    case (minor, None):
                        comparators.append(Comparator(Op.LESS, self.major, minor + 1, 0, None))  # type: ignore
                    case (minor, patch):
                        comparators.append(Comparator(Op.LESS_EQ, self.major, minor, patch, self.pre))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.TILDE:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.extend(Comparator(Op.EXACT, self.major, None, None, None).normalize())
                    case (minor, None):
                        comparators.extend(Comparator(Op.EXACT, self.major, minor, None, None).normalize())
                    case (minor, patch):
                        comparators.append(Comparator(Op.GREATER_EQ, self.major, minor, patch, self.pre))
                        comparators.append(Comparator(Op.LESS, self.major, minor + 1, 0, None))  # type: ignore
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.CARET:
                match (self.major, self.minor, self.patch):
                    case (major, None, None):
                        comparators.extend(Comparator(Op.EXACT, major, None, None, None).normalize())
                    case (0, 0, None):
                        comparators.extend(Comparator(Op.EXACT, 0, 0, None, None).normalize())
                    case (major, minor, None):
                        comparators.extend(Comparator(Op.CARET, major, minor, 0, None).normalize())
                    case (0, 0, patch):
                        comparators.extend(Comparator(Op.EXACT, 0, 0, patch, self.pre).normalize())
                    case (0, minor, patch):
                        comparators.append(Comparator(Op.GREATER_EQ, 0, minor, patch, self.pre))
                        comparators.append(Comparator(Op.LESS, 0, minor + 1, 0, None))  # type: ignore
                    case (major, minor, patch):
                        comparators.append(Comparator(Op.GREATER_EQ, major, minor, patch, self.pre))
                        comparators.append(Comparator(Op.LESS, major + 1, 0, 0, None))
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case Op.WILDCARD:
                match (self.minor, self.patch):
                    case (None, None):
                        comparators.extend(Comparator(Op.EXACT, self.major, None, None, None).normalize())
                    case (minor, None):
                        comparators.extend(Comparator(Op.EXACT, self.major, minor, None, None).normalize())
                    case _:  # pragma nocover
                        raise RuntimeError("Unreachable: This should never happen.")

            case _:  # pragma nocover
                raise ValueError(f"Unknown operator: {self.op} (this should never happen)")

        return comparators

    def to_rpm(self, crate: str, feature: Optional[str]) -> str:
        """
        Formats the `Comparator` object as an equivalent RPM dependency.
        Raises a `ValueError` if the comparator cannot be converted into a valid
        RPM dependency (for example, if it was not normalized or uses an
        unsupported operator).
        """

        if self.normalize() != [self]:
            raise ValueError("Cannot format non-normalized comparators in RPM syntax.")  # pragma nocover

        if feature is None:
            feature_str = ""
        else:
            feature_str = f"/{feature}"

        version_str = f"{self.major}.{self.minor}.{self.patch}"

        if self.pre is None:
            pre_str = ""
            pre_str_less = "~"
        else:
            pre = self.pre.replace("-", "_")
            pre_str = f"~{pre}"
            pre_str_less = f"~{pre}"

        match self.op:
            case Op.EXACT:
                return f"crate({crate}{feature_str}) = {version_str}{pre_str}"
            case Op.GREATER:
                return f"crate({crate}{feature_str}) > {version_str}{pre_str}"
            case Op.GREATER_EQ:
                return f"crate({crate}{feature_str}) >= {version_str}{pre_str}"
            case Op.LESS:
                return f"crate({crate}{feature_str}) < {version_str}{pre_str_less}"
            case Op.LESS_EQ:
                return f"crate({crate}{feature_str}) <= {version_str}{pre_str}"
            case _:  # pragma nocover
                raise ValueError(f"Unsupported operator for RPM syntax formatting: {self.op}")


class VersionReq:
    """
    Version requirement.

    A `VersionReq` consists of a - possibly empty -list of a `Comparators`.

    An empty list represents the "no requirements" case (i.e. any version
    matches this requirement).

    For a version to match a version requirement with a non-empty list of
    comparators, it must match with all comparators in the list.
    """

    def __init__(self, comparators: list[Comparator]):
        self.comparators = comparators

    def __str__(self):
        if not self.comparators:
            return "*"

        return ",".join(str(comparator) for comparator in self.comparators)

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        if not isinstance(other, VersionReq):
            return False  # pragma nocover

        return self.comparators == other.comparators

    def __contains__(self, item):
        if not isinstance(item, Version):
            return False  # pragma nocover

        normalized = self.normalize().comparators
        return all(item in comparator for comparator in normalized)

    @staticmethod
    def parse(req: str) -> "VersionReq":
        """
        Parses a version requirement string and return a `VersionReq`.
        Raises a `ValueError` if the string does not match the expected format.
        """

        if not req:
            raise ValueError("Invalid version requirement (empty string).")

        if req == "*":
            return VersionReq([])

        reqs = req.replace(" ", "").split(",")
        comparators = [Comparator.parse(req) for req in reqs]

        return VersionReq(comparators)

    def normalize(self) -> "VersionReq":
        """
        Normalizes this version requirement into an equivalent requirement with
        comparators that only use ">=", ">", "<", "<=", and "=" operators.
        Other operators (i.e. "^", "~", and "*") are not supported by RPM.
        """

        comparators = []
        for comparator in self.comparators:
            comparators.extend(comparator.normalize())

        return VersionReq(comparators)

    def to_rpm(self, crate: str, feature: Optional[str]) -> str:
        """
        Formats the `VersionReq` object as an equivalent RPM dependency string.

        Raises a `ValueError` if the requirement cannot be converted into a
        valid RPM dependency - for example, if normalizing the comparators in
        this requirement results in a list of comparators with three or more
        items, which cannot easily be represented as RPM dependencies.
        """

        comparators = self.normalize().comparators

        if len(comparators) == 0:
            if feature is None:
                feature_str = ""
            else:
                feature_str = f"/{feature}"
            return f"crate({crate}{feature_str})"

        if len(comparators) == 1:
            return comparators[0].to_rpm(crate, feature)

        if len(comparators) == 2:
            return f"({comparators[0].to_rpm(crate, feature)} with {comparators[1].to_rpm(crate, feature)})"

        # len(comparators) > 2:
        raise ValueError("Using more than 2 comparators is not supported by RPM.")
