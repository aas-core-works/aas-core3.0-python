"""Generate the common functions to de/serialize instances of a class."""
import enum
import io
import os
import pathlib
import sys
import textwrap
from typing import List, Optional

import aas_core_codegen.common
import aas_core_codegen.python.naming
import aas_core_codegen.naming
import aas_core_codegen.parse
import aas_core_codegen.run
from aas_core_codegen import intermediate
from aas_core_codegen.common import Stripped
import aas_core_codegen.python.common
from aas_core_codegen.python.common import (
    INDENT as I,
    INDENT2 as II,
    INDENT3 as III,
    INDENT4 as IIII,
    INDENT5 as IIIII,
    INDENT6 as IIIIII,
)

import dev_scripts.test_codegen.common
import dev_scripts.test_codegen.test_data_io


class ExampleKind(enum.Enum):
    """Represent kind of an instance example."""

    #: Maximal instance with all the properties set
    MAXIMAL = 0

    #: Minimal instance with only the required properties set
    MINIMAL = 1


def _generate_load_expected(
    cls: intermediate.ConcreteClass,
    container_cls: intermediate.ConcreteClass,
    example_kind: ExampleKind,
) -> Stripped:
    """
    Generate the function to load the maximal example from a container.

    If ``cls`` is self-contained, then ``cls is container_cls``.
    """

    # noinspection PyUnusedLocal
    container_kind = None  # type: Optional[Stripped]
    if cls is container_cls:
        container_kind = Stripped("SelfContained")
    elif container_cls.name == "Environment":
        container_kind = Stripped("ContainedInEnvironment")
    else:
        raise ValueError(f"Unexpected container class: {container_cls.name!r}")

    container_kind_literal = aas_core_codegen.python.common.string_literal(
        container_kind
    )

    model_type_literal = aas_core_codegen.python.common.string_literal(
        aas_core_codegen.naming.json_model_type(cls.name)
    )

    file_name_literal = None  # type: Optional[Stripped]
    if example_kind is ExampleKind.MAXIMAL:
        file_name_literal = Stripped(
            aas_core_codegen.python.common.string_literal("maximal.json")
        )
    elif example_kind is ExampleKind.MINIMAL:
        file_name_literal = Stripped(
            aas_core_codegen.python.common.string_literal("minimal.json")
        )
    else:
        aas_core_codegen.common.assert_never(example_kind)

    blocks = [
        Stripped(
            f"""\
path = (
{II}tests.common.TEST_DATA_DIR
{II}/ "Json"
{II}/ {container_kind_literal}
{II}/ "Expected"
{II}/ {model_type_literal}
{II}/ {file_name_literal}
)"""
        ),
        Stripped(
            f"""\
with path.open("rt") as fid:
{I}try:
{II}jsonable = json.load(fid)
{I}except json.decoder.JSONDecodeError as exception:
{II}raise AssertionError(
{III}f"Unexpected non-JSON content in {{path}}"
{II}) from exception"""
        ),
    ]  # type: List[Stripped]

    deserialization_function = aas_core_codegen.python.naming.function_name(
        aas_core_codegen.common.Identifier(f"{container_cls.name}_from_jsonable")
    )

    cls_name = aas_core_codegen.python.naming.class_name(cls.name)

    if cls is container_cls:
        blocks.append(
            Stripped(
                f"""\
return aas_jsonization.{deserialization_function}(
{I}jsonable
)"""
            )
        )
    else:
        blocks.append(
            Stripped(
                f"""\
container = aas_jsonization.{deserialization_function}(
{I}jsonable
)

instance: Optional[
{I}aas_types.{cls_name}
] = None

for something in container.descend():
{I}if isinstance(
{III}something,
{III}aas_types.{cls_name}
{I}):
{II}# We pick the least deep instance, so that we can also test for
{II}# nested instances *etc.*
{II}instance = something
{II}break

if instance is None:
{I}raise AssertionError(
{II}f"Expected to find an instance of {cls_name} "
{II}f"in {{path}}, but found none."
{I})

return instance"""
            )
        )

    function_name = None  # type: Optional[Stripped]
    if example_kind is ExampleKind.MAXIMAL:
        function_name = Stripped(
            aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"load_maximal_{cls.name}")
            )
        )
    elif example_kind is ExampleKind.MINIMAL:
        function_name = Stripped(
            aas_core_codegen.python.naming.function_name(
                aas_core_codegen.common.Identifier(f"load_minimal_{cls.name}")
            )
        )
    else:
        aas_core_codegen.common.assert_never(example_kind)

    docstring_literal = None  # type: Optional[Stripped]
    if example_kind is ExampleKind.MAXIMAL:
        docstring_literal = Stripped(
            f"""\
\"\"\"
Load a maximal example
of :py:class:`aas_types.{cls_name}`
from :py:attr:`tests.common.TEST_DATA_DIR`.
\"\"\""""
        )
    elif example_kind is ExampleKind.MINIMAL:
        docstring_literal = Stripped(
            f"""\
\"\"\"
Load a minimal example
of :py:class:`aas_types.{cls_name}`
from :py:attr:`tests.common.TEST_DATA_DIR`.
\"\"\""""
        )
    else:
        aas_core_codegen.common.assert_never(example_kind)

    writer = io.StringIO()
    writer.write(
        f"""\
def {function_name}(
) -> aas_types.{cls_name}:
{I}{aas_core_codegen.common.indent_but_first_line(docstring_literal, I)}
"""
    )

    for i, block in enumerate(blocks):
        if i > 0:
            writer.write("\n\n")

        writer.write(textwrap.indent(block, I))

    return Stripped(writer.getvalue())


