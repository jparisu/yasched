# Tasks

Tasks are the core building blocks of yasched. Each task represents a scheduled action that runs at specified intervals.

## Task Components

A task consists of:

1. **Name**: Unique identifier
2. **Schedule**: When to run
3. **Action**: What to do
4. **Parameters**: Action-specific configuration
5. **State**: Enabled/disabled status

## Creating Tasks

### Via Web Interface

1. Go to the "Tasks" page
2. Click "Add Task" tab
3. Fill in the task details
4. Click "Add Task" button

### Via Python API

```python
from yasched import Scheduler, Task
from yasched.actions import get_action

scheduler = Scheduler()

task = Task(
    name="my_task",
    schedule_spec="every 1 hour",
    action=get_action("print"),
    description="My example task",
    enabled=True,
    message="Task executed!"
)

scheduler.add_task(task)
```

### Via YAML Configuration

```yaml
tasks:
  - name: my_task
    description: My example task
    schedule: every 1 hour
    action: print
    enabled: true
    parameters:
      message: Task executed!
```

## Managing Tasks

### Enable/Disable Tasks

```python
# Disable a task
scheduler.disable_task("my_task")

# Enable a task
scheduler.enable_task("my_task")
```

### Remove Tasks

```python
scheduler.remove_task("my_task")
```

### Get Task Information

```python
# Get a specific task
task = scheduler.get_task("my_task")

# Get all tasks
tasks = scheduler.get_tasks()

# Task properties
print(task.name)
print(task.schedule_spec)
print(task.enabled)
print(task.run_count)
print(task.last_run)
```

## Task Execution

### Manual Execution

```python
# Execute a task manually
task.execute()
```

### Automatic Execution

Tasks are automatically executed by the scheduler based on their schedule:

```python
# Run the scheduler
scheduler.run()
```

## Task State

Tasks maintain their execution state:

- **run_count**: Number of times the task has been executed
- **last_run**: Timestamp of the last execution
- **enabled**: Whether the task is active

## Example: Complex Task

```yaml
tasks:
  - name: data_pipeline
    description: Run data processing pipeline
    schedule: every day at 03:00
    action: custom
    enabled: true
    parameters:
      function: pipeline.process_data
      source: s3://bucket/data
      destination: database://prod
      batch_size: 1000
      retry_count: 3
```

## Best Practices

1. **Use descriptive names**: Make task names self-explanatory
2. **Add descriptions**: Document what each task does
3. **Monitor execution**: Check run counts and last run times
4. **Handle errors**: Tasks should handle errors gracefully
5. **Test thoroughly**: Test tasks before enabling in production
6. **Keep tasks simple**: Each task should do one thing well

## Next Steps

- Learn about [Actions](actions.md)
- Explore [Scheduling](scheduling.md)
- Use the [Web Interface](web-interface.md)
