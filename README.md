![Logo](https://raw.githubusercontent.com/razbuild/raztodo/master/assets/logo.png)

![GitHub License](https://img.shields.io/github/license/razbuild/raztodo?logoColor=ffffff&logoSize=auto&label=License&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml?branch=master&event=push&logo=githubactions&logoColor=ffffff&logoSize=auto&label=Build&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)
![Codecov](https://img.shields.io/codecov/c/github/razbuild/raztodo?logo=codecov&logoColor=ffffff&logoSize=auto&label=Coverage&labelColor=1b1b1b&color=ba0000&cacheSeconds=3600)
![PyPI - Version](https://img.shields.io/pypi/v/raztodo?pypiBaseUrl=https%3A%2F%2Fpypi.org&logo=pypi&logoColor=ffffff&logoSize=auto&label=PyPi&labelColor=1b1b1b&color=ba0000&cacheSeconds=3600)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Frazbuild%2Fraztodo%2Fmain%2Fpyproject.toml&logo=python&logoColor=ffffff&logoSize=auto&label=Python&labelColor=1b1b1b&color=ab0000&cacheSeconds=3600)

---

## About

RazTodo is a lightweight, cross-platform CLI task manager powered by SQLite, offering fast, privacy-first todo management with minimal external dependencies.

| Preview |
|:-------:|
| ![Preview](https://raw.githubusercontent.com/razbuild/raztodo/master/assets/preview.gif) |

---

## Why RazTodo?

**Lightweight & Fast** — Minimal dependencies, SQLite-powered, optimized for speed  
**Privacy-First** — Your data stays local, no cloud services, no tracking  
**Developer-Friendly** — Clean Architecture, well-tested, type-safe, modern Python  
**Simple & Powerful** — Intuitive CLI, works out of the box, rich features  
**Cross-Platform** — Works seamlessly on Linux, macOS, and Windows  

Perfect for developers, power users, and anyone who wants a fast, reliable, local-first task manager.

---

## Quick Start

### Installation

```bash
# Recommended: Install via pipx (isolated environment)
pipx install raztodo

# Alternative: Install via pip
pip install raztodo
```

> 📖 For more installation options (virtual environments, from source), see the [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)

### Basic Usage

```bash
# Create a task with priority and due date
rt add "Buy groceries" --priority H --due 2024-12-31

# List all tasks
rt list

# Mark task as done
rt done 1

# Search for tasks
rt search "groceries"

# Update a task
rt update 1 --title "Buy groceries and milk"

# Delete a task
rt remove 1
```

> 📖 For complete command reference, see the [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md)

---

## Features

- ✅ **Task Management** — Create, update, delete, and organize tasks
- 🏷️ **Tags & Projects** — Organize tasks with tags and project names
- 🔍 **Full-Text Search** — Search across all task fields
- 📅 **Due Dates & Priority** — Set deadlines and priority levels (L/M/H)
- 💾 **Import/Export** — Backup and restore tasks via JSON
- 🎨 **Colored Output** — Beautiful ANSI colors and icons
- 🗄️ **SQLite Storage** — No external services required
- 🚀 **Cross-Platform** — Works on Linux, macOS, and Windows
- ⚡ **Fast Performance** — Lazy loading and optimized architecture
- 🏗️ **Clean Architecture** — Maintainable and testable codebase

---

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Create a new task | `rt add "Task title" --priority H` |
| `list` | List tasks with filters | `rt list --pending --priority H` |
| `update` | Update a task | `rt update 1 --title "New title"` |
| `done` | Mark task as done/undone | `rt done 1` |
| `remove` | Delete a task | `rt remove 1` |
| `search` | Search tasks | `rt search "keyword"` |
| `export` | Export to JSON | `rt export backup.json` |
| `import` | Import from JSON | `rt import backup.json` |
| `migrate` | Run database migration | `rt migrate` |
| `clear` | Delete all tasks | `rt clear --confirm` |

```bash
# Get help for any command
rt --help
rt add --help
```

> 📖 See the [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md) for detailed command documentation

---

## Configuration

RazTodo can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `RAZTODO_DB` | Database filename or path | `tasks.db` |
| `LOG_LEVEL` | Logging level | `ERROR` |

**Example:**

```bash
# Use a custom database location
export RAZTODO_DB="/path/to/custom.db"

# Enable debug logging
export LOG_LEVEL="DEBUG"
```

> 📖 For detailed configuration options, see the [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)

---

## Documentation

Complete documentation is available in the `docs/` directory:

- 📦 **[Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)** — Install via pip, pipx, or from source
- 📖 **[Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md)** — Complete command reference with examples
- ⚙️ **[Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)** — Environment variables and options
- 🏗️ **[Architecture](https://github.com/razbuild/raztodo/blob/master/docs/ARCHITECTURE.md)** — Project structure and design patterns
- 🧪 **[Testing](https://github.com/razbuild/raztodo/blob/master/docs/TESTING.md)** — Running tests and development setup
- 📝 **[Changelog](https://github.com/razbuild/raztodo/blob/master/CHANGELOG.md)** — Release notes and version history

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and ensure quality:
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   ruff check src/ tests/
   black --check src/ tests/
   mypy src/
   ```
4. **Submit a pull request**

For detailed guidelines, see the [Contributing Guide](https://github.com/razbuild/raztodo/blob/master/CONTRIBUTING.md).

---

## License

MIT License

---

## Support

- 🐛 **Found a bug?** [Open an issue](https://github.com/razbuild/raztodo/issues)
- 💡 **Have a suggestion?** [Open an issue](https://github.com/razbuild/raztodo/issues)
- 📧 **Questions?** Check the [Documentation](https://github.com/razbuild/raztodo/blob/master/docs/)
