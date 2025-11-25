#!/usr/bin/env python3

"""Check that the distribution and aas_core_codegen/__init__.py are in sync."""

import os
import pathlib
import sys
from typing import Optional

import aas_core3

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def main() -> int:
    """Execute the main routine."""
    repo_root = pathlib.Path(os.path.realpath(__file__)).parent.parent

    pyproject_toml_pth = repo_root / "pyproject.toml"
    if not pyproject_toml_pth.exists():
        raise RuntimeError(
            f"Could not find_our_type the pyproject.toml: {pyproject_toml_pth}"
        )

    with pyproject_toml_pth.open("r") as pyproject_toml_file:
        pyproject_toml_str = pyproject_toml_file.read()

    pyproject_toml_map = tomllib.loads(pyproject_toml_str)

    success = True

    ##
    # Check basic fields
    ##

    author_names = [
        author["name"] for author in pyproject_toml_map["project"]["authors"]
    ]

    if aas_core3.__author__ not in author_names:
        print(
            "The author aas_core_codegen/__init__.py is not part of authors in pyproject.toml. "
            f"authors in pyproject.toml is {pyproject_toml_map['authors']}, "
            f"while the author in aas_core_codegen/__init__.py is: "
            f"{aas_core3.__author__}",
            file=sys.stderr,
        )
        success = False

    if pyproject_toml_map["project"]["license"] != aas_core3.__license__:
        print(
            f"The license in the pyproject.toml is {pyproject_toml_map['project']['license']}, "
            f"while the license in aas_core_codegen/__init__.py is: "
            f"{aas_core3.__license__}",
            file=sys.stderr,
        )
        success = False

    if pyproject_toml_map["project"]["description"] != aas_core3.__doc__:
        print(
            f"The description in the pyproject.toml is {pyproject_toml_map['project']['description']}, "
            f"while the description in aas_core_codegen/__init__.py is: "
            f"{aas_core3.__doc__}",
            file=sys.stderr,
        )
        success = False

    ##
    # Classifiers need special attention as there are multiple.
    ##

    # This is the map from the distribution to expected status in __init__.py.
    status_map = {
        "Development Status :: 1 - Planning": "Planning",
        "Development Status :: 2 - Pre-Alpha": "Pre-Alpha",
        "Development Status :: 3 - Alpha": "Alpha",
        "Development Status :: 4 - Beta": "Beta",
        "Development Status :: 5 - Production/Stable": "Production/Stable",
        "Development Status :: 6 - Mature": "Mature",
        "Development Status :: 7 - Inactive": "Inactive",
    }

    classifiers = pyproject_toml_map["project"]["classifiers"]

    status_classifier = None  # type: Optional[str]
    for classifier in classifiers:
        if classifier in status_map:
            status_classifier = classifier
            break

    if status_classifier is None:
        print(
            "Expected a status classifier in pyproject.toml "
            "(e.g., 'Development Status :: 3 - Alpha'), but found none.",
            file=sys.stderr,
        )
        success = False
    else:
        expected_status_in_init = status_map[status_classifier]

        if expected_status_in_init != aas_core3.__status__:
            print(
                f"Expected status {expected_status_in_init} "
                f"according to pyproject.toml in aas_core_codegen/__init__.py, "
                f"but found: {aas_core3.__status__}"
            )
            success = False

    if not success:
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
