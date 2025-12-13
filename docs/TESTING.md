# Testing

This document provides guidelines for running tests and maintaining code quality in the RazTodo project.

## Requirements

This project requires **Python 3.14**.
Older Python versions are **not supported** and will not pass tests or static analysis **mypy**, **ruff**, **pytest**.

Install development dependencies:

* Python >= 3.13
* pytest
* mypy
* black
* ruff
* coverage

Install them using:

```bash
pip install pytest mypy black ruff coverage
# Or, if you cloned the project:
pip install .[dev]
```

## Tools Used

* **Unit and Functional Testing:** [pytest](https://docs.pytest.org/)
* **Type Checking:** [mypy](http://mypy-lang.org/)
* **Formatting and Linting:** [black](https://black.readthedocs.io/) and [ruff](https://beta.ruff.rs/docs/)
* **Test Coverage:** [coverage](https://coverage.readthedocs.io/)

## Running Tests

All tests are located in the `tests/` folder. Run tests from the project root directory:

```bash
# Run all tests with verbose output
pytest -v

# Run all tests with concise output
pytest -q

# Run specific test file
pytest tests/test_example.py

# Run specific test function
pytest tests/test_example.py::test_function_name
```

### Organizing Tests

Consider organizing tests by type:

```bash
pytest tests/domain
pytest tests/infrastructure
```

## Checking Test Coverage

To see test coverage of your code:

```bash
coverage run -m pytest
coverage report -m
coverage html  # optional: generates HTML report in htmlcov/ folder
```

Open `htmlcov/index.html` in your browser to visualize coverage.

## Type Checking

Ensure type correctness using:

```bash
mypy src/
```

You can configure strictness in a `mypy.ini` or `pyproject.toml`.

## Formatting and Linting

### Code Formatting

```bash
black src/ tests/
```

### Linting and Error Checking

```bash
ruff check src/ tests/
```

Fix any errors reported by ruff before committing code.
