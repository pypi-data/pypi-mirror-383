import importlib.resources

from cargo2rpm.metadata import Metadata


def load_metadata_from_resource(filename: str) -> Metadata:
    """
    Utility function for locating and loading test data (i.e. the JSON dump from
    `cargo metadata`) as identified by its file name, and parse it into a
    `Metadata` object.
    """

    data = importlib.resources.files("cargo2rpm.testdata").joinpath(filename).read_text()
    return Metadata.from_json(data)


def short_repr(obj) -> str:
    """
    Utility function for returning a truncated `repr` of the object that was
    passed as an argument. Used for identifying test cases in parametrized
    `pytest` tests.
    """

    s = repr(obj)
    if len(s) >= 22:
        return s[0:22] + ".."
    else:
        return s
