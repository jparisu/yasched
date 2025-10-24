#!/bin/bash
# Start yasched streamlit app as a daemon

set -e

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_SCRIPT="${APP_DIR}/app/main.py"
PID_FILE="${APP_DIR}/.yasched_daemon.pid"
LOG_FILE="${APP_DIR}/.yasched_daemon.log"
PORT="${YASCHED_PORT:-8501}"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "yasched daemon is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: streamlit is not installed"
    echo "Install it with: pip install streamlit"
    exit 1
fi

# Check if app script exists
if [ ! -f "$APP_SCRIPT" ]; then
    echo "Error: App script not found at $APP_SCRIPT"
    exit 1
fi

# Start the daemon
echo "Starting yasched daemon..."
cd "$APP_DIR"

nohup streamlit run "$APP_SCRIPT" --server.port "$PORT" --server.headless true > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo "$PID" > "$PID_FILE"

# Wait a moment and check if it started successfully
sleep 2
if ps -p "$PID" > /dev/null 2>&1; then
    echo "yasched daemon started successfully (PID: $PID)"
    echo "Access the interface at: http://localhost:$PORT"
    echo "Logs are being written to: $LOG_FILE"
    echo "Use 'scripts/stop_daemon.sh' to stop the daemon"
else
    echo "Error: Failed to start yasched daemon"
    rm -f "$PID_FILE"
    exit 1
fi
