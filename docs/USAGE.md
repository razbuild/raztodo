# Usage Guide

Complete reference for all **RazTodo** commands and options.

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

## Commands

### `add` - Create a New Task

Create a new task with a title and optional metadata.

```bash
rt add <title> [options]
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
rt add "Complete project" --priority H --due 2024-12-31
rt add "Call client" -p M --desc "Discuss requirements" --tags work,urgent
rt add "Buy milk" --project shopping
```

---

### `list` - List Tasks

List tasks with optional filtering, sorting, and pagination.

```bash
rt list [options]
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
rt list --pending --priority H
rt list --project work --sort priority --desc
rt list --tags urgent,important --due-before 2024-12-31
rt list --limit 10 --offset 20
```

---

### `update` - Update a Task

Update one or more fields of an existing task.

```bash
rt update <id> [options]
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
rt update 1 --title "Updated title"
rt update 5 --priority H --due 2024-12-31
rt update 3 --tags work,urgent --project client
```

---

### `done` - Mark Task as Done/Undone

Mark a task as completed or revert it to pending.

```bash
rt done <id> [options]
```

| Option | Description |
|--------|-------------|
| `--undo` | Mark as pending instead of done |
| `--json` | Output result as JSON |

**Examples:**

```bash
rt done 1
rt done 5 --undo
rt done 3 --json
```

---

### `remove` - Delete a Task

Delete a task by ID. This action cannot be undone.

```bash
rt remove <id> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

**Examples:**

```bash
rt remove 1
rt remove 5 --json
```

---

### `search` - Search Tasks

Search for tasks by keyword in title or description.

```bash
rt search <keyword> [options]
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
rt search "meeting" --pending
rt search "project" --priority H --project work
rt search "urgent" --tags important,work
```

---

### `export` - Export Tasks

Export all tasks to a JSON file for backup or transfer.

```bash
rt export <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--json` | Output result as JSON |

**Examples:**

```bash
rt export tasks_backup.json
rt export ~/backups/tasks_2024.json
```

---

### `import` - Import Tasks

Import tasks from a JSON file (exported by the export command).

```bash
rt import <filepath> [options]
```

| Option | Description |
|--------|-------------|
| `--upsert` | Update existing tasks if they match by title |
| `--json` | Output result as JSON |

**Examples:**

```bash
rt import tasks_backup.json
rt import ~/backups/tasks.json --upsert
```

---

### `migrate` - Database Migration

Run database migration to deduplicate task titles and enforce unique index.

```bash
rt migrate
```

Run this command when upgrading from an older version.

---

### `clear` - Delete all tasks

Delete all tasks from the database. This action cannot be undone.

| Option | Description |
|--------|-------------|
| `--confirm` | Confirm that you want to delete all tasks (required) (default: False) |
| `--json` | Output result as JSON instead of human-readable format (default: False) |


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
rt --no-color list
rt --db ~/work/tasks.db add "Work task"
rt --help
rt list --help
```

---

## JSON Output

Most commands support `--json` flag for automation and scripting:

```bash
# Get tasks as JSON
rt list --json

# Parse with jq
rt list --json | jq '.[].title'
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
rt add "Meeting" --due 2024-12-31
rt list --due-before 2024-06-01
```

