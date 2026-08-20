# Docker Guide  

This document describes how to run **RazTodo** with Docker, covering both the **CLI** (`rt`) and the **Web UI** (`rt-web`), with persistent SQLite storage via a `/data` volume.

Docker is **optional** and does not replace the native installation (see [INSTALLATION.md](INSTALLATION.md)).

---

## Goals

* Provide a **light, stable, and documented** Docker image users can run without installing Python or pip on their host.
* Keep the project philosophy (local, minimal, privacy-first) intact — Docker is **optional** and **does not replace** the native install instructions.
* Ensure SQLite database persists by mounting a host directory as a volume.

---

## Image overview

* Base image: `python:3.13-slim`
* Built from the repository source with `uv sync --frozen` (CLI + Web UI + shell completion via the `all` extra)
* Runs as a **non-root user** (default UID/GID `1000`, configurable via build args)
* Database at `/data/tasks.db` (`RAZTODO_DB`), persisted through a `/data` volume
* Web UI listens on `0.0.0.0:8000` (`RAZTODO_WEB_HOST` / `RAZTODO_WEB_PORT`)

CLI and Web UI share the same SQLite database whenever they use the same `/data` volume.

---

## Build

```bash
docker build -t raztodo:local .
```

To create files on the host with your own user id:

```bash
docker build --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g) -t raztodo:local .
```

---

## CLI

```bash
mkdir -p "$HOME/raztodo-data"

docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local add "My first docker task"
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local list
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local search "docker"
```

The database is created at `$HOME/raztodo-data/tasks.db`. Without `-v`, the container is ephemeral.

---

## Web UI

### With `docker run`

```bash
docker run -d --name raztodo-web -p 8000:8000 -v "$HOME/raztodo-data:/data" raztodo:local rt-web
```

Open `http://localhost:8000`.

### With Docker Compose (recommended)

```bash
docker compose up -d web
```

Open `http://localhost:8000`. Data is stored in the named volume `raztodo-data`, which survives `docker compose down`.

Stop the Web UI:

```bash
docker compose down
```

---

## CLI + Web UI sharing one database

Compose ships a `cli` service that uses the same named volume:

```bash
docker compose up -d web
docker compose run --rm cli add "Task added from the CLI"
# The task is immediately visible in the Web UI
```

With `docker run`, mount the same host folder in both containers:

```bash
docker run --rm -v "$HOME/raztodo-data:/data" raztodo:local add "Via CLI"
docker run -d -p 8000:8000 -v "$HOME/raztodo-data:/data" raztodo:local rt-web
```

---

## Security notes

* The image runs as a non-root user.
* The Compose `web` service runs with a read-only root filesystem, no new privileges, and all capabilities dropped.

---

## Troubleshooting

* **Database file owned by root on the host**: the container runs as UID `1000` by default; build with `--build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g)` to match your user, or run with `docker run --user $(id -u):$(id -g)`.
* **Web UI not reachable from the host**: ensure the container listens on `0.0.0.0` (`RAZTODO_WEB_HOST=0.0.0.0`, already set in the image) and that `-p 8000:8000` is used.
* **pip fails to download while building**: build with `--network=host`, or set Docker daemon DNS in `/etc/docker/daemon.json`.

---

## Local testing checklist (before commit / PR)

1. `docker build -t raztodo:test .`
2. `mkdir -p ~/raztodo-data && docker run --rm -it -v ~/raztodo-data:/data raztodo:test add "Test task from Docker"`
3. `docker run --rm -it -v ~/raztodo-data:/data raztodo:test list`
4. `docker run -d --name rt-web-test -p 8000:8000 -v ~/raztodo-data:/data raztodo:test rt-web` and open `http://localhost:8000`
5. `docker stop rt-web-test && docker rm rt-web-test` then run step 4 again — the tasks must still be listed (persistence).
6. `docker compose up -d web && docker compose run --rm cli list` — same database for CLI and Web.
7. `uv run pytest` — existing test suite must pass.
