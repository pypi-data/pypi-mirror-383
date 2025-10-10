# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Prepare a virtual environment for moving to another directory."""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys
import typing

import click

from . import defs
from . import detect
from . import impl
from . import util


if typing.TYPE_CHECKING:
    from typing import Any, Final


@dataclasses.dataclass
class ConfigHolder:
    """Hold a `Config` object."""

    cfg: defs.Config | None = None
    """The `Config` object stashed by the main function."""


def extract_cfg(ctx: click.Context) -> defs.Config:
    """Extract the `Config` object that the main function built."""
    cfg_hold: Final = ctx.find_object(ConfigHolder)
    if cfg_hold is None:
        sys.exit("Internal error: no click config holder object")

    cfg: Final = cfg_hold.cfg
    if cfg is None:
        sys.exit("Internal error: no config in the click config holder")

    return cfg


def arg_features(_ctx: click.Context, _self: click.Parameter, value: bool) -> bool:  # noqa: FBT001
    """Display program features information and exit."""
    if not value:
        return value

    print("Features: " + " ".join(f"{name}={value}" for name, value in defs.FEATURES.items()))
    sys.exit(0)


def encode_to_json(obj: Any) -> Any:  # noqa: ANN401  # yep, Any is what we need here
    """Turn something into something else, mmkay."""
    if dataclasses.is_dataclass(type(obj)):
        return {name: encode_to_json(value) for name, value in dataclasses.asdict(obj).items()}

    if isinstance(obj, pathlib.Path):
        return str(obj)

    if isinstance(obj, dict):
        return {name: encode_to_json(value) for name, value in obj.items()}

    if isinstance(obj, list):
        return [encode_to_json(value) for value in obj]

    return obj


@click.command(name="detect")
@click.option(
    "--use-prefix",
    is_flag=True,
    help="query the Python interpreter within the environment for its prefix",
)
@click.argument(
    "venvdir",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        exists=True,
        readable=True,
        executable=True,
        path_type=pathlib.Path,
        resolve_path=True,
    ),
)
@click.pass_context
def cmd_detect(ctx: click.Context, *, use_prefix: bool, venvdir: pathlib.Path) -> None:
    """Examine a virtual environment."""
    cfg: Final = extract_cfg(ctx)

    detected: Final = detect.detect_path(cfg, venvdir, use_prefix=use_prefix)
    print(json.dumps(detected, indent=2, default=encode_to_json))


@click.command(name="retarget")
@click.option(
    "--venvdst",
    "-d",
    type=click.Path(path_type=pathlib.Path),
    help="the absolute path to retarget to, if not the same as the venv directory itself",
)
@click.option(
    "--venvsrc",
    "-s",
    type=click.Path(path_type=pathlib.Path),
    help="the absolute path to retarget from, if different from what is recorded into the venv",
)
@click.argument(
    "venvdir",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        exists=True,
        readable=True,
        executable=True,
        path_type=pathlib.Path,
        resolve_path=True,
    ),
)
@click.pass_context
def cmd_retarget(
    ctx: click.Context,
    *,
    venvsrc: pathlib.Path | None,
    venvdst: pathlib.Path | None,
    venvdir: pathlib.Path,
) -> None:
    """Examine a virtual environment."""
    cfg: Final = extract_cfg(ctx)

    impl.retarget(cfg, venvdir, venvsrc=venvsrc, venvdst=venvdst)


@click.group(name="venv-retarget")
@click.option(
    "--features",
    is_flag=True,
    is_eager=True,
    callback=arg_features,
    help="display program features information and exit",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="quiet operation; only display warning and error messages",
)
@click.option("--verbose", "-v", is_flag=True, help="verbose operation; display diagnostic output")
@click.pass_context
def main(ctx: click.Context, *, features: bool, quiet: bool, verbose: bool) -> None:
    """Prepare a virtual environment for moving to another directory."""
    if features:
        sys.exit("Internal error: how did we get to main() with features=True?")

    ctx.ensure_object(ConfigHolder)
    ctx.obj.cfg = defs.Config(log=util.build_logger(quiet=quiet, verbose=verbose), verbose=verbose)


main.add_command(cmd_detect)
main.add_command(cmd_retarget)


if __name__ == "__main__":
    main()
