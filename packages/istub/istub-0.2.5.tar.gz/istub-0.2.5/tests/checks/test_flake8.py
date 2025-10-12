from pathlib import Path

from istub.checks.flake8 import Flake8Check
from istub.config import Config


class TestFlake8Check:
    def test_init(self) -> None:
        root_path = Path(__file__).parent.parent.parent
        config = Config(root_path / "istub.yml")
        package = config.packages[0]
        check = Flake8Check(package)
        check.run()
