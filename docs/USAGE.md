# Usage Guide

Complete reference for the `rt` CLI and the optional `rt-web` launcher.

---

## Quick Start

```bash
# Add a task
rt add "Buy groceries" --priority H --due 2024-12-31

# List all tasks
rt list

# Mark task as done
rt done 1

# Search tasks
rt search "groceries"
```

---

## Global Options

These options are available on the top-level CLI:

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help |
| `--version` | Show the installed RazTodo version |

Examples:

```bash
rt --help
rt --version
rt add --help
```

> RazTodo does not currently provide a global `--db` or `--no-color` flag. Use environment variables such as `RAZTODO_DB` and `LOG_LEVEL` for configuration instead.

---

## Commands

### `add` — Create a New Task

Create a new task with a title and optional metadata.

```bash
rt add <title> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--desc TEXT`, `--description TEXT` | `-d` | Task description |
| `--priority LEVEL` | `-p` | Priority: `L`, `M`, `H` |
| `--due DATE`, `--due-date DATE` |  | Due date value. For predictable filtering/sorting, use `YYYY-MM-DD`. |
| `--tags TAGS` | `-t` | Comma-separated tags |
| `--project NAME` |  | Project or category name |
| `--json` |  | Output result as JSON |

Examples:

```bash
rt add "Complete project" --priority H --due 2024-12-31
rt add "Call client" -p M --desc "Discuss requirements" --tags work,urgent
rt add "Buy milk" --project shopping
```

---

### `list` — List Tasks

List tasks with optional filtering, sorting, and pagination.

```bash
rt list [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--done` |  | Show only completed tasks |
| `--pending` |  | Show only pending tasks |
| `--priority LEVEL` | `-p` | Filter by priority: `L`, `M`, `H` |
| `--project NAME` |  | Filter by project or category |
| `--tags TAGS` | `-t` | Filter by tags (comma-separated) |
| `--due-before DATE` |  | Show tasks due before `YYYY-MM-DD` |
| `--due-after DATE` |  | Show tasks due after `YYYY-MM-DD` |
| `--limit N` |  | Limit number of results |
| `--offset N` |  | Skip N results |
| `--sort FIELD` |  | One of `id`, `title`, `created_at`, `done`, `priority`, `due_date` |
| `--desc` |  | Sort descending |
| `--json` |  | Output tasks as JSON |

Examples:

```bash
rt list --pending --priority H
rt list --project work --sort priority --desc
rt list --tags urgent,important --due-before 2024-12-31
rt list --limit 10 --offset 20
```

---

### `update` — Update a Task

Update one or more fields of an existing task.

```bash
rt update <id> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--title TEXT` |  | New title |
| `--desc TEXT`, `--description TEXT` |  | New description |
| `--priority LEVEL` | `-p` | New priority: `L`, `M`, `H` |
| `--due DATE`, `--due-date DATE` |  | New due date value. `YYYY-MM-DD` is recommended. |
| `--tags TAGS` | `-t` | New tags (comma-separated) |
| `--project NAME` |  | New project/category |
| `--json` |  | Output result as JSON |

Examples:

```bash
rt update 1 --title "Updated title"
rt update 5 --priority H --due 2024-12-31
rt update 3 --tags work,urgent --project client
```

---

### `done` — Mark Task as Done or Undone

Mark a task as completed, or revert it to pending with `--undo`.

```bash
rt done <id> [options]
```

| Option | Description |
|--------|-------------|
| `--undo` | Mark the task as pending instead of done |
| `--json` | Output result as JSON |

Examples:

```bash
rt done 1
rt done 5 --undo
rt done 3 --json
```

---

### `remove` — Delete a Task

Delete a task by ID.

```bash
rt remove <id> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

Examples:

```bash
rt remove 1
rt remove 5 --json
```

---

### `search` — Search Tasks

Search for tasks by keyword in title or description, with optional filters.

```bash
rt search <keyword> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--done` |  | Show only completed matches |
| `--pending` |  | Show only pending matches |
| `--priority LEVEL` | `-p` | Filter by priority: `L`, `M`, `H` |
| `--project NAME` |  | Filter by project/category |
| `--tags TAGS` | `-t` | Filter by tags (comma-separated) |
| `--json` |  | Output matches as JSON |

Examples:

```bash
rt search "meeting" --pending
rt search "project" --priority H --project work
rt search "urgent" --tags important,work
```

---

### `export` — Export Tasks

Export all tasks to a JSON file.

```bash
rt export <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

Examples:

```bash
rt export tasks_backup.json
rt export ~/backups/tasks_2024.json --json
```

---

### `import` — Import Tasks

Import tasks from a JSON file previously exported by RazTodo.

```bash
rt import <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--upsert` | Update existing tasks when titles match; otherwise skip duplicates |
| `--json` | Output result as JSON |

Examples:

```bash
rt import tasks_backup.json
rt import ~/backups/tasks.json --upsert --json
```

---

### `migrate` — Run Database Migration

Run the migration that deduplicates task titles and enforces the unique title index.

```bash
rt migrate
```

Example output:

```text
Migration completed: fixed=0, unique_index=True
```

Run this when upgrading from an older version of RazTodo.

---

### `clear` — Delete All Tasks

Delete all tasks from the database.

```bash
rt clear --confirm [options]
```

| Option | Description |
|--------|-------------|
| `--confirm` | Required confirmation flag |
| `--json` | Output result as JSON |

Examples:

```bash
rt clear --confirm
rt clear --confirm --json
```

---

### `completion` — Output Shell Completion Script

Generate the shell snippet used to enable completions.

```bash
rt completion {bash,zsh,fish}
```

Examples:

```bash
rt completion bash
rt completion zsh
rt completion fish
```

> For bash/zsh completion support, install the optional `completion` extra first: `pip install "raztodo[completion]"`.

---

## JSON Output

Most task commands support `--json` for scripting and automation:

```bash
rt list --json
rt add "Example" --json
rt clear --confirm --json
```

---

## Priority Levels

| Level | Code | Description |
|-------|------|-------------|
| High | `H` | Urgent tasks |
| Medium | `M` | Normal priority |
| Low | `L` | Can wait |

---

## Due-Date Format Notes

For best results, use ISO dates (`YYYY-MM-DD`), especially if you rely on:

- `rt list --due-before`
- `rt list --due-after`
- sorting by `due_date`

Examples:

```bash
rt add "Meeting" --due 2024-12-31
rt update 1 --due 2025-01-15
rt list --due-before 2025-02-01
```

---

## Optional Web UI

If you install the optional `web` extra, RazTodo also provides the `rt-web` launcher:

```bash
pip install "raztodo[web]"
rt-web
```

This starts the local web UI on `http://127.0.0.1:8000`.
