#!/bin/sh

# Start Redis in the background
redis-server &

# Start the main application
exec python /app/app.py