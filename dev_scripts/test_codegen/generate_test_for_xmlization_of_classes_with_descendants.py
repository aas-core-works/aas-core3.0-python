"""Generate the test code for the XML de/serialization of classes with descendants."""

import io
import os
import pathlib
import sys
import textwrap
from typing import List

import aas_core_codegen
import aas_core_codegen.common
import aas_core_codegen.naming
import aas_core_codegen.parse
import aas_core_codegen.python.common
import aas_core_codegen.python.naming
import aas_core_codegen.run
from aas_core_codegen import intermediate
from aas_core_codegen.common import Stripped
from aas_core_codegen.python.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
)

import dev_scripts.test_codegen.common


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    this_path = pathlib.Path(os.path.realpath(__file__))

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    blocks = [
        warning,
        Stripped('"""Test XML de/serialization of classes with descendants."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import io
import pathlib
import tempfile
import unittest
import xml.etree.ElementTree as ET

import {aas_module}.xmlization as aas_xmlization

import tests.common
import tests.common_jsonization
import tests.common_xmlization"""
        ),
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(
            our_type, (intermediate.AbstractClass, intermediate.ConcreteClass)
        ):
            continue

        if len(our_type.concrete_descendants) == 0:
            continue

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        test_methods = []  # type: List[Stripped]
        for descendant in our_type.concrete_descendants:
            load_concrete_maximal_name = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"load_maximal_{descendant.name}")
            )

            from_iterparse = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"{our_type.name}_from_iterparse")
            )

            from_stream = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"{our_type.name}_from_stream")
            )

            from_file = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"{our_type.name}_from_file")
            )

            from_str = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"{our_type.name}_from_str")
            )

            test_method_name = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"test_over_{descendant.name}")
            )

            test_methods.append(
                Stripped(
                    f"""\
def {test_method_name}(self) -> None:
{I}concrete_instance = (
{II}tests.common_jsonization.{load_concrete_maximal_name}()
{I})
{I}text = aas_xmlization.to_str(concrete_instance)
{I}et_concrete = ET.fromstring(text)

{I}# region From iterparse
{I}iterator = ET.iterparse(
{II}source=io.StringIO(text),
{II}events=['start', 'end']
{I})
{I}got_from_iterparse = (
{II}aas_xmlization.{from_iterparse}(
{III}iterator
{II})
{I})

{I}et_from_iterparse = (
{II}ET.fromstring(
{III}aas_xmlization.to_str(got_from_iterparse)
{II})
{I})
{I}tests.common_xmlization.remove_redundant_whitespace(
{II}et_from_iterparse
{I})
{I}tests.common_xmlization.assert_elements_equal(
{II}et_concrete, et_from_iterparse
{I})
{I}# endregion

{I}# region From stream
{I}got_from_stream = aas_xmlization.{from_stream}(
{II}io.StringIO(text)
{I})
{I}et_from_stream = (
{II}ET.fromstring(
{III}aas_xmlization.to_str(got_from_stream)
{II})
{I})
{I}tests.common_xmlization.remove_redundant_whitespace(
{II}et_from_stream
{I})
{I}tests.common_xmlization.assert_elements_equal(
{II}et_concrete, et_from_stream
{I})
{I}# endregion

{I}# region From file
{I}with tempfile.TemporaryDirectory() as tmp_dir:
{II}path = pathlib.Path(tmp_dir) / "something.xml"
{II}path.write_text(text, encoding='utf-8')

{II}got_from_file = aas_xmlization.{from_file}(
{III}path
{II})
{I}et_from_file = (
{II}ET.fromstring(
{III}aas_xmlization.to_str(got_from_file)
{II})
{I})
{I}tests.common_xmlization.remove_redundant_whitespace(
{II}et_from_file
{I})
{I}tests.common_xmlization.assert_elements_equal(
{II}et_concrete, et_from_file
{I})
{I}# endregion

{I}# region From string
{I}got_from_str = aas_xmlization.{from_str}(
{II}text
{I})
{I}et_from_str = (
{II}ET.fromstring(
{III}aas_xmlization.to_str(got_from_str)
{II})
{I})
{I}tests.common_xmlization.remove_redundant_whitespace(
{II}et_from_str
{I})
{I}tests.common_xmlization.assert_elements_equal(
{II}et_concrete, et_from_str
{I})
{I}# endregion"""
                )
            )

        class_writer = io.StringIO()
        class_writer.write(
            f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test round-trip XML de/serialization over concrete descendants
{I}of :py:class:`aas_types.{cls_name}`.
{I}\"\"\""""
        )

        for test_method in test_methods:
            class_writer.write("\n\n")
            class_writer.write(textwrap.indent(test_method, I))

        blocks.append(Stripped(class_writer.getvalue()))

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
        / "tests/test_xmlization_of_classes_with_descendants.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
