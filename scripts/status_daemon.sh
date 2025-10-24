#!/bin/bash
# Check status of yasched streamlit daemon

# Configuration
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="${APP_DIR}/.yasched_daemon.pid"
LOG_FILE="${APP_DIR}/.yasched_daemon.log"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: Not running"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Status: Running"
    echo "PID: $PID"
    
    # Get process info
    if command -v ps &> /dev/null; then
        echo "Process info:"
        ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime
    fi
    
    # Show last few log lines
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "Last 10 log lines:"
        tail -n 10 "$LOG_FILE"
    fi
    
    exit 0
else
    echo "Status: Not running (stale PID file)"
    exit 1
fi
