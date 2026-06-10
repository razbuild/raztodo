# Testing

This document provides guidelines for running tests and maintaining code quality in the RazTodo project.

## Requirements

- This project requires **Python 3.10+**.
- [`uv`](https://docs.astral.sh/uv/) for environment management

## Setup

Clone the repository and install development dependencies (pytest, ty, ruff, coverage):

```bash
git clone https://github.com/razbuild/raztodo.git
cd raztodo
uv sync --editable --group dev --extra web
```

---

## Tools Used

* **Unit and Functional Testing:** [pytest](https://docs.pytest.org/)
* **Type Checking:** [ty](https://astral.sh/)
* **Formatting and Linting:** [ruff](https://docs.astral.sh/ruff/) for formatting and linting
* **Test Coverage:** [coverage](https://coverage.readthedocs.io/)

## Running Tests

All tests are in the `tests/` folder. Run from the project root:

```bash
# All tests (verbose)
uv run pytest -v

# Quiet mode
uv run pytest -q

# Single test file
uv run pytest tests/application/use_cases/test_create_task.py

# Single test function
uv run pytest tests/application/use_cases/test_create_task.py::TestCreateTaskUseCase::test_create_task_success

# By subfolder
uv run pytest tests/domain
uv run pytest tests/infrastructure
uv run pytest tests/presentation/web
```

## Checking Test Coverage

To see test coverage of your code:

```bash
uv run coverage run -m pytest
uv run coverage html
uv run coverage report
```

Open `htmlcov/index.html` in your browser to visualize coverage.

## Type Checking

Ensure type correctness using:

```bash
uv run ty check src/
```

## Formatting and Linting

### Code Formatting

```bash
uv run ruff format src/ tests/
```

### Linting and Error Checking

```bash
uv run ruff check --fix src/ tests/
```

Fix any errors reported by ruff before committing code.
