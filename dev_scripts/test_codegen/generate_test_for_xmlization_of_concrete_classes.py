"""Generate the test code for the de/serialization of instances in XML."""

import io
import os
import pathlib
import sys
import textwrap
from typing import List, Optional

import aas_core_codegen
import aas_core_codegen.common
import aas_core_codegen.python.naming
import aas_core_codegen.python.common
import aas_core_codegen.naming
import aas_core_codegen.parse
import aas_core_codegen.run
from aas_core_codegen import intermediate
from aas_core_codegen.common import Stripped
from aas_core_codegen.python.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
    INDENT4 as IIII,
    INDENT5 as IIIII,
)

import dev_scripts.test_codegen.common
import dev_scripts.test_codegen.test_data_io


def _generate_test_case(
    cls: intermediate.ConcreteClass,
    container_cls: intermediate.ConcreteClass,
    aas_module: aas_core_codegen.python.common.QualifiedModuleName,
) -> Stripped:
    """Generate the test class for a self-contained class."""
    xml_class_name_literal = aas_core_codegen.python.common.string_literal(
        aas_core_codegen.naming.xml_class_name(cls.name)
    )

    from_str = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_str")
    )

    from_iterparse = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_iterparse")
    )

    from_stream = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_stream")
    )

    from_file = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_file")
    )

    target_variable = "instance" if cls is container_cls else "container"

    cls_name = aas_core_codegen.python.naming.class_name(cls.name)

    # noinspection PyUnusedLocal
    container_kind = None  # type: Optional[Stripped]
    if cls is container_cls:
        container_kind = Stripped("SelfContained")
    elif container_cls.name == "Environment":
        container_kind = Stripped("ContainedInEnvironment")
    else:
        raise ValueError(f"Unexpected container class: {container_cls.name!r}")

    container_kind_literal = aas_core_codegen.python.common.string_literal(
        container_kind
    )

    methods = [
        Stripped(
            f"""\
def test_ok(self) -> None:
{I}paths = sorted(
{II}(
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "Xml"
{IIII}/ {container_kind_literal}
{IIII}/ "Expected"
{IIII}/ {xml_class_name_literal}
{II}).glob("**/*.xml")
{I})

{I}for path in paths:
{II}text = path.read_text(encoding='utf-8')

{II}try:
{III}{target_variable} = aas_xmlization.{from_str}(
{IIII}text
{III})
{II}except Exception as exception:  # pylint: disable=broad-except
{III}raise AssertionError(
{IIII}f"Unexpected exception when de-serializing: {{path}}"
{III}) from exception

{II}errors = list(aas_verification.verify({target_variable}))

{II}if len(errors) > 0:
{III}errors_joined = "\\n\\n".join(
{IIII}f"{{error.path}}: {{error.cause}}"
{IIII}for error in errors
{III})
{III}raise AssertionError(
{IIII}f"One or more unexpected errors from {{path}}:\\n{{errors_joined}}"
{III})

{II}writer = io.StringIO()
{II}aas_xmlization.write({target_variable}, writer)

{II}# Check the round-trip
{II}original = ET.fromstring(text)
{II}tests.common_xmlization.remove_redundant_whitespace(original)

{II}serialized = ET.fromstring(
{III}aas_xmlization.to_str({target_variable})
{II})
{II}tests.common_xmlization.remove_redundant_whitespace(serialized)

{II}tests.common_xmlization.assert_elements_equal(
{III}original, serialized, f"={{path}}"
{II})"""
        ),
        Stripped(
            f"""\
def test_deserialization_failures(self) -> None:
{I}for cause in _CAUSES_FOR_DESERIALIZATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Xml"
{III}/ {container_kind_literal}
{III}/ "Unexpected"
{III}/ cause
{III}/ {xml_class_name_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.xml")):
{III}observed_exception: Optional[
{IIII}aas_xmlization.DeserializationException
{III}] = None

{III}try:
{IIII}_ = aas_xmlization.{from_str}(
{IIIII}path.read_text(encoding='utf-8')
{IIII})
{III}except aas_xmlization.DeserializationException as exception:
{IIII}observed_exception = exception

{III}assert observed_exception is not None, (
{IIII}f"Expected an exception, but got none for: {{path}}"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".exception"),
{IIII}got=f"{{observed_exception.path}}: {{observed_exception.cause}}"
{III})"""
        ),
        Stripped(
            f"""\
def test_verification_failures(self) -> None:
{I}for cause in tests.common.CAUSES_FOR_VERIFICATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Xml"
{III}/ {container_kind_literal}
{III}/ "Unexpected"
{III}/ cause
{III}/ {xml_class_name_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.xml")):
{III}try:
{IIII}{target_variable} = aas_xmlization.{from_str}(
{IIIII}path.read_text(encoding='utf-8')
{IIII})
{III}except aas_xmlization.DeserializationException as exception:
{IIII}raise AssertionError(
{IIIII}f"Unexpected failure in deserialization from {{path}} "
{IIIII}f"at {{exception.path}}: {{exception.cause}}"
{IIII}) from exception

{III}errors = list(aas_verification.verify({target_variable}))

{III}self.assertGreater(
{IIII}len(errors),
{IIII}0,
{IIII}f"Expected verification errors from {{path}}, but got none"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".errors"),
{IIII}got="\\n".join(
{IIIII}f"{{error.path}}: {{error.cause}}"
{IIIII}for error in errors
{IIII})
{III})"""
        ),
        Stripped(
            f"""\
def test_different_input_forms_give_equal_outcomes(self) -> None:
{I}paths = sorted(
{II}(
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "Xml"
{IIII}/ {container_kind_literal}
{IIII}/ "Expected"
{IIII}/ {xml_class_name_literal}
{II}).glob("**/*.xml")
{I})

{I}for path in paths:
{II}with path.open('rt', encoding='utf-8') as fid:
{III}iterator = ET.iterparse(
{IIII}source=fid,
{IIII}events=['start', 'end']
{III})
{III}got_from_iterparse = (
{IIII}aas_xmlization.{from_iterparse}(
{IIIII}iterator
{IIII})
{III})

{II}with path.open('rt', encoding='utf-8') as fid:
{III}got_from_stream = (
{IIII}aas_xmlization.{from_stream}(
{IIIII}fid
{IIII})
{III})

{II}got_from_file = (
{III}aas_xmlization.{from_file}(
{IIII}path
{III})
{II})

{II}got_from_str = (
{III}aas_xmlization.{from_str}(
{IIII}path.read_text(encoding='utf-8')
{III})
{II})

{II}et_from_iterparse = ET.fromstring(
{III}aas_xmlization.to_str(
{IIII}got_from_iterparse
{III})
{II})
{II}tests.common_xmlization.remove_redundant_whitespace(
{III}et_from_iterparse
{II})

{II}et_from_stream = ET.fromstring(
{III}aas_xmlization.to_str(
{IIII}got_from_stream
{III})
{II})
{II}tests.common_xmlization.remove_redundant_whitespace(
{III}et_from_stream
{II})

{II}et_from_file = ET.fromstring(
{III}aas_xmlization.to_str(
{IIII}got_from_file
{III})
{II})
{II}tests.common_xmlization.remove_redundant_whitespace(
{III}et_from_file
{II})

{II}et_from_str = ET.fromstring(
{III}aas_xmlization.to_str(
{IIII}got_from_str
{III})
{II})
{II}tests.common_xmlization.remove_redundant_whitespace(
{III}et_from_str
{II})

{II}tests.common_xmlization.assert_elements_equal(
{III}et_from_iterparse, et_from_stream, f"={{path}}"
{II})

{II}tests.common_xmlization.assert_elements_equal(
{III}et_from_iterparse, et_from_file, f"={{path}}"
{II})

{II}tests.common_xmlization.assert_elements_equal(
{III}et_from_iterparse, et_from_str, f"={{path}}"
{II})"""
        ),
    ]

    writer = io.StringIO()
    writer.write(
        f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test XML de/serialization of the concrete class
{I}:py:class:`{aas_module}.types.{cls_name}`.
{I}\"\"\""""
    )

    for method in methods:
        writer.write("\n\n")
        writer.write(textwrap.indent(method, I))

    return Stripped(writer.getvalue())


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    this_path = pathlib.Path(os.path.realpath(__file__))

    test_data_dir = dev_scripts.test_codegen.common.REPO_ROOT / "test_data"

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    blocks = [
        warning,
        Stripped('"""Test JSON de/serialization of concrete classes."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import io
import xml.etree.ElementTree as ET
import unittest
from typing import Optional

import {aas_module}.xmlization as aas_xmlization
import {aas_module}.verification as aas_verification

import tests.common
import tests.common_xmlization"""
        ),
        Stripped(
            f"""\
_CAUSES_FOR_DESERIALIZATION_FAILURE = [
{I}"TypeViolation",
{I}"RequiredViolation",
{I}"EnumViolation",
{I}"UnexpectedAdditionalProperty",
]"""
        ),
    ]  # type: List[Stripped]

    environment_cls = symbol_table.must_find_concrete_class(
        aas_core_codegen.common.Identifier("Environment")
    )

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.ConcreteClass):
            continue

        container_cls = dev_scripts.test_codegen.test_data_io.determine_container_class(
            cls=our_type, test_data_dir=test_data_dir, environment_cls=environment_cls
        )

        blocks.append(
            _generate_test_case(
                cls=our_type, container_cls=container_cls, aas_module=aas_module
            )
        )

    blocks.append(
        Stripped(
            """\
if __name__ == "__main__":
    unittest.main()"""
        )
    )

    blocks.append(warning)

    writer = io.StringIO()
    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n\n")

        writer.write(block)

    writer.write("\n")

    target_pth = (
        dev_scripts.test_codegen.common.REPO_ROOT
        / "tests/test_xmlization_of_concrete_classes.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
