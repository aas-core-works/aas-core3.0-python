"""Generate the test code for the JSON de/serialization of classes with descendants."""

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
    INDENT4 as IIII,
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
        Stripped('"""Test JSON de/serialization of classes with descendants."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import unittest

import {aas_module}.jsonization as aas_jsonization

import tests.common
import tests.common_jsonization"""
        ),
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(
            our_type, (intermediate.AbstractClass, intermediate.ConcreteClass)
        ):
            continue

        if len(our_type.concrete_descendants) == 0:
            continue

        # NOTE (mristin, 2022-10-23):
        # There are indeed classes who have concrete descendants, but don't indicate
        # the model type in the serialization as there are no properties referring to
        # the *abstract* class, but only properties referring to the concrete
        # descendants. Therefore, we need to skip testing for abstract classes without
        # the model type as we would not know how to de-serialize the instances.
        if not our_type.serialization.with_model_type:
            continue

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        test_methods = []  # type: List[Stripped]
        for descendant in our_type.concrete_descendants:
            load_concrete_maximal_name = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"load_maximal_{descendant.name}")
            )

            abstract_from_jsonable_name = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"{our_type.name}_from_jsonable")
            )

            test_method_name = aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(
                    f"test_round_trip_over_{descendant.name}"
                )
            )

            test_methods.append(
                Stripped(
                    f"""\
def {test_method_name}(self) -> None:
{I}concrete_instance = (
{II}tests.common_jsonization.{load_concrete_maximal_name}()
{I})
{I}jsonable = aas_jsonization.to_jsonable(concrete_instance)

{I}abstract_instance = aas_jsonization.{abstract_from_jsonable_name}(
{II}jsonable
{I})
{I}another_jsonable = aas_jsonization.to_jsonable(abstract_instance)

{I}self.assertListEqual(
{II}[],
{II}list(
{III}map(
{IIII}str,
{IIII}tests.common_jsonization.check_equal(jsonable, another_jsonable)
{III})
{II})
{I})"""
                )
            )

        class_writer = io.StringIO()
        class_writer.write(
            f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test round-trip JSON de/serialization over concrete descendants
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
        / "tests/test_jsonization_of_classes_with_descendants.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
