# Configuration

yasched uses YAML files for configuration, making it easy to define and manage tasks.

## Configuration Structure

A basic configuration file has the following structure:

```yaml
tasks:
  - name: task_name
    description: Optional description
    schedule: schedule_specification
    action: action_name
    enabled: true
    parameters:
      key: value
```

## Required Fields

Each task must have:

- **name**: Unique identifier for the task
- **schedule**: When the task should run
- **action**: What the task should do

## Optional Fields

- **description**: Human-readable description of the task
- **enabled**: Whether the task is active (default: `true`)
- **parameters**: Dictionary of parameters to pass to the action

## Example Configuration

```yaml
tasks:
  - name: backup_database
    description: Daily database backup
    schedule: every day at 02:00
    action: custom
    enabled: true
    parameters:
      function: backup.run_backup
      database: production
  
  - name: send_report
    description: Weekly report generation
    schedule: every friday at 17:00
    action: log
    enabled: true
    parameters:
      message: "Weekly report generated"
      level: info
  
  - name: health_check
    description: Check system health every 5 minutes
    schedule: every 5 minutes
    action: print
    enabled: true
    parameters:
      message: "System health check"
```

## Loading Configuration

### From File

```python
from yasched.config import load_config

config = load_config("path/to/config.yaml")
```

### Validating Configuration

```python
from yasched.config import validate_config

try:
    validate_config(config)
    print("Configuration is valid!")
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

### Saving Configuration

```python
from yasched.config import save_config

config = {
    "tasks": [
        {
            "name": "my_task",
            "schedule": "every 1 hour",
            "action": "print",
            "parameters": {"message": "Hello!"}
        }
    ]
}

save_config(config, "path/to/config.yaml")
```

## Configuration Best Practices

1. **Use descriptive names**: Make task names clear and meaningful
2. **Add descriptions**: Help others understand what each task does
3. **Group related tasks**: Organize tasks logically
4. **Version control**: Keep configuration files in version control
5. **Test before deployment**: Validate configurations before running
6. **Use comments**: YAML supports comments with `#`

## Example with Comments

```yaml
# Task configurations for production environment
tasks:
  # Database maintenance tasks
  - name: optimize_tables
    description: Optimize database tables weekly
    schedule: every sunday at 03:00
    action: custom
    enabled: true
    parameters:
      function: db.optimize_tables
  
  # Monitoring tasks
  - name: disk_space_check
    description: Check disk space every hour
    schedule: every 1 hour
    action: log
    enabled: true
    parameters:
      message: "Disk space check completed"
      level: info
```

## Next Steps

- Learn about [Tasks](../user-guide/tasks.md)
- Explore [Actions](../user-guide/actions.md)
- Set up [Scheduling](../user-guide/scheduling.md)
