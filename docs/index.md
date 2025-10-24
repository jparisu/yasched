# yasched

Welcome to **yasched** - a simple yet powerful task scheduler that allows you to define and manage scheduled tasks using YAML configuration files.

## Features

- 📝 **YAML-based Configuration**: Define tasks in simple, readable YAML format
- ⏰ **Flexible Scheduling**: Support for various schedule patterns (hourly, daily, weekly, etc.)
- 🎯 **Action System**: Predefined actions (print, log) with extensibility for custom actions
- 🖥️ **Web Interface**: Beautiful Streamlit-based UI for managing tasks
- 📊 **Monitoring**: Track task execution history and statistics
- 🐍 **Python API**: Programmatic access to scheduler functionality

## Quick Example

Create a simple task configuration in YAML:

```yaml
tasks:
  - name: daily_report
    description: Generate daily report
    schedule: every day at 09:00
    action: print
    enabled: true
    parameters:
      message: "Time to generate the daily report!"
```

Load and run it with Python:

```python
from yasched import create_scheduler_from_config

scheduler = create_scheduler_from_config("config.yaml")
scheduler.run()
```

Or use the web interface:

```bash
streamlit run app/main.py
```

## Why yasched?

- **Simple**: Easy to understand YAML configuration
- **Lightweight**: Minimal dependencies and resource usage
- **Flexible**: Support for various schedule patterns
- **Extensible**: Easy to add custom actions
- **Modern**: Web-based UI for easy management

## Getting Started

Check out the [Installation Guide](getting-started/installation.md) to get started with yasched.

## License

yasched is released under the MIT License. See the [LICENSE](https://github.com/jparisu/yasched/blob/main/LICENSE) file for details.
