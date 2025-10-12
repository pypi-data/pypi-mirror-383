import unittest
from unittest.mock import MagicMock, patch

from istub.yaml import dumps, loads


class TestYaml(unittest.TestCase):
    def test_dumps(self):
        assert dumps({"key": "value"}) == "key: value\n"

    def test_loads(self):
        assert loads("key: value") == {"key": "value"}
