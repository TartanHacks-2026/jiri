#!/bin/bash
set -e

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! python -c "import redis; r=redis.from_url('${REDIS_URL:-redis://redis:6379/0}'); r.ping()" 2>/dev/null; do
    sleep 1
done
echo "Redis is ready!"

# Start the application
exec uvicorn src.api.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload
