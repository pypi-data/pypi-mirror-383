"""Context variables used throughout Choppr."""

from __future__ import annotations

from pathlib import Path


__all__ = ["config_directory"]
__author__ = "Jesse Boswell <jesse.a.boswell@lmco.com>"
__copyright__ = "Copyright (C) 2025 Lockheed Martin Corporation"
__license__ = "MIT License"


config_directory: Path = Path.cwd()
