<div align="center">
  <img src="https://raw.githubusercontent.com/razbuild/raztodo/main/assets/RazTodo.svg" alt="RazTodo" width="185" />

# RazTodo

**A local-first task manager for developers, with a native CLI and local AI assistance powered by Ollama.**

<br>

[![PyPI Version](https://img.shields.io/pypi/v/raztodo)](https://pypi.org/project/raztodo/)
[![Python Versions](https://img.shields.io/pypi/pyversions/raztodo)](https://pypi.org/project/raztodo/)
[![CI](https://img.shields.io/github/actions/workflow/status/razbuild/raztodo/ci.yml)](https://github.com/razbuild/raztodo/actions/workflows/ci.yml)
[![Codecov (with branch)](https://img.shields.io/codecov/c/github/razbuild/raztodo/main)](https://codecov.io/gh/razbuild/raztodo)

</div>

---

## Preview

<p align="center">
  <img src="https://github.com/razbuild/raztodo/raw/main/assets/preview.gif" width="700">
</p>

<p align="center">
  <i>A command-line task manager powered by SQLite, with optional AI-assisted task explanations via Ollama.</i>
</p>

---

## Why RazTodo

Most task managers pull you into a browser tab or a cloud account just to jot down a to-do. RazTodo stays entirely in your terminal, backed by a single local SQLite database, with no accounts, no telemetry, and no background services.

### Highlights

- 💻 Native CLI built for daily terminal workflows
- 🗄️ Single local SQLite database, your data never leaves your machine
- 🤖 Optional local AI task explanations powered by Ollama
- 🔒 No cloud services, accounts, or telemetry
- ⚡ Fast startup with zero background services
- ⌨️ Shell completion for bash, zsh, and fish
- 🌐 Optional Web UI via the companion [raztodo-web](https://pypi.org/project/raztodo-web/) package

### Architecture

RazTodo follows a layered architecture, keeping the core task-management logic independent of any interface:

```
src/raztodo/
├── application/     # use cases / orchestration
├── domain/          # core task model and business rules
├── infrastructure/  # SQLite, settings, logging, LLM (Ollama) integration
└── presentation/
    └── cli/         # the `rt` command-line interface
```

- **Separation of concerns**: core logic is independent of the CLI.
- **Local-first storage**: all data stays on your machine in SQLite.

---

## Quick Start

### Installation

```bash
# Recommended (pipx)
pipx install raztodo

# No-install (uv)
uvx --from raztodo rt

# Standard install
pip install raztodo

# Shell completion (optional)
pip install "raztodo[completion]"

# Web UI (optional, separate package)
pip install raztodo-web
```

For virtual environment and source installation, see the [Installation Guide](https://github.com/razbuild/raztodo/blob/main/docs/INSTALLATION.md).

### Basic Usage

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

### Shell Completion

```bash
# Requires raztodo[completion]
eval "$(rt completion bash)"
```

Supports bash, zsh, and fish. For permanent setup, see the [Completion Guide](https://github.com/razbuild/raztodo/blob/main/docs/COMPLETION.md).

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
| `explain`    | Explain a task using AI (requires Ollama) | `rt explain 1 --plan`     |

```bash
rt --help
rt add --help
```

📖 See the [Usage Guide](https://github.com/razbuild/raztodo/blob/main/docs/USAGE.md) for full command documentation.

---

## AI / Ollama Integration

RazTodo can optionally use [Ollama](https://ollama.com) to explain a task locally, no data leaves your machine.

```bash
rt explain 1 --short   # concise summary
rt explain 1 --plan    # actionable step-by-step plan
rt explain 1 --deep    # detailed analysis and recommendations
```

> [!NOTE]
> Requires Ollama with a compatible local model. All AI processing runs locally.

📖 See the [Explain Guide](https://github.com/razbuild/raztodo/blob/main/docs/EXPLAIN.md) for installation, configuration, supported models, and usage examples.

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

📖 See the [Configuration Guide](https://github.com/razbuild/raztodo/blob/main/docs/CONFIGURATION.md).

---

## Docker

An optional Docker image runs RazTodo's CLI (`rt`) directly as the container entrypoint.

```bash
docker build \
  --build-arg USER_UID=$(id -u) \
  --build-arg USER_GID=$(id -g) \
  -t raztodo:local .
```

```bash
docker run --rm raztodo:local --help

docker run --rm \
  -v raztodo-data:/data \
  raztodo:local add "Buy milk"

docker run --rm \
  -v raztodo-data:/data \
  raztodo:local list
```

> [!NOTE]
> The container stores its SQLite database in `/data` (`RAZTODO_DB=/data/tasks.db`). Mount a named volume or host folder there to persist data between runs. The image runs as a non-root user.
>
> 💡 To use plain `rt` commands that are forwarded to the container automatically (on Linux, macOS, and Windows), see the [seamless wrapper setup](https://github.com/razbuild/raztodo/blob/main/docs/DOCKER.md#-seamless-rt-usage-with-a-wrapper).

📖 See the [Docker Guide](https://github.com/razbuild/raztodo/blob/main/docs/DOCKER.md).

---

## Documentation

**Core:**
- 📦 [Installation Guide](https://github.com/razbuild/raztodo/blob/main/docs/INSTALLATION.md)
- 📖 [Usage Guide](https://github.com/razbuild/raztodo/blob/main/docs/USAGE.md)
- ⚙️ [Configuration Guide](https://github.com/razbuild/raztodo/blob/main/docs/CONFIGURATION.md)
- 🤖 [Explain Guide](https://github.com/razbuild/raztodo/blob/main/docs/EXPLAIN.md)

**Advanced:**
- ⌨️ [Completion Guide](https://github.com/razbuild/raztodo/blob/main/docs/COMPLETION.md)
- 🐳 [Docker Guide](https://github.com/razbuild/raztodo/blob/main/docs/DOCKER.md)
- 🏗️ [Architecture](https://github.com/razbuild/raztodo/blob/main/docs/ARCHITECTURE.md)
- 🧪 [Testing](https://github.com/razbuild/raztodo/blob/main/docs/TESTING.md)

---

## Ecosystem

RazTodo is part of the [RazBuild](https://github.com/razbuild) ecosystem of open-source developer tools.

- [RazTint](https://github.com/razbuild/raztint): Zero-dependency ANSI colors, icons, and terminal formatting utilities powering RazTodo's CLI output.
- [raztodo-web](https://pypi.org/project/raztodo-web/): Optional Web UI, installs on top of `raztodo` (`pip install raztodo-web`).

---

## Contributing

Contributions are welcome! Whether it's bug reports, feature requests, documentation improvements, or code changes, check the contribution guide before getting started.

See the [Contributing Guide](https://github.com/razbuild/raztodo/blob/main/CONTRIBUTING.md) for development setup, testing, coding standards, and pull request guidelines.

---

## License

[![License](https://img.shields.io/github/license/razbuild/raztodo)](https://github.com/razbuild/raztodo/blob/main/LICENSE)

<div align="center">
  <img src="https://raw.githubusercontent.com/razbuild/.github/main/assets/badge.svg" alt="Made by RazBuild" width="160">
</div>