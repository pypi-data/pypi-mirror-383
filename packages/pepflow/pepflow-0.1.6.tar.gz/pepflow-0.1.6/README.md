# PEPFlow: Performance Estimation Problem Workflow

[![CI](https://github.com/BichengYing/pepper/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/BichengYing/pepper/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

TODO

## Development Guide

We use `uv` to manage the packages and python enviromnents. To start 

```bash
uv sync; source .venv/bin/activate;
```

In windows, use `.venv\Scripts\activate` instead.

### Lint & Testing
We use `ruff` to do the format and lint and `isort` to do the import ordering.

```bash
ruff format;
ruff check .;
isort .;
```

We use `pytest` framework to do the test. To run all unit tests, run the following command:

```bash
pytest -s -vv pepflow
```

We have a convenient script to above
```bash
scripts/check.sh [format|lint|typecheck|test]
```
See the script for the options.

### Build doc website

Install the required library (one-time) and `pandoc` in order to build ipynb.
```bash
pip install -r docs/requirements.txt
```

To build the website, run
```bash
scripts/build_doc.sh [--serve-only]
```
The argument `--serve-only` is optional for hosting the website locally.



