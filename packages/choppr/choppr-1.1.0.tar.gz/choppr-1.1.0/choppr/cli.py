"""Script to generate an environment file with the current release information."""

from __future__ import annotations

import logging
import sys

from pathlib import Path
from typing import Annotated

import typer

from pydantic import ValidationError
from rich.logging import RichHandler

from choppr import __version__
from choppr.choppr import Choppr
from choppr.types.enums import OperatingMode
from choppr.utils.files import version_existing_file


__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2025 Lockheed Martin Corporation"
__license__ = "MIT License"


def _version_callback(value: bool) -> None:
    if value:
        print(f"Choppr Version: {__version__}")  # noqa: T201
        raise typer.Exit


def _cli(  # noqa: PLR0913, PLR0917
    operating_mode: Annotated[OperatingMode, typer.Argument(help="The operating mode to use")],
    config: Annotated[Path, typer.Option("--config", "-f", help="The configuration file to use")] = Path("choppr.yml"),
    output_sbom: Annotated[
        Path | None, typer.Option("--output-sbom", "-o", help="The file to write the chopped SBOM to")
    ] = None,
    log_file: Annotated[Path, typer.Option("--log", "-l", help="The log file to write to")] = Path("choppr.log"),
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable debug logging")] = False,
    version: Annotated[bool, typer.Option("--version", callback=_version_callback, is_eager=True)] = False,  # noqa: ARG001
) -> None:
    version_existing_file(log_file)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(module)s:%(lineno)d] - %(message)s", "[%Y-%m-%d %H:%M:%S]")
    )
    logging.basicConfig(
        format="[%(module)s:%(lineno)d] - %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(rich_tracebacks=True), file_handler],
    )
    log = logging.getLogger("Choppr")
    log.setLevel(logging.DEBUG if verbose else logging.INFO)

    try:
        choppr = Choppr(operating_mode, config, log, output_sbom)

        match operating_mode:
            case OperatingMode.RUN:
                choppr.run()
            case OperatingMode.CACHE:
                choppr.cache()
    except (FileNotFoundError, ValidationError, ValueError):
        sys.exit(1)
    except Exception:
        log.exception("Unexpected exception")
        sys.exit(255)


def _entrypoint() -> None:
    typer.run(_cli)


if __name__ == "__main__":
    _entrypoint()
