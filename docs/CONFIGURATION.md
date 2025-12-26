# Configuration Guide

This document explains all configuration options available in **RazTodo** and how to customize them for your needs.

---

## Table of Contents

- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [Logging Configuration](#logging-configuration)
- [Command-Line Options](#command-line-options)

---

## Environment Variables

RazTodo uses environment variables to configure its behavior. These can be set temporarily for a single session or permanently for all future sessions.

### Available Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RAZTODO_DB` | Database filename or absolute path | `tasks.db` | No |
| `LOG_LEVEL` | Logging verbosity level | `ERROR` | No |

### Setting Environment Variables

#### Method 1: Temporary (Current Session Only)

**Linux & macOS (Bash/Zsh):**

```bash
# Set for current terminal session
export RAZTODO_DB="my_tasks.db"
export LOG_LEVEL="DEBUG"

# Verify the settings
echo $RAZTODO_DB
echo $LOG_LEVEL
```

**Windows (PowerShell):**

```powershell
# Set for current PowerShell session
$env:RAZTODO_DB = "my_tasks.db"
$env:LOG_LEVEL = "DEBUG"

# Verify the settings
echo $env:RAZTODO_DB
echo $env:LOG_LEVEL
```

**Windows (Command Prompt):**

```cmd
set RAZTODO_DB=my_tasks.db
set LOG_LEVEL=DEBUG
```

#### Method 2: Permanent (All Future Sessions)

**Linux & macOS:**

1. Open your shell configuration file:
   - **Bash**: `~/.bashrc` or `~/.bash_profile`
   - **Zsh**: `~/.zshrc`

2. Add the export statements:

```bash
# Add these lines to ~/.bashrc or ~/.zshrc
export RAZTODO_DB="my_tasks.db"
export LOG_LEVEL="INFO"
```

3. Reload your shell configuration:

```bash
# For Bash
source ~/.bashrc

# For Zsh
source ~/.zshrc
```

**Windows (PowerShell):**

1. Open PowerShell profile (create if it doesn't exist):

```powershell
# Check if profile exists
Test-Path $PROFILE

# Create profile if needed
New-Item -Path $PROFILE -Type File -Force

# Edit profile
notepad $PROFILE
```

2. Add the environment variables:

```powershell
# Add these lines to your PowerShell profile
$env:RAZTODO_DB = "my_tasks.db"
$env:LOG_LEVEL = "INFO"
```

3. Reload PowerShell or restart your terminal.

**Windows (System-Wide):**

1. Open **System Properties** → **Environment Variables**
2. Under **User variables**, click **New**
3. Add variable name and value
4. Click **OK** to save
5. Restart any open terminals for changes to take effect

---

## Database Configuration

RazTodo uses SQLite to store your tasks. By default, it creates the database in a platform-specific directory, but you can customize the location.

### Default Database Locations

RazTodo automatically stores the database in the appropriate location for your operating system:

| Platform | Default Path | Full Example |
|----------|--------------|--------------|
| **Linux** | `~/.local/share/raztodo/tasks.db` | `/home/username/.local/share/raztodo/tasks.db` |
| **macOS** | `~/Library/Application Support/raztodo/tasks.db` | `/Users/username/Library/Application Support/raztodo/tasks.db` |
| **Windows** | `%APPDATA%\raztodo\tasks.db` | `C:\Users\username\AppData\Roaming\raztodo\tasks.db` |

> **Note:** The directory is created automatically when you first run RazTodo.

### Using a Custom Database Location

You can specify a custom database location using the `RAZTODO_DB` environment variable.

#### Option 1: Custom Filename (Same Directory)

Use a custom filename while keeping the default directory:

```bash
# Linux/macOS
export RAZTODO_DB="work_tasks.db"

# Windows PowerShell
$env:RAZTODO_DB = "work_tasks.db"
```

This will create the database at:
- **Linux**: `~/.local/share/raztodo/work_tasks.db`
- **macOS**: `~/Library/Application Support/raztodo/work_tasks.db`
- **Windows**: `%APPDATA%\raztodo\work_tasks.db`

#### Option 2: Absolute Path (Custom Location)

Use an absolute path to store the database anywhere on your system:

```bash
# Linux/macOS
export RAZTODO_DB="/home/username/projects/my_tasks.db"
export RAZTODO_DB="/Users/username/Documents/tasks.db"

# Windows PowerShell
$env:RAZTODO_DB = "C:\Users\username\Documents\tasks.db"
```

**Example Use Cases:**

```bash
# Use different databases for different projects
export RAZTODO_DB="/home/raz/projects/work/tasks.db"
rt add "Work task"

export RAZTODO_DB="/home/raz/projects/personal/tasks.db"
rt add "Personal task"

# Use a database on a network drive (Windows)
$env:RAZTODO_DB = "\\server\shared\tasks.db"
rt list

# Use a database in a Dropbox/OneDrive folder for sync
export RAZTODO_DB="$HOME/Dropbox/tasks.db"
rt add "Synced task"
```

### Database File Management

**Backup your database:**

```bash
# Linux/macOS
cp ~/.local/share/raztodo/tasks.db ~/backup/tasks_$(date +%Y%m%d).db

# Windows PowerShell
Copy-Item "$env:APPDATA\raztodo\tasks.db" "C:\backup\tasks_$(Get-Date -Format 'yyyyMMdd').db"
```

**Move your database:**

```bash
# 1. Export tasks (optional, for safety)
rt export backup.json

# 2. Move the database file
mv ~/.local/share/raztodo/tasks.db /new/location/tasks.db

# 3. Update RAZTODO_DB to point to new location
export RAZTODO_DB="/new/location/tasks.db"

# 4. Verify it works
rt list
```

---

## Logging Configuration

RazTodo includes built-in logging to help with debugging and monitoring. You can control the verbosity of log messages using the `LOG_LEVEL` environment variable.

### Available Log Levels

| Level | Value | Description | Use Case |
|-------|-------|-------------|----------|
| `DEBUG` | 10 | Most verbose - shows all details | Development, troubleshooting |
| `INFO` | 20 | General operational information | Normal usage monitoring |
| `WARNING` | 30 | Warning messages about potential issues | Production monitoring |
| `ERROR` | 40 | Error messages only (default) | Production (quiet mode) |
| `CRITICAL` | 50 | Only critical errors | Minimal logging |

### Setting Log Level

**Temporary (Single Command):**

```bash
# Linux/macOS
LOG_LEVEL=DEBUG rt list
LOG_LEVEL=INFO rt add "Test task"

# Windows PowerShell
$env:LOG_LEVEL = "DEBUG"; rt list
```

**Permanent (All Commands):**

```bash
# Linux/macOS - Add to ~/.bashrc or ~/.zshrc
export LOG_LEVEL="INFO"

# Windows PowerShell - Add to profile
$env:LOG_LEVEL = "INFO"
```

### Log Level Examples

**Debug Mode (Most Verbose):**

```bash
LOG_LEVEL=DEBUG rt add "Test task"
# Shows detailed information about:
# - Database connections
# - Query execution
# - Internal state changes
```

**Info Mode (Normal Monitoring):**

```bash
LOG_LEVEL=INFO rt list
# Shows general information about:
# - Command execution
# - Task operations
# - Warnings
```

**Error Mode (Default - Quiet):**

```bash
# No LOG_LEVEL set, or explicitly:
LOG_LEVEL=ERROR rt list
# Only shows errors if something goes wrong
# Perfect for normal daily use
```

### When to Use Each Level

- **DEBUG**: When troubleshooting issues, developing, or need to see all internal operations
- **INFO**: When you want to monitor normal operations without too much noise
- **WARNING**: When you want to be notified about potential issues but not every detail
- **ERROR**: For normal daily use - only shows problems (default)
- **CRITICAL**: For minimal logging in production environments

---

## Command-Line Options

RazTodo provides global command-line options that work with all commands.

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message for the command |
| `--version` | | Show RazTodo version information |

### Using Help

Get help for any command:

```bash
# General help
rt --help

# Help for specific command
rt add --help
rt list --help
rt update --help
```

### Version Information

Check your RazTodo version:

```bash
rt --version
# Output: raztodo 0.2.0
```

This is useful for:
- Verifying installation
- Reporting bugs (include version in bug reports)
- Checking if updates are available

---

## Configuration Examples

### Example 1: Development Setup

For development with verbose logging:

```bash
# ~/.bashrc or ~/.zshrc
export RAZTODO_DB="dev_tasks.db"
export LOG_LEVEL="DEBUG"
```

### Example 2: Production Setup

For production use with minimal logging:

```bash
# ~/.bashrc or ~/.zshrc
export RAZTODO_DB="tasks.db"  # or leave default
export LOG_LEVEL="ERROR"      # or leave default
```

### Example 3: Multiple Project Databases

Switch between different databases for different projects:

```bash
# Project 1
export RAZTODO_DB="/projects/work/tasks.db"
rt add "Work task"

# Project 2
export RAZTODO_DB="/projects/personal/tasks.db"
rt add "Personal task"
```

### Example 4: Troubleshooting

When encountering issues, enable debug logging:

```bash
LOG_LEVEL=DEBUG rt list
# Review the output for detailed information
```

---

## Troubleshooting

### Environment Variables Not Working

**Problem:** Changes to environment variables don't take effect.

**Solutions:**
1. Make sure you've reloaded your shell configuration (`source ~/.bashrc`)
2. Restart your terminal
3. Verify the variable is set: `echo $RAZTODO_DB` (Linux/macOS) or `echo $env:RAZTODO_DB` (Windows)
4. Check for typos in variable names (case-sensitive)

### Database Not Found

**Problem:** RazTodo can't find your database file.

**Solutions:**
1. Check if the database path is correct: `echo $RAZTODO_DB`
2. Verify the directory exists and is writable
3. Check file permissions: `ls -la ~/.local/share/raztodo/` (Linux/macOS)
4. Try using an absolute path instead of relative

### Logging Not Working

**Problem:** No log output even with `LOG_LEVEL=DEBUG`.

**Note:** RazTodo uses Python's logging system with `NullHandler` by default, which means logs are not printed to console. The `LOG_LEVEL` setting controls the internal logging level but may not produce visible output unless you're running in a development environment.

---

## Next Steps

- Learn about available commands in the [Usage Guide](USAGE.md)
- Understand the architecture in the [Architecture Documentation](ARCHITECTURE.md)
- Check installation options in the [Installation Guide](INSTALLATION.md)