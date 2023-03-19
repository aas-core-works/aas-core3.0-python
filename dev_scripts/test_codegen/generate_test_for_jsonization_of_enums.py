"""Generate the test code for the JSON de/serialization of enums."""

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
from aas_core_codegen.python.common import INDENT as I, INDENT2 as II, INDENT3 as III

import dev_scripts.test_codegen.common


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    this_path = pathlib.Path(os.path.realpath(__file__))

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    blocks = [
        warning,
        Stripped('"""Test JSON de/serialization of enumeration literals."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import unittest

import {aas_module}.jsonization as aas_jsonization"""
        ),
    ]  # type: List[Stripped]

    for our_type in symbol_table.our_types:
        if not isinstance(our_type, intermediate.Enumeration):
            continue

        enum_name = aas_core_codegen.python.naming.enum_name(our_type.name)

        assert (
            len(our_type.literals) > 0
        ), f"Unexpected enumeration without literals: {our_type.name}"

        literal_value = our_type.literals[0].value

        from_jsonable_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"{our_type.name}_from_jsonable")
        )

        blocks.append(
            Stripped(
                f"""\
class Test_{enum_name}(unittest.TestCase):
{I}def test_round_trip(self) -> None:
{II}jsonable = {aas_core_codegen.python.common.string_literal(literal_value)}

{II}enum_literal = aas_jsonization.{from_jsonable_name}(
{III}jsonable
{II})

{II}self.assertEqual(enum_literal.value, jsonable)"""
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
        dev_scripts.test_codegen.common.REPO_ROOT / "tests/test_jsonization_of_enums.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
