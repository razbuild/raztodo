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
|--------|:-----:|-------------|
| `--title TEXT` | — | New title |
| `--desc TEXT`, `--description TEXT` | — | New description |
| `--priority LEVEL` | `-p` | New priority: `L`, `M`, `H` |
| `--due DATE`, `--due-date DATE` | — | New due date. `YYYY-MM-DD` is recommended. |
| `--tags TAGS` | `-t` | New tags (comma-separated) |
| `--project NAME` | — | New project/category |
| `--clear-priority` | — | Remove the task priority |
| `--clear-due` | — | Remove the due date |
| `--clear-tags` | — | Remove all tags |
| `--clear-project` | — | Remove the project/category |
| `--json` | — | Output the result as JSON |

Examples:

```bash
rt update 1 --title "Updated title"
rt update 5 --priority H --due 2026-12-31
rt update 3 --tags work,urgent --project client

# Clear values
rt update 7 --clear-priority
rt update 7 --clear-due
rt update 7 --clear-tags
rt update 7 --clear-project

# Mix update and clear options
rt update 10 --title "Refactor CLI" --clear-tags --priority M

# Output as JSON
rt update 2 --priority L --json
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

### `explain` — Explain a Task with AI

Use a locally-running [Ollama](https://ollama.com) model to analyse or plan a task.
The task's full data (title, description, priority, due date, tags, project) is passed
to the model as JSON. No data leaves your machine.

```bash
rt explain <id> [mode] [options]
```

**Modes** (mutually exclusive, default: `--short`):

| Flag | Description |
|------|-------------|
| `--short` | 2–3 sentence plain-language summary (default) |
| `--deep` | In-depth analysis: goal, blockers, approach, risks |
| `--plan` | Numbered step-by-step action plan with a time estimate |

**Other options:**

| Option | Description |
|--------|-------------|
| `--config` | View or update Ollama settings (no task ID needed) |
| `--model NAME` | Set the model to use (used with `--config`) |
| `--host URL` | Set the Ollama server URL (used with `--config`) |
| `--timeout SECONDS` | Set the request timeout (used with `--config`) |
| `--system-prompt TEXT` | Override the default system prompt (used with `--config`) |
| `--json` | Output result or config as JSON |

Examples:

```bash
# Explain task 5 with a short summary
rt explain 5

# Deep analysis of task 12
rt explain 12 --deep

# Step-by-step plan for task 3
rt explain 3 --plan

# JSON output (useful for scripting)
rt explain 7 --short --json
```

#### Requirements

`explain` requires Ollama to be running locally and a model to be configured.
There is no default model — you must set one before first use.

Install Ollama from [ollama.com](https://ollama.com), pull a model, then configure it:

```bash
ollama serve                                    # start the server (or run the desktop app)
ollama pull mistral                             # download a model
rt explain --config --model mistral            # tell RazTodo which model to use
```

If you run `rt explain` without configuring a model first, you will see:

```
[✖] OllamaError: No model configured.
    Run: rt explain --config --model <name>
    To see available models: ollama list
```

#### Configuration

Settings are stored in a JSON file in the RazTodo data directory:

| Platform | Path |
|----------|------|
| Linux / BSD | `~/.local/share/raztodo/llm.json` |
| macOS | `~/Library/Application Support/raztodo/llm.json` |
| Windows | `%APPDATA%\raztodo\llm.json` |

The file is created on first save. Before that, built-in defaults are used.

**View current config:**

```bash
rt explain --config
rt explain --config --json
```

Example output:

```
LLM config  [~/.local/share/raztodo/llm.json  exists]

  model         mistral
  host          http://localhost:11434
  timeout       120s
  system_prompt You are a helpful productivity assistant. The user wi…
```

**Update config:**

```bash
# Change model
rt explain --config --model mistral

# Change model and timeout
rt explain --config --model qwen2.5-coder:3b --timeout 180

# Change server URL (e.g. Ollama running in Docker)
rt explain --config --host http://localhost:11434

# Override the system prompt
rt explain --config --system-prompt "You are a senior software engineer."
```

#### Environment Variables

Environment variables take precedence over the config file and are useful
for one-off overrides or CI environments:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server base URL |
| `OLLAMA_MODEL` | `None` | Model name |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |

```bash
OLLAMA_MODEL=qwen2.5-coder:3b rt explain 5 --deep
```

#### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot connect to Ollama` | Server not running | Run `ollama serve` or start the Ollama desktop app |
| `Model 'X' not found` | Model not downloaded | Run `ollama pull X` |
| `Ollama returned HTTP 404` | Wrong model name | Run `ollama list` to see available models, then `rt explain --config --model <name>` |
| Slow response | Large model or low-end hardware | Try a smaller model (`ollama pull mistral`) or increase `--timeout` |

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

The web UI includes an **Explain** button on each task that opens a modal with the
same three modes (Summary, Deep Analysis, Action Plan). Responses stream in
token-by-token, so you see output immediately as the model generates it.
Ollama must be configured and running for this feature to work; see the
[`explain` command section](#explain--explain-a-task-with-ai) above for setup instructions.
