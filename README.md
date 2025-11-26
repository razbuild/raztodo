<p align="center">
    <img src="src/raztodo/assets/logo.png" alt="Project Logo" width="500">
</p>

<p align="center">

  <img alt="GitHub License" src="https://img.shields.io/github/license/razbuild/raztodo?style=flat&logoSize=auto&labelColor=333333&color=66ffff&cacheSeconds=3600">

  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/formatcheck.yml?branch=master&event=push&style=flat&logoSize=auto&label=black&labelColor=333333&color=666666&cacheSeconds=3600">

  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/lint.yml?branch=master&event=push&style=flat&logoSize=auto&label=ruff&labelColor=333333&color=blue&cacheSeconds=3600">

  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/typecheck.yml?branch=master&event=push&style=flat&logoSize=auto&label=mypy&labelColor=333333&color=violet&cacheSeconds=3600">

  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/test.yml?branch=master&event=push&style=flat&logoSize=auto&labelColor=333333&color=66ff66&cacheSeconds=3600">

  <img alt="Codecov (with branch)" src="https://img.shields.io/codecov/c/github/razbuild/raztodo/master?style=flat&logoSize=auto&labelColor=333333&cacheSeconds=%203600">

</p>

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](/docs/ARCHITECTURE.md)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Task Management:** Add, update, remove, list, mark as done, set due dates, manage tags and projects, edit tasks, set priority.
- **Search:** Full-text search across tasks.
- **Pagination:** Paginated listings for long task lists.
- **Terminal Output:** Optional colored output with ANSI and icons.
- **Data Import/Export:** Export and import tasks via [JSON](https://www.json.org/json-en.html).
- **Storage:** Persistent storage with [SQLite](https://sqlite.org) (no external services required).
- **Logging:** Configurable logging via environment variables.
- **Database Migration:** Run database migrations.
- **Cross-Platform:** Supports Linux, macOS, and Windows.


---

## Requirements

| Requirement | Details |
|-------------|---------|
| Python      | 3.9+ |
| Dependencies| None (zero external dependencies) |

---

## Installation

### From PyPI
```bash
pip install raztodo
```

### Local Development
```bash
git clone https://github.com/razbuild/raztodo.git
cd raztodo
pip install -e .
# or (if you prefer isolating CLI)
pipx install .
```

---

## Usage

### Example Workflow
```bash
# Add
raztodo add "Buy groceries" "Milk, eggs, bread"
raztodo add "Read a book"

# List
raztodo list

# Update
raztodo update 1 --title "Buy groceries & snacks" --desc "Milk, eggs, bread, chips"

# Show
raztodo show 1

# Search
raztodo search "book"

# Remove
raztodo remove 2

# JSON export/import
raztodo export tasks.json
raztodo import tasks.json
```

### Global Options

| Option | Description |
|--------|-------------|
| `--no-color` | Disable colored output |
| `--db path/to/db.sqlite` | Use custom database path (default: `~/.local/share/raztodo/tasks.db`) |

---

## Configuration

| Variable | Description |
|----------|-------------|
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `RAZTASK_DB` | Default database path (default: `~/.local/share/raztodo/tasks.db`) |

You can set these environment variables in your shell or in a `.env` file.

### Virtual Environment Setup

To keep dependencies isolated, it's recommended to use a virtual environment.  
You can read more in the official Python documentation:  
[Creating Virtual Environments](https://docs.python.org/3/library/venv.html)

#### For Linux & macOS
```bash
python -m venv venv
source venv/bin/activate
```

#### For Windows
```bash
python -m venv venv
venv\Scripts\activate
```

---

## Project Structure

```
raztodo/
│
├── src/raztodo/
│   ├── core/       # Core logic and data management
│   │   ├── storage.py
│   │   └── logger.py
│   ├── cli/        # CLI commands and terminal colors
│   │   ├── commands.py
│   │   └── colors.py
│   ├── __main__.py
│   └── __init__.py
│
├── tests/          # Unit tests for core and CLI modules
│   ├── core/
│   │   ├── storage.py
│   │   └── logger.py
│   └── cli/
│       ├── commands.py
│       └── colors.py
│
└── README.md
```

---

## Running Tests

Install testing and formatting tools:
```bash
pip install pytest ruff black
```

Run tests, check code style, and format code:
```bash
pytest tests/ && ruff check src/ && black --check src/ tests/
```

Format code automatically:
```bash
black src/ tests/
```

---

## Contributing

Contributions, issues, and feature requests are welcome. You can open a pull request or an issue.

Before contributing:
- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for code style.
- Run tests locally to ensure everything works.

---

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/razbuild/raztodo/blob/main/LICENSE) file for details.

