# 🐳 Podman Guide

This document describes how to run **RazTodo** with [Podman](https://podman.io/).

Podman is optional, just like Docker, and does not replace the native installation (see [INSTALLATION.md](INSTALLATION.md)).

> The image contains the **RazTodo CLI only**. The Web UI is maintained separately in the [`raztodo-web`](https://github.com/razbuild/raztodo-web) project.

## Why Podman?

- No Docker daemon required — Podman runs containers directly (rootless by default)
- Drop-in compatible with the Docker CLI for every command this project uses (`build`, `run`, `exec`, `ps`, `image inspect`, `start`, `rm`)
- The same image and the same `/data` volume layout work unchanged

The RazTodo `Dockerfile` builds cleanly with Podman, and the same persistent `/data` SQLite volume layout applies. Everything documented in the [Docker Guide](DOCKER.md) works with Podman — this page notes the small differences.

---

## 🎯 Same goals

- Provide a light, stable, documented image that runs without installing Python on the host
- Keep the project philosophy intact: local, minimal, privacy-first
- Run RazTodo as a non-root user
- Persist the SQLite database through a `/data` volume

---

## 📦 Image overview

Identical to the [Docker image](DOCKER.md#-image-overview):

- Base image: `python:3.13-slim`
- Built from source with `uv sync --frozen`
- Runs as a non-root user (default UID/GID `1000`, configurable via build args)
- Database location: `/data/tasks.db` (via `RAZTODO_DB`)
- `/data` is declared as a volume
- Entrypoint: `rt`

---

## 🔨 Build

```bash
podman build -t raztodo:local .
```

To match the container user with your host user (helps avoid permission issues with bind mounts):

```bash
podman build \
  --build-arg USER_UID=$(id -u) \
  --build-arg USER_GID=$(id -g) \
  -t raztodo:local .
```

> 💡 The seamless `rt` wrappers in `docker/` (the `rt-docker.sh` / `rt-docker.ps1` helpers added in #81) work with Podman out of the box. By default they use Docker; to point them at Podman, set `RAZTODO_CONTAINER_RUNTIME=podman` before sourcing/importing the wrapper. See [Seamless `rt` usage](#-seamless-rt-usage-with-the-wrapper).

---

## ⚙️ CLI usage

Since the entrypoint is `rt`, arguments pass straight to the RazTodo CLI:

```bash
podman run --rm raztodo:local --help
podman run --rm raztodo:local --version
podman run --rm raztodo:local add "My first Podman task"
podman run --rm raztodo:local list
podman run --rm raztodo:local search "podman"
```

---

## ⚡ Seamless `rt` usage with the wrapper

The `docker/` wrappers (from #81) are runtime-agnostic. They pick a container CLI in this order:

1. `RAZTODO_CONTAINER_RUNTIME` if set to `docker` or `podman`
2. otherwise `docker` when it is on `PATH`
3. otherwise `podman`
4. otherwise they fail with a clear message

### Use the existing wrappers with Podman

**Linux / macOS** — set the runtime, then source the shell wrapper:

```bash
export RAZTODO_CONTAINER_RUNTIME=podman
source /path/to/raztodo/docker/rt-docker.sh
```

**Windows** — set the runtime in PowerShell, then import the module:

```powershell
$env:RAZTODO_CONTAINER_RUNTIME = "podman"
Import-Module /path/to/raztodo/docker/rt-docker.ps1
```

Then use `rt` exactly as documented in the [Docker Guide](DOCKER.md#-seamless-rt-usage-with-a-wrapper):

```bash
rt add "Prepare weekly groceries" --priority H
rt list
rt done 1
```

All lifecycle commands (`rt-docker status` / `start` / `stop` / `rebuild` on Unix, `Invoke-RtDocker ...` on Windows) are unchanged — they just run against Podman instead of Docker.

### Configuration

The wrappers honor the same environment variables as the Docker workflow:

| Variable | Description | Default |
|---|---|---|
| `RAZTODO_DOCKER_IMAGE` | Image to run | `raztodo:local` |
| `RAZTODO_DOCKER_CONTAINER` | Container name | `raztodo` |
| `RAZTODO_DATA_DIR` | Host data directory mounted at `/data` | `$HOME/raztodo-data` |
| `RAZTODO_CONTAINER_RUNTIME` | Container CLI: `docker` or `podman` | auto (`docker`, falling back to `podman`) |

> The image/container variable names keep the `RAZTODO_DOCKER_*` prefix for backward compatibility; they apply to Podman runs too.

---

## 💾 Persistent database

The same bind-mount and named-volume patterns from the [Docker Guide](DOCKER.md#-persistent-database) work with Podman, substituting `podman` for `docker`:

```bash
mkdir -p "$HOME/raztodo-data"

podman run --rm \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  add "My first persistent task"

podman run --rm \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  list
```

The database lives at `$HOME/raztodo-data/tasks.db` and survives container restarts.

---

## 🖥️ Interactive shell

```bash
podman run --rm -it --entrypoint sh raztodo:local
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
- No capabilities required
- Application data isolated under `/data`
- Podman is rootless by default (no privileged mode needed)

For runtime hardening, use the same flags as the [Docker workflow](DOCKER.md#-security):

```bash
podman run --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  -v "$HOME/raztodo-data:/data" \
  raztodo:local \
  list
```

---

## ✅ Local testing checklist

Before committing Podman changes:

1. Build the image
   ```bash
   podman build \
     --build-arg USER_UID=$(id -u) \
     --build-arg USER_GID=$(id -g) \
     -t raztodo:test .
   ```
2. Test the CLI: `podman run --rm raztodo:test --help`
3. Test the version: `podman run --rm raztodo:test --version`
4. Create a task
   ```bash
   podman run --rm -v "$HOME/raztodo-test-data:/data" raztodo:test add "Podman persistence test"
   ```
5. Verify the task
   ```bash
   podman run --rm -v "$HOME/raztodo-test-data:/data" raztodo:test list
   ```
6. Confirm the container runs as non-root: `podman run --rm --entrypoint id raztodo:test -un`
7. Clean up: `rm -rf "$HOME/raztodo-test-data"`
8. Run the Python test suite: `uv run pytest`

> The automated wrapper test `docker/test_wrapper.sh` is runtime-agnostic too: set `RAZTODO_CONTAINER_RUNTIME=podman` to exercise the Podman path.
