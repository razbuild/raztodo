<div align="center">
  <img src="assets/RazTodo.svg" alt="RazTodo" width="400" />
  <br><br>

[![License](https://img.shields.io/github/license/razbuild/raztodo)](https://github.com/razbuild/raztodo/blob/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/raztodo)](https://pypi.org/project/raztodo/)
[![CI](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml)](https://github.com/razbuild/raztodo/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/razbuild/raztodo)](https://codecov.io/gh/razbuild/raztodo)
[![Python Versions](https://img.shields.io/pypi/pyversions/raztodo)](https://pypi.org/project/raztodo/)
[![PyPI Downloads](https://static.pepy.tech/badge/raztodo)](https://pepy.tech/project/raztodo)

  <p>A fast, local-first task manager with a CLI and an optional web UI, backed by SQLite.</p>
</div>

---

## Preview

<p align="center">
  <img src="https://raw.githubusercontent.com/razbuild/raztodo/master/assets/preview.gif" alt="Preview">
</p>

---

## Why RazTodo?

**Lightweight & Fast** — Single runtime dependency, SQLite-powered, optimized for speed  
**Privacy-First** — Your data stays local, no cloud, no tracking  
**Developer-Friendly** — Clean Architecture, well-tested, type-safe, modern Python  
**Simple & Powerful** — Intuitive CLI with an optional web UI  
**Cross-Platform** — Works on Linux, macOS, and Windows  

---

## Ecosystem

RazTodo is part of the [RazBuild](https://github.com/razbuild) ecosystem of open-source developer tools.

- [RazTint](https://github.com/razbuild/raztint) — Zero-dependency ANSI colors, icons, and terminal formatting utilities powering RazTodo's CLI output.

---

## Installation

```bash
# Recommended: isolated environment via pipx
pipx install raztodo

# Or via pip
pip install raztodo

# With optional web UI
pip install "raztodo[web]"

# With shell completion support
pip install "raztodo[completion]"
```

> 📖 For virtual environment and source installation, see the [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)

---

## Quick Start

### CLI

```bash
# Add a task
rt add "Buy groceries" --priority H --due 2026-12-31

# List all tasks
rt list

# Mark as done
rt done 1

# Search
rt search "groceries"

# Update
rt update 1 --title "Buy groceries and milk"

# Delete
rt remove 1
```

### Web UI

```bash
# Requires raztodo[web]
rt-web
```

Opens a single-page interface in your browser for creating, listing, searching, completing, deleting, importing, and exporting tasks.

### Shell Completion

```bash
# Requires raztodo[completion]
eval "$(rt completion bash)"
```

Supports bash, zsh, and fish. For permanent setup see the [Completion Guide](https://github.com/razbuild/raztodo/blob/master/docs/COMPLETION.md).

---

## Features

- 📝 **Task Management** — Create, update, complete, and delete tasks
- 🏷️ **Tags & Projects** — Organize tasks with tags and project names
- 🔍 **Search** — Filter by keyword with optional scope controls
- 📅 **Due Dates & Priority** — Deadlines and priority levels (L/M/H)
- 💾 **Import/Export** — Backup and restore via JSON
- 🌐 **Web UI** — Optional single-page FastAPI interface via `rt-web`
- 🎨 **Colored Output** — ANSI colors and icons via RazTint
- 🗄️ **SQLite Storage** — No external services required
- 🚀 **Cross-Platform** — Linux, macOS, and Windows
- ⚡ **Fast** — Lazy loading and optimized query layer
- ✨ **Shell Autocompletion** — Tab completion for bash, zsh, and fish

---

## Commands

| Command      | Description                            | Example                             |
|--------------|----------------------------------------|-------------------------------------|
| `add`        | Create a new task                      | `rt add "Task" --priority H`        |
| `list`       | List tasks with filters                | `rt list --pending --priority H`    |
| `update`     | Update a task                          | `rt update 1 --title "New title"`   |
| `done`       | Toggle task done/undone                | `rt done 1`                         |
| `remove`     | Delete a task                          | `rt remove 1`                       |
| `search`     | Search tasks by keyword                | `rt search "keyword"`               |
| `export`     | Export tasks to JSON                   | `rt export backup.json`             |
| `import`     | Import tasks from JSON                 | `rt import backup.json`             |
| `migrate`    | Run database migrations                | `rt migrate`                        |
| `clear`      | Delete all tasks                       | `rt clear --confirm`                |
| `completion` | Output shell completion script         | `rt completion bash`                |

```bash
rt --help
rt add --help
```

> 📖 See the [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md) for full command documentation.

---

## Configuration

| Variable     | Description                   | Default    |
|--------------|-------------------------------|------------|
| `RAZTODO_DB` | Database filename or path     | `tasks.db` |
| `LOG_LEVEL`  | Logging level                 | `ERROR`    |

```bash
export RAZTODO_DB="/path/to/custom.db"
export LOG_LEVEL="DEBUG"
```

> 📖 See the [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)

---

## Docker

```bash
docker build -t raztodo:local .
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local add "My first task"
```

> 📖 See the [Docker Guide](https://github.com/razbuild/raztodo/blob/master/docs/DOCKER.md)

---

## Documentation

- 📦 [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)
- ⌨️ [Completion Guide](https://github.com/razbuild/raztodo/blob/master/docs/COMPLETION.md)
- 🐳 [Docker Guide](https://github.com/razbuild/raztodo/blob/master/docs/DOCKER.md)
- 📖 [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md)
- ⚙️ [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)
- 🏗️ [Architecture](https://github.com/razbuild/raztodo/blob/master/docs/ARCHITECTURE.md)
- 🧪 [Testing](https://github.com/razbuild/raztodo/blob/master/docs/TESTING.md)
- 📝 [Changelog](https://github.com/razbuild/raztodo/blob/master/CHANGELOG.md)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and verify quality:
   ```bash
   uv run pytest
   uv run ruff format --check src/ tests/
   uv run ruff check src/ tests/
   uv run ty check src/
   ```
4. Submit a pull request

See the shared [RazBuild contributing guide](https://github.com/razbuild/.github/blob/main/CONTRIBUTING.md) for detailed guidelines.

---

## License

MIT License

<div align="center">
  <img src="https://raw.githubusercontent.com/razbuild/.github/main/profile/svg/badge.svg" alt="Made by RazBuild" width="160">
</div>
