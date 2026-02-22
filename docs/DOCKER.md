# Docker Guide  

This document describes how to provide an **optional** Docker experience for users of **RazTodo**. It contains a minimal, well-tested `Dockerfile`, recommended `README` snippet, and troubleshooting / testing steps so you (or contributors) can add Docker as an *opt-in* installation method.

---

## Goals

* Provide a **light, stable, and documented** Docker image users can run without installing Python or pip on their host.
* Keep the project philosophy (local, minimal, privacy-first) intact — Docker is **optional** and **does not replace** the native install instructions.
* Ensure SQLite database persists by mounting a host directory as a volume.

---

## Dockerfile

This `Dockerfile` installs `raztodo` from PyPI and ensures the app uses `/data/tasks.db` as its database when the host mounts `~/raztodo-data` (or any host path you choose).

```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RAZTODO_DB=/data/tasks.db

WORKDIR /app

# Install raztodo from PyPI (no cache)
RUN pip install --no-cache-dir raztodo

# Persist data under /data (mount this from host)
VOLUME ["/data"]

# Use a shell wrapper to ensure environment variables are applied at runtime
ENTRYPOINT ["sh", "-c", "rt \"$@\"", "--"]
```

**Notes:**

* `RAZTODO_DB` is the environment variable that raztodo reads to determine the database path. Setting it to `/data/tasks.db` ensures the app writes to the mounted volume.
* `VOLUME ["/data"]` declares the container mount point; when running, bind a host folder to `/data`.
* The `sh -c` wrapper passes arguments safely and ensures environment variables are visible at runtime.

---

## Installation

Build the image locally:
```bash
docker build -t raztodo:local .
````

Run raztodo and persist your tasks on the host (recommended):

```bash
mkdir -p "$HOME/raztodo-data"
# Add a task
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local add "My first docker task"
# List tasks
docker run --rm -it -v "$HOME/raztodo-data:/data" raztodo:local list
```

Notes:

* The database file will be created at `$HOME/raztodo-data/tasks.db` on your machine.
* Without `-v` the container is ephemeral and tasks will not persist.
* This is an **optional** convenience for users who prefer containers; keep the native install (pipx / pip) as the primary recommended path.

---

## Local testing checklist (before commit / PR)
1. Build image locally:
```bash
docker build -t raztodo:test .
````
2. Prepare host folder for database:
```bash
mkdir -p ~/raztodo-data
```
3. Add a task (ensure the container creates the DB in the mounted folder):
```bash
docker run --rm -it -v ~/raztodo-data:/data raztodo:test add "Test task from Docker"
```
4. List tasks (should show previously added item):
```bash
docker run --rm -it -v ~/raztodo-data:/data raztodo:test list
```
5. Confirm `tasks.db` exists on host:
```bash
ls -la ~/raztodo-data
# tasks.db should appear
```
6. Optional: remove image and test building/publishing steps in CI.
---

## Troubleshooting

* **No tasks found after adding**: confirm you ran the container with `-v host_path:/data` and that `RAZTODO_DB` in the image points to `/data/tasks.db` (see `ENV RAZTODO_DB=/data/tasks.db`). Also make sure the ENTRYPOINT wrapper is present.

* **DNS/network errors while building (`pip` fails to download)**: try building with network host mode:

```bash
docker build --network=host -t raztodo:test .
```

Or set Docker daemon DNS in `/etc/docker/daemon.json`:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

Then restart Docker: `sudo systemctl restart docker`.

* **File ownership/permission issues**: because `pip` runs as root inside image, created DB may be owned by `root` on the host. If you want files to be created with the same UID as the host user, consider (optionally) running the container with `--user $(id -u):$(id -g)` or adding a small non-root user in the Dockerfile. Example on `docker run`:

```bash
docker run --rm -it -u $(id -u):$(id -g) -v ~/raztodo-data:/data raztodo:test add "Task"
```