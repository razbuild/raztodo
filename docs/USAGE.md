# Usage Guide

Complete reference for all **RazTodo** commands and options.

---

## Quick Start

```bash
# Add a task
raztodo add "Buy groceries" --priority H --due 2024-12-31

# List all tasks
raztodo list

# Mark task as done
raztodo done 1

# Search tasks
raztodo search "groceries"
```

---

## Commands

### `add` - Create a New Task

Create a new task with a title and optional metadata.

```bash
raztodo add <title> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--desc TEXT` | `-d` | Task description |
| `--priority LEVEL` | `-p` | Priority: `L` (Low), `M` (Medium), `H` (High) |
| `--due DATE` | | Due date (YYYY-MM-DD format) |
| `--tags TAGS` | `-t` | Comma-separated tags |
| `--project NAME` | | Project or category name |
| `--json` | | Output result as JSON |

**Examples:**

```bash
raztodo add "Complete project" --priority H --due 2024-12-31
raztodo add "Call client" -p M --desc "Discuss requirements" --tags work,urgent
raztodo add "Buy milk" --project shopping
```

---

### `list` - List Tasks

List tasks with optional filtering, sorting, and pagination.

```bash
raztodo list [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--done` | | Show only completed tasks |
| `--pending` | | Show only pending tasks |
| `--priority LEVEL` | `-p` | Filter by priority: `L`, `M`, `H` |
| `--project NAME` | | Filter by project name |
| `--tags TAGS` | `-t` | Filter by tags (comma-separated) |
| `--due-before DATE` | | Tasks due before date (YYYY-MM-DD) |
| `--due-after DATE` | | Tasks due after date (YYYY-MM-DD) |
| `--limit N` | | Limit number of results |
| `--offset N` | | Skip N tasks (pagination) |
| `--sort FIELD` | | Sort by: `id`, `title`, `created_at`, `done`, `priority`, `due_date` |
| `--desc` | | Sort in descending order |
| `--json` | | Output as JSON array |

**Examples:**

```bash
raztodo list --pending --priority H
raztodo list --project work --sort priority --desc
raztodo list --tags urgent,important --due-before 2024-12-31
raztodo list --limit 10 --offset 20
```

---

### `update` - Update a Task

Update one or more fields of an existing task.

```bash
raztodo update <id> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--title TEXT` | | New title |
| `--desc TEXT` | | New description |
| `--priority LEVEL` | `-p` | New priority: `L`, `M`, `H` |
| `--due DATE` | | New due date (YYYY-MM-DD) |
| `--tags TAGS` | `-t` | New tags (comma-separated) |
| `--project NAME` | | New project name |
| `--json` | | Output result as JSON |

**Examples:**

```bash
raztodo update 1 --title "Updated title"
raztodo update 5 --priority H --due 2024-12-31
raztodo update 3 --tags work,urgent --project client
```

---

### `done` - Mark Task as Done/Undone

Mark a task as completed or revert it to pending.

```bash
raztodo done <id> [options]
```

| Option | Description |
|--------|-------------|
| `--undo` | Mark as pending instead of done |
| `--json` | Output result as JSON |

**Examples:**

```bash
raztodo done 1
raztodo done 5 --undo
raztodo done 3 --json
```

---

### `remove` - Delete a Task

Delete a task by ID. This action cannot be undone.

```bash
raztodo remove <id> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

**Examples:**

```bash
raztodo remove 1
raztodo remove 5 --json
```

---

### `search` - Search Tasks

Search for tasks by keyword in title or description.

```bash
raztodo search <keyword> [options]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--done` | | Show only completed matches |
| `--pending` | | Show only pending matches |
| `--priority LEVEL` | `-p` | Filter by priority: `L`, `M`, `H` |
| `--project NAME` | | Filter by project name |
| `--tags TAGS` | `-t` | Filter by tags (comma-separated) |
| `--json` | | Output as JSON array |

**Examples:**

```bash
raztodo search "meeting" --pending
raztodo search "project" --priority H --project work
raztodo search "urgent" --tags important,work
```

---

### `export` - Export Tasks

Export all tasks to a JSON file for backup or transfer.

```bash
raztodo export <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

**Examples:**

```bash
raztodo export tasks_backup.json
raztodo export ~/backups/tasks_2024.json
```

---

### `import` - Import Tasks

Import tasks from a JSON file (exported by the export command).

```bash
raztodo import <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--upsert` | Update existing tasks if they match by title |
| `--json` | Output result as JSON |

**Examples:**

```bash
raztodo import tasks_backup.json
raztodo import ~/backups/tasks.json --upsert
```

---

### `migrate` - Database Migration

Run database migration to deduplicate task titles and enforce unique index.

```bash
raztodo migrate
```

Run this command when upgrading from an older version.

---

## Global Options

These options work with all commands:

| Option | Description |
|--------|-------------|
| `--no-color` | Disable colored (ANSI) output |
| `--db PATH` | Use a custom database file |
| `--help` | Show help message |
| `--version` | Show version information |

**Examples:**

```bash
raztodo --no-color list
raztodo --db ~/work/tasks.db add "Work task"
raztodo --help
raztodo list --help
```

---

## JSON Output

Most commands support `--json` flag for automation and scripting:

```bash
# Get tasks as JSON
raztodo list --json

# Parse with jq
raztodo list --json | jq '.[].title'
```

---

## Priority Levels

| Level | Code | Description |
|-------|------|-------------|
| High | `H` | Urgent tasks |
| Medium | `M` | Normal priority |
| Low | `L` | Can wait |

---

## Date Format

All dates should be in **YYYY-MM-DD** format:

```bash
raztodo add "Meeting" --due 2024-12-31
raztodo list --due-before 2024-06-01
```

