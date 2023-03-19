"""Generate the test code for the xmlization of classes outside a container."""

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
)

import dev_scripts.test_codegen.common
import dev_scripts.test_codegen.test_data_io


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
        Stripped(
            '"""Test de/serialization from XML of concrete classes '
            'outside a container."""'
        ),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import unittest
import xml.etree.ElementTree as ET

import {aas_module}.xmlization as aas_xmlization
import {aas_module}.verification as aas_verification

import tests.common
import tests.common_jsonization
import tests.common_xmlization"""
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

        if container_cls is our_type:
            # NOTE (mristin, 2022-06-27):
            # These classes are tested already in
            # ``test_xmlization_of_concrete_classes``. We only need to test for class
            # instances contained in a container.
            continue

        assert container_cls is environment_cls

        load_maximal_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"load_maximal_{our_type.name}")
        )

        from_str = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"{our_type.name}_from_str")
        )

        methods = [
            Stripped(
                f"""\
def test_ok(self) -> None:
{I}instance = tests.common_jsonization.{load_maximal_name}()
{I}text = aas_xmlization.to_str(instance)

{I}another_instance = aas_xmlization.{from_str}(
{II}text
{I})

{I}errors = list(aas_verification.verify(another_instance))
{I}self.assertListEqual([], errors)

{I}et_instance = ET.fromstring(text)
{I}tests.common_xmlization.remove_redundant_whitespace(et_instance)

{I}et_another_instance = ET.fromstring(
{II}aas_xmlization.to_str(another_instance)
{I})
{I}tests.common_xmlization.remove_redundant_whitespace(et_another_instance)

{I}tests.common_xmlization.assert_elements_equal(
{II}et_instance, et_another_instance
{I})"""
            )
        ]  # type: List[Stripped]

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        class_writer = io.StringIO()
        class_writer.write(
            f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test XML de/serialization of the concrete class
{I}:py:class:`{aas_module}.types.{cls_name}` outside a container.
{I}\"\"\""""
        )

        for method in methods:
            class_writer.write("\n\n")
            class_writer.write(textwrap.indent(method, I))

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
        / "tests/test_xmlization_of_concrete_classes_outside_container.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
