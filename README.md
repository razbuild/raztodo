<div align="center">
  <img src="https://raw.githubusercontent.com/razbuild/raztodo/master/assets/RazTodo.svg" alt="RazTodo" width="400" />
  <br><br>

[![PyPI Version](https://img.shields.io/pypi/v/raztodo)](https://pypi.org/project/raztodo/)
[![Python Versions](https://img.shields.io/pypi/pyversions/raztodo)](https://pypi.org/project/raztodo/)
[![CI](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml)](https://github.com/razbuild/raztodo/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/razbuild/raztodo)](https://codecov.io/gh/razbuild/raztodo)

  <p>A local-first task manager for developers with a native CLI, optional Web UI, and local AI assistance powered by Ollama.</p>
</div>

---

## Preview

<p align="center">
  <b>CLI</b>
</p>

<p align="center">
  <img src="https://github.com/razbuild/raztodo/raw/master/assets/preview.gif" width="700">
</p>

<p align="center">
  <i>Local AI assistance powered by Ollama</i>
</p>

<p align="center">
  <b>Web UI</b>
</p>

<p align="center">
  <img src="https://github.com/razbuild/raztodo/raw/master/assets/web-preview.png" width="700">
</p>

<p align="center">
  <i>CLI + optional Web UI powered by FastAPI</i>
</p>

---

## Why RazTodo

Most task managers are either web-first, cloud-dependent, or tied to a single interface. RazTodo keeps everything local while letting you manage the same tasks from a native CLI or an optional Web UI.

### Highlights

- 💻 Native CLI built for daily terminal workflows
- 🌐 Optional Web UI backed by the same local database
- 🤖 Local AI assistance powered by Ollama
- 🗄️ Single SQLite database shared across all interfaces
- 🔒 No cloud services, accounts, or telemetry
- ⚡ Fast startup with zero background services

### Architecture

```
CLI ─┐
     ├── Core Engine ─── SQLite
Web ─┘
```

Both the CLI and Web UI use the same core engine and SQLite database, so every interface stays synchronized automatically.

The architecture follows three design principles:

- **Separation of concerns** — core logic is independent of the user interface.
- **Local-first storage** — all data stays on your machine.
- **Composable interfaces** — use only the interfaces you need.

---

## Quick Start

### CLI

```bash
# Add a task
rt add "Prepare weekly groceries" --priority H --due 2026-12-31

# List all tasks
rt list

# Mark as done
rt done 1

# Search
rt search "groceries"

# Update
rt update 1 --title "Weekly groceries: milk, vegetables, essentials"

# Delete
rt remove 1
```

### Web UI

Start the server:

```bash
rt-web
```

Then open `http://127.0.0.1:8000`.

> [!NOTE]
> Runs locally only (not exposed to the internet)
> Single-user design with no authentication layer
> CLI and Web UI share one SQLite database (real-time sync)
> Local-first architecture optimized for personal use
> Built with FastAPI + lightweight static frontend
> AI-powered task explanations (Summary / Deep Analysis / Action Plan) via Ollama

### Shell Completion

```bash
# Requires raztodo[completion]
eval "$(rt completion bash)"
```

Supports bash, zsh, and fish. For permanent setup see the [Completion Guide](https://github.com/razbuild/raztodo/blob/master/docs/COMPLETION.md).

---

## LLM Integration

RazTodo integrates with Ollama to provide optional local AI assistance for your tasks. Every explanation runs locally using your own LLM, keeping your data private.

Available explanation modes:

- `--short` — concise summary of the task
- `--plan` — actionable step-by-step plan
- `--deep` — detailed analysis and recommendations

Example:

```bash
rt explain 1 --short
rt explain 1 --plan
rt explain 1 --deep
```

> [!NOTE]
> Requires Ollama with a compatible local model. All AI processing is performed locally.

📖 See the [Explain Guide](https://github.com/razbuild/raztodo/blob/master/docs/EXPLAIN.md) for installation, configuration, supported models, and usage examples.

---

## Installation

```bash
# Recommended (pipx)
pipx install raztodo

# No-install (uv)
uvx --from raztodo rt

# Standard install
pip install raztodo

# Web UI (optional)
pip install "raztodo[web]"

# Shell completion (optional)
pip install "raztodo[completion]"

# Everything (web + completion)
pip install "raztodo[all]"
```

For virtual environment and source installation, see the [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md).

---

## Commands

| Command      | Description                     | Example                           |
|--------------|----------------------------------|------------------------------------|
| `add`        | Create a new task                | `rt add "Task" --priority H`       |
| `list`       | List tasks with filters          | `rt list --pending --priority H`   |
| `update`     | Update a task                    | `rt update 1 --title "New title"`  |
| `done`       | Toggle task done/undone          | `rt done 1`                        |
| `remove`     | Delete a task                    | `rt remove 1`                      |
| `search`     | Search tasks by keyword          | `rt search "keyword"`              |
| `export`     | Export tasks to JSON             | `rt export backup.json`            |
| `import`     | Import tasks from JSON           | `rt import backup.json`            |
| `migrate`    | Run database migrations          | `rt migrate`                       |
| `clear`      | Delete all tasks                 | `rt clear --confirm`               |
| `completion` | Output shell completion script   | `rt completion bash`               |
| `explain`    | Get an AI explanation of a task  | `rt explain 1 --plan`              |

```bash
rt --help
rt add --help
```

📖 See the [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md) for full command documentation.

---

## Configuration

| Variable     | Description                | Default    |
|--------------|-----------------------------|------------|
| `RAZTODO_DB` | Database filename or path   | `tasks.db` |
| `LOG_LEVEL`  | Logging level                | `ERROR`    |

```bash
export RAZTODO_DB="/path/to/custom.db"
export LOG_LEVEL="DEBUG"
```

> [!TIP]
> 📖 See the [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)

---

## Docker

```bash
docker build -t raztodo:local .
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local add "My first task"
```

> [!NOTE]
> kept CLI-only to minimize image size and dependencies

> [!TIP]
> 📖 See the [Docker Guide](https://github.com/razbuild/raztodo/blob/master/docs/DOCKER.md)

---

## Documentation

**Core:**
- 📦 [Installation Guide](https://github.com/razbuild/raztodo/blob/master/docs/INSTALLATION.md)
- 📖 [Usage Guide](https://github.com/razbuild/raztodo/blob/master/docs/USAGE.md)
- ⚙️ [Configuration Guide](https://github.com/razbuild/raztodo/blob/master/docs/CONFIGURATION.md)
- 🤖 [Explain Guide](https://github.com/razbuild/raztodo/blob/master/docs/EXPLAIN.md)

**Advanced:**
- ⌨️ [Completion Guide](https://github.com/razbuild/raztodo/blob/master/docs/COMPLETION.md)
- 🐳 [Docker Guide](https://github.com/razbuild/raztodo/blob/master/docs/DOCKER.md)
- 🏗️ [Architecture](https://github.com/razbuild/raztodo/blob/master/docs/ARCHITECTURE.md)
- 🧪 [Testing](https://github.com/razbuild/raztodo/blob/master/docs/TESTING.md)
- 📝 [Changelog](https://github.com/razbuild/raztodo/blob/master/CHANGELOG.md)

---

## Ecosystem

RazTodo is part of the [RazBuild](https://github.com/razbuild) ecosystem of open-source developer tools.

- [RazTint](https://github.com/razbuild/raztint) Zero-dependency ANSI colors, icons, and terminal formatting utilities powering RazTodo's CLI output.

---

## Contributing

We welcome bug reports, feature requests, and pull requests.

```bash
git clone https://github.com/razbuild/raztodo
cd raztodo
uv sync
```

### Quality checks

```bash
uv run pytest
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run ty check src/
```

### Workflow

1. Create feature branch
2. Implement changes
3. Ensure tests pass
4. Submit PR

See the [CONTRIBUTING](https://github.com/razbuild/.github/blob/main/CONTRIBUTING.md) guide for details.

---

## License

[![License](https://img.shields.io/github/license/razbuild/raztodo)](https://github.com/razbuild/raztodo/blob/master/LICENSE)

<div align="center">
  <img src="https://raw.githubusercontent.com/razbuild/.github/main/assets/badge.svg" alt="Made by RazBuild" width="160">
</div>