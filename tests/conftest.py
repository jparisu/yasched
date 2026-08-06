"""Pytest configuration and shared fixtures for the test suite."""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path so tests import the package without install.
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def example_path():
    """Path to the comprehensive example agenda."""
    return Path(__file__).parent.parent / "resources" / "example" / "agenda.yaml"


@pytest.fixture
def example_db(example_path):
    """The example loaded into a Database."""
    from yasched.backending.loading.ElementLoader import ElementLoader

    return ElementLoader.load(example_path)


@pytest.fixture
def example_resolver(example_db):
    """A Resolver over the example."""
    from yasched.backending.resolving.Resolver import Resolver

    return Resolver(example_db)
