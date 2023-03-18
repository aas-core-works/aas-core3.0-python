"""Provide common functionality for XML de-serialization."""
import io
import xml.etree.ElementTree as ET
import sys
from typing import Iterator, Optional

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import aas_core3.xmlization as aas_xmlization


class Difference:
    """Represent a single difference between two XML documents."""

    #: Human-readable description of the difference
    message: Final[str]

    #: Path to the expected XML element which is different from
    #: the obtained XML element
    path: Final[aas_xmlization.Path]

    def __init__(self, message: str) -> None:
        """Initialize with the given message and empty path."""
        self.message = message
        self.path = aas_xmlization.Path()

    def __str__(self) -> str:
        return f"#{self.path}: {self.message}"


def remove_redundant_whitespace(element: ET.Element) -> None:
    """
    Remove the whitespace which will be ignored in the XML parsing.

    :param element: to remove the whitespace from
    """
    if len(element) > 0:
        if element.text is not None and len(element.text.strip()) == 0:
            element.text = None

        for child in element:
            if child.tail is not None and len(child.tail.strip()) == 0:
                child.tail = None

            remove_redundant_whitespace(child)


def check_equal(
    expected: ET.Element,
    got: ET.Element,
) -> Iterator[Difference]:
    """
    Compare recursively two XML elements for equality.

    Make sure you called :py:function:`.remove_redundant_whitespace`
    so that your comparison does not trip over trivial whitespace.

    :param expected: expected XML element
    :param got: obtained XML element
    :yield: differences
    """
    # NOTE (mristin, 2022-10-23):
    # We need to ignore the white-space before the children as it is ignored
    # by the XML parser.

    stop_recursion = False
    if expected.text is not None and got.text is None:
        stop_recursion = True
        yield Difference(f"Expected text {expected.text!r}, but got none")

    if expected.text is None and got.text is not None:
        stop_recursion = True
        yield Difference(f"Expected no text, but got {got.text!r}")

    if expected.tail is not None and got.tail is None:
        stop_recursion = True
        yield Difference(f"Expected tail {expected.tail!r}, but got none")

    if expected.tail is None and got.tail is not None:
        stop_recursion = True
        yield Difference(f"Expected no tail, but got {got.tail!r}")

    if expected.text is not None and got.text is not None and expected.text != got.text:
        stop_recursion = True
        yield Difference(f"Expected text {expected.text!r}, but got {got.text!r}")

    if expected.tail is not None and got.tail is not None and expected.tail != got.tail:
        stop_recursion = True
        yield Difference(f"Expected tail {expected.tail!r}, but got {got.tail!r}")

    if expected.tag != got.tag:
        stop_recursion = True
        yield Difference(f"Expected tail {expected.tag!r}, but got {got.tag!r}")

    expected_children = [  # pylint: disable=unnecessary-comprehension
        child for child in expected
    ]

    got_children = [child for child in got]  # pylint: disable=unnecessary-comprehension

    if len(expected_children) != len(got_children):
        stop_recursion = True
        yield Difference(
            f"Expected {len(expected_children)} child element(s), "
            f"but got {len(got_children)} child element(s)"
        )

    children_tag_unique = len(set(child.tag for child in expected_children)) == len(
        expected_children
    )

    if stop_recursion:
        return

    for i, (expected_child, got_child) in enumerate(
        zip(expected_children, got_children)
    ):
        for difference in check_equal(expected_child, got_child):
            if children_tag_unique:
                difference.path._prepend(aas_xmlization.ElementSegment(expected_child))
            else:
                difference.path._prepend(aas_xmlization.IndexSegment(expected_child, i))

            yield difference


def assert_elements_equal(
    expected: ET.Element, got: ET.Element, message_if_not_equal: Optional[str] = None
) -> None:
    """
    Assert that the two elements are equal.

    Make sure you called :py:function:`.remove_redundant_whitespace`
    so that your comparison does not trip over trivial whitespace.

    :param expected: what you expected
    :param got: what you got
    :param message_if_not_equal: description or identifier to help debugging
    :raise: :py:class:`AssertionError` if the two elements are not equal
    """
    findings_text = "\n".join(
        str(difference) for difference in check_equal(expected=expected, got=got)
    )

    if len(findings_text) != 0:
        writer = io.StringIO()
        writer.write(
            f"Expected two elements to be equal, but they are not. "
            f"Differences related to the expected element:\n"
            f"{findings_text}"
        )

        if message_if_not_equal is not None:
            writer.write("\n\n")
            writer.write(message_if_not_equal)

        raise AssertionError(writer.getvalue())
