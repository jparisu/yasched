"""
Pytest configuration file for yasched tests.
"""

import sys
from pathlib import Path

import pytest  # noqa: F401

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
