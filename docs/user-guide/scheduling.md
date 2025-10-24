# Scheduling

yasched provides flexible scheduling patterns for defining when tasks should run.

## Schedule Syntax

The basic syntax is: `every [interval] [unit] [at time]`

### Time Units

Supported time units:
- `second` / `seconds`
- `minute` / `minutes`
- `hour` / `hours`
- `day` / `days`
- `week` / `weeks`
- Day names: `monday`, `tuesday`, `wednesday`, `thursday`, `friday`, `saturday`, `sunday`

## Simple Intervals

### Seconds
```yaml
schedule: every 30 seconds
schedule: every 1 second
```

### Minutes
```yaml
schedule: every 5 minutes
schedule: every 1 minute
schedule: every 15 minutes
```

### Hours
```yaml
schedule: every 1 hour
schedule: every 2 hours
schedule: every 6 hours
```

### Days
```yaml
schedule: every day
schedule: every 2 days
schedule: every 1 day
```

### Weeks
```yaml
schedule: every week
schedule: every 2 weeks
```

## Time-based Scheduling

### Daily at Specific Time
```yaml
schedule: every day at 09:00
schedule: every day at 14:30
schedule: every day at 23:59
```

### Weekly on Specific Days
```yaml
schedule: every monday
schedule: every friday at 17:00
schedule: every wednesday at 12:00
```

## Examples

### Common Patterns

**Every 30 seconds:**
```yaml
tasks:
  - name: frequent_check
    schedule: every 30 seconds
    action: print
    parameters:
      message: "Quick check"
```

**Every 15 minutes:**
```yaml
tasks:
  - name: status_update
    schedule: every 15 minutes
    action: log
    parameters:
      message: "Status update"
      level: info
```

**Daily morning report:**
```yaml
tasks:
  - name: morning_report
    schedule: every day at 09:00
    action: print
    parameters:
      message: "Good morning! Here's your daily report."
```

**Weekly backup:**
```yaml
tasks:
  - name: weekly_backup
    schedule: every sunday at 03:00
    action: custom
    parameters:
      function: backup.run_full_backup
```

**Business hours check:**
```yaml
tasks:
  - name: business_hours_check
    schedule: every monday at 09:00
    action: log
    parameters:
      message: "Starting business week"
      level: info
```

## Schedule Testing

Test your schedules before deploying:

```python
from yasched import Scheduler, Task
from yasched.actions import get_action

scheduler = Scheduler()

# Create test task
task = Task(
    name="test_task",
    schedule_spec="every 5 seconds",
    action=get_action("print"),
    message="Test execution"
)

scheduler.add_task(task)

# Run for a limited time to test
import time
scheduler._running = True
for _ in range(3):
    scheduler.run_pending()
    time.sleep(5)
scheduler.stop()
```

## Best Practices

1. **Choose appropriate intervals**: Don't schedule tasks too frequently
2. **Avoid peak hours**: Schedule resource-intensive tasks during off-peak hours
3. **Use specific times**: For daily tasks, specify exact times
4. **Consider time zones**: Be aware of server time zones
5. **Test schedules**: Test with shorter intervals first
6. **Monitor execution**: Check task run counts and last run times

## Schedule Validation

yasched validates schedule specifications when tasks are added:

```python
from yasched import Scheduler, Task
from yasched.actions import get_action

scheduler = Scheduler()

try:
    task = Task(
        name="invalid_task",
        schedule_spec="invalid schedule spec",
        action=get_action("print")
    )
    scheduler.add_task(task)
except ValueError as e:
    print(f"Invalid schedule: {e}")
```

## Advanced Scheduling

For more complex scheduling needs, you can:

1. **Multiple tasks**: Create multiple tasks with different schedules
2. **Conditional execution**: Use task parameters to control behavior
3. **Dynamic scheduling**: Modify task schedules programmatically

### Example: Multiple Schedules

```yaml
tasks:
  # Frequent during business hours
  - name: business_hours_check
    schedule: every 15 minutes
    action: log
    enabled: true
    parameters:
      message: "Business hours check"
  
  # Less frequent at night
  - name: night_check
    schedule: every 1 hour
    action: log
    enabled: true
    parameters:
      message: "Night check"
  
  # Once daily
  - name: daily_summary
    schedule: every day at 23:00
    action: print
    parameters:
      message: "Daily summary"
```

## Troubleshooting

### Task not running
- Check if task is enabled
- Verify schedule syntax
- Check scheduler is running
- Review logs for errors

### Task running too frequently
- Verify interval specification
- Check for duplicate tasks
- Review schedule syntax

### Task missing executions
- Ensure scheduler runs continuously
- Check system resources
- Review execution times

## Next Steps

- Learn about [Tasks](tasks.md)
- Explore [Actions](actions.md)
- Use the [Web Interface](web-interface.md)
