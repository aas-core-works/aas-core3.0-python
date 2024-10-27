"""Test general XML de-serialization of a type given by the start element."""

# pylint: disable=missing-docstring

import io
import unittest
import xml.etree.ElementTree as ET


import aas_core3.xmlization as aas_xmlization
import aas_core3.verification as aas_verification

import tests.common
import tests.common_xmlization


class TestGeneral(unittest.TestCase):
    def test_ok(self) -> None:
        paths = sorted((tests.common.TEST_DATA_DIR / "Xml").glob("*/Expected/**/*.xml"))

        for path in paths:
            text = path.read_text(encoding="utf-8")

            try:
                instance = aas_xmlization.from_file(path)
            except Exception as exception:  # pylint: disable=broad-except
                raise AssertionError(
                    f"Unexpected exception when de-serializing: {path}"
                ) from exception

            errors = list(aas_verification.verify(instance))

            if len(errors) > 0:
                errors_joined = "\n\n".join(
                    f"{error.path}: {error.cause}" for error in errors
                )
                raise AssertionError(
                    f"One or more unexpected errors from {path}:\n{errors_joined}"
                )

            writer = io.StringIO()
            aas_xmlization.write(instance, writer)

            # Check the round-trip
            original = ET.fromstring(text)
            tests.common_xmlization.remove_redundant_whitespace(original)

            serialized = ET.fromstring(aas_xmlization.to_str(instance))
            tests.common_xmlization.remove_redundant_whitespace(serialized)

            tests.common_xmlization.assert_elements_equal(
                original, serialized, f"={path}"
            )


if __name__ == "__main__":
    unittest.main()
