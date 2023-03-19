"""Generate the test code for the ``Descend`` methods and ``VisitorThrough``."""

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
import dev_scripts.test_codegen.test_data_io


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
        Stripped(
            f"""\
\"\"\"
Test jointly :py:method:`{aas_module}.types.Class.descend` and
:py:method:`{aas_module}.types.PassThroughVisitor`.
\"\"\""""
        ),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            f"""\
from typing import (
{I}List,
{I}Sequence,
)
import unittest

import {aas_module}.types as aas_types

import tests.common
import tests.common_jsonization"""
        ),
        Stripped(
            f"""\
class _TracingVisitor(aas_types.PassThroughVisitor):
{I}\"\"\"Visit the instances and trace them.\"\"\"

{I}def __init__(self) -> None:
{II}\"\"\"Initialize with an empty log.\"\"\"
{II}self._log = []  # type: List[str]

{I}@property
{I}def log(self) -> Sequence[str]:
{II}\"\"\"Get the tracing log.\"\"\"
{II}return self._log

{I}def visit(self, that: aas_types.Class) -> None:
{II}self._log.append(
{III}tests.common.trace(that)
{II})
{II}super().visit(that)"""
        ),
        Stripped(
            f"""\
def assert_tracing_logs_from_descend_and_visitor_are_the_same(
{II}that: aas_types.Class,
{II}test_case: unittest.TestCase
) -> None:
{I}\"\"\"
{I}Check that the tracing logs are the same when :paramref:`that` instance
{I}is visited and when :paramref:`that` is ran through
{I}:py:method:`aas_types.Class.descend`.

{I}:param that: instance to be iterated over
{I}:param test_case: in which this assertion runs
{I}:raise: :py:class:`AssertionError` if the logs differ
{I}\"\"\"
{I}log_from_descend = [
{II}tests.common.trace(something)
{II}for something in that.descend()
{I}]

{I}visitor = _TracingVisitor()
{I}visitor.visit(that)
{I}log_from_visitor = visitor.log

{I}test_case.assertGreater(len(log_from_visitor), 0)
{I}test_case.assertEqual(
{II}tests.common.trace(that),
{II}log_from_visitor[0]
{I})

{I}# noinspection PyTypeChecker
{I}test_case.assertListEqual(log_from_descend, log_from_visitor[1:])  # type: ignore"""
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
{I}def test_descend_against_recorded_trace_log(self) -> None:
{II}instance = tests.common_jsonization.{load_maximal_name}()
{II}expected_path = (
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "descend_and_pass_through_visitor"
{IIII}/ {model_type_literal}
{IIII}/ "maximal.json.trace"
{II})

{II}log = [
{III}tests.common.trace(something)
{III}for something in instance.descend()
{II}]
{II}got_text = tests.common.trace_log_as_text_file_content(log)
{II}tests.common.record_or_check(expected_path, got_text)

{I}def test_descend_against_visitor(self) -> None:
{II}instance = tests.common_jsonization.{load_maximal_name}()
{II}assert_tracing_logs_from_descend_and_visitor_are_the_same(
{III}instance,
{III}self
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
        / "tests/test_descend_and_pass_through_visitor.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
