# yasched Setup Guide

This document provides a complete overview of the yasched repository setup.

## 🎯 Project Overview

yasched is a scheduler for agenda and tasks orchestration via YAML. It provides:
- A Python backend package for task scheduling
- A Streamlit web interface for task management
- Comprehensive documentation and examples
- Production-ready daemon mode

## 📁 Repository Structure

```
yasched/
├── yasched/              # Backend package
│   ├── __init__.py       # Package initialization
│   ├── scheduler.py      # Core scheduler and Task classes
│   ├── config.py         # Configuration management
│   ├── actions.py        # Predefined actions
│   └── utils.py          # Utility functions
│
├── app/                  # Frontend (Streamlit)
│   ├── __init__.py
│   └── main.py           # Main Streamlit application
│
├── tests/                # Test suite
│   ├── test_scheduler.py
│   ├── test_config.py
│   ├── test_actions.py
│   └── test_utils.py
│
├── docs/                 # Documentation (mkdocs)
│   ├── index.md
│   ├── getting-started/
│   ├── user-guide/
│   └── api/
│
├── examples/             # Usage examples
│   ├── sample_config.yaml
│   ├── simple_example.py
│   └── config_example.py
│
├── scripts/              # Daemon management
│   ├── start_daemon.sh
│   ├── stop_daemon.sh
│   ├── status_daemon.sh
│   └── restart_daemon.sh
│
├── .github/              # CI/CD workflows
│   └── workflows/
│       ├── ruff.yml      # Linting
│       ├── mypy.yml      # Type checking
│       ├── codespell.yml # Spell checking
│       ├── tests.yml     # Test suite
│       └── docs.yml      # Documentation
│
├── pyproject.toml        # Project configuration
├── README.md             # Project overview
├── CONTRIBUTING.md       # Contribution guidelines
└── LICENSE               # MIT License
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/jparisu/yasched.git
cd yasched

# Install dependencies
pip install -e ".[dev,docs]"
```

### 2. Run the Web Interface

```bash
# Start Streamlit
streamlit run app/main.py

# Or as a daemon
./scripts/start_daemon.sh
```

### 3. Try Examples

```bash
# Run simple example
python examples/simple_example.py

# Run with configuration
python examples/config_example.py examples/sample_config.yaml
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yasched --cov=app

# Run specific test file
pytest tests/test_scheduler.py -v
```

## 🔍 Code Quality

```bash
# Linting
ruff check .

# Formatting
ruff format .

# Type checking
mypy yasched app

# Spell checking
codespell
```

## 📚 Documentation

```bash
# Build documentation locally
mkdocs build

# Serve documentation with live reload
mkdocs serve

# Deploy to GitHub Pages (automatic via workflow)
mkdocs gh-deploy
```

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature
```

### 2. Make Changes

Edit files, add features, fix bugs, etc.

### 3. Run Quality Checks

```bash
# Format code
ruff format .

# Run linters
ruff check .
mypy yasched app
codespell

# Run tests
pytest
```

### 4. Commit and Push

```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

### 5. Create Pull Request

Open a PR on GitHub for review.

## 🔧 Configuration

### pyproject.toml

Main project configuration file containing:
- Package metadata
- Dependencies (core, dev, docs)
- Tool configurations (ruff, mypy, pytest, coverage, codespell)

### Key Dependencies

**Core:**
- streamlit: Web interface
- pyyaml: YAML parsing
- schedule: Task scheduling
- python-dateutil: Date handling

**Development:**
- pytest: Testing framework
- ruff: Linting and formatting
- mypy: Type checking
- codespell: Spell checking

**Documentation:**
- mkdocs: Documentation generator
- mkdocs-material: Material theme
- mkdocstrings: API documentation

## 📦 Package Structure

### yasched Package

- **scheduler.py**: Core scheduler logic
  - `Scheduler`: Main scheduler class
  - `Task`: Task representation

- **config.py**: Configuration management
  - `load_config()`: Load YAML config
  - `validate_config()`: Validate config
  - `save_config()`: Save config

- **actions.py**: Predefined actions
  - `print_action`: Print messages
  - `log_action`: Log messages
  - `custom_action`: Custom functions
  - `ACTIONS`: Action registry

- **utils.py**: Utility functions
  - `create_scheduler_from_config()`: Create from YAML
  - `create_task_from_dict()`: Create task from dict
  - `task_to_dict()`: Convert task to dict

### app Package

- **main.py**: Streamlit application
  - Dashboard page
  - Task management page
  - Configuration page
  - About page

## 🎨 Streamlit Interface

### Features

1. **Dashboard**
   - Task statistics
   - Quick task execution
   - Status monitoring

2. **Tasks Management**
   - View all tasks
   - Add new tasks
   - Edit existing tasks
   - Enable/disable tasks
   - Delete tasks

3. **Configuration**
   - Edit YAML directly
   - Import configurations
   - Export configurations
   - Validate configs

4. **About**
   - Feature overview
   - Documentation links
   - Quick start guide

## 🤖 CI/CD

### GitHub Actions Workflows

All workflows run on push and pull requests to main/develop branches:

1. **Ruff**: Code linting and formatting checks
2. **MyPy**: Type checking
3. **Codespell**: Spell checking
4. **Tests**: Full test suite with coverage
5. **Docs**: Build and deploy documentation

### Workflow Permissions

All workflows use minimal permissions for security:
- Read: `contents: read`
- Docs deploy also has: `contents: write`, `pages: write`

## 🔐 Security

- CodeQL scanning: 0 alerts
- Minimal workflow permissions
- No secrets in code
- Type-safe with mypy
- Input validation
- Error handling

## 📖 Documentation

### Structure

- **Getting Started**: Installation, quickstart, configuration
- **User Guide**: Tasks, actions, scheduling, web interface
- **API Reference**: Auto-generated from docstrings
- **Changelog**: Version history

### Building Locally

```bash
mkdocs serve
# Visit http://localhost:8000
```

## 🚀 Deployment

### As a Daemon

```bash
# Start
./scripts/start_daemon.sh

# Check status
./scripts/status_daemon.sh

# Stop
./scripts/stop_daemon.sh
```

### As a System Service

See `scripts/README.md` for systemd service setup.

### Docker (Future)

Docker support can be added in the future for containerized deployment.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick checklist:
- [ ] Code passes all linters
- [ ] Tests are added and passing
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description is complete

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Streamlit for the web framework
- schedule library for task scheduling
- PyYAML for configuration parsing
- All contributors and users

## 📞 Support

- Issues: https://github.com/jparisu/yasched/issues
- Documentation: https://jparisu.github.io/yasched
- Discussions: https://github.com/jparisu/yasched/discussions

## 🎉 Getting Help

If you need help:
1. Check the [documentation](https://jparisu.github.io/yasched)
2. Look at [examples](examples/)
3. Search [existing issues](https://github.com/jparisu/yasched/issues)
4. Open a new issue if needed

Happy scheduling! 🎯
