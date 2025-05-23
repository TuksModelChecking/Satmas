# Satmas

Multi-Agent Resource Allocation using PySAT.

This project uses `uv` for dependency management and task running.

## Prerequisites

- Python >=3.8 (as specified in [pyproject.toml](pyproject.toml))
- `uv` (the Python package installer and resolver)

If you don't have `uv`, please install it first. You can find installation instructions on the [official `uv` documentation](https://docs.astral.sh/uv/getting-started/).

## Setup

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/TuksModelChecking/Satmas.git
    cd satmas
    ```

2.  **Install dependencies**:
    This command will create a virtual environment (if one doesn't exist) and install all project dependencies specified in [pyproject.toml](pyproject.toml).

    ```bash
    uv sync
    ```

3.  **Install development dependencies**:
    To install development dependencies, including `pytest` for running tests:
    ```bash
    uv pip install -e ".[dev]"
    ```

## Running Tests

The project uses `pytest` for testing. Test files are located in the `tests/` directory.

To run all tests:

```bash
uv run pytest
```

Pytest configuration can be found in the `[tool.pytest.ini_options]` section of the [pyproject.toml](pyproject.toml) file.

## Running Examples

A minimal example is provided in the [examples/minimal/](examples/minimal/) directory.

To run the minimal example ([examples/minimal/minimal_example.py](examples/minimal/minimal_example.py)):

```bash
uv run python examples/minimal/minimal_example.py
```

This example uses the configuration from [examples/minimal/minimal_example.yml](examples/minimal/minimal_example.yml).

## Legacy Code

The `__legacy/` directory contains a previous version of this project's implementation. This code is archived for reference and is not part of the current, refactored codebase. For more information on the legacy system, please see the [\_\_legacy/README.md](__legacy/README.md) file.
