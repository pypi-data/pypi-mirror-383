# Advent of Code Module

[![aoc-mod](https://github.com/cosmos1255/aoc_mod/actions/workflows/build_wheel.yml/badge.svg)](https://github.com/cosmos1255/aoc_mod/actions/workflows/build_wheel.yml)

A library for Advent of Code containing utilities to use while solving problems!

If any issues or bugs are discovered, please submit an issue and I'll fix it!

## About

The design of this project is meant to facilitate the full problem solution flow of Advent of Code puzzles without ever having to utilize the web browser (after the initial step of authenticating with Advent of Code and getting the session id, of course).

## Installation with Poetry

The build system has been updated to utilize poetry for installation, building, and dependency management. To install/build locally, install the poetry build system through `pipx`.

```sh
# install pipx
sudo apt install pipx

# install poetry
pipx install poetry
```

Once poetry is installed, the following commands can be used to install, build, and run unit tests locally.

```sh
# install the library
poetry install

# build a wheel
poetry build

# run the tests
poetry run pytest
```

Formatting and linting is also available through `ruff`.

```sh
# run a linter check
poetry run ruff check

# run a linter check and correct issues
poetry run ruff check --fix

# format the code
poetry run ruff format
```

Some vulnerability scanning is also available with `bandit`.

```sh
poetry run bandit -c pyproject.toml -r .
```

## Documentation

The documentation is managed and built using Sphinx through the Poetry build system. To build the documentation and open it, run the following commands:

```bash
poetry run sphinx-build -M html docs/source/ docs/build/
firefox docs/build/html/index.html
```

## Getting and Using the SESSION_ID

The `SESSION_ID` is necessary to perform advanced operations like getting puzzle input and
submitting puzzle answers. Without this variable, the only operations available are getting basic
puzzle instructions and setting up a solution template file.

| Feature | `session-id` | no `session-id` |
|:--:|:--:|:--:|
| Get puzzle instructions | full support | partial support |
| Get puzzle input | full support | no support |
| Submit puzzle solutions | full support | no support |
| Setup puzzle solution folder | full support | full support |

In order to obtain this variable, authenticate with <https://adventofcode.com> and then press `F12` in the browser and navigate to the Application or Storage Tabs, if they exist, and search the cookies for the `session` or `sessionid` value.

**NOTE: The session id value is a unique key for your own authenticated session with Advent of Code. You should protect it like a password and never share it (i.e. never push a session id to GitHub or store in an insecure location).**
