# 🐳 Docker Guide

This document describes how to run **RazTodo** with Docker.

Docker is optional and does not replace the native installation (see [INSTALLATION.md](INSTALLATION.md)).

> The Docker image contains the **RazTodo CLI only**. The Web UI is maintained separately in the [`raztodo-web`](https://github.com/razbuild/raztodo-web) project.

---

## 🎯 Goals

- Provide a light, stable, documented image that runs without installing Python on the host
- Keep the project philosophy intact: local, minimal, privacy-first
- Run RazTodo as a non-root user
- Persist the SQLite database through a `/data` volume

---

## 📦 Image overview

- Base image: `python:3.13-slim`
- Built from source with `uv sync --frozen`
- Runs as a non-root user (default UID/GID `1000`, configurable via build args)
- Database location: `/data/tasks.db` (via `RAZTODO_DB`)
- `/data` is declared as a Docker volume
- Entrypoint: `rt`

---

## 🔨 Build

```bash
docker build -t raztodo:local .
```

To match the container user with your host user (helps avoid permission issues with bind mounts):

```bash
docker build \
  --build-arg USER_UID=$(id -u) \
  --build-arg USER_GID=$(id -g) \
  -t raztodo:local .
```

---

## ⚙️ CLI usage

Since the entrypoint is `rt`, arguments pass straight to the RazTodo CLI:

```bash
docker run --rm raztodo:local --help
docker run --rm raztodo:local --version
docker run --rm raztodo:local add "My first Docker task"
docker run --rm raztodo:local list
docker run --rm raztodo:local search "docker"
```

---

## ⚡ Seamless `rt` usage with a wrapper

Instead of typing `docker exec` / `docker run` every time, you can set up a
**wrapper** that delegates local `rt ...` commands to a persistent Docker
container automatically (starting it on demand). This works on **Linux**,
**macOS**, and **Windows**.

### How it works

The wrapper runs a single long-lived container (named `raztodo`) with your
host's `$HOME/raztodo-data` directory mounted at `/data`. When you type
`rt <command>`, it:

1. Starts the container if it is not already running;
2. Executes `docker exec raztodo rt <command>` and returns the output.

> [!TIP]
> When the wrapper is sourced/imported, `rt` always runs inside the Docker
> container. If you prefer the native CLI, install raztodo directly and do
> **not** source the wrapper (see [INSTALLATION.md](INSTALLATION.md)).

The database is persisted at `$HOME/raztodo-data/tasks.db`.

### Build the image once

```bash
docker build \
  --build-arg USER_UID=$(id -u) \
  --build-arg USER_GID=$(id -g) \
  -t raztodo:local .
```

### Linux / macOS

Add the wrapper to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
source /path/to/raztodo/docker/rt-docker.sh
```

Then use `rt` normally:

```bash
rt add "Prepare weekly groceries" --priority H
rt list
rt done 1
rt search "groceries"
```

Manage the container with:

```bash
rt-docker status   # is it running?
rt-docker start    # create (if needed) and start it
rt-docker stop     # stop and remove it
rt-docker rebuild  # rebuild the image and restart
```

### Windows

Add the wrapper to your PowerShell profile:

```powershell
Import-Module /path/to/raztodo/docker/rt-docker.ps1
```

Then use `rt` exactly as above. Manage the container with:

```powershell
Invoke-RtDocker status
Invoke-RtDocker start
Invoke-RtDocker stop
Invoke-RtDocker rebuild
```

### Configuration

All wrappers honor these environment variables (set before sourcing/importing):

| Variable | Description | Default |
|---|---|---|
| `RAZTODO_DOCKER_IMAGE` | Docker image to run | `raztodo:local` |
| `RAZTODO_DOCKER_CONTAINER` | Container name | `raztodo` |
| `RAZTODO_DATA_DIR` | Host data directory mounted at `/data` | `$HOME/raztodo-data` |

---

## 💾 Persistent database

### Bind mount

```bash
mkdir -p "$HOME/raztodo-data"

docker run --rm \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  add "My first persistent task"

docker run --rm \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  list
```

The database lives at `$HOME/raztodo-data/tasks.db` and survives container restarts.

> Without a volume mount, the database only exists inside the container's writable layer and is lost when the container is removed.

### Named volume

```bash
docker volume create raztodo-data

docker run --rm \
  -v raztodo-data:/data \
  raztodo:local \
  add "Task stored in Docker volume"

docker run --rm \
  -v raztodo-data:/data \
  raztodo:local \
  list

docker volume inspect raztodo-data
```

> Removing the volume permanently deletes the database stored in it: `docker volume rm raztodo-data`

---

## 🖥️ Interactive shell

Normal usage invokes `rt` directly. For debugging, override the entrypoint:

```bash
docker run --rm -it --entrypoint sh raztodo:local
```

Then, inside the container:

```bash
rt --version
rt list
rt add "Interactive test"
```

---

## 🔒 Security

- Runs as a non-root user
- No Linux capabilities required
- Application data isolated under `/data`
- No privileged access required

For extra runtime hardening:

```bash
docker run --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  list
```

---

## 🩹 Troubleshooting

**Database permission errors**
Build with your host UID/GID (see [Build](#-build)), or make sure the mounted directory is writable by the container user.

**Changing the database location**

```bash
docker run --rm \
  -e RAZTODO_DB=/data/custom.db \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  list
```

**Build or network problems**
The image installs dependencies from the lock file with `uv`. If downloads fail during the build, check Docker's network and DNS access.

---

## ✅ Local testing checklist

Before committing Docker changes:

1. Build the image
   ```bash
   docker build \
     --build-arg USER_UID=$(id -u) \
     --build-arg USER_GID=$(id -g) \
     -t raztodo:test .
   ```
2. Test the CLI: `docker run --rm raztodo:test --help`
3. Test the version: `docker run --rm raztodo:test --version`
4. Clean up any stale test volume: `docker volume rm raztodo-test-data 2>/dev/null || true`
5. Create a task
   ```bash
   docker run --rm -v raztodo-test-data:/data raztodo:test add "Docker persistence test"
   ```
6. Verify the task
   ```bash
   docker run --rm -v raztodo-test-data:/data raztodo:test list
   ```
7. Confirm the container runs as non-root: `docker run --rm --entrypoint id raztodo:test -un`
8. Remove the test volume: `docker volume rm raztodo-test-data`
9. Run the Python test suite: `uv run pytest`