#!/bin/bash
# Stop yasched streamlit daemon

set -e

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${APP_DIR}/.yasched_daemon.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "yasched daemon is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "yasched daemon is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

# Stop the daemon
echo "Stopping yasched daemon (PID: $PID)..."
kill "$PID"

# Wait for process to terminate
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "yasched daemon stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Force killing yasched daemon..."
    kill -9 "$PID"
    sleep 1
fi

rm -f "$PID_FILE"
echo "yasched daemon stopped"
