"""Generate the test code for the ``XOrDefault`` methods."""

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
from aas_core_codegen.python.common import INDENT as I, INDENT3 as III

import dev_scripts.test_codegen.common


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    this_path = pathlib.Path(os.path.realpath(__file__))

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    # noinspection PyListCreation
    blocks = [
        warning,
        Stripped('"""Test ``X_or_default`` methods on classes which contain lists."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            """\
import unittest

import tests.common
import tests.common_jsonization"""
        ),
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.ConcreteClass):
            continue

        x_or_default_methods = []  # type: List[intermediate.Method]
        for method in our_type.methods:
            if method.name.endswith("_or_default"):
                x_or_default_methods.append(method)

        if len(x_or_default_methods) == 0:
            continue

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        model_type_literal = aas_core_codegen.python.common.string_literal(
            aas_core_codegen.naming.json_model_type(our_type.name)
        )

        load_maximal_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"load_maximal_{our_type.name}")
        )

        load_minimal_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"load_minimal_{our_type.name}")
        )

        test_case_methods = []  # type: List[Stripped]

        for x_or_default_method in x_or_default_methods:
            assert x_or_default_method.returns is not None, (
                f"Expected all X_or_default to return something, "
                f"but got None for {our_type}.{x_or_default_method.name}"
            )

            test_case_method_name = aas_core_codegen.python.naming.method_name(
                aas_core_codegen.common.Identifier(
                    f"test_{x_or_default_method.name}_"
                    f"on_maximal_instance_against_recorded"
                )
            )

            x_or_default_name = aas_core_codegen.python.naming.method_name(
                x_or_default_method.name
            )

            file_name = f"{x_or_default_name}.trace"

            test_case_methods.append(
                Stripped(
                    f"""\
def {test_case_method_name}(self) -> None:
{I}instance = tests.common_jsonization.{load_maximal_name}()
{I}expected_path = (
{III}tests.common.TEST_DATA_DIR
{III}/ "test_X_or_default"
{III}/ {model_type_literal}
{III}/ "on_maximal.json"
{III}/ {aas_core_codegen.python.common.string_literal(file_name)}
{I})

{I}log = [tests.common.trace(instance.{x_or_default_name}())]
{I}got_text = tests.common.trace_log_as_text_file_content(log)
{I}tests.common.record_or_check(expected_path, got_text)"""
                )
            )

            test_case_method_name = aas_core_codegen.python.naming.method_name(
                aas_core_codegen.common.Identifier(
                    f"test_{x_or_default_method.name}_"
                    f"on_minimal_instance_against_recorded"
                )
            )

            test_case_methods.append(
                Stripped(
                    f"""\
def {test_case_method_name}(self) -> None:
{I}instance = tests.common_jsonization.{load_minimal_name}()
{I}expected_path = (
{III}tests.common.TEST_DATA_DIR
{III}/ "test_X_or_default"
{III}/ {model_type_literal}
{III}/ "on_minimal.json"
{III}/ {aas_core_codegen.python.common.string_literal(file_name)}
{I})

{I}log = [tests.common.trace(instance.{x_or_default_name}())]
{I}got_text = tests.common.trace_log_as_text_file_content(log)
{I}tests.common.record_or_check(expected_path, got_text)"""
                )
            )

        class_writer = io.StringIO()
        class_writer.write(
            f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test ``X_or_default`` on instances of
{I}:py:class:`{aas_module}.types.{cls_name}`.
{I}\"\"\""""
        )

        for test_case_method in test_case_methods:
            class_writer.write("\n\n")
            class_writer.write(textwrap.indent(test_case_method, I))

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
        dev_scripts.test_codegen.common.REPO_ROOT / "tests/test_x_or_default.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
