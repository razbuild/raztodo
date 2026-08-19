#!/bin/sh
set -e

mkdir -p /data 2>/dev/null || true

if [ "$1" = "rt-web" ] || [ "$1" = "web" ]; then
    shift
    exec rt-web "$@"
fi

exec rt "$@"
