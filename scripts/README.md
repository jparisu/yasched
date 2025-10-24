# Daemon Management Scripts

This directory contains scripts for managing the yasched Streamlit app as a daemon (background service).

## Scripts

- `start_daemon.sh` - Start the yasched daemon
- `stop_daemon.sh` - Stop the yasched daemon
- `status_daemon.sh` - Check daemon status
- `restart_daemon.sh` - Restart the daemon

## Usage

### Start the Daemon

```bash
./scripts/start_daemon.sh
```

This will:
- Start the Streamlit app in headless mode
- Run it as a background process
- Create a PID file (`.yasched_daemon.pid`)
- Log output to `.yasched_daemon.log`
- Make it accessible at http://localhost:8501

### Stop the Daemon

```bash
./scripts/stop_daemon.sh
```

This will gracefully stop the running daemon and clean up the PID file.

### Check Status

```bash
./scripts/status_daemon.sh
```

This will show:
- Whether the daemon is running
- Process ID (PID)
- Process information
- Last 10 log lines

### Restart the Daemon

```bash
./scripts/restart_daemon.sh
```

This will stop the daemon (if running) and start it again.

## Configuration

### Custom Port

Set a custom port using the `YASCHED_PORT` environment variable:

```bash
export YASCHED_PORT=8080
./scripts/start_daemon.sh
```

The daemon will then be accessible at http://localhost:8080

### Log Files

Daemon logs are written to `.yasched_daemon.log` in the project root. You can:

```bash
# View logs in real-time
tail -f .yasched_daemon.log

# View recent logs
tail -n 50 .yasched_daemon.log

# Search logs
grep "error" .yasched_daemon.log
```

## System Service (Optional)

For production deployments, consider creating a systemd service:

### Create Service File

Create `/etc/systemd/system/yasched.service`:

```ini
[Unit]
Description=yasched Task Scheduler
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/yasched
ExecStart=/usr/bin/streamlit run app/main.py --server.port 8501 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Manage Service

```bash
# Enable and start service
sudo systemctl enable yasched
sudo systemctl start yasched

# Check status
sudo systemctl status yasched

# View logs
sudo journalctl -u yasched -f

# Stop service
sudo systemctl stop yasched
```

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Find and kill process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
export YASCHED_PORT=8502
./scripts/start_daemon.sh
```

### Permission Denied

Make sure scripts are executable:

```bash
chmod +x scripts/*.sh
```

### Daemon Won't Start

1. Check if streamlit is installed: `streamlit --version`
2. Check if app script exists: `ls app/main.py`
3. Review logs: `cat .yasched_daemon.log`
4. Try running directly: `streamlit run app/main.py`

### Daemon Won't Stop

If the daemon won't stop gracefully:

```bash
# Force kill using PID
kill -9 $(cat .yasched_daemon.pid)

# Or find and kill all streamlit processes
pkill -f "streamlit run"
```

## Notes

- The daemon scripts use `nohup` to detach from the terminal
- PID and log files are created in the project root
- These files are ignored by git (see `.gitignore`)
- Always check logs if something goes wrong
