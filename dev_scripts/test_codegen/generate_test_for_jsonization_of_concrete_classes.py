"""Generate the test code for the JSON de/serialization of classes."""

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
import aas_core_codegen.python.naming
import aas_core_codegen.python.common
from aas_core_codegen.python.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
    INDENT4 as IIII,
    INDENT5 as IIIII,
)
from icontract import require

import dev_scripts.test_codegen.common
import dev_scripts.test_codegen.test_data_io


def _generate_for_self_contained(
    cls: intermediate.ConcreteClass,
    aas_module: aas_core_codegen.python.common.QualifiedModuleName,
) -> Stripped:
    """Generate the test class for a self-contained class."""
    # noinspection PyListCreation
    cls_name_json = aas_core_codegen.naming.json_model_type(cls.name)

    cls_name_json_literal = aas_core_codegen.python.common.string_literal(cls_name_json)

    deserialization_function = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{cls.name}_from_jsonable")
    )

    cls_name = aas_core_codegen.python.naming.class_name(cls.name)

    methods = [
        Stripped(
            f"""\
def test_ok(self) -> None:
{I}paths = sorted(
{II}(
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "Json"
{IIII}/ "SelfContained"
{IIII}/ "Expected"
{IIII}/ {cls_name_json_literal}
{II}).glob("**/*.json")
{I})

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}instance = aas_jsonization.{deserialization_function}(jsonable)

{II}errors = list(aas_verification.verify(instance))

{II}self.assertListEqual([], errors, f"path is: {{path}}")

{II}# Check the round-trip
{II}another_jsonable = aas_jsonization.to_jsonable(instance)
{II}self.assertListEqual(
{III}[],
{III}list(
{IIII}map(
{IIIII}str,
{IIIII}tests.common_jsonization.check_equal(jsonable, another_jsonable)
{IIII})
{III})
{II})"""
        ),
        Stripped(
            f"""\
def test_that_deserialization_from_non_object_fails(self) -> None:
{I}jsonable = "not an object"

{I}observed_exception: Optional[
{II}aas_jsonization.DeserializationException
{I}] = None

{I}try:
{II}aas_jsonization.{deserialization_function}(jsonable)
{I}except aas_jsonization.DeserializationException as exception:
{II}observed_exception = exception

{I}assert observed_exception is not None
{I}self.assertEqual(
{II}"Expected a mapping, but got: <class 'str'>",
{II}observed_exception.cause
{I})

{I}self.assertEqual("", str(observed_exception.path))"""
        ),
        Stripped(
            f"""\
def test_deserialization_failures(self) -> None:
{I}unserializable_dir = (
{II}tests.common.TEST_DATA_DIR
{II}/ "Json"
{II}/ "SelfContained"
{II}/ "Unexpected"
{II}/ "Unserializable"
{I})

{I}# The first ``*`` corresponds to the cause.
{I}glob_pattern = "*/{cls_name_json}/**/*.json"

{I}paths = sorted(unserializable_dir.glob(glob_pattern))

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}observed_exception: Optional[
{III}aas_jsonization.DeserializationException
{II}] = None

{II}try:
{III}_ = aas_jsonization.{deserialization_function}(jsonable)
{II}except aas_jsonization.DeserializationException as exception:
{III}observed_exception = exception

{II}assert observed_exception is not None, (
{III}f"Expected an exception, but got none for: {{path}}"
{II})

{II}tests.common.record_or_check(
{III}path=path.parent / (path.name + ".exception"),
{III}got=f"{{observed_exception.path}}: {{observed_exception.cause}}"
{II})"""
        ),
        Stripped(
            f"""\
def test_verification_failures(self) -> None:
{I}invalid_dir = (
{II}tests.common.TEST_DATA_DIR
{II}/ "Json"
{II}/ "SelfContained"
{II}/ "Unexpected"
{II}/ "Invalid"
{I})

{I}# The first ``*`` corresponds to the cause.
{I}glob_pattern = "*/{cls_name_json}/**/*.json"

{I}paths = sorted(invalid_dir.glob(glob_pattern))

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}try:
{III}instance = aas_jsonization.{deserialization_function}(jsonable)
{II}except aas_jsonization.DeserializationException as exception:
{III}raise AssertionError(
{IIII}f"Expected no deserialization exception from {{path}}"
{III}) from exception

{II}errors = list(aas_verification.verify(instance))

{II}self.assertGreater(
{III}len(errors),
{III}0,
{III}f"Expected verification errors from {{path}}, but got none"
{II})

{II}tests.common.record_or_check(
{III}path=path.parent / (path.name + ".errors"),
{III}got="\\n".join(
{IIII}f"{{error.path}}: {{error.cause}}"
{IIII}for error in errors
{III})
{II})"""
        ),
    ]

    writer = io.StringIO()
    writer.write(
        f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test JSON de/serialization of the concrete class
{I}:py:class:`{aas_module}.types.{cls_name}`.
{I}\"\"\""""
    )

    for method in methods:
        writer.write("\n\n")
        writer.write(textwrap.indent(method, I))

    return Stripped(writer.getvalue())


