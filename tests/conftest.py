"""
Pytest configuration for generated-project tests.
"""

import sys
from pathlib import Path

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"value": 42, "data": [1, 2, 3, 4, 5]}


@pytest.fixture
def sample_value():
    """Provide a sample value for tests."""
    return 10


@pytest.fixture
def teacher_path():
    """Path to the comprehensive teacher-example agenda."""
    return Path(__file__).parent.parent / "resources" / "teacher_example" / "teacher_main.yaml"


@pytest.fixture
def teacher_db(teacher_path):
    """The teacher example loaded into a Database."""
    from yasched.backending.loading.DatabaseLoader import DatabaseLoader

    return DatabaseLoader.load(teacher_path)


@pytest.fixture
def teacher_resolver(teacher_db):
    """A Resolver over the teacher example."""
    from yasched.backending.resolving.Resolver import Resolver

    return Resolver(teacher_db)
