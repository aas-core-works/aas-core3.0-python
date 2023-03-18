"""Provide functionality used across the tests."""

import base64
import collections.abc
import difflib
import enum
import io
import os
import pathlib
import textwrap
from typing import Union, Sequence

import aas_core3.common as aas_common
import aas_core3.types as aas_types

_REPO_ROOT = pathlib.Path(os.path.realpath(__file__)).parent.parent

#: Path to the directory which contains input and golden files
TEST_DATA_DIR = _REPO_ROOT / "test_data"

#: If set, the golden files in the tests should be re-recorded instead
#: of checked against.
RECORD_MODE = os.environ.get("AAS_CORE3_0_PYTHON_TESTS_RECORD_MODE", "").lower() in (
    "1",
    "on",
    "true",
)

#: List of identifiers for verification failures (corresponding to subdirectory names
#: in the directory with test data)
CAUSES_FOR_VERIFICATION_FAILURE = [
    "DateTimeStampUtcViolationOnFebruary29th",
    "MaxLengthViolation",
    "MinLengthViolation",
    "PatternViolation",
    "InvalidValueExample",
    "InvalidMinMaxExample",
    "SetViolation",
    "ConstraintViolation",
]


def record_or_check(path: pathlib.Path, got: str) -> None:
    """
    Re-record or check that :paramref:`got` content matches the content of
    :paramref:`path`.

    If :py:attr:`~RECORD_MODE` is set, the content of :paramref:`path` will be
    simply overwritten with :paramref:`got` content, and no checks are performed.

    :param path: to the golden file
    :param got: obtained content
    :raise: :py:class:`AssertionError` if the contents do not match
    """
    if RECORD_MODE:
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(got, encoding="utf-8")
    else:
        if not path.exists():
            raise FileNotFoundError(
                f"The golden file could not be found: {path}; did you record it?"
            )

        expected = path.read_text(encoding="utf-8")
        if expected != got:
            writer = io.StringIO()

            diff = difflib.ndiff(
                expected.splitlines(keepends=True), got.splitlines(keepends=True)
            )

            diff_text = "".join(diff)
            writer.write(
                f"""\
The obtained content and the content of {path} do not match:
{diff_text}"""
            )

            raise AssertionError(writer.getvalue())


def trace(
    that: Union[
        bool,
        int,
        float,
        str,
        bytes,
        enum.Enum,
        aas_types.Class,
        Sequence[aas_types.Class],
    ]
) -> str:
    """
    Generate a segment in a trace of an iteration.

    :param that: to be traced
    :return: segment in the descent trace
    """
    if isinstance(that, aas_types.Class):
        if isinstance(that, aas_types.Identifiable):
            return f"{that.__class__.__name__} with ID {that.id}"
        elif isinstance(that, aas_types.Referable):
            return f"{that.__class__.__name__} with ID-short {that.id_short}"
        else:
            return that.__class__.__name__
    elif isinstance(that, (bool, int, float, str, enum.Enum)):
        return str(that)
    elif isinstance(that, bytes):
        return base64.b64encode(that).decode("ascii")
    elif isinstance(that, collections.abc.Sequence):
        if len(that) == 0:
            return "[]"
        writer = io.StringIO()
        writer.write("[\n")
        for i, item in enumerate(that):
            assert isinstance(item, aas_types.Class)

            writer.write(textwrap.indent(trace(item), "  "))

            if i < len(that) - 1:
                writer.write(",\n")
            else:
                writer.write("\n")

        writer.write("]")
        return writer.getvalue()
    else:
        aas_common.assert_never(that)


def trace_log_as_text_file_content(log: Sequence[str]) -> str:
    """
    Convert the trace log to a text to be stored in a file.

    :param log: to be converted to text
    :return: content of the file, including the new-line at the end
    """
    writer = io.StringIO()
    for entry in log:
        writer.write(f"{entry}\n")
    writer.write("\n")
    return writer.getvalue()
