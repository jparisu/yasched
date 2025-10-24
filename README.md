# yasched

[![Tests](https://github.com/jparisu/yasched/actions/workflows/tests.yml/badge.svg)](https://github.com/jparisu/yasched/actions/workflows/tests.yml)
[![Ruff](https://github.com/jparisu/yasched/actions/workflows/ruff.yml/badge.svg)](https://github.com/jparisu/yasched/actions/workflows/ruff.yml)
[![MyPy](https://github.com/jparisu/yasched/actions/workflows/mypy.yml/badge.svg)](https://github.com/jparisu/yasched/actions/workflows/mypy.yml)
[![Codespell](https://github.com/jparisu/yasched/actions/workflows/codespell.yml/badge.svg)](https://github.com/jparisu/yasched/actions/workflows/codespell.yml)

**yasched** - Scheduler for agenda and tasks orchestration via YAML

A simple yet powerful task scheduler that allows you to define and manage scheduled tasks using YAML configuration files, with a beautiful Streamlit-based web interface.

## ✨ Features

- 📝 **YAML-based Configuration**: Define tasks in simple, readable YAML format
- ⏰ **Flexible Scheduling**: Support for various schedule patterns (seconds, minutes, hours, days, weeks)
- 🎯 **Action System**: Predefined actions (print, log) with extensibility for custom actions
- 🖥️ **Web Interface**: Beautiful Streamlit-based UI for managing tasks
- 📊 **Monitoring**: Track task execution history and statistics
- 🐍 **Python API**: Programmatic access to scheduler functionality
- 🔧 **Daemon Mode**: Run as a background service with management scripts

## 🚀 Quick Start

### Installation

```bash
pip install yasched
```

Or install from source:

```bash
git clone https://github.com/jparisu/yasched.git
cd yasched
pip install -e .
```

### Using the Web Interface

Start the Streamlit app:

```bash
streamlit run app/main.py
```

Or run as a daemon:

```bash
./scripts/start_daemon.sh   # Start daemon
./scripts/status_daemon.sh  # Check status
./scripts/stop_daemon.sh    # Stop daemon
```

### Using Python API

```python
from yasched import Scheduler, Task
from yasched.actions import get_action

# Create a scheduler
scheduler = Scheduler()

# Create and add a task
task = Task(
    name="hello_task",
    schedule_spec="every 10 seconds",
    action=get_action("print"),
    message="Hello from yasched!"
)

scheduler.add_task(task)

# Run the scheduler
scheduler.run()
```

### Using YAML Configuration

Create a `config.yaml` file:

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

Load and run:

```python
from yasched.utils import create_scheduler_from_config

scheduler = create_scheduler_from_config("config.yaml")
scheduler.run()
```

## 📖 Documentation

Full documentation is available at [https://jparisu.github.io/yasched](https://jparisu.github.io/yasched)

- [Installation Guide](docs/getting-started/installation.md)
- [Quick Start](docs/getting-started/quickstart.md)
- [Configuration](docs/getting-started/configuration.md)
- [User Guide](docs/user-guide/tasks.md)

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/jparisu/yasched.git
cd yasched
pip install -e ".[dev,docs]"
```

### Run Tests

```bash
pytest
```

### Run Linters

```bash
ruff check .        # Linting
ruff format .       # Formatting
mypy yasched app    # Type checking
codespell           # Spell checking
```

### Build Documentation

```bash
mkdocs serve
```

## 📁 Project Structure

```
yasched/
├── yasched/          # Backend package
│   ├── __init__.py
│   ├── scheduler.py  # Core scheduler logic
│   ├── config.py     # Configuration management
│   ├── actions.py    # Predefined actions
│   └── utils.py      # Utility functions
├── app/              # Frontend (Streamlit)
│   ├── __init__.py
│   └── main.py       # Main Streamlit app
├── tests/            # Test suite
├── docs/             # Documentation
├── scripts/          # Daemon management scripts
│   ├── start_daemon.sh
│   ├── stop_daemon.sh
│   ├── status_daemon.sh
│   └── restart_daemon.sh
├── .github/          # GitHub Actions workflows
│   └── workflows/
│       ├── ruff.yml
│       ├── mypy.yml
│       ├── codespell.yml
│       └── tests.yml
├── pyproject.toml    # Project configuration
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Schedule Patterns

yasched supports various schedule patterns:

- `every 30 seconds` - Run every 30 seconds
- `every 5 minutes` - Run every 5 minutes
- `every 1 hour` - Run every hour
- `every 2 hours` - Run every 2 hours
- `every day` - Run once per day
- `every day at 10:30` - Run daily at 10:30 AM
- `every monday` - Run every Monday
- `every friday at 17:00` - Run every Friday at 5:00 PM

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Scheduling powered by [schedule](https://github.com/dbader/schedule)
- Configuration via [PyYAML](https://pyyaml.org/)
