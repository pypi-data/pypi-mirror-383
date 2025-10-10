#!/bin/sh
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

set -e

: "${UV:=uv}"
: "${UVOXEN:=uvoxen}"

run()
{
	echo "Running $UVOXEN with the default Python version"
	"$UVOXEN" uv run

	echo 'Obtaining the list of supported Python versions'
	local venv_py_versions=''
	venv_py_versions="$("$UVOXEN" list pythons)"
	echo "- got $venv_py_versions"

	local venv_py_ver=''
	# Hardcode some additional versions for now
	for venv_py_ver in '3.9' '3.10' $venv_py_versions; do
		echo "Making sure Python $venv_py_ver is available"
		if ! "$UV" python find --no-project -- "$venv_py_ver" > /dev/null 2>&1; then
			"$UV" python install -- "$venv_py_ver"
		fi

		local venv_py_path=''
		venv_py_path="$("$UV" python find --no-project -- "$venv_py_ver")"
		echo "- found at $venv_py_path"
		env \
			VENV_PYTHON="$venv_py_path" \
			"$UVOXEN" \
				-p supported \
				uv run -e mypy,unit-tests
	done
}

run
