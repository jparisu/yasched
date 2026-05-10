# My Yaml Scheduler

`My Yaml Scheduler` is version 2.0 of the original project, refreshed as a
modern Python package.

## ✨ Features

- 📝 **YAML-based Configuration**: Define tasks in simple, readable YAML format
- ⏰ **Flexible Scheduling**: Support for various schedule patterns (seconds, minutes, hours, days, weeks)
- 🎯 **Action System**: Predefined actions (print, log) with extensibility for custom actions
- 🖥️ **Web Interface**: Beautiful web-based UI for managing tasks
- 📊 **Monitoring**: Track task execution history and statistics
- 🐍 **Python API**: Programmatic access to scheduler functionality
- 🔧 **Daemon Mode**: Run as a background service with management scripts


## Installation

From Git:

```bash
python -m pip install "git+https://github.com/jparisu/yasched.git"
```

From a local checkout:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
pre-commit install
```

## Quick Start

```python
import yasched

print(yasched.__version__)
```

Current release: `2.0.0`


## Development

Useful commands:

```bash
make install
make install-current
make lint
make test
make docs
```

## License

Licensed under the Apache 2.0 License.
