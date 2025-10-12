import argparse
from pathlib import Path

import pytest

from istub.cli import get_version, load_config, parse_args


class TestCliParser:
    def test_parse_args(self):
        assert parse_args(["--exitfirst"]).exitfirst

    def test_get_version(self):
        assert get_version()

    def test_load_config(self):
        path = Path(__file__).parent.parent / "istub.yml"
        config = load_config(path.as_posix())
        assert config.path
        with pytest.raises(argparse.ArgumentTypeError):
            load_config("not_exist.yml")
