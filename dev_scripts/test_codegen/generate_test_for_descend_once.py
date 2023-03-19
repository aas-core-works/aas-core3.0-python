"""Generate the test code for the ``DescendOnce`` methods."""

import io
import os
import pathlib
import sys
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

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    this_path = pathlib.Path(os.path.realpath(__file__))

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    # noinspection PyListCreation
    blocks = [
        warning,
        Stripped(f'"""Test :py:method:`{aas_module}.types.Class.descend_once`."""'),
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

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        model_type_literal = aas_core_codegen.python.common.string_literal(
            aas_core_codegen.naming.json_model_type(our_type.name)
        )

        load_maximal_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"load_maximal_{our_type.name}")
        )

        blocks.append(
            Stripped(
                f"""\
class Test_{cls_name}(unittest.TestCase):
{I}def test_descend_once_against_recorded_trace_log(self) -> None:
{II}instance = tests.common_jsonization.{load_maximal_name}()
{II}expected_path = (
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "descend_once"
{IIII}/ {model_type_literal}
{IIII}/ "maximal.json.trace"
{II})

{II}log = [
{III}tests.common.trace(something)
{III}for something in instance.descend_once()
{II}]
{II}got_text = tests.common.trace_log_as_text_file_content(log)
{II}tests.common.record_or_check(expected_path, got_text)"""
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
        dev_scripts.test_codegen.common.REPO_ROOT / "tests/test_descend_once.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