# fmt: off
@require(
    lambda container_cls:
    container_cls.name == "Environment",
    "Hint for the future reader what to expect; "
    "assume this might change in the future"
)
# fmt: on
def _generate_for_contained_in_environment(
    cls: intermediate.ConcreteClass,
    container_cls: intermediate.ConcreteClass,
    aas_module: aas_core_codegen.python.common.QualifiedModuleName,
) -> Stripped:
    """Generate the tests for a class contained in an ``Environment`` instance."""
    cls_name_json = aas_core_codegen.naming.json_model_type(cls.name)

    cls_name_json_literal = aas_core_codegen.python.common.string_literal(cls_name_json)

    deserialization_function = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_jsonable")
    )

    cls_name = aas_core_codegen.python.naming.class_name(cls.name)

    methods = [
        Stripped(
            f"""\
def test_ok(self) -> None:
{I}paths = sorted(
{II}(
{IIII}tests.common.TEST_DATA_DIR
{IIII}/ "Json"
{IIII}/ "ContainedInEnvironment"
{IIII}/ "Expected"
{IIII}/ {cls_name_json_literal}
{II}).glob("**/*.json")
{I})

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}container = aas_jsonization.{deserialization_function}(jsonable)

{II}errors = list(aas_verification.verify(container))

{II}self.assertListEqual([], errors, f"path is {{path}}")

{II}# Check the round-trip
{II}another_jsonable = aas_jsonization.to_jsonable(container)
{II}self.assertListEqual(
{III}[],
{III}list(
{IIII}map(
{IIIII}str,
{IIIII}tests.common_jsonization.check_equal(jsonable, another_jsonable)
{IIII})
{III})
{II})"""
        ),
        Stripped(
            f"""\
def test_that_deserialization_from_non_object_fails(self) -> None:
{I}jsonable = "not an object"

{I}observed_exception: Optional[
{II}aas_jsonization.DeserializationException
{I}] = None

{I}try:
{II}aas_jsonization.{deserialization_function}(jsonable)
{I}except aas_jsonization.DeserializationException as exception:
{II}observed_exception = exception

{I}assert observed_exception is not None
{I}self.assertEqual(
{II}"Expected a mapping, but got: <class 'str'>",
{II}observed_exception.cause
{I})

{I}self.assertEqual("", str(observed_exception.path))"""
        ),
        Stripped(
            f"""\
def test_deserialization_failures(self) -> None:
{I}unserializable_dir = (
{II}tests.common.TEST_DATA_DIR
{II}/ "Json"
{II}/ "ContainedInEnvironment"
{II}/ "Unexpected"
{II}/ "Unserializable"
{I})

{I}# The first ``*`` corresponds to the cause.
{I}glob_pattern = "*/{cls_name_json}/**/*.json"

{I}paths = sorted(unserializable_dir.glob(glob_pattern))

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}observed_exception: Optional[
{III}aas_jsonization.DeserializationException
{II}] = None

{II}try:
{III}_ = aas_jsonization.{deserialization_function}(jsonable)
{II}except aas_jsonization.DeserializationException as exception:
{III}observed_exception = exception

{II}assert observed_exception is not None, (
{III}f"Expected an exception, but got none for: {{path}}"
{II})

{II}tests.common.record_or_check(
{III}path=path.parent / (path.name + ".exception"),
{III}got=f"{{observed_exception.path}}: {{observed_exception.cause}}"
{II})"""
        ),
        Stripped(
            f"""\
def test_verification_failures(self) -> None:
{I}invalid_dir = (
{II}tests.common.TEST_DATA_DIR
{II}/ "Json"
{II}/ "ContainedInEnvironment"
{II}/ "Unexpected"
{II}/ "Invalid"
{I})

{I}# The first ``*`` corresponds to the cause.
{I}glob_pattern = "*/{cls_name_json}/**/*.json"

{I}paths = sorted(invalid_dir.glob(glob_pattern))

{I}for path in paths:
{II}with path.open("rt") as fid:
{III}jsonable = json.load(fid)

{II}try:
{III}container = aas_jsonization.{deserialization_function}(jsonable)
{II}except aas_jsonization.DeserializationException as exception:
{III}raise AssertionError(
{IIII}f"Expected no deserialization exception from {{path}}"
{III}) from exception

{II}errors = list(aas_verification.verify(container))

{II}self.assertGreater(
{III}len(errors),
{III}0,
{III}f"Expected verification errors from {{path}}, but got none"
{II})

{II}tests.common.record_or_check(
{III}path=path.parent / (path.name + ".errors"),
{III}got="\\n".join(
{IIII}f"{{error.path}}: {{error.cause}}"
{IIII}for error in errors
{III})
{II})"""
        ),
    ]

    writer = io.StringIO()
    writer.write(
        f"""\
class Test_{cls_name}(unittest.TestCase):
{I}\"\"\"
{I}Test JSON de/serialization of the concrete class
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
import json
import unittest
from typing import Optional

import {aas_module}.jsonization as aas_jsonization
import {aas_module}.verification as aas_verification

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
            blocks.append(
                _generate_for_self_contained(
                    cls=our_type, aas_module=dev_scripts.test_codegen.common.AAS_MODULE
                )
            )
        else:
            blocks.append(
                _generate_for_contained_in_environment(
                    cls=our_type,
                    container_cls=container_cls,
                    aas_module=dev_scripts.test_codegen.common.AAS_MODULE,
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
        / "tests/test_jsonization_of_concrete_classes.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
