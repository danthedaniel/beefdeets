import unittest
from typing import Optional, Type

from ..helpers import parse_timestamp, catch


class TestHelpers(unittest.TestCase):
    @catch(ValueError)
    def _catch_test(self, throw: Optional[Type[BaseException]] = None) -> int:
        if throw:
            raise throw

        return 1

    def test_parse_timestamp(self) -> None:
        self.assertEqual(parse_timestamp("2:03"), 123)
        self.assertEqual(parse_timestamp("1:02:03"), 3723)
        self.assertEqual(parse_timestamp("foobar"), None)

    def test_catch(self) -> None:
        with self.assertRaises(TypeError):
            self._catch_test(TypeError)

        self.assertEqual(self._catch_test(ValueError), None)
        self.assertEqual(self._catch_test(), 1)
