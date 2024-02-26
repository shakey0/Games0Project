#!/bin/sh

# Start Redis in the background
redis-server &

# Run database migrations
flask db upgrade

# Start the main application
exec python /app/run.py