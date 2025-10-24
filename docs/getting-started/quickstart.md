# Quick Start

This guide will help you get started with yasched in just a few minutes.

## Using the Web Interface

The easiest way to get started is using the Streamlit web interface:

```bash
streamlit run app/main.py
```

This will open a browser window with the yasched dashboard where you can:

1. View and manage tasks
2. Create new tasks
3. Monitor task execution
4. Edit YAML configurations

## Using Python API

### Creating a Simple Task

```python
from yasched import Scheduler, Task
from yasched.actions import get_action

# Create a scheduler
scheduler = Scheduler()

# Create a task
task = Task(
    name="hello_task",
    schedule_spec="every 10 seconds",
    action=get_action("print"),
    message="Hello from yasched!"
)

# Add task to scheduler
scheduler.add_task(task)

# Run the scheduler
scheduler.run()
```

### Loading from Configuration File

Create a file named `config.yaml`:

```yaml
tasks:
  - name: morning_greeting
    description: Print a morning greeting
    schedule: every day at 08:00
    action: print
    enabled: true
    parameters:
      message: "Good morning! Time to start the day."
  
  - name: hourly_check
    description: Hourly status check
    schedule: every 1 hour
    action: log
    enabled: true
    parameters:
      message: "Hourly check complete"
      level: info
```

Then load and run it:

```python
from yasched.utils import create_scheduler_from_config

scheduler = create_scheduler_from_config("config.yaml")
scheduler.run()
```

## Common Schedule Patterns

Here are some common schedule patterns you can use:

- `every 30 seconds` - Run every 30 seconds
- `every 5 minutes` - Run every 5 minutes
- `every 1 hour` - Run every hour
- `every 2 hours` - Run every 2 hours
- `every day` - Run once per day
- `every day at 10:30` - Run daily at 10:30 AM
- `every monday` - Run every Monday
- `every friday at 17:00` - Run every Friday at 5:00 PM

## Next Steps

- Learn more about [Configuration](configuration.md)
- Explore [Tasks](../user-guide/tasks.md) in detail
- Discover available [Actions](../user-guide/actions.md)
