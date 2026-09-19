#!/bin/bash
set -e

# Run database seed in background on startup (seeds 18 fictional candidates if table is empty)
# python seed.py &

# Start the uvicorn server in foreground
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
