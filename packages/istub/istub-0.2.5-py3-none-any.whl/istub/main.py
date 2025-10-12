#!/usr/bin/env python
"""
Main API entrypoint.
"""

import logging
import shlex
import sys
from typing import List, Sequence

from istub.cli import CLINamespace, parse_args
from istub.config import Config
from istub.constants import LOGGER_NAME
from istub.exceptions import CheckFailedError, ConfigError, RunFailedError
from istub.logger import get_logger
from istub.subprocess import check_call


def pip_install(config: Config) -> None:
    """
    Install pip requirements.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if config.pip_uninstall:
        logger.info("Uninstalling pip packages...")
        check_call(
            [
                config.python_path,
                "-m",
                "pip",
                "uninstall",
                "--yes",
                "--no-input",
                *config.pip_uninstall,
            ]
        )
    if config.pip_install:
        logger.info("Installing pip requirements...")
        check_call(
            [config.python_path, "-m", "pip", "install", "-U", "--no-input", *config.pip_install]
        )


def path_install(config: Config) -> None:
    """
    Install requirements.
    """
    if not config.path_install:
        return

    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Installing requirements...")
    for path_package in config.path_install:
        logger.debug(f"Installing {path_package.as_posix()}")
        check_call(
            [config.python_path, "-m", "pip", "install", "--no-input", path_package.as_posix()]
        )


def build(config: Config) -> None:
    """
    Build requirements.
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Building requirements...")
    for build_cmd in config.build:
        command = shlex.split(build_cmd)
        if command and command[0] == "python":
            command[0] = config.python_path
        check_call(command)


def check_packages(config: Config, args: CLINamespace) -> None:
    """
    Check packages.
    """
    logger = logging.getLogger(LOGGER_NAME)
    errors: List[CheckFailedError] = []
    for check in config.iterate_package_checks():
        logger.info(f"Checking {check.package.name} with {check.NAME}...")
        try:
            check.check()
        except CheckFailedError as e:
            if args.update:
                logger.info(f"Updating {check.NAME} snapshot for {check.package.name}...")
                check.set_snapshot(e.data)
                continue

            logger.error(e)
            for line in e.diff:
                logger.error(line)
            errors.append(e)

            if args.exitfirst:
                break
    if errors:
        raise RunFailedError("Some checks failed", errors)


def main() -> None:
    """
    Entry point for the main CLI.
    """
    try:
        main_api(sys.argv[1:])
    except ConfigError as e:
        logger = logging.getLogger(LOGGER_NAME)
        logger.error(f"Configuration error: {e}")
        exit(1)
    except RunFailedError as e:
        logger = logging.getLogger(LOGGER_NAME)
        logger.error(f"Check error: {e}")
        exit(1)


def main_api(args: Sequence[str]) -> None:
    """
    Entry point for the main API.
    """
    cli_namespace = parse_args(args)

    logger = get_logger(cli_namespace.log_level)
    config = cli_namespace.config
    if cli_namespace.packages:
        config.filter_packages(cli_namespace.packages)
    if cli_namespace.checks:
        config.filter_checks(cli_namespace.checks)
    if cli_namespace.install:
        pip_install(config)
    if cli_namespace.build and config.build:
        build(config)
    if cli_namespace.install:
        path_install(config)

    check_packages(config, cli_namespace)

    if config.is_updated():
        logger.info("Saving configuration...")
        config.save()


if __name__ == "__main__":
    main()
