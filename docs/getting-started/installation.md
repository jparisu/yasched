# Installation

## Prerequisites

- Python 3.9 or higher
- pip package manager

## Installing from PyPI

Once published, you'll be able to install yasched using pip:

```bash
pip install yasched
```

## Installing from Source

To install the latest development version:

```bash
git clone https://github.com/jparisu/yasched.git
cd yasched
pip install -e .
```

## Development Installation

If you want to contribute to yasched, install with development dependencies:

```bash
git clone https://github.com/jparisu/yasched.git
cd yasched
pip install -e ".[dev,docs]"
```

This will install:

- Core dependencies (streamlit, pyyaml, schedule, etc.)
- Development tools (pytest, ruff, mypy, etc.)
- Documentation tools (mkdocs, mkdocs-material, etc.)

## Verifying Installation

To verify that yasched is installed correctly:

```python
import yasched
print(yasched.__version__)
```

Or run the web interface:

```bash
streamlit run app/main.py
```

## Next Steps

- Continue to the [Quick Start Guide](quickstart.md)
