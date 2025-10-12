from pathlib import Path

from istub.checks.mypy import MypyCheck
from istub.config import Config


class TestMypyCheck:
    def test_init(self) -> None:
        root_path = Path(__file__).parent.parent.parent
        config = Config(root_path / "istub.yml")
        package = config.packages[0]
        check = MypyCheck(package)
        check.run()
