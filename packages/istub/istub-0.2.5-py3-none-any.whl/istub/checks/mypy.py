"""
Check package with mypy.
"""

from typing import Tuple

from istub.checks.base import BaseCheck
from istub.exceptions import SubprocessError


class MypyCheck(BaseCheck):
    """
    Check package with mypy.
    """

    NAME = "mypy"

    @property
    def default_command(self) -> Tuple[str, ...]:
        """
        Default command to run the check.
        """
        return (
            self.python_path,
            "-m",
            "mypy",
        )

    def run(self) -> str:
        """
        Run mypy check on the package.
        """
        try:
            self.get_call_output(
                [
                    *self.command,
                    self.package.path.as_posix(),
                    "--exclude",
                    "build",
                ],
                capture_stderr=False,
                raise_errors=True,
            )
        except SubprocessError as e:
            return "\n".join(e.data.splitlines()[:-1])

        return ""
