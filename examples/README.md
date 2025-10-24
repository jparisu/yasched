# Examples

This directory contains example configurations and usage patterns for yasched.

## Files

- `sample_config.yaml`: A comprehensive example configuration showing various task types and schedules

## Usage

### Using the Sample Configuration

```bash
# Load and run the sample configuration
python -c "
from yasched.utils import create_scheduler_from_config
scheduler = create_scheduler_from_config('examples/sample_config.yaml')
scheduler.run()
"
```

### Using with Streamlit

```bash
# Start the web interface
streamlit run app/main.py

# Then use the Configuration -> Import tab to upload sample_config.yaml
```

### Creating Your Own Configuration

1. Copy `sample_config.yaml` to a new file
2. Modify the tasks to suit your needs
3. Test with a short interval first (e.g., "every 10 seconds")
4. Update to production schedule once validated

## Configuration Examples

### Every N Seconds/Minutes/Hours
```yaml
tasks:
  - name: frequent_task
    schedule: every 30 seconds
    action: print
    parameters:
      message: "This runs every 30 seconds"
```

### Daily at Specific Time
```yaml
tasks:
  - name: daily_task
    schedule: every day at 09:00
    action: log
    parameters:
      message: "This runs every day at 9 AM"
      level: info
```

### Weekly on Specific Day
```yaml
tasks:
  - name: weekly_task
    schedule: every friday at 17:00
    action: print
    parameters:
      message: "This runs every Friday at 5 PM"
```

### Multiple Tasks with Different Schedules
```yaml
tasks:
  - name: task1
    schedule: every 1 minute
    action: print
    parameters:
      message: "Task 1"
  
  - name: task2
    schedule: every 5 minutes
    action: log
    parameters:
      message: "Task 2"
      level: info
  
  - name: task3
    schedule: every day at 12:00
    action: print
    parameters:
      message: "Task 3"
```

## Tips

1. Start with disabled tasks (`enabled: false`) and enable them after testing
2. Use shorter intervals for testing, then update to production schedules
3. Add clear descriptions to help others understand what each task does
4. Group related tasks together in the configuration file
5. Use version control for your configuration files
