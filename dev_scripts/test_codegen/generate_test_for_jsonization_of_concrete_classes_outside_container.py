"""Generate the test code for the jsonization of classes outside a container."""

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
    INDENT5 as IIIII,
)

import dev_scripts.test_codegen.common
import dev_scripts.test_codegen.test_data_io


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    aas_module = dev_scripts.test_codegen.common.AAS_MODULE

    this_path = pathlib.Path(os.path.realpath(__file__))

    test_data_dir = dev_scripts.test_codegen.common.REPO_ROOT / "test_data"

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    blocks = [
        warning,
        Stripped(
            '"""Test de/serialization from JSON of concrete classes '
            'outside a container."""'
        ),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
import unittest

import {aas_module}.jsonization as aas_jsonization

import tests.common
import tests.common_jsonization"""
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
            # NOTE (mristin, 2022-10-23):
            # These classes are tested already in
            # :py:module:`tests.test_jsonization_of_concrete_classes`. We only need to
            # test here for class instances contained in a container.
            continue

        cls_name = aas_core_codegen.python.naming.class_name(our_type.name)

        load_maximal_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"load_maximal_{our_type.name}")
        )

        from_jsonable_name = aas_core_codegen.python.naming.function_name(
            aas_core_codegen.common.Identifier(f"{our_type.name}_from_jsonable")
        )

        blocks.append(
            Stripped(
                f"""\
class Test_{cls_name}(unittest.TestCase):
{I}def test_round_trip(self) -> None:
{II}instance = tests.common_jsonization.{load_maximal_name}()

{II}jsonable = aas_jsonization.to_jsonable(instance)

{II}another_instance = aas_jsonization.{from_jsonable_name}(
{III}jsonable
{II})

{II}another_jsonable = aas_jsonization.to_jsonable(another_instance)

{II}# Check the round-trip
{II}self.assertListEqual(
{III}[],
{III}list(
{IIII}map(
{IIIII}str,
{IIIII}tests.common_jsonization.check_equal(jsonable, another_jsonable)
{IIII})
{III})
{II})"""
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
        / "tests/test_jsonization_of_concrete_classes_outside_container.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
