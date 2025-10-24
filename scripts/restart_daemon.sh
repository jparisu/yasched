#!/bin/bash
# Restart yasched streamlit daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Restarting yasched daemon..."

# Stop the daemon if running
"${SCRIPT_DIR}/stop_daemon.sh"

# Wait a moment
sleep 2

# Start the daemon
"${SCRIPT_DIR}/start_daemon.sh"
