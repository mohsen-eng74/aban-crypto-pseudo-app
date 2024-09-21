#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail


case "${1}" in
    app)
        echo "Starting web app..."
        ENVIRONMENT=${ENVIRONMENT} python fastapi run --host ${SERVER_HOST:-0.0.0.0} --port ${SERVER_PORT:-8000} --workers ${SERVER_WORKER_AMOUNT:-4} ${SERVER_ASGI_APP}
        ;;

    app-uvicorn)
        echo "Starting web app..."
        /project/docker/entrypoint.sh
        ;;

    *)
        echo "Unknown Operation!!!"
        ;;
esac
