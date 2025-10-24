"""
yasched - Scheduler for agenda and tasks orchestration via YAML.

This package provides a simple API for scheduling and managing tasks
defined in YAML configuration files.
"""

__version__ = "0.1.0"

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["utils"]
