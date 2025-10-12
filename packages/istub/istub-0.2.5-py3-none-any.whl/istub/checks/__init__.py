"""
Checks catalogue.
"""

from typing import Dict, Type

from istub.checks.base import BaseCheck
from istub.checks.flake8 import Flake8Check
from istub.checks.mypy import MypyCheck
from istub.checks.pyright import PyrightCheck
from istub.checks.ruff import RuffCheck
from istub.checks.stubtest import StubtestCheck

CHECKS_MAP: Dict[str, Type[BaseCheck]] = {
    Flake8Check.NAME: Flake8Check,
    MypyCheck.NAME: MypyCheck,
    PyrightCheck.NAME: PyrightCheck,
    RuffCheck.NAME: RuffCheck,
    StubtestCheck.NAME: StubtestCheck,
}
