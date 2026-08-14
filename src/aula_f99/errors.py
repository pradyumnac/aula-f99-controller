"""Shared exception types for this project's error handling.

A hand-edited config file can go bad in any number of ways: invalid TOML,
a missing key, a value of the wrong type. Every load function that reads
one of these files collapses all of that into `ConfigLoadError`, so a
caller has exactly one thing to catch, fall back to safe defaults, and
tell the user about.
"""

from __future__ import annotations

from pathlib import Path


class ConfigLoadError(Exception):
    """`path` exists but could not be read as a valid config file.

    Carries the path and the original exception so the caller can show
    the user which file is at fault and why, instead of a bare traceback.
    """

    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(f"{path}: {cause}")
        self.path = path
        self.cause = cause
