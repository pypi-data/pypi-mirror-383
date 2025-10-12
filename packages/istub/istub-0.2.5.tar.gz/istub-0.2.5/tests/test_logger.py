import unittest
from unittest.mock import MagicMock, patch

from istub.logger import get_logger


class TestLogging(unittest.TestCase):
    @patch("istub.logger.logging")
    def test_get_logger(self, logging_mock: MagicMock):
        logging_mock.getLogger().handlers = []

        self.assertTrue(get_logger(level=10))
        logging_mock.getLogger.assert_called_with("istub")
        logging_mock.getLogger().setLevel.assert_called_with(10)
        logging_mock.StreamHandler().setLevel.assert_called_with(10)
