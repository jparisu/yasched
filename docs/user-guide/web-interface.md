# Web Interface

yasched includes a beautiful web interface built with Streamlit for managing tasks visually.

## Starting the Web Interface

### Regular Mode

```bash
streamlit run app/main.py
```

The interface will be available at `http://localhost:8501`

### Daemon Mode

Run as a background service:

```bash
# Start daemon
./scripts/start_daemon.sh

# Check status
./scripts/status_daemon.sh

# Stop daemon
./scripts/stop_daemon.sh

# Restart daemon
./scripts/restart_daemon.sh
```

### Custom Port

```bash
# Set custom port
export YASCHED_PORT=8080
./scripts/start_daemon.sh

# Or directly with streamlit
streamlit run app/main.py --server.port 8080
```

## Interface Overview

### Dashboard

The dashboard provides an overview of your tasks:

- **Total Tasks**: Number of configured tasks
- **Enabled Tasks**: Number of active tasks
- **Disabled Tasks**: Number of inactive tasks
- **Total Runs**: Combined execution count

**Quick Actions:**
- View task details
- Run tasks manually
- Monitor execution status

### Tasks Page

Manage your tasks with three tabs:

#### View Tasks Tab
- List all tasks
- See task status (enabled/disabled)
- Enable/disable tasks
- Delete tasks
- View task details

#### Add Task Tab
Create new tasks with:
- Task name (required)
- Description (optional)
- Schedule specification (required)
- Action selection (required)
- Action parameters
- Enable/disable toggle

#### Edit Task Tab
Modify existing tasks:
- Select task from dropdown
- Update description
- Change schedule
- Toggle enabled status

### Configuration Page

Manage YAML configurations:

#### View/Edit Tab
- Edit configuration directly in YAML format
- Validate configuration
- Apply changes
- Reset to defaults

#### Import Tab
- Upload YAML configuration files
- Preview configuration before applying
- Validate imported configurations
- Apply imported configurations

#### Export Tab
- View current configuration
- Download as YAML file
- Share configurations with team

### About Page

Information about yasched:
- Feature overview
- Quick start guide
- Configuration examples
- Available actions
- Links to documentation

## Features

### Task Management

**Create Tasks:**
1. Go to Tasks → Add Task
2. Fill in task details
3. Click "Add Task"

**Edit Tasks:**
1. Go to Tasks → Edit Task
2. Select task from dropdown
3. Modify fields
4. Click "Update Task"

**Delete Tasks:**
1. Go to Tasks → View Tasks
2. Click "Delete" button for task
3. Task is removed immediately

**Enable/Disable Tasks:**
1. Go to Tasks → View Tasks
2. Click "Enable" or "Disable" button
3. Status updates immediately

**Manual Execution:**
1. Go to Dashboard
2. Expand task details
3. Click "Run Now"
4. Task executes immediately

### Configuration Management

**Edit Configuration:**
1. Go to Configuration → View/Edit
2. Edit YAML directly
3. Click "Save & Apply"
4. Changes take effect immediately

**Import Configuration:**
1. Go to Configuration → Import
2. Upload YAML file
3. Review preview
4. Click "Apply Configuration"

**Export Configuration:**
1. Go to Configuration → Export
2. Review configuration
3. Click "Download Configuration"

## Tips and Tricks

### Keyboard Shortcuts

Streamlit provides several keyboard shortcuts:
- `R`: Rerun the app
- `C`: Clear cache
- `?`: Show keyboard shortcuts

### Sidebar Navigation

Use the sidebar to quickly navigate between pages:
- Dashboard
- Tasks
- Configuration
- About

### Quick Actions

Sidebar provides quick actions:
- **Reload Config**: Refresh configuration from session
- **Clear All Tasks**: Remove all tasks (use with caution!)

### Task Filtering

Tasks are displayed in order of creation. Use the search feature in your browser (Ctrl+F / Cmd+F) to find specific tasks.

## Customization

### Custom Port

Change the default port (8501):

```bash
streamlit run app/main.py --server.port 8080
```

### Theme

Streamlit supports light and dark themes. Toggle using the menu (≡) → Settings → Theme.

### Server Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = false
enableCORS = false

[theme]
primaryColor = "#4F46E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
```

## Security Considerations

### Production Deployment

When deploying to production:

1. **Use authentication**: Configure Streamlit authentication
2. **Enable HTTPS**: Use SSL/TLS certificates
3. **Restrict access**: Use firewall rules
4. **Regular updates**: Keep dependencies updated

### Example: Basic Authentication

Use Streamlit's authentication features or deploy behind a reverse proxy with authentication.

## Troubleshooting

### Port Already in Use

```bash
# Kill process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run app/main.py --server.port 8080
```

### Interface Not Loading

1. Check if Streamlit is installed: `pip list | grep streamlit`
2. Verify app script exists: `ls app/main.py`
3. Check for errors in terminal output
4. Try clearing cache: Delete `.streamlit` directory

### Changes Not Appearing

1. Click the "Rerun" button or press `R`
2. Clear cache: Menu (≡) → Clear cache
3. Restart the application

## Next Steps

- Learn about [Tasks](tasks.md)
- Explore [Actions](actions.md)
- Configure [Scheduling](scheduling.md)
