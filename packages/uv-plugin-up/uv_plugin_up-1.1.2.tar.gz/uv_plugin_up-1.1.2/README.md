<div align="center">
  <img alt="logo" src="https://github.com/pivoshenko/uv-plugin-up/blob/main/assets/logo.svg?raw=True" height=200>
</div>

<br>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img alt="License" src="https://img.shields.io/pypi/l/uv-plugin-up?style=flat-square&logo=opensourceinitiative&logoColor=white&color=0A6847&label=License">
  </a>
  <a href="https://pypi.org/project/uv-plugin-up">
    <img alt="Python" src="https://img.shields.io/pypi/pyversions/uv-plugin-up?style=flat-square&logo=python&logoColor=white&color=4856CD&label=Python">
  </a>
  <a href="https://pypi.org/project/uv-plugin-up">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/uv-plugin-up?style=flat-square&logo=pypi&logoColor=white&color=4856CD&label=PyPI">
  </a>
  <a href="https://github.com/pivoshenko/uv-plugin-up/releases">
    <img alt="Release" src="https://img.shields.io/github/v/release/pivoshenko/uv-plugin-up?style=flat-square&logo=github&logoColor=white&color=4856CD&label=Release">
  </a>
</p>

<p align="center">
  <a href="https://semantic-release.gitbook.io">
    <img alt="Semantic_Release" src="https://img.shields.io/badge/Semantic_Release-angular-e10079?style=flat-square&logo=semanticrelease&logoColor=white&color=D83A56">
  </a>
  <a href="https://pycqa.github.io/isort">
    <img alt="Imports" src="https://img.shields.io/badge/Imports-isort-black.svg?style=flat-square&logo=improvmx&logoColor=white&color=637A9F&">
  </a>
  <a href="https://docs.astral.sh/ruff">
    <img alt="Ruff" src="https://img.shields.io/badge/Style-ruff-black.svg?style=flat-square&logo=ruff&logoColor=white&color=D7FF64">
  </a>
  <a href="https://mypy.readthedocs.io/en/stable/index.html">
    <img alt="mypy" src="https://img.shields.io/badge/mypy-checked-success.svg?style=flat-square&logo=pypy&logoColor=white&color=0A6847">
  </a>
</p>

<p align="center">
  <a href="https://github.com/pivoshenko/uv-plugin-up/actions/workflows/tests.yaml">
    <img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/pivoshenko/uv-plugin-up/tests.yaml?label=Tests&style=flat-square&logo=pytest&logoColor=white&color=0A6847">
  </a>
  <a href="https://github.com/pivoshenko/uv-plugin-up/actions/workflows/linters.yaml">
    <img alt="Linters" src="https://img.shields.io/github/actions/workflow/status/pivoshenko/uv-plugin-up/linters.yaml?label=Linters&style=flat-square&logo=lintcode&logoColor=white&color=0A6847">
  </a>
  <a href="https://github.com/pivoshenko/uv-plugin-up/actions/workflows/release.yaml">
    <img alt="Release" src="https://img.shields.io/github/actions/workflow/status/pivoshenko/uv-plugin-up/release.yaml?label=Release&style=flat-square&logo=pypi&logoColor=white&color=0A6847">
  </a>
  <a href="https://codecov.io/gh/pivoshenko/uv-plugin-up" >
    <img alt="Codecov" src="https://img.shields.io/codecov/c/gh/pivoshenko/uv-plugin-up?token=cqRQxVnDR6&style=flat-square&logo=codecov&logoColor=white&color=0A6847&label=Coverage"/>
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/uv-plugin-up">
    <img alt="Downloads" src="https://img.shields.io/pypi/dm/uv-plugin-up?style=flat-square&logo=pythonanywhere&logoColor=white&color=4856CD&label=Downloads">
  </a>
  <a href="https://github.com/pivoshenko/uv-plugin-up">
    <img alt="Stars" src="https://img.shields.io/github/stars/pivoshenko/uv-plugin-up?style=flat-square&logo=apachespark&logoColor=white&color=4856CD&label=Stars">
  </a>
</p>

<p align="center">
  <a href="https://stand-with-ukraine.pp.ua">
    <img alt="StandWithUkraine" src="https://img.shields.io/badge/Support-Ukraine-FFC93C?style=flat-square&labelColor=07689F">
  </a>
</p>

## Overview

`uv-plugin-up` - is a plugin for automated dependency updates and version bumping in `pyproject.toml` files.

### Features

- Fully type-safe
- Automatically updates dependencies to their latest versions from PyPI
- Multiple dependency groups support - handles `project.dependencies`, `project.optional-dependencies`, and `dependency-groups`
- Selective updates - exclude specific packages from being updated
- Dry-run mode - preview changes without modifying files
- Safe updates - automatically runs `uv lock` after updates and rolls back on failure

## Installation

```bash
uv add --dev uv-plugin-up
# or
uv add uv-plugin-up --group dev
```

## Usage and Configuration

By default, the plugin updates all dependencies in the `pyproject.toml`:

```bash
uv-plugin-up
```

### Command-line Options

#### `filepath`

**Type**: `Path`

**Default**: `./pyproject.toml`

**Short flag**: `-f`

Specifies the path to the `pyproject.toml` file. If your project file is located elsewhere or has a different name, you can set this parameter.

#### `exclude`

**Type**: `str`

**Default**: `()`

**Multiple values**: `allowed`

Specifies packages to exclude from updating. You can provide multiple package names to prevent them from being updated.

#### `dry-run`

**Type**: `bool`

**Default**: `false`

Enables preview mode where changes are displayed without modifying the `pyproject.toml` file. This is useful for reviewing what would be updated before applying changes.

## Examples

```bash
uv-plugin-up --exclude click

# Updating dependencies in 'project' group
# Skipping 'click>=8.1.8' (excluded)
# Skipping 'httpx>=0.28.1' (no new version available)
# Skipping 'tomlkit>=0.13.3' (no new version available)
# Updating dependencies in 'dependency-groups' group
# Skipping 'python-semantic-release~=10.4.1' (no new version available)
# Skipping 'poethepoet>=0.37.0' (no new version available)
# Skipping 'pyupgrade>=3.21.0' (no new version available)
# Skipping 'ruff>=0.14.0' (no new version available)
# Skipping 'commitizen>=4.9.1' (no new version available)
# Skipping 'mypy>=1.18.2' (no new version available)
# Skipping 'ruff>=0.14.0' (no new version available)
# Skipping 'coverage[toml]>=7.10.7' (no new version available)
# Excluding dependency 'pytest'
# Skipping 'pytest==7.4.4' (no new version available)
# Skipping 'pytest-cov>=7.0.0' (no new version available)
# Skipping 'pytest-lazy-fixture>=0.6.3' (no new version available)
# Skipping 'pytest-mock>=3.15.1' (no new version available)
# Skipping 'pytest-sugar>=1.1.1' (no new version available)
# Skipping 'sh>=2.2.2' (no new version available)
# Skipping 'xdoctest>=1.3.0' (no new version available)
```
