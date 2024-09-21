#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail


HYPHEN_SYMBOL='-'
uvicorn \
    --host ${SERVER_HOST:-0.0.0.0} \
    --port ${SERVER_PORT:-8000} \
    --workers ${SERVER_WORKER_AMOUNT:-4} \
    --log-level ${SERVER_LOG_LEVEL:-info} \
    --access-log \
    --proxy-headers \
    --limit-concurrency ${SERVER_LIMIT_CONCURRENCY:-4096} \
    --backlog ${SERVER_BACKLOG:-2048} \
    --limit-max-requests ${SERVER_LIMIT_MAX_REQUESTS:-2048} \
    --timeout-keep-alive ${SERVER_TIMEOUT_KEEP_ALIVE:-15} \
    --timeout-graceful-shutdown ${SERVER_TIMEOUT_GRACEFUL_SHUTDOWN:-15} \
    "${SERVER_ASGI_APP}"
