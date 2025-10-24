# Contributing to yasched

Thank you for your interest in contributing to yasched! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/yasched.git
   cd yasched
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev,docs]"
   ```

## Development Workflow

### 1. Create a Branch

Create a new branch for your feature or bugfix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

### 2. Make Changes

- Write clean, readable code
- Follow the existing code style
- Add docstrings to functions and classes
- Update documentation as needed

### 3. Run Tests

Before committing, ensure all tests pass:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yasched --cov=app
```

### 4. Run Linters

Ensure code quality with our linting tools:

```bash
# Run ruff linting
ruff check .

# Run ruff formatting
ruff format .

# Run mypy type checking
mypy yasched app

# Run codespell
codespell
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "Add feature: description of your change"
```

Follow these commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests when applicable

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Update user documentation in `docs/` when adding features

Example docstring:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    More detailed description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: Description of when this is raised.
    """
    pass
```

### Testing

- Write tests for new features
- Maintain or improve test coverage
- Use descriptive test names
- Test edge cases and error conditions

Example test:

```python
def test_feature_name() -> None:
    """Test that feature works correctly."""
    # Arrange
    input_data = "test"

    # Act
    result = my_function(input_data)

    # Assert
    assert result == expected_value
```

## Project Structure

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
│   ├── test_scheduler.py
│   ├── test_config.py
│   └── ...
├── docs/             # Documentation
│   ├── index.md
│   └── ...
├── scripts/          # Daemon management scripts
│   └── ...
├── .github/          # GitHub Actions workflows
│   └── workflows/
└── pyproject.toml    # Project configuration
```

## Types of Contributions

### Bug Reports

When filing a bug report, include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)

### Feature Requests

When suggesting a feature:
- Describe the feature and its benefits
- Provide use cases
- Suggest implementation approaches if possible

### Code Contributions

We welcome contributions for:
- Bug fixes
- New features
- Documentation improvements
- Test improvements
- Performance optimizations

### Documentation

- Fix typos and clarify existing documentation
- Add examples and tutorials
- Improve API documentation
- Translate documentation (future)

## Review Process

1. All pull requests require review before merging
2. Address reviewer feedback promptly
3. Keep pull requests focused and manageable
4. Ensure CI checks pass

## Questions?

- Open an issue for questions
- Check existing issues and documentation
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md (future Contributors section)
- Release notes
- Documentation credits

Thank you for contributing to yasched! 🎉
