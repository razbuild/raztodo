#!/usr/bin/env bash

# rt-docker.sh
#
# Wrapper for RazTodo that delegates `rt` commands to a persistent Docker
# container named "raztodo" so you can use the tool without installing it
# on your host machine.
#
# Usage (add to your shell profile, e.g. ~/.bashrc or ~/.zshrc):
#
#   source /path/to/raztodo/docker/rt-docker.sh
#
# Then use `rt` as usual. When sourced, rt always runs inside the container
# (it is started on demand if it is not already running):
#
#   rt add "Prepare weekly groceries" --priority H
#   rt list
#   rt done 1
#
# Container lifecycle management:
#
#   rt-docker start     # create (if needed) and start the container
#   rt-docker stop      # stop and remove the container
#   rt-docker status    # show whether the container is running
#   rt-docker rebuild   # rebuild the image and restart the container
#
# Supported on Linux and macOS. For Windows, see rt-docker.ps1.
#
# Configuration (environment variables, all optional):
#   RAZTODO_DOCKER_IMAGE       Image name (default: raztodo:local)
#   RAZTODO_DOCKER_CONTAINER   Container name (default: raztodo)
#   RAZTODO_DATA_DIR           Host data directory mounted at /data (default: $HOME/raztodo-data)

set -u

_RT_DOCKER_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RT_DOCKER_PROJECT_DIR="$(dirname "$_RT_DOCKER_SCRIPT_DIR")"

RAZTODO_DOCKER_IMAGE="${RAZTODO_DOCKER_IMAGE:-raztodo:local}"
RAZTODO_DOCKER_CONTAINER="${RAZTODO_DOCKER_CONTAINER:-raztodo}"
RAZTODO_DATA_DIR="${RAZTODO_DATA_DIR:-$HOME/raztodo-data}"

_rt_docker_container_running() {
    docker ps --format '{{.Names}}' | grep -Fxq "$RAZTODO_DOCKER_CONTAINER"
}

_rt_docker_container_exists() {
    docker ps -a --format '{{.Names}}' | grep -Fxq "$RAZTODO_DOCKER_CONTAINER"
}

_rt_docker_create() {
    mkdir -p "$RAZTODO_DATA_DIR"
    local rc=0
    docker run -d \
        --name "$RAZTODO_DOCKER_CONTAINER" \
        -v "$RAZTODO_DATA_DIR:/data" \
        --entrypoint sleep \
        "$RAZTODO_DOCKER_IMAGE" \
        infinity >/dev/null 2>&1 || rc=$?
    return $rc
}

_rt_docker_start() {
    if _rt_docker_container_running; then
        printf 'RazTodo container "%s" is already running.\n' "$RAZTODO_DOCKER_CONTAINER"
        return 0
    fi

    if ! docker image inspect "$RAZTODO_DOCKER_IMAGE" >/dev/null 2>&1; then
        printf 'Image "%s" not found. Build it first:\n' "$RAZTODO_DOCKER_IMAGE" >&2
        printf '  docker build --build-arg USER_UID=$(id -u) --build-arg USER_GID=$(id -g) -t %s %s\n' \
            "$RAZTODO_DOCKER_IMAGE" "$RT_DOCKER_PROJECT_DIR" >&2
        return 1
    fi

    if _rt_docker_container_exists; then
        docker start "$RAZTODO_DOCKER_CONTAINER" >/dev/null 2>&1 || {
            printf 'Failed to start container "%s".\n' "$RAZTODO_DOCKER_CONTAINER" >&2
            return 1
        }
        printf 'Started RazTodo container "%s".\n' "$RAZTODO_DOCKER_CONTAINER"
        return 0
    fi

    _rt_docker_create || {
        printf 'Failed to create container "%s".\n' "$RAZTODO_DOCKER_CONTAINER" >&2
        return 1
    }
    printf 'Created and started RazTodo container "%s".\n' "$RAZTODO_DOCKER_CONTAINER"
    printf 'Database is persisted at %s/tasks.db\n' "$RAZTODO_DATA_DIR"
}

_rt_docker_stop() {
    if _rt_docker_container_exists; then
        docker rm -f "$RAZTODO_DOCKER_CONTAINER" >/dev/null
        printf 'Stopped and removed RazTodo container "%s".\n' "$RAZTODO_DOCKER_CONTAINER"
    else
        printf 'RazTodo container "%s" does not exist.\n' "$RAZTODO_DOCKER_CONTAINER"
    fi
}

_rt_docker_status() {
    if _rt_docker_container_running; then
        printf 'RazTodo container "%s" is running.\n' "$RAZTODO_DOCKER_CONTAINER"
        printf 'Host data directory: %s\n' "$RAZTODO_DATA_DIR"
    else
        printf 'RazTodo container "%s" is not running.\n' "$RAZTODO_DOCKER_CONTAINER"
    fi
}

_rt_docker_rebuild() {
    _rt_docker_stop
    docker build \
        --build-arg USER_UID="$(id -u)" \
        --build-arg USER_GID="$(id -g)" \
        -t "$RAZTODO_DOCKER_IMAGE" \
        "$RT_DOCKER_PROJECT_DIR" || return $?
    _rt_docker_start
}

rt() {
    if ! command -v docker >/dev/null 2>&1; then
        printf 'Docker is required to run raztodo via the %s container but was not found.\n' "$RAZTODO_DOCKER_IMAGE" >&2
        printf 'Install Docker first, or install raztodo natively (pipx install raztodo).\n' >&2
        return 1
    fi

    if ! _rt_docker_container_running; then
        _rt_docker_start || return $?
    fi

    local -a exec_opts=(-i)
    [[ -t 1 ]] && exec_opts+=(-t)
    docker exec "${exec_opts[@]}" "$RAZTODO_DOCKER_CONTAINER" rt "$@"
}

rt-docker() {
    local cmd="${1:-status}"
    shift 2>/dev/null || true

    case "$cmd" in
        start)   _rt_docker_start ;;
        stop)    _rt_docker_stop ;;
        status)  _rt_docker_status ;;
        rebuild) _rt_docker_rebuild ;;
        *)
            printf 'Usage: rt-docker {start|stop|status|rebuild}\n' >&2
            return 1
            ;;
    esac
}
