# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Examine a virtual environment, determine the path it thinks it is at."""

from __future__ import annotations

import dataclasses
import functools
import json
import pathlib
import shlex
import subprocess  # noqa: S404
import sysconfig
import typing

from . import defs


if typing.TYPE_CHECKING:
    from typing import Final


@dataclasses.dataclass
class DetectError(defs.Error):
    """An error that occurred while examining a virtual environment."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not examine the {self.venvdir} virtual environment"


@dataclasses.dataclass
class NoPathsError(DetectError):
    """The virtual environment does not seem to know where it is at."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return f"Could not find a venv path in any of the {self.venvdir} configuration files"


@dataclasses.dataclass
class ConflictingPathsError(DetectError):
    """The virtual environment seems to be confused about where it is at."""

    paths: list[pathlib.Path]
    """The paths that the virtual environment thinks it is at, at the same time."""

    def __str__(self) -> str:
        """Provide a human-readable description of the error."""
        return (
            f"Conflicting paths found in the {self.venvdir} configuration files: "
            f"{' '.join(str(path) for path in self.paths)}"
        )


@dataclasses.dataclass(frozen=True)
class Python:
    """The properties of the Python interpreter used to create the virtual environment."""

    cache_tag: str
    """The tag to look for in `__pycache__` filenames."""

    interpreter: pathlib.Path
    """The path to the Python interpreter within the virtual environment."""

    libs: list[pathlib.Path]
    """The library directories within the virtual environment."""

    prefix: str
    """The path to the virtual environment as determined at runtime by the interpreter."""

    version_info: tuple[int, ...]
    """The Python version."""


@dataclasses.dataclass(frozen=True)
class Detected:
    """The various paths that a virtual environment thinks it is at.

    If detection is successful, then:
    - at least one of the optional fields (`cfg_path`, `prefix_path`) is set
    - all of the optional values that are set are set to the same path
    - the `path` field is set to that consensus path
    """

    path: pathlib.Path
    """The path that the virtual environment thinks it is at."""

    cache_path: pathlib.Path | None
    """The path deduced from the `.pyc` files in the lib directories."""

    cfg_path: pathlib.Path | None
    """The path determined from the `pyvenv.cfg` file."""

    prefix_path: pathlib.Path | None
    """The path extracted from the `bin/activate` script."""


@functools.lru_cache
def detect_python_properties(cfg: defs.Config, venvdir: pathlib.Path) -> Python:
    """Query the virtual environment's Python interpreter for its settings."""
    exe_ext: Final = sysconfig.get_config_var("EXE")
    python: Final = venvdir / "bin" / f"python3{exe_ext}"
    cfg.log.debug("- querying %(python)s for its properties", {"python": python})
    raw: Final = subprocess.check_output(  # noqa: S603
        [
            python,
            "-c",
            (
                "import json; "
                "import sys; "
                "print(json.dumps({"
                '    "cache_tag": sys.implementation.cache_tag,'
                '    "libs": [path for path in sys.path if path.startswith(sys.prefix)],'
                '    "prefix": sys.prefix,'
                '    "version_info": sys.version_info,'
                "}))"
            ),
        ],
        encoding="UTF-8",
    )
    decoded: Final = json.loads(raw)
    cfg.log.debug("- got %(prop)r", {"python": python, "prop": decoded})
    return Python(
        cache_tag=decoded["cache_tag"],
        interpreter=python,
        libs=[pathlib.Path(lib) for lib in decoded["libs"]],
        prefix=decoded["prefix"],
        version_info=(
            decoded["version_info"][0],
            decoded["version_info"][1],
            decoded["version_info"][3],
        ),
    )


def _detect_path_pyvenv(cfg: defs.Config, venvdir: pathlib.Path) -> pathlib.Path | None:
    """Examine the `pyvenv.cfg` file within the virtual environment."""
    pyvenv: Final = venvdir / "pyvenv.cfg"
    if not pyvenv.is_file():
        cfg.log.debug("- no %(pyvenv)s file", {"pyvenv": pyvenv})
        return None

    lines: Final = pyvenv.read_text(encoding="UTF-8").splitlines()
    match [shlex.split(line)[-1] for line in lines if line.startswith("command = ")]:
        case [single]:
            return pathlib.Path(single)

        case _:
            # No match or more than one match
            return None


def _detect_path_prefix(cfg: defs.Config, venvdir: pathlib.Path) -> pathlib.Path | None:
    """Examine `sys.prefix` within the virtual environment."""
    try:
        return pathlib.Path(detect_python_properties(cfg, venvdir).prefix)
    except Exception as err:  # noqa: BLE001
        cfg.log.debug(
            "- could not query the Python in %(path)s: %(err)s",
            {"path": venvdir, "err": err},
        )
        return None


