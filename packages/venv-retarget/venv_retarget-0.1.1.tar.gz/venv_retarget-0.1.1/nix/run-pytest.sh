#!/bin/sh
#
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

set -e

: "${PY_MINVER_MIN:=11}"
: "${PY_MINVER_MAX:=14}"

: "${PY_VENV_MINVER_MIN:=10}"
: "${PY_VENV_MINVER_MAX:=14}"

for pyver in $(seq -- "$PY_MINVER_MIN" "$PY_MINVER_MAX"); do
	for pyver_venv in $(seq -- "$PY_VENV_MINVER_MIN" "$PY_VENV_MINVER_MAX"); do
		nix/cleanpy.sh
		printf -- '\n===== Running tests for 3.%s and 3.%s in the venv\n\n\n' "$pyver" "$pyver_venv"
		nix-shell --pure --argstr py-ver "$pyver" --argstr py-venv-ver "$pyver_venv" nix/python-pytest.nix
		printf -- '\n===== Done with 3.%s and 3.%s\n\n' "$pyver" "$pyver_venv"
	done
done
