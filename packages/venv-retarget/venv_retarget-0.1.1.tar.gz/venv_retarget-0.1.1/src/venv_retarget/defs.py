# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Common definitions for the venv-retarget library."""

from __future__ import annotations

import dataclasses
import typing


if typing.TYPE_CHECKING:
    import logging
    import pathlib
    from typing import Final


VERSION: Final = "0.1.1"
"""The venv-retarget library version, semver-like."""


FEATURES: Final = {
    "venv-retarget": VERSION,
}
"""The list of features supported by the venv-retarget library."""


@dataclasses.dataclass
class Error(Exception):
    """An error that occurred while examining or processing a virtual environment."""

    venvdir: pathlib.Path
    """The virtual environment that we tried to examine or process."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not process the {self.venvdir} virtual environment"


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for the venv-retarget library."""

    log: logging.Logger
    """The logger to send diagnostic, informational, and error messages to."""

    verbose: bool
    """Verbose operation; display diagnostic output."""
