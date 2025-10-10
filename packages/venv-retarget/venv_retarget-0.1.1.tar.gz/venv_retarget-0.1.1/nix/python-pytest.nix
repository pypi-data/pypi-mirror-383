# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? import <nixpkgs> { }
, py-ver ? "11"
, py-venv-ver ? "9"
}:
let
  python-name = "python3${py-ver}";
  python = builtins.getAttr python-name pkgs;
  python-venv-name = "python3${py-venv-ver}";
  python-venv = builtins.getAttr python-venv-name pkgs;
  python-pkgs = python.withPackages (p: with p; [ click pytest ]);
in
pkgs.mkShell {
  buildInputs = [
    python-pkgs
    python-venv
    pkgs.uv
  ];
  shellHook = ''
    set -e
    PYTHONPATH="$(pwd)/src" VENV_PYTHON=python3.${py-venv-ver} python3.${py-ver} -m pytest -v tests/unit
    exit
  '';
}
