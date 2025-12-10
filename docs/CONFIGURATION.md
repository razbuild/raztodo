# Configuration

This document explains all configuration options available in **RazTodo**.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAZTODO_DB` | Database filename or path | `tasks.db` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `ERROR` |

### Setting Environment Variables

#### Linux & macOS

```bash
export RAZTODO_DB="my_tasks.db"
export LOG_LEVEL="DEBUG"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

#### Windows (PowerShell)

```powershell
$env:RAZTODO_DB = "my_tasks.db"
$env:LOG_LEVEL = "DEBUG"
```

For permanent settings, use System Properties → Environment Variables.

---

## Database Location

RazTodo stores the SQLite database in platform-specific directories:

| Platform | Default Path |
|----------|--------------|
| **Linux** | `~/.local/share/raztodo/tasks.db` |
| **macOS** | `~/Library/Application Support/raztodo/tasks.db` |
| **Windows** | `%APPDATA%\raztodo\tasks.db` |

### Custom Database Path

Use the `--db` option to specify a custom database:

```bash
rt --db /path/to/custom.db list
```

Or set `RAZTODO_DB` to an absolute path:

```bash
export RAZTODO_DB="/path/to/custom.db"
```

---

## Command-Line Options

### Global Options

| Option | Description |
|--------|-------------|
| `--no-color` | Disable colored (ANSI) output |
| `--db PATH` | Use a custom database file |
| `--help` | Show help message |
| `--version` | Show version information |

### Examples

```bash
# Disable colors
rt --no-color list

# Use custom database
rt --db ~/work/tasks.db add "Work task"

# Combine options
rt --no-color --db ./project.db list
```

---

## Logging

Configure logging level via `LOG_LEVEL` environment variable:

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed information for debugging |
| `INFO` | General operational information |
| `WARNING` | Warning messages (default) |
| `ERROR` | Error messages only |
| `CRITICAL` | Critical errors only |

```bash
# Enable debug logging
LOG_LEVEL=DEBUG rt list
```

---

## Virtual Environment (Recommended)

Using a virtual environment keeps your Python packages isolated.

### Linux & macOS

```bash
python -m venv venv
source venv/bin/activate
pip install raztodo
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install raztodo
```

See [Python venv documentation](https://docs.python.org/3/library/venv.html) for more details.

