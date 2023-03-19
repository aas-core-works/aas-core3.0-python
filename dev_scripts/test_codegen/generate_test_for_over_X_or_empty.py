"""Generate the test code for the ``OverXOrEmpty`` methods."""

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
import aas_core_codegen.run
from aas_core_codegen import intermediate
from aas_core_codegen.common import Stripped
from aas_core_codegen.python import naming as python_naming
from aas_core_codegen.python.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
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
        Stripped('"""Test ``over_X_or_empty`` methods."""'),
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

        test_case_methods = []  # type: List[Stripped]

        cls_name = python_naming.class_name(our_type.name)

        model_type_literal = aas_core_codegen.python.common.string_literal(
            aas_core_codegen.naming.json_model_type(our_type.name)
        )

        load_maximal_name = python_naming.function_name(
            aas_core_codegen.common.Identifier(f"load_maximal_{our_type.name}")
        )

        load_minimal_name = python_naming.function_name(
            aas_core_codegen.common.Identifier(f"load_minimal_{our_type.name}")
        )

        maximal_instance = dev_scripts.test_codegen.test_data_io.load_maximal(
            test_data_dir=test_data_dir, cls=our_type
        )

        minimal_instance = dev_scripts.test_codegen.test_data_io.load_minimal(
            test_data_dir=test_data_dir, cls=our_type
        )

        for prop in our_type.properties:
            if isinstance(
                prop.type_annotation, intermediate.OptionalTypeAnnotation
            ) and isinstance(
                prop.type_annotation.value, intermediate.ListTypeAnnotation
            ):
                over_x_or_empty_name = python_naming.method_name(
                    aas_core_codegen.common.Identifier(f"over_{prop.name}_or_empty")
                )

                test_case_method_name = python_naming.method_name(
                    aas_core_codegen.common.Identifier(
                        f"test_{over_x_or_empty_name}_"
                        f"on_maximal_instance_against_recorded"
                    )
                )

                prop_name = python_naming.property_name(prop.name)

                file_name = f"{over_x_or_empty_name}.trace"

                if getattr(maximal_instance, prop_name) is not None:
                    test_case_methods.append(
                        Stripped(
                            f"""\
def {test_case_method_name}(self) -> None:
{I}instance = tests.common_jsonization.{load_maximal_name}()
{I}expected_path = (
{III}tests.common.TEST_DATA_DIR
{III}/ "test_over_X_or_empty"
{III}/ {model_type_literal}
{III}/ "on_maximal.json"
{III}/ {aas_core_codegen.python.common.string_literal(file_name)}
{I})

{I}assert instance.{prop_name} is not None, (
{II}"Unexpected {prop_name} is None "
{II}"in the maximal example of "
{II}"{cls_name}"
{I})

{I}log = [
{II}tests.common.trace(
{III}list(instance.{over_x_or_empty_name}())
{II})
{I}]
{I}got_text = tests.common.trace_log_as_text_file_content(log)
{I}tests.common.record_or_check(expected_path, got_text)"""
                        )
                    )
                else:
                    test_case_methods.append(
                        Stripped(
                            f"""\
# The maximal example of {cls_name} contains no {prop_name},
# so we can not generate the corresponding test case
# {test_case_method_name}."""
                        )
                    )

                test_case_method_name = python_naming.method_name(
                    aas_core_codegen.common.Identifier(
                        f"test_{over_x_or_empty_name}_"
                        f"on_minimal_instance_against_recorded"
                    )
                )

                if not getattr(minimal_instance, prop_name) is not None:
                    test_case_methods.append(
                        Stripped(
                            f"""\
def {test_case_method_name}(self) -> None:
{I}instance = tests.common_jsonization.{load_minimal_name}()
{I}expected_path = (
{III}tests.common.TEST_DATA_DIR
{III}/ "test_over_X_or_empty"
{III}/ {model_type_literal}
{III}/ "on_minimal.json"
{III}/ {aas_core_codegen.python.common.string_literal(file_name)}
{I})

{I}assert instance.{prop_name} is None, (
{II}"Unexpected {prop_name} not None "
{II}"in the minimal example of "
{II}"{cls_name}"
{I})

{I}log = [
{II}tests.common.trace(
{III}list(instance.{over_x_or_empty_name}())
{II})
{I}]
{I}got_text = tests.common.trace_log_as_text_file_content(log)
{I}tests.common.record_or_check(expected_path, got_text)"""
                        )
                    )
                else:
                    test_case_methods.append(
                        Stripped(
                            f"""\
# The minimal example of {cls_name} contains no {prop_name},
# so we can not generate the corresponding test case
# {test_case_method_name}."""
                        )
                    )

        if len(test_case_methods) > 0:
            class_writer = io.StringIO()
            class_writer.write(
                f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test ``over_X_or_default`` on instances of
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
        dev_scripts.test_codegen.common.REPO_ROOT / "tests/test_over_x_or_empty.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
