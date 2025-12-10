# Contributing to RazTodo

Thank you for your interest in contributing! This guide will help you get started.

---

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/raztodo.git
cd raztodo
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install with dev dependencies
pip install -e .[dev]
```

### 3. Verify Setup

```bash
rt --help
pytest
```

---

## Development Workflow

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Make Changes

1. Write your code
2. Add tests for new features
3. Update documentation if needed

### Run Quality Checks

Before committing, ensure all checks pass:

```bash
# Run tests
pytest

# Check formatting
black --check src/ tests/

# Run linter
ruff check src/ tests/

# Type checking
mypy src/
```

### Fix Issues Automatically

```bash
# Format code
black src/ tests/

# Fix linting issues
ruff check --fix src/ tests/
```

---

## Code Style

### General Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all functions
- Keep functions small and focused
- Write descriptive variable names

### Example

```python
def create_task(
    title: str,
    description: str = "",
    priority: str | None = None,
) -> int:
    """
    Create a new task.

    Args:
        title: Task title (required)
        description: Task description
        priority: Priority level (L, M, H)

    Returns:
        The ID of the created task
    """
    ...
```

---

## Project Structure

```
src/raztodo/
├── domain/          # Business logic, entities
├── application/     # Use cases
├── infrastructure/  # Database, logging, config
└── presentation/    # CLI commands
```

See [Architecture](docs/ARCHITECTURE.md) for details.

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Tests

```bash
# Single file
pytest tests/domain/test_task_entity.py

# Single test
pytest tests/domain/test_task_entity.py::test_create_task

# With coverage
coverage run -m pytest
coverage report -m
```

### Writing Tests

- Place tests in `tests/` mirroring `src/` structure
- Name test files `test_*.py`
- Name test functions `test_*`

---

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add due date filtering to list command
fix: handle empty tags in task creation
docs: update installation guide
test: add tests for search functionality
refactor: simplify task repository
```

### Prefixes

| Prefix | Use for |
|--------|---------|
| `feat` | New features |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Code refactoring |
| `chore` | Maintenance tasks |

---

## Pull Request Process

1. **Update your branch** with latest master:
   ```bash
   git fetch origin
   git rebase origin/master
   ```

2. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request** on GitHub

4. **Fill out the PR template** with:
   - Description of changes
   - Type of change
   - Related issues

5. **Wait for review** and address feedback

---

## Reporting Issues

### Bug Reports

Include:
- Steps to reproduce
- Expected vs actual behavior
- OS and Python version
- RazTodo version (`raztodo --version`)

### Feature Requests

Include:
- Clear description
- Use case / why it's useful
- Proposed solution (optional)

---

## Questions?

- Check existing [Issues](https://github.com/razbuild/raztodo/issues)

---

Thank you for contributing!

