![Logo](https://raw.githubusercontent.com/razbuild/raztodo/master/src/raztodo/assets/logo.png)

![GitHub License](https://img.shields.io/github/license/razbuild/raztodo?logoSize=auto&cacheSeconds=3600)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml?branch=master&event=push&logoSize=auto&cacheSeconds=3600)
![Codecov (with branch)](https://img.shields.io/codecov/c/github/razbuild/raztodo/master?logoSize=auto&cacheSeconds=3600)

RazTodo is a fast, zero-dependency command-line task manager powered by SQLite.

---

## Features

- **Task Management** — Add, update, remove, list, and mark tasks as done
- **Tags & Projects** — Organize tasks with tags and project names
- **Search** — Full-text search across all tasks
- **Due Dates & Priority** — Set deadlines and priority levels (L/M/H)
- **Import/Export** — Backup and restore tasks via JSON
- **Colored Output** — Beautiful ANSI colors and icons
- **SQLite Storage** — No external services required
- **Cross-Platform** — Works on Linux, macOS, and Windows

---

## Quick Start

### Installation

```bash
pip install raztodo
```

> For more installation options, see [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)

### Basic Usage

```bash
# Create a task
raztodo add "Buy groceries" --priority H --due 2024-12-31

# List all tasks
raztodo list

# Mark as done
raztodo done 1

# Search
raztodo search "groceries"
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

```bash
# Get help for any command
raztodo --help
raztodo add --help
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

- [Installation Guide](https://github.com/razbuild/raztodo/blob/main/docs/INSTALLATION.md) — Install via pip, pipx, or from source
- [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md) — Complete command reference
- [Configuration](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md) — Environment variables and options
- [Architecture](https://github.com/razbuild/raztodo/blob/master/docs/ARCHITECTURE.md) — Project structure and design
- [Testing](https://github.com/razbuild/raztodo/blob/master/docs/TESTING.md) — Running tests and contributing

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest && ruff check src/ && black --check src/`
4. Submit a pull request

---

## License

MIT License — see [LICENSE](https://github.com/razbuild/raztodo/blob/master/LICENSE) for details.
