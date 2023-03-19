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
    cls_name_json_literal = aas_core_codegen.python.common.string_literal(
        aas_core_codegen.naming.json_model_type(cls.name)
    )

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
{I}for cause in _CAUSES_FOR_DESERIALIZATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Json"
{III}/ "SelfContained"
{III}/ "Unexpected"
{III}/ cause
{III}/ {cls_name_json_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.json")):
{III}with path.open("rt") as fid:
{IIII}jsonable = json.load(fid)

{III}observed_exception: Optional[
{IIII}aas_jsonization.DeserializationException
{III}] = None

{III}try:
{IIII}_ = aas_jsonization.{deserialization_function}(jsonable)
{III}except aas_jsonization.DeserializationException as exception:
{IIII}observed_exception = exception

{III}assert observed_exception is not None, (
{IIII}f"Expected an exception, but got none for: {{path}}"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".exception"),
{IIII}got=f"{{observed_exception.path}}: {{observed_exception.cause}}"
{III})"""
        ),
        Stripped(
            f"""\
def test_verification_failures(self) -> None:
{I}for cause in tests.common.CAUSES_FOR_VERIFICATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Json"
{III}/ "SelfContained"
{III}/ "Unexpected"
{III}/ cause
{III}/ {cls_name_json_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.json")):
{III}with path.open("rt") as fid:
{IIII}jsonable = json.load(fid)

{III}try:
{IIII}instance = aas_jsonization.{deserialization_function}(jsonable)
{III}except aas_jsonization.DeserializationException as exception:
{IIII}raise AssertionError(
{IIIII}f"Expected no deserialization exception from {{path}}"
{IIII}) from exception

{III}errors = list(aas_verification.verify(instance))

{III}self.assertGreater(
{IIII}len(errors),
{IIII}0,
{IIII}f"Expected verification errors from {{path}}, but got none"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".errors"),
{IIII}got="\\n".join(
{IIIII}f"{{error.path}}: {{error.cause}}"
{IIIII}for error in errors
{IIII})
{III})"""
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
    cls_name_json_literal = aas_core_codegen.python.common.string_literal(
        aas_core_codegen.naming.json_model_type(cls.name)
    )

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
{I}for cause in _CAUSES_FOR_DESERIALIZATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Json"
{III}/ "ContainedInEnvironment"
{III}/ "Unexpected"
{III}/ cause
{III}/ {cls_name_json_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.json")):
{III}with path.open("rt") as fid:
{IIII}jsonable = json.load(fid)

{III}observed_exception: Optional[
{IIII}aas_jsonization.DeserializationException
{III}] = None

{III}try:
{IIII}_ = aas_jsonization.{deserialization_function}(jsonable)
{III}except aas_jsonization.DeserializationException as exception:
{IIII}observed_exception = exception

{III}assert observed_exception is not None, (
{IIII}f"Expected an exception, but got none for: {{path}}"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".exception"),
{IIII}got=f"{{observed_exception.path}}: {{observed_exception.cause}}"
{III})"""
        ),
        Stripped(
            f"""\
def test_verification_failures(self) -> None:
{I}for cause in tests.common.CAUSES_FOR_VERIFICATION_FAILURE:
{II}base_dir = (
{III}tests.common.TEST_DATA_DIR
{III}/ "Json"
{III}/ "ContainedInEnvironment"
{III}/ "Unexpected"
{III}/ cause
{III}/ {cls_name_json_literal}
{II})

{II}if not base_dir.exists():
{III}# There are no failure cases
{III}# for :py:class:`{aas_module}.types.{cls_name}`
{III}# and this ``cause``.
{III}continue

{II}for path in sorted(base_dir.glob("**/*.json")):
{III}with path.open("rt") as fid:
{IIII}jsonable = json.load(fid)

{III}try:
{IIII}container = aas_jsonization.{deserialization_function}(jsonable)
{III}except aas_jsonization.DeserializationException as exception:
{IIII}raise AssertionError(
{IIIII}f"Expected no deserialization exception from {{path}}"
{IIII}) from exception

{III}errors = list(aas_verification.verify(container))

{III}self.assertGreater(
{IIII}len(errors),
{IIII}0,
{IIII}f"Expected verification errors from {{path}}, but got none"
{III})

{III}tests.common.record_or_check(
{IIII}path=path.parent / (path.name + ".errors"),
{IIII}got="\\n".join(
{IIIII}f"{{error.path}}: {{error.cause}}"
{IIIII}for error in errors
{IIII})
{III})"""
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
        Stripped(
            f"""\
#: List of identifiers for serialization failures (corresponding to subdirectory names
#: in the directory with test data)
_CAUSES_FOR_DESERIALIZATION_FAILURE = [
{I}"TypeViolation",
{I}"RequiredViolation",
{I}"EnumViolation",
{I}"NullViolation",
{I}"UnexpectedAdditionalProperty",
]"""
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
