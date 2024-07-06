# pylint: disable=missing-docstring

# NOTE (mristin):
# We explicitly check that dictionaries are not mistaken for array-like objects during
# the de-serialization.
#
# This is a regression test for the following issue:
# https://github.com/aas-core-works/aas-core3.0-python/issues/31

import unittest
from typing import Optional

import aas_core3.jsonization as aasjsonization


class TestIsArrayLike(unittest.TestCase):
    def test_example(self) -> None:
        jsonable = {"submodels": {}}  # type: aasjsonization.Jsonable

        got_exception = None  # type: Optional[aasjsonization.DeserializationException]

        try:
            _ = aasjsonization.environment_from_jsonable(jsonable)
        except aasjsonization.DeserializationException as exception:
            got_exception = exception

        assert got_exception is not None
        self.assertEqual(
            "Expected something array-like, but got: <class 'dict'>", str(got_exception)
        )


if __name__ == "__main__":
    unittest.main()
