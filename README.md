<p align="center">
    <img src="src/raztodo/assets/logo.png" alt="RazTodo Logo" width="300">
</p>

<p align="center">
    <strong>A fast, zero-dependency command-line task manager powered by SQLite</strong>
</p>

<p align="center">
  <img alt="GitHub License" src="https://img.shields.io/github/license/razbuild/raztodo?style=for-the-badge&labelColor=ffffff&color=000000">
  <img alt="Python" src="https://img.shields.io/badge/python-3.14+-000000?style=for-the-badge&labelColor=ffffff">
  <img alt="Codecov (with branch)" src="https://img.shields.io/codecov/c/github/razbuild/raztodo/master?style=for-the-badge&logoSize=auto&label=coverage&labelColor=ffffff&color=000000&cacheSeconds=3600">
</p>

<p align="center">
  <a href="https://github.com/razbuild/raztodo/actions/workflows/ci.yml">
  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml?branch=master&event=push&style=for-the-badge&logoSize=auto&label=ci&labelColor=ffffff&color=000000&cacheSeconds=3600">

  </a>
</p>

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

> For more installation options, see [Installation Guide](docs/INSTALLATION.md)

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

> For complete command reference, see [Usage Guide](docs/USAGE.md)

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

> For detailed configuration, see [Configuration Guide](docs/CONFIGURATION.md)

---

## Documentation

- [Installation Guide](docs/INSTALLATION.md) — Install via pip, pipx, or from source
- [Usage Guide](docs/USAGE.md) — Complete command reference
- [Configuration](docs/CONFIGURATION.md) — Environment variables and options
- [Architecture](docs/ARCHITECTURE.md) — Project structure and design
- [Testing](docs/TESTING.md) — Running tests and contributing

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest && ruff check src/ && black --check src/`
4. Submit a pull request

---

## License

MIT License — see [LICENSE](LICENSE) for details.
