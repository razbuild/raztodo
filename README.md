![Logo](https://raw.githubusercontent.com/razbuild/raztodo/master/assets/logo.png)

![GitHub License](https://img.shields.io/github/license/razbuild/raztodo?logoColor=ffffff&logoSize=auto&label=License&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml?branch=master&event=push&logo=githubactions&logoColor=ffffff&logoSize=auto&label=Build&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)
![Codecov](https://img.shields.io/codecov/c/github/razbuild/raztodo?logo=codecov&logoColor=ffffff&logoSize=auto&label=Coverage&labelColor=1b1b1b&color=ba0000&cacheSeconds=3600)
![PyPI - Version](https://img.shields.io/pypi/v/raztodo?pypiBaseUrl=https%3A%2F%2Fpypi.org&logo=pypi&logoColor=ffffff&logoSize=auto&label=PyPi&labelColor=1b1b1b&color=ba0000&cacheSeconds=3600)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Frazbuild%2Fraztodo%2Fmain%2Fpyproject.toml&logo=python&logoColor=ffffff&logoSize=auto&label=Python&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)


---

RazTodo is a lightweight and cross-platform CLI tool for efficient todo and task management, using SQLite as its storage backend.

| Preview |
|:-------:|
| <img src="https://raw.githubusercontent.com/razbuild/raztodo/master/assets/preview.gif" alt="Preview"> |

## Features

- **Task Management** — Add, update, remove, list, and mark tasks as done, clear tasks
- **Tags & Projects** — Organize tasks with tags and project names
- **Search** — Full-text search across all tasks
- **Due Dates & Priority** — Set deadlines and priority levels L | M | H
- **Import/Export** — Backup and restore tasks via **JSON**
- **Colored Output** — Beautiful **ANSI** colors and icons
- **SQLite Storage** — No external services required
- **Cross-Platform** — Works on **Linux**, **macOS**, and **Windows**
- **Fast Performance** — Lazy loading and optimized architecture
- **Clean Architecture** — Maintainable and testable codebase

---

## Quick Start

### Installation

```bash
# Recommended for CLI usage
pipx install raztodo

# Or install via pip 
pip install raztodo
```

> For more installation options, see [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)

### Basic Usage

```bash
# Create a task
rt add "Buy groceries" --priority H --due 2024-12-31

# List all tasks
rt list

# Mark as done
rt done 1

# Search
rt search "groceries"
```

> For complete command reference, see [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md)

---

## Commands

| Command | Description |
|---------|-------------|
| `add` | Create a new task |
| `list` | List tasks with filters |
| `update` | Update a task |
| `done` | Mark task as done/undone |
| `remove` | Delete a task |
| `search` | Search tasks |
| `export` | Export to JSON |
| `import` | Import from JSON |
| `migrate` | Run database migration |
| `clear` | Delete all tasks |

```bash
# Get help for any command
rt --help
rt add --help
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RAZTODO_DB` | Database path | `tasks.db` |
| `LOG_LEVEL` | Logging level | `ERROR` |

> For detailed configuration, see [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)

---

## Documentation

- [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md) — Install via pip, pipx, or from source
- [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md) — Complete command reference
- [Configuration](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md) — Environment variables and options
- [Architecture](https://github.com/razbuild/raztodo/blob/master/docs/ARCHITECTURE.md) — Project structure and design
- [Testing](https://github.com/razbuild/raztodo/blob/master/docs/TESTING.md) — Running tests and contributing
- [Changelog](https://github.com/razbuild/raztodo/blob/master/CHANGELOG.md) — Release notes and version history

---

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run quality checks:
   ```bash
   pytest
   ruff check src/ tests/
   black --check src/ tests/
   mypy src/
   ```
4. Submit a pull request

For detailed guidelines, see [Contributing Guide](https://github.com/razbuild/raztodo/blob/master/CONTRIBUTING.md).

---

## License

MIT License
