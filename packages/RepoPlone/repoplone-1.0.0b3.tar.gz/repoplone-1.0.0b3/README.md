# RepoPlone

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/repoplone)](https://pypi.org/project/repoplone/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/repoplone)](https://pypi.org/project/repoplone/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/repoplone)](https://pypi.org/project/repoplone/)
[![PyPI - License](https://img.shields.io/pypi/l/repoplone)](https://pypi.org/project/repoplone/)
[![PyPI - Status](https://img.shields.io/pypi/status/repoplone)](https://pypi.org/project/repoplone/)


[![Code Quality](https://github.com/plone/repoplone/actions/workflows/main.yml/badge.svg)](https://github.com/plone/repoplone/actions/workflows/main.yml)

[![GitHub contributors](https://img.shields.io/github/contributors/plone/repoplone)](https://github.com/plone/repoplone)
[![GitHub Repo stars](https://img.shields.io/github/stars/plone/repoplone?style=social)](https://github.com/plone/repoplone)

</div>

## Overview

The **RepoPlone** is a tool designed to manage mono repos containing a `repository.toml` configuration file at the repository root.

It provides various commands to streamline repository management, versioning, and release processes.

## Setup

### Installation

To use the latest version of this tool, run the command:

```sh
uvx repoplone
```

### Authentications

#### PyPi

We use `uv` to make the release, please make sure authentication is in place by setting the environment variable `UV_PUBLISH_TOKEN`:

```sh
export UV_PUBLISH_TOKEN=<MYTOKEN>
```

or by using the `uv auth` command, as explained [here](https://docs.astral.sh/uv/concepts/authentication/cli/#the-uv-auth-cli).

#### NPM

```sh
npm whoami
```

#### GitHub

To add releases to GitHub, you should have an environment variable `GH_TOKEN` set -- with a valid token -- before running this tool.

```sh
export GH_TOKEN='<token>'
```

## Usage

### Prepare the repository

Ensure that your monorepo contains a `repository.toml` file. Below is an example of such a configuration:

```toml
[repository]
name = "fake-distribution"
changelog = "CHANGELOG.md"
version = "version.txt"
version_format = "semver"
compose = ["docker-compose.yml"]

[repository.towncrier]
section = "Project"
settings = "towncrier.toml"

[backend.package]
name = "fake.distribution"
path = "backend"
changelog = "backend/CHANGELOG.md"
towncrier_settings = "backend/pyproject.toml"
base_package = "Products.CMFPlone"
publish = false

[frontend.package]
name = "fake-distribution"
path = "frontend/packages/fake-distribution"
changelog = "frontend/packages/fake-distribution/CHANGELOG.md"
towncrier_settings = "frontend/packages/fake-distribution/towncrier.toml"
publish = false
```

### List Available Commands
To see all available commands, run:

```bash
uvx repoplone
```

### Check Installed Version
To check the installed version of the tool, use:

```bash
uvx repoplone --version
```

## Check repository versions

### Current versions

List current versions for:

- Repository
- Backend package
- Frontend package

```bash
uvx repoplone versions current
```

### Next versions

Report next version of all components of this repository:

- Repository
- Backend package
- Frontend package

```bash
uvx repoplone versions next
```

### Dependencies

Report version information for major dependencies:

- Backend base package
- Frontend base package
- Frontend @plone/volto package

```bash
uvx repoplone versions dependencies
```

## Preview Changelog

To generate and display the draft changelog, run:

```bash
uvx repoplone changelog
```

## Releasing Monorepo Packages

The `release` command creates a new release and accepts the following arguments:

#### `version`
The version argument defines the new version to be used in the release. It can be a specific version number or a version segment. Below is a reference table showing how version segments modify an existing `1.0.0` version:

| Segment | New Version |
|---------|------------|
| `release` | `1.0.0` |
| `major` | `2.0.0` |
| `minor` | `1.1.0` |
| `micro` / `patch` / `fix` | `1.0.1` |
| `a` / `alpha` | `1.0.0a0` |
| `b` / `beta` | `1.0.0b0` |
| `c` / `rc` / `pre` / `preview` | `1.0.0rc0` |
| `r` / `rev` / `post` | `1.0.0.post0` |
| `dev` | `1.0.0.dev0` |

#### `--dry-run`

Use this flag to simulate the release process without actually publishing the new version.

**Example:**

```bash
uvx repoplone release a
```

This will create an `alpha` release.

---

## Dependencies

### Manage backend's base package

The following commands are available exclusively for projects managed by UV and with a base_package set in the `[backend.package]` section of repository.toml.

#### Report the base package
To check which is the current base package, run:

```bash
uvx repoplone deps info
```

#### Check version
To check the current base package version, run:

```bash
uvx repoplone deps check
```

#### Upgrade version

To upgrade the base package to a specific version, use:

```bash
uvx repoplone deps upgrade 6.1.1
```

## Contribute 🤝

We welcome contributions to RepoPlone.

You can create an issue in the issue tracker, or contact a maintainer.

- [Issue Tracker](https://github.com/plone/repoplone/issues)
- [Source Code](https://github.com/plone/repoplone/)

### Development requirements

- [uv](https://docs.astral.sh/uv/)

### Setup

Clone this repository:

```sh
git clone git@github.com:plone/repoplone.git
```

Install `UV`, and create a local virtual environment with the following command.

```shell
make install
```

### Run the checked out branch of RepoPlone

```shell
uv run repoplone
```

### Check and format the codebase

```shell
make check
```

### Run tests

[`pytest`](https://docs.pytest.org/) is this package's test runner.

Run all tests with the following command.

```shell
make test
```

Run all tests, but stop on the first error and open a `pdb` session with the following command.

```shell
uv run pytest -x --pdb
```

Run only tests that match `test_release_backend` with the following command.

```shell
uv run pytest -k test_release_backend
```

Run only tests that match `test_release_backend`, but stop on the first error and open a `pdb` session with the following command.

```shell
uv run pytest -k test_release_backend -x --pdb
```

### Run type checker

We use [`mypy`](https://www.mypy-lang.org/) to run static type checking for this codebase.

Run the checker with the following command.

```shell
uv run mypy src
```


## Support 📢

For support, questions, or more detailed documentation, visit the [official RepoPlone repository](https://github.com/plone/repoplone).


## This project is supported by

<p align="left">
    <a href="https://plone.org/foundation/">
      <img alt="Plone Foundation Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-foundation.png">
    </a>
</p>

## License

The project is released under the [MIT License](./LICENSE).
