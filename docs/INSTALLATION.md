# Installation

This guide explains how to install and work with **RazTodo**, both as an end-user CLI tool and as a contributor.

---

## Prerequisites

* Python **3.13+**
* `pip` or `pipx` installed

---

## Installing from PyPI

You can install **raztodo** using either `pip` or `pipx`. Choose the method that fits your workflow.

### Using pip

```bash
pip install raztodo
```

### Using pipx

```bash
pipx install raztodo
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

#### Using pip

```bash
pip install -e .
```

#### Using pipx (optional)

```bash
pipx install .
```

> Using `pipx` for development is optional, mainly useful if you want to test the CLI in isolation.

---

## Installing Development Dependencies

To contribute or run tests, install development dependencies:

```bash
pip install -e .[dev]
```

This ensures you have all packages for testing, linting, and formatting.

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
  COMMAND     Available commands
    add       Create a new task
    list      List all tasks
    remove    Delete a task
    update    Update an existing task
    search    Search tasks by keyword
    export    Export tasks to a JSON file
    import    Import tasks from a JSON file
    done      Mark a task as done or undone
    migrate   Run database migration
    clear     Delete all tasks

options:
  -h, --help  show this help message and exit
  --version   Show raztodo version information and exit

Examples:
  rt add 'Buy groceries' --priority H --due tomorrow
  rt list --priority H --pending
  rt update 1 --title 'New title' --done
  rt search 'meeting' --project work

Tips:
  • Show command help: rt <command> --help
  • Output in JSON mode when available for automation
```

If you see output like this, the installation was successful.
