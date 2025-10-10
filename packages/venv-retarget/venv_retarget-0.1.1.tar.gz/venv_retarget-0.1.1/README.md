<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# venv-retarget - prepare a virtual environment for moving to another directory

\[[Home][ringlet-home] | [Download][ringlet-download] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

## Overview

The `venv-retarget` tool modifies several files within a virtual environment so that
their contents will correspond to what the `venv` module would have done if that
virtual environment were created in a different directory.
This may be useful if a virtual environment is created with the intention of being
packaged and copied over to other systems in a shared path.

## Invocation

``` sh
venv-retarget [-qv] detect [--use-prefix] path/to/venv

venv-retarget [-qv] retarget
	[-d /dest/venv | --venvdst /dest/venv]
	[-s /source/venv | --venvsrc /source/venv]
	path/to/venv

venv-retarget --features

venv-retarget --help
```

### Detect the path stored into a virtual environment's files

The `detect` subcommand causes `venv-retarget` to examine the files within
the virtual environment and check several places where `venv` records
the path to the virtual environment:

- the `command = ...` line in the `pyvenv.cfg` file
- the paths to the source files stored in the precompiled `__pycache__/*.pyc` files
- if `--use-prefix` is specified, the `sys.prefix` value from the Python
  interpreter within the virtual environment

Note that the `sys.prefix` value will reflect the *current* location of the virtual
environment, so if it has already been moved, this path will differ from the rest and
result in the `detect` subcommand failing because of inconsistent paths.

### Change the paths to reflect a new location for the virtual environment

The main purpose of the `venv-retarget` tool is the `retarget` subcommand: look for
files within the virtual environment that record the source path (either specified with
the `-s` / `--venvsrc` command-line option, or autodetected as per the `detect` subcommand),
and modifies those files to refer to the destination path (either specified with
the `-d` / `--venvdst` command-line option, or the current path to the virtual environment).
This allows `retarget` to be used in three ways:

- after the virtual environment was created in a temporary location, in order to
  prepare to move it to either a temporary buildroot location or its final one
- after the virtual environment has been moved to a temporary buildroot location
- after the virtual environment has been moved to its final location

In each of the three cases, the source directly should generally not need to be specified.
In any but the last case, the destination directory should be specified, or
`venv-retarget` will record the temporary location of the virtual environment instead.

## Examples

Figure out what the files within a virtual environment think about where it is at:

``` sh
venv-retarget detect /path/to/venv
```

Prepare the files in an existing virtual environment to be moved somewhere else:

``` sh
venv-retarget retarget -d /usr/libexec/venvs/agent agent-venv
```

Update the files after a virtual environment has been moved:

``` sh
venv-retarget retarget -s /home/build/program/agent-venv buildroot/usr/libexec/venvs/agent
```

The same, but let the `venv-retarget` tool figure out the source directory by
examining the contents of the files within the virtual environment, e.g.
when the installation program was able to copy the files directly to
the destination directory instead of a temporary buildroot:

``` sh
venv-retarget retarget /usr/libexec/venvs/agent
```

## Contact

The `venv-retarget` tool was written by [Peter Pentchev][roam].
It is developed in [a GitLab repository][gitlab].
This documentation is hosted at [Ringlet][ringlet-home] with a copy at [ReadTheDocs][readthedocs].

[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[gitlab]: https://gitlab.com/ppentchev/venv-retarget "The venv-retarget GitLab repository"
[pypi]: https://pypi.org/project/venv-retarget/ "The venv-retarget Python Package Index page"
[readthedocs]: https://venv-retarget.readthedocs.io/ "The venv-retarget ReadTheDocs page"
[ringlet-home]: https://devel.ringlet.net/sysutils/venv-retarget/ "The Ringlet venv-retarget homepage"
[ringlet-download]: https://devel.ringlet.net/sysutils/venv-retarget/download/ "The Ringlet venv-retarget download page"
