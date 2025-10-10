# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Modify the files within the virtual environment to prepare it for moving."""

from __future__ import annotations

import dataclasses
import os
import pathlib
import subprocess  # noqa: S404
import tempfile
import typing

from . import defs
from . import detect


if typing.TYPE_CHECKING:
    from typing import Final


@dataclasses.dataclass
class ProcessError(defs.Error):
    """An error that occurred while processing the virtual environment."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not process the {self.venvdir} virtual environment"


@dataclasses.dataclass
class SameSrcDstError(ProcessError):
    """Neither a from- nor a to-path was specified."""

    src: pathlib.Path
    """The source that appears to be the same as the destination."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return (
            f"Retargeting {self.venvdir}: "
            f"the same {self.src} specified as both source and destination"
        )


@dataclasses.dataclass
class NotAbsolutePathError(ProcessError):
    """The source and destination paths must be absolute."""

    path: pathlib.Path
    """The non-absolute path that was specified."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Retargeting {self.venvdir}: non-absolute path {self.path} specified"


def _detect_and_validate(
    cfg: defs.Config,
    venvdir: pathlib.Path,
    *,
    venvsrc: pathlib.Path | None,
    venvdst: pathlib.Path | None,
) -> tuple[detect.Python, pathlib.Path, pathlib.Path]:
    """Fill in the default values and check for inconsistencies."""
    python: Final = detect.detect_python_properties(cfg, venvdir)
    if venvsrc is None:
        cfg.log.info("Attempting to detect a source directory at %(venv)s", {"venv": venvdir})
        venvsrc = detect.detect_path(cfg, venvdir).path

    if venvdst is None:
        cfg.log.info("Using the current path as a destination directory")
        venvdst = venvdir

    cfg.log.info(
        "Retargeting %(venv)s from %(src)s to %(dst)s",
        {"venv": venvdir, "src": venvsrc, "dst": venvdst},
    )
    if venvsrc == venvdst:
        raise SameSrcDstError(venvdir, venvsrc)
    if not venvsrc.is_absolute():
        raise NotAbsolutePathError(venvdir, venvsrc)
    if not venvdst.is_absolute():
        raise NotAbsolutePathError(venvdir, venvdst)

    return python, venvsrc, venvdst


def _examine_files(
    venvdir: pathlib.Path,
    venvsrc: pathlib.Path,
    python: detect.Python,
) -> tuple[list[pathlib.Path], list[pathlib.Path], list[pathlib.Path]]:
    """Figure out which files need to be modified in which way."""
    bindir: Final = venvdir / "bin"
    pyvenv: Final = venvdir / "pyvenv.cfg"
    cache_ext: Final = f".{python.cache_tag}.pyc"

    files_before: Final = [
        pathlib.Path(line)
        for line in subprocess.check_output(  # noqa: S603
            ["grep", "-Flare", venvsrc, "--", venvdir],  # noqa: S607
            encoding="UTF-8",
        ).splitlines()
    ]
    recompile: set[pathlib.Path] = set()
    replace: set[pathlib.Path] = set()
    ignore: set[pathlib.Path] = set()
    for path in files_before:
        if path == pyvenv:
            replace.add(path)
            continue

        if bindir in path.parents:
            replace.add(path)
            continue

        if path.parent.name == "__pycache__":
            if path.name.endswith(cache_ext):
                libtrees = sorted(lib for lib in python.libs if lib in path.parents)
                if libtrees:
                    recompile.add(libtrees[-1])
                    continue

            if path.name.endswith(".pyc"):
                ignore.add(path)
                continue

        raise NotImplementedError(repr((python, path)))

    return sorted(recompile), sorted(replace), sorted(ignore)


def _recompile_cached(  # noqa: PLR0913
    cfg: defs.Config,
    path: pathlib.Path,
    venvdir: pathlib.Path,
    python: detect.Python,
    *,
    venvsrc: pathlib.Path,
    venvdst: pathlib.Path,
) -> None:
    """Rebuild the `*.pyc` precompiled modules within the specified directory."""
    cfg.log.debug("About to recompile files in %(path)s", {"path": path})

    # So this part is a bit weird...
    if python.version_info[:2] < (3, 13) and venvdir == venvdst:
        add_prefix = venvdst.parent
    else:
        add_prefix = venvdst

    cfg.log.debug(
        "- invoking compileall -s %(strip)s -p %(prefix)s",
        {"strip": venvsrc, "prefix": add_prefix},
    )
    subprocess.check_call(  # noqa: S603
        [
            python.interpreter,
            "-m",
            "compileall",
            "-f",
            "-q",
            "-s",
            f"{venvsrc}",
            "-p",
            f"{add_prefix}",
            "--",
            path,
        ],
    )


def _restore_metadata(meta: os.stat_result, path: pathlib.Path) -> None:
    """Restore the file mode and possibly the owner and group."""
    current: Final = path.stat()

    if (current.st_mode & 0o7777) != (meta.st_mode & 0o7777):
        path.chmod(meta.st_mode & 0o7777)

    if current.st_uid != meta.st_uid or current.st_gid != meta.st_gid:
        os.chown(path, meta.st_uid, meta.st_gid)


def _replace_strings(
    cfg: defs.Config,
    path: pathlib.Path,
    venvsrc: pathlib.Path,
    venvdst: pathlib.Path,
) -> None:
    """Replace the paths to the virtual environment within a text file."""
    cfg.log.debug("About to replace strings in %(path)s", {"path": path})
    meta: Final = path.stat()
    contents: Final = path.read_text(encoding="UTF-8")
    updated: Final = contents.replace(str(venvsrc), str(venvdst))

    temppath = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f"replace-{path.name}",
            delete=False,
            mode="wt",
            encoding="UTF-8",
        ) as tempf:
            temppath = pathlib.Path(tempf.name)
            print(updated, file=tempf, end="")
            tempf.flush()
            temppath.rename(path)
            temppath = None
            _restore_metadata(meta, path)
    finally:
        if temppath is not None:
            temppath.unlink()


def retarget(
    cfg: defs.Config,
    venvdir: pathlib.Path,
    *,
    venvsrc: pathlib.Path | None = None,
    venvdst: pathlib.Path | None = None,
) -> None:
    """Modify the files within the virtual environment to prepare it for moving."""
    python, venvsrc, venvdst = _detect_and_validate(cfg, venvdir, venvsrc=venvsrc, venvdst=venvdst)
    recompile, replace, ignore = _examine_files(venvdir, venvsrc, python)
    cfg.log.info(
        (
            "- %(recompile)d directories to recompile, "
            "%(replace)d files to replace strings in, "
            "%(ignore)d files ignored"
        ),
        {"recompile": len(recompile), "replace": len(replace), "ignore": len(ignore)},
    )

    for path in recompile:
        _recompile_cached(cfg, path, venvdir, python, venvsrc=venvsrc, venvdst=venvdst)

    for path in replace:
        _replace_strings(cfg, path, venvsrc, venvdst)
