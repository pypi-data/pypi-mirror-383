<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the venv-retarget project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-10-10

### Fixes

- Test framework:
    - also test with virtual environments created using `uv`

### Additions

- Build framework:
    - mark Python 3.14 as supported
- Test framework:
    - add the `run-uvoxen` helper tool for testing with all supported Python versions
- Documentation:
    - link to the download page
- Nix test framework:
    - add Python 3.14
    - add `uv` as a dependency now that the test suite uses it

### Other changes

- Build framework:
    - switch to a PEP 639 license specification, bump the `hatchling`
      dependency version to 0.26 to support it
    - move the runtime dependencies into the `pyproject.toml` file
    - use PEP 735 dependency groups for the documentation and
      test suite dependencies
- Test framework:
    - switch to `uvoxen` for generating and running the tests
    - allow some new dependency versions
    - bump some lower requirements for dependency versions for `uv --resolution=lowest`
    - only use `pytest` 8.x
    - use `ruff` 0.14.0 with no changes
    - simplify some unit test functions
- Nix test framework:
    - drop Python 3.9, it was dropped from `nixpkgs/unstable`

## [0.1.0] - 2024-11-15

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/venv-retarget/-/compare/release%2F0.1.1...main
[0.1.1]: https://gitlab.com/ppentchev/venv-retarget/-/tags/release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/venv-retarget/-/tags/release%2F0.1.0
