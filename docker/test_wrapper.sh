#!/usr/bin/env bash

# test_wrapper.sh
#
# Integration tests for docker/rt-docker.sh. Requires Docker and the project
# Dockerfile. Uses a dedicated image/container/data-dir so it never touches
# a user's real "raztodo" setup.
#
# Usage:
#   bash docker/test_wrapper.sh
#
# Exit status: 0 if all tests pass, 1 otherwise.

set -u

TEST_IMAGE="raztodo:test-wrapper"
TEST_CONTAINER="raztodo-test-wrapper"
TEST_DATA_DIR="$(mktemp -d)"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PASSED=0
FAILED=0

cleanup() {
    docker rm -f "$TEST_CONTAINER" >/dev/null 2>&1 || true
    docker image rm "$TEST_IMAGE" >/dev/null 2>&1 || true
    rm -rf "$TEST_DATA_DIR"
    [ -n "${TEST_REBUILD_DIR:-}" ] && rm -rf "$TEST_REBUILD_DIR"
}
trap cleanup EXIT

fail() {
    printf '  FAIL: %s\n' "$1"
    FAILED=$((FAILED + 1))
}

ok() {
    printf '  ok:   %s\n' "$1"
    PASSED=$((PASSED + 1))
}

test_not_running_initially() {
    printf '\n[test] container not running initially\n'
    if _rt_docker_container_running; then
        fail "container reported as running before creation"
    else
        ok "container not reported as running before creation"
    fi

    if _rt_docker_container_exists; then
        fail "container reported as existing before creation"
    else
        ok "container not reported as existing before creation"
    fi
}

test_start_creates_container() {
    printf '\n[test] start creates and starts the container\n'
    _rt_docker_start
    if ! _rt_docker_container_running; then
        fail "container not running after start"
    else
        ok "container running after start"
    fi
}

test_start_is_idempotent() {
    printf '\n[test] start is idempotent\n'
    local before
    before="$(docker ps -a --format '{{.Names}}' | grep -c "$TEST_CONTAINER")"
    _rt_docker_start
    local after
    after="$(docker ps -a --format '{{.Names}}' | grep -c "$TEST_CONTAINER")"
    if [ "$after" -ne "$before" ] || [ "$after" -ne 1 ]; then
        fail "start duplicated the container (before=$before after=$after)"
    else
        ok "start left a single container (count=$after)"
    fi
}

test_container_runs_as_nonroot() {
    printf '\n[test] container runs as non-root\n'
    local user_id
    user_id="$(docker exec "$TEST_CONTAINER" id -u)"
    if [ "$user_id" != "0" ]; then
        ok "container user id is non-root ($user_id)"
    else
        fail "container runs as root"
    fi
}

test_rt_delegates_to_container() {
    printf '\n[test] rt delegates to the container\n'
    local output
    output="$(rt --version 2>&1)"
    if printf '%s' "$output" | grep -q "raztodo"; then
        ok "rt --version returned raztodo output: $output"
    else
        fail "rt --version did not return raztodo output: $output"
    fi
}

test_persistence_across_restart() {
    printf '\n[test] data persists across stop/start\n'
    rt add "wrapper persistence test"

    _rt_docker_stop
    if _rt_docker_container_exists; then
        fail "container still exists after stop"
    fi

    rt list >/dev/null 2>&1
    if rt list 2>&1 | grep -q "wrapper persistence test"; then
        ok "task persisted across container restart"
    else
        fail "task did not persist across container restart"
    fi
}

test_stop_removes_container() {
    printf '\n[test] stop removes the container\n'
    _rt_docker_start
    _rt_docker_stop
    if _rt_docker_container_exists; then
        fail "container still exists after stop"
    else
        ok "container removed after stop"
    fi
}

test_start_fails_without_image() {
    printf '\n[test] start fails cleanly when the image is missing\n'
    local original_image="$RAZTODO_DOCKER_IMAGE"
    RAZTODO_DOCKER_IMAGE="raztodo:does-not-exist"

    local output rc=0
    output="$(_rt_docker_start 2>&1)" || rc=$?

    RAZTODO_DOCKER_IMAGE="$original_image"

    if [ "$rc" -ne 0 ]; then
        ok "start returned non-zero when image is missing"
    else
        fail "start succeeded with a missing image"
    fi
    if printf '%s' "$output" | grep -q "Image.*not found"; then
        ok "start reported the missing image"
    else
        fail "start did not report the missing image: $output"
    fi
}

test_rebuild_from_subdirectory() {
    printf '\n[test] rebuild succeeds when invoked outside the project directory\n'
    TEST_REBUILD_DIR="$(mktemp -d)"

    (cd "$TEST_REBUILD_DIR" && _rt_docker_rebuild)
    local rc=$?

    if [ "$rc" -eq 0 ]; then
        ok "rebuild succeeded from $TEST_REBUILD_DIR"
    else
        fail "rebuild failed from $TEST_REBUILD_DIR (exit $rc)"
    fi

    if _rt_docker_container_running; then
        ok "container running after rebuild"
    else
        fail "container not running after rebuild"
    fi
}

main() {
    if ! command -v docker >/dev/null 2>&1; then
        printf 'Docker is required to run this test script.\n' >&2
        return 1
    fi

    printf 'Building test image "%s" (this may take a while)...\n' "$TEST_IMAGE"
    docker build \
        --build-arg USER_UID="$(id -u)" \
        --build-arg USER_GID="$(id -g)" \
        -t "$TEST_IMAGE" \
        "$PROJECT_DIR" || {
        printf 'Failed to build the test image.\n' >&2
        return 1
    }

    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/rt-docker.sh"
    RAZTODO_DOCKER_IMAGE="$TEST_IMAGE"
    RAZTODO_DOCKER_CONTAINER="$TEST_CONTAINER"
    RAZTODO_DATA_DIR="$TEST_DATA_DIR"

    test_not_running_initially
    test_start_creates_container
    test_start_is_idempotent
    test_container_runs_as_nonroot
    test_rt_delegates_to_container
    test_persistence_across_restart
    test_stop_removes_container
    test_start_fails_without_image
    test_rebuild_from_subdirectory

    printf '\n%s passed, %s failed\n' "$PASSED" "$FAILED"
    [ "$FAILED" -eq 0 ]
}

main