#!/bin/sh
set -eu

mkdir -p /home/app/.cache /app/tmp
chown -R app:app /home/app/.cache /app/tmp

exec gosu app "$@"
