"""
Check package with flake8.
"""

from typing import Tuple

from istub.checks.base import BaseCheck


class Flake8Check(BaseCheck):
    """
    Check package with flake8.
    """

    NAME = "flake8"

    @property
    def default_command(self) -> Tuple[str, ...]:
        """
        Default command to run the check.
        """
        return (self.python_path, "-m", "flake8")

    def run(self) -> str:
        """
        Run the flake8 check on the package.
        """
        return self.get_call_output(
            [
                *self.command,
                "--ignore",
                "E203,W503,E501,D200,D107,D401,D105,D205,D400,D101,D102,D403",
                self.package.path.as_posix(),
            ],
            capture_stderr=True,
        )