def _path_from_pyc(cfg: defs.Config, python: Python, pycpath: pathlib.Path) -> pathlib.Path | None:
    """Parse a `.pyc` file just enough to find its original `.py` file path."""
    try:
        lines: Final = subprocess.check_output(  # noqa: S603
            [
                python.interpreter,
                "-c",
                (
                    f"import marshal; "
                    f'inf = open("{pycpath}", mode="rb"); '
                    f"inf.read(16); "
                    f"print(marshal.load(inf).co_filename); "
                ),
            ],
            encoding="UTF-8",
        ).splitlines()
    except (OSError, subprocess.CalledProcessError) as err:
        cfg.log.debug(
            "Could not use %(py)s to parse %(pyc)s: %(err)s",
            {"py": python.interpreter, "pyc": pycpath, "err": err},
        )
        return None

    match lines:
        case [single]:
            return pathlib.Path(single)

        case _:
            # No output or more than one line (unexpected)
            cfg.log.debug(
                "Parsing %(pyc)s via %(py)s yielded an unexpected result: %(lines)r",
                {"py": python.interpreter, "pyc": pycpath, "lines": lines},
            )
            return None


def _detect_path_cache(cfg: defs.Config, venvdir: pathlib.Path) -> pathlib.Path | None:
    """Examine byte-compiled files in the lib directory."""
    try:
        python: Final = detect_python_properties(cfg, venvdir)
    except Exception as err:  # noqa: BLE001
        cfg.log.debug(
            "- could not query the Python in %(path)s: %(err)s",
            {"path": venvdir, "err": err},
        )
        return None

    # Look for just one `.pyc` file in any of these directories
    cache_ext: Final = f".{python.cache_tag}.pyc"
    cfg.log.debug("- looking for %(ext)s files in %(venv)s", {"ext": cache_ext, "venv": venvdir})
    for path in (path for path in python.libs if venvdir in path.parents):
        cfg.log.debug("  - looking in %(path)s", {"path": path})
        for pycpath in path.glob(f"**/__pycache__/*{cache_ext}"):
            cfg.log.debug("  - examining %(pyc)s", {"pyc": pycpath})

            if pycpath.parent.name != "__pycache__":
                cfg.log.debug("    - not within a __pycache__ directory?!")
                continue
            if not pycpath.name.endswith(cache_ext):
                cfg.log.debug("    - no %(ext)s extension?!", {"ext": cache_ext})
                continue
            pypath = pycpath.parent.parent / (pycpath.name.removesuffix(cache_ext) + ".py")
            if not pypath.is_file():
                cfg.log.debug("    - no %(py)s file?!", {"py": pypath})
                continue
            try:
                pyrel = pypath.relative_to(venvdir)
            except ValueError:
                # Hm, it seems that something went wrong with our filters above?
                cfg.log.debug("    - not under %(venv)s?!", {"venv": venvdir})
                continue

            origpath = _path_from_pyc(cfg, python, pycpath)
            if origpath is None:
                continue
            cfg.log.debug("    - got original path %(orig)s", {"orig": origpath})

            origbase = str(origpath).removesuffix(f"/{pyrel}")
            if origbase == str(origpath):
                cfg.log.debug("    - does not seem to end in /%(rel)s", {"rel": pyrel})
                continue

            cfg.log.debug("    - found %(base)s", {"base": origbase})
            return pathlib.Path(origbase)

    return None


def detect_path(cfg: defs.Config, venvdir: pathlib.Path, *, use_prefix: bool = False) -> Detected:
    """Examine a virtual environment, determine the path it thinks it is at."""
    cfg.log.debug("Examining %(venvdir)s", {"venvdir": venvdir})

    cache_path: Final = _detect_path_cache(cfg, venvdir)
    cfg.log.debug("- got cache_path %(cache_path)r", {"cache_path": cache_path})

    cfg_path: Final = _detect_path_pyvenv(cfg, venvdir)
    cfg.log.debug("- got cfg_path %(cfg_path)r", {"cfg_path": cfg_path})

    prefix_path: Final = _detect_path_prefix(cfg, venvdir) if use_prefix else None
    cfg.log.debug("- got prefix_path %(prefix_path)r", {"prefix_path": prefix_path})

    paths: Final = sorted(
        {path for path in (cfg_path, prefix_path, cache_path) if path is not None},
    )
    match paths:
        case []:
            raise NoPathsError(venvdir)

        case [single]:
            return Detected(
                path=single,
                cfg_path=cfg_path,
                cache_path=cache_path,
                prefix_path=prefix_path,
            )

        case too_many_paths:
            raise ConflictingPathsError(venvdir, paths=too_many_paths)
