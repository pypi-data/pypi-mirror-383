"""
CLI parser.
"""

import argparse
import contextlib
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from istub.checks import CHECKS_MAP
from istub.config import Config
from istub.constants import PACKAGE_NAME, PROG_NAME

if sys.version_info >= (3, 8):
    from importlib import metadata  # type: ignore
else:
    import importlib_metadata as metadata  # type: ignore


def get_version() -> str:
    """
    Get istub package version.

    Returns:
        Version as a string.
    """
    with contextlib.suppress(metadata.PackageNotFoundError):
        return metadata.version(PACKAGE_NAME)

    return "0.0.0"


@dataclass
class CLINamespace:
    """
    CLI namespace.
    """

    build: bool
    install: bool
    update: bool
    exitfirst: bool
    log_level: int
    config: Config
    packages: List[str]
    checks: List[str]


def load_config(path_str: str) -> Config:
    """
    Load config.
    """
    path = Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Config file {path.as_posix()} does not exist")
    return Config(path)


def parse_args(args: Sequence[str]) -> CLINamespace:
    """
    CLI parser.
    """
    parser = argparse.ArgumentParser(PROG_NAME)
    parser.add_argument("-b", "--build", action="store_true", help="Generate packages")
    parser.add_argument("-i", "--install", action="store_true", help="Install packages")
    parser.add_argument("-u", "--update", action="store_true", help="Update snapshots")
    parser.add_argument(
        "-x", "--exitfirst", action="store_true", help="Exit on first check failure"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=load_config,
        default=None,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--checks",
        nargs="*",
        default=[],
        choices=list(CHECKS_MAP),
        help="Checks to run",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Verbose output")
    parser.add_argument("-V", "--version", action="store_true", help="Show version")
    parser.add_argument(
        "packages",
        nargs="*",
        help="Packages to check",
    )
    namespace = parser.parse_args(args)

    if namespace.version:
        version = get_version()
        print(version)
        exit()

    return CLINamespace(
        config=namespace.config or Config(Path.cwd() / "istub.yml"),
        build=namespace.build,
        install=namespace.install,
        update=namespace.update,
        exitfirst=namespace.exitfirst,
        packages=namespace.packages,
        log_level=logging.DEBUG if namespace.debug else logging.INFO,
        checks=namespace.checks,
    )
