# Actions

Actions define what tasks should do when they execute. yasched provides several built-in actions and supports custom actions.

## Built-in Actions

### Print Action

Prints a message to stdout.

**Parameters:**
- `message` (string): The message to print

**Example:**
```yaml
tasks:
  - name: hello_world
    schedule: every 1 minute
    action: print
    parameters:
      message: "Hello, World!"
```

### Log Action

Logs a message using Python's logging module.

**Parameters:**
- `message` (string): The message to log
- `level` (string): Log level (debug, info, warning, error, critical)

**Example:**
```yaml
tasks:
  - name: log_status
    schedule: every 5 minutes
    action: log
    parameters:
      message: "System status check"
      level: info
```

### Custom Action

Execute a custom Python function.

**Parameters:**
- `function` (string): Fully qualified function name
- Additional parameters are passed to the function

**Example:**
```yaml
tasks:
  - name: custom_task
    schedule: every 1 hour
    action: custom
    parameters:
      function: "mymodule.myfunction"
      param1: value1
      param2: value2
```

## Creating Custom Actions

### Via Python API

```python
from yasched.actions import register_action

def my_custom_action(param1: str, param2: int) -> None:
    """My custom action."""
    print(f"Executing with {param1} and {param2}")

# Register the action
register_action("my_action", my_custom_action)
```

### Using Custom Actions

Once registered, use your custom action in configurations:

```yaml
tasks:
  - name: custom_task
    schedule: every 30 minutes
    action: my_action
    parameters:
      param1: "test"
      param2: 42
```

## Action Best Practices

1. **Keep actions simple**: Each action should do one thing well
2. **Handle errors**: Actions should handle exceptions gracefully
3. **Use parameters**: Make actions configurable via parameters
4. **Add logging**: Log important events and errors
5. **Document actions**: Provide clear documentation for custom actions
6. **Test thoroughly**: Test actions with various parameters and edge cases

## Action Registry

View available actions:

```python
from yasched.actions import ACTIONS

# List all available actions
print(list(ACTIONS.keys()))
```

## Example: Database Backup Action

```python
from yasched.actions import register_action
import subprocess

def backup_database(database: str, output_dir: str) -> None:
    """Backup a database."""
    try:
        cmd = f"pg_dump {database} > {output_dir}/backup.sql"
        subprocess.run(cmd, shell=True, check=True)
        print(f"Database {database} backed up successfully")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")

# Register the action
register_action("backup_db", backup_database)
```

Use it in configuration:

```yaml
tasks:
  - name: nightly_backup
    description: Backup production database
    schedule: every day at 02:00
    action: backup_db
    parameters:
      database: production_db
      output_dir: /backups
```

## Next Steps

- Learn about [Scheduling](scheduling.md)
- Explore the [Web Interface](web-interface.md)
- See [API Reference](../api/actions.md)
