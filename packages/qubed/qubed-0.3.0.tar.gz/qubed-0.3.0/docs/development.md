# Development


## Installation

To install the latest stable release from PyPI (recommended):

```bash
pip install "qubed[cli,stac_server,docs,dev]"
```
Delete optional feature dependencies as appropriate.


To install the latest version from github (requires a rust tool chain):

```bash
pip install qubed@git+https://github.com/ecmwf/qubed.git@main
```

To build the develop branch from source
1. Install a rust toolchain
2. `pip install maturin` then run:

```
git clone -b develop git@github.com:ecmwf/qubed.git
cd qubed
maturin develop
```

## Pre-commit hooks

The repo comes with a `.pre-commit-config.yaml` that should be used to format the code before commiting. See [the pre-commit docs](https://pre-commit.com/) but the gist is:

```bash
pip install pre-commit
pre-commit install # In the root of this repo
```

## CI

The tests are in `./tests`.  The CI is setup using tox to run the tests in a few different environments, they are currently:

* python 3.13
* python 3.12
* python 3.11
* python 3.12 with numpy version 1.x as opposed to version 2.x which is used by default.


## Git Large File Storage

This repo uses git Large file storage to store some qubes larger than 100MB. These files are not downloaded by `git clone` by default. In order to download them do, for example:
```bash
git lfs pull --include="tests/example_qubes/climate-dt/ten_yearly/climate-dt-1990-2000.cbor" --exclude=""
```

That these files are not downloaded by default is controlled the contents of `.lfsconfig`

You can use `git lfs ls-files` to see which files are currently tracked by lfs.

## Docs

The docs are built with sphinx with a plugin that allows code the run and the output to be saved into the docs. This code can break when you update qubed so use `docs/test_docs.sh` to check it hasn't broken. The CI also has a job to check for this.
