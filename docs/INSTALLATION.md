# Installation

This guide explains how to install and work with **RazTodo**, both as an end-user CLI tool and as a contributor.

---

## Prerequisites

* Python **3.10+**
* `pip` or `pipx` installed

---

## Installing from PyPI

You can install **raztodo** using either `pip` or `pipx`. Choose the method that fits your workflow.

### Using pip

```bash
# CLI only
pip install raztodo

# CLI + optional web UI
pip install "raztodo[web]"

# CLI + bash/zsh completion support
pip install "raztodo[completion]"

# Install both optional extras
pip install "raztodo[web,completion]"
```

### Using pipx

```bash
# CLI only
pipx install raztodo

# CLI + optional web UI
pipx install "raztodo[web]"

# CLI + bash/zsh completion support
pipx install "raztodo[completion]"
```
### Uninstall

```bash
pip uninstall raztodo
# For pipx:
pipx uninstall raztodo
```

> `pipx` installs the CLI in an isolated environment, preventing conflicts with your global Python packages.

---

## Local Development Setup

Clone the repository to work on the project locally:

```bash
git clone https://github.com/razbuild/raztodo.git
cd raztodo
```

### Editable Installation

Editable installation allows you to test changes locally without reinstalling the package.

#### Install ‍uv (if not already installed)
```bash
pip install uv
```

#### Install the project in editable 
```bash
# CLI only
uv sync --editable

# CLI + optional web UI
uv sync --editable --extra web

# CLI + bash/zsh completion support
uv sync --editable --extra completion

# Install both optional extras
uv sync --editable --extra web --extra completion
```
This will:

- Create a virtual environment `.venv`

- Install the project in editable mode

- Lock dependencies in `uv.lock`
---

## Installing Development Dependencies

For testing, linting, and formatting:

```bash
uv sync --group dev --extra web
```

If you are working on bash/zsh completion locally, add the completion extra too:

```bash
uv sync --group dev --extra web --extra completion
```

Now you can run commands via uv run:

```bash
uv run pytest
uv run ruff check .
```

---

## Verifying Installation

Confirm that the CLI is installed and accessible:

```bash
rt --help
```

You should see output like:

```text
usage: raztodo [-h] [--version] COMMAND ...

A command-line task manager powered by SQLite. Use one of the commands below to manage your todos.

positional arguments:
  COMMAND       Available commands
    add         Create a new task
    list        List all tasks
    remove      Delete a task
    update      Update an existing task
    search      Search tasks by keyword
    export      Export tasks to a JSON file
    import      Import tasks from a JSON file
    done        Mark a task as done or undone
    migrate     Run database migration
    clear       Delete all tasks
    completion  Output shell completion script for bash, zsh, or fish

options:
  -h, --help    show this help message and exit
  --version     Show raztodo version information and exit

Examples:
  rt add 'Buy groceries' --priority H --due 2024-12-31
  rt list --priority H --pending
  rt update 1 --title 'New title'
  rt search 'meeting' --project work

Tips:
  • Show command help: rt <command> --help
  • Output in JSON mode when available for automation
```

If you see output like this, the installation was successful.

To verify the optional web UI install, run:

```bash
rt-web
```

This starts the local web UI at `http://127.0.0.1:8000`. Press `Ctrl+C` to stop it.
