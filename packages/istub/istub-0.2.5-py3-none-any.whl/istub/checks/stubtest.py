"""
Check package with mypy.stubtest.
"""

from typing import Tuple

from istub.checks.base import BaseCheck


class StubtestCheck(BaseCheck):
    """
    Check package with mypy.stubtest.
    """

    NAME = "stubtest"

    @property
    def default_command(self) -> Tuple[str, ...]:
        """
        Default command to run the check.
        """
        return (
            self.python_path,
            "-m",
            "mypy.stubtest",
        )

    def run(self) -> str:
        """
        Run the check using mypy.stubtest.
        """
        output = self.get_call_output(
            [*self.command, self.package.name],
            capture_stderr=False,
        )
        return "\n".join(output.splitlines()[:-1])

    def is_ignored_line_diff(self, line: str) -> bool:
        """
        Whether line is ignored in diff.
        """
        if super().is_ignored_line_diff(line):
            return True

        if "at line" in line:
            return True

        return False
