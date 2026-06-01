"""Pytest config for frontending (web) tests."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(_ROOT / "apps" / "web"))
sys.path.insert(0, str(_ROOT / "src"))