def main() -> int:
    """Execute the main routine."""
    symbol_table = dev_scripts.test_codegen.common.load_symbol_table()

    this_path = pathlib.Path(os.path.realpath(__file__))

    test_data_dir = dev_scripts.test_codegen.common.REPO_ROOT / "test_data"

    warning = dev_scripts.test_codegen.common.generate_warning_comment(
        this_path.relative_to(dev_scripts.test_codegen.common.REPO_ROOT)
    )

    blocks = [
        warning,
        Stripped('"""Provide common functionality for JSON de-serialization."""'),
        Stripped("# pylint: disable=missing-docstring"),
        Stripped(
            """\
import collections.abc
import json
import sys
from typing import Iterator, Optional

if sys.version_info >= (3, 8):
    from typing import Final
else:
    from typing_extensions import Final

import aas_core3.common as aas_common
import aas_core3.jsonization as aas_jsonization
import aas_core3.types as aas_types

import tests.common"""
        ),
        Stripped(
            f"""\
class Difference:
{I}\"\"\"Represent a single difference between two JSON-ables.\"\"\"

{I}#: Human-readable description of the difference
{I}message: Final[str]

{I}#: Path in the expected JSON-able value which is different from
{I}#: the obtained JSON-able value
{I}path: Final[aas_jsonization.Path]

{I}def __init__(self, message: str) -> None:
{II}\"\"\"Initialize with the given message and empty path.\"\"\"
{II}self.message = message
{II}self.path = aas_jsonization.Path()

{I}def __str__(self) -> str:
{II}return f"#{{self.path}}: {{self.message}}\""""
        ),
        Stripped(
            f"""\
def check_equal(
{I}expected: aas_jsonization.Jsonable,
{I}got: aas_jsonization.Jsonable,
) -> Iterator[Difference]:
{I}\"\"\"
{I}Compare recursively two JSON-able values for equality.

{I}:param expected: expected JSON-able value
{I}:param got: obtained JSON-able value
{I}:yield: differences
{I}\"\"\"
{I}if isinstance(expected, (bool, int, float, str, bytes)):
{II}if type(expected) != type(got):  # pylint: disable=unidiomatic-typecheck
{III}yield Difference(f"Expected {{type(expected)}}, but got {{type(got)}}")

{II}if expected != got:
{III}yield Difference(f"Expected {{expected!r}}, but got {{got!r}}")
{I}elif isinstance(expected, collections.abc.Sequence):
{II}if not isinstance(got, collections.abc.Sequence):
{III}yield Difference(f"Expected a sequence, but got {{type(got)}}")
{II}else:
{III}if len(expected) != len(got):
{IIII}yield Difference(
{IIIII}f"Expected a sequence of {{len(expected)}} item(s), "
{IIIII}f"but got {{len(got)}} item(s)"
{IIII})

{III}for i, (expected_item, got_item) in enumerate(zip(expected, got)):
{IIII}for difference in check_equal(expected_item, got_item):
{IIIII}difference.path._prepend(aas_jsonization.IndexSegment(expected, i))
{IIIII}yield difference

{I}elif isinstance(expected, collections.abc.Mapping):
{II}if not isinstance(got, collections.abc.Mapping):
{III}yield Difference(f"Expected a mapping, but got {{type(got)}}")
{II}else:
{III}if not all(isinstance(key, str) for key in expected.keys()):
{IIII}raise ValueError(
{IIIII}f"Expected all keys in the expected JSON-able value to be strings, "
{IIIII}f"but got: {{list(expected.keys())}}"
{IIII})

{III}if not all(isinstance(key, str) for key in got.keys()):
{IIII}yield Difference(
{IIIII}f"Expected all keys in a mapping to be strings, "
{IIIII}f"but got: {{list(got.keys())}}"
{IIII})

{III}expected_key_set = set(expected.keys())
{III}got_key_set = set(got.keys())

{III}expected_got_diff = expected_key_set.difference(got_key_set)
{III}if expected_got_diff:
{IIII}yield Difference(f"Expected key(s) {{sorted(expected_got_diff)}} missing")

{III}got_expected_diff = got_key_set.difference(expected_key_set)
{III}if got_expected_diff:
{IIII}yield Difference(f"Unexpected key(s) {{sorted(got_expected_diff)}}")

{III}for key, expected_value in expected.items():
{IIII}got_value = got[key]

{IIII}for difference in check_equal(expected_value, got_value):
{IIIII}difference.path._prepend(
{IIIIII}aas_jsonization.PropertySegment(expected, key)
{IIIII})
{IIIII}yield difference
{I}else:
{II}aas_common.assert_never(expected)"""
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

        blocks.append(
            _generate_load_expected(
                cls=our_type,
                container_cls=container_cls,
                example_kind=ExampleKind.MAXIMAL,
            )
        )

        blocks.append(
            _generate_load_expected(
                cls=our_type,
                container_cls=container_cls,
                example_kind=ExampleKind.MINIMAL,
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
        dev_scripts.test_codegen.common.REPO_ROOT / "tests/common_jsonization.py"
    )
    target_pth.write_text(writer.getvalue(), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
