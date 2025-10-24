"""
yasched - Scheduler for agenda and tasks orchestration via YAML.

This package provides a simple API for scheduling and managing tasks
defined in YAML configuration files.
"""

__version__ = "0.1.0"

from yasched.scheduler import Scheduler, Task
from yasched.config import load_config, validate_config

__all__ = ["Scheduler", "Task", "load_config", "validate_config"]
