# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Make sure that `venv-retarget run` starts up at least."""

from __future__ import annotations

import dataclasses
import functools
import itertools
import json
import os
import pathlib
import subprocess  # noqa: S404
import sys
import tempfile
import typing

import pytest

from venv_retarget import defs
from venv_retarget import detect
from venv_retarget import impl
from venv_retarget import util


if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Final


@functools.lru_cache
def get_venv_python() -> str:
    """Either use the specified Python implementation or the current interpreter."""
    return os.environ.get("VENV_PYTHON", sys.executable)


@functools.lru_cache
def get_venv_python_version_info() -> tuple[int, int]:
    """Get the first two components of the `sys.version_info` tuple."""
    py: Final = get_venv_python()
    lines: Final = subprocess.check_output(  # noqa: S603
        [py, "-c", "import sys; print(sys.version_info[0]); print(sys.version_info[1]);"],
        encoding="UTF-8",
    ).splitlines()
    match lines:
        case [major, minor]:
            return int(major), int(minor)

        case _:
            raise RuntimeError(repr(lines))


def create_venv(venvdir: pathlib.Path, *, use_uv: bool = False) -> None:
    """Create the virtual environment."""
    if use_uv:
        subprocess.check_call(  # noqa: S603
            ["uv", "venv", "-p", get_venv_python(), "--", venvdir],  # noqa: S607
        )
    else:
        subprocess.check_call([get_venv_python(), "-m", "venv", "--", venvdir])  # noqa: S603


def detect_venv(
    cfg: defs.Config,
    venvdir: pathlib.Path,
    expected: pathlib.Path,
    *,
    use_uv: bool,
    use_prefix: bool = False,
) -> detect.Detected:
    """Run some basic checks on the created or updated virtual environment."""
    detected: Final = detect.detect_path(cfg, venvdir, use_prefix=use_prefix)
    assert os.access(venvdir / "pyvenv.cfg", os.R_OK)
    if use_uv:
        assert not (venvdir / "bin" / "pip").exists()
    else:
        assert os.access(venvdir / "bin" / "pip", os.X_OK)

    assert detected.path == expected
    assert detected.cache_path == expected
    if use_prefix:
        assert detected.prefix_path == expected
    else:
        assert detected.prefix_path is None

    if get_venv_python_version_info() >= (3, 11) and not use_uv:
        assert detected.cfg_path == expected
    else:
        assert detected.cfg_path is None

    return detected


@pytest.mark.parametrize("use_uv", [False, True])
def test_detect(*, use_uv: bool) -> None:
    """Create the simplest venv, make sure `detect_path()` works on it."""
    cfg: Final = defs.Config(log=util.build_logger(verbose=True), verbose=True)
    with tempfile.TemporaryDirectory(prefix="venv-retarget-test.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        print(f"\nUsing {tempd} as a temporary directory")

        venvdir: Final = tempd / "harumph"
        create_venv(venvdir, use_uv=use_uv)
        detected: Final = detect_venv(cfg, venvdir, venvdir, use_uv=use_uv, use_prefix=True)

        venvnew: Final = tempd / "hooray"
        venvdir.rename(venvnew)

        detected_new: Final = detect.detect_path(cfg, venvnew)
        assert detected_new == dataclasses.replace(detected, prefix_path=None)


def test_run_detect() -> None:
    """Create the simplest venv, run `venv-retarget detect` on it."""
    with tempfile.TemporaryDirectory(prefix="venv-retarget-test.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        print(f"\nUsing {tempd} as a temporary directory")

        venvdir: Final = tempd / "trinket"
        create_venv(venvdir)

        raw: Final = subprocess.check_output(  # noqa: S603
            [sys.executable, "-m", "venv_retarget", "detect", "--", venvdir],
            encoding="UTF-8",
        )
        print(f"{raw=!r}")
        decoded: Final = json.loads(raw)
        print(f"{decoded=!r}")
        assert decoded["path"] == str(venvdir)
        assert sorted(decoded.keys()) == sorted(
            field.name for field in dataclasses.fields(detect.Detected)
        )


def do_test_retarget(
    cb_retarget: Callable[[defs.Config, pathlib.Path, pathlib.Path | None], None],
    *,
    use_uv: bool,
    before: bool,
) -> None:
    """Create a venv, move it, make sure `.detect_path()` works on the new venv."""
    cfg: Final = defs.Config(log=util.build_logger(verbose=True), verbose=True)
    with tempfile.TemporaryDirectory(prefix="venv-retarget-test.") as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        print(f"\nUsing {tempd} as a temporary directory")

        venvdir: Final = tempd / "this"
        create_venv(venvdir, use_uv=use_uv)
        detect_venv(cfg, venvdir, venvdir, use_uv=use_uv, use_prefix=True)

        venvnew: Final = tempd / "that"

        if before:
            cb_retarget(cfg, venvdir, venvnew)
            detected_before: Final = detect_venv(cfg, venvdir, venvnew, use_uv=use_uv)

        venvdir.rename(venvnew)

        if before:
            detected_after: Final = detect.detect_path(cfg, venvnew, use_prefix=True)
            assert detected_after == dataclasses.replace(detected_before, prefix_path=venvnew)
        else:
            cb_retarget(cfg, venvnew, None)
            detect_venv(cfg, venvnew, venvnew, use_uv=use_uv, use_prefix=True)


@pytest.mark.parametrize(("use_uv", "before"), itertools.product([False, True], [False, True]))
def test_retarget(*, use_uv: bool, before: bool) -> None:
    """Create a venv, move it, make sure `.detect_path()` works on the new venv."""

    def retarget_call_func(
        cfg: defs.Config,
        venvdir: pathlib.Path,
        venvnew: pathlib.Path | None,
    ) -> None:
        """Invoke the function directly."""
        impl.retarget(cfg, venvdir, venvdst=venvnew)

    do_test_retarget(retarget_call_func, use_uv=use_uv, before=before)


@pytest.mark.parametrize(("use_uv", "before"), itertools.product([False, True], [False, True]))
def test_run_retarget(*, use_uv: bool, before: bool) -> None:
    """Create a venv, move it, make sure `.detect_path()` works on the new venv."""

    def retarget_spawn(
        _cfg: defs.Config,
        venvdir: pathlib.Path,
        venvnew: pathlib.Path | None,
    ) -> None:
        """Spawn the command-line tool to retarget the venv."""
        vnewopts: Final[list[str | pathlib.Path]] = ["-d", venvnew] if venvnew is not None else []
        subprocess.check_call(  # noqa: S603
            [sys.executable, "-m", "venv_retarget", "-v", "retarget", *vnewopts, "--", venvdir],
        )

    do_test_retarget(retarget_spawn, use_uv=use_uv, before=before)
