"""Utility functions for yasched."""

import logging
from typing import Any

from yasched.actions import get_action
from yasched.config import load_config, validate_config
from yasched.scheduler import Scheduler, Task

logger = logging.getLogger(__name__)


def create_scheduler_from_config(config_path: str) -> Scheduler:
    """
    Create a scheduler from a YAML configuration file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        Configured Scheduler instance.
    """
    config = load_config(config_path)
    validate_config(config)

    scheduler = Scheduler()

    for task_config in config.get("tasks", []):
        task = create_task_from_dict(task_config)
        scheduler.add_task(task)

    return scheduler


def create_task_from_dict(task_dict: dict[str, Any]) -> Task:
    """
    Create a Task from a dictionary configuration.

    Args:
        task_dict: Dictionary containing task configuration.

    Returns:
        Task instance.
    """
    name = task_dict["name"]
    schedule_spec = task_dict["schedule"]
    action_name = task_dict["action"]
    description = task_dict.get("description", "")
    enabled = task_dict.get("enabled", True)
    parameters = task_dict.get("parameters", {})

    action = get_action(action_name)

    return Task(
        name=name,
        schedule_spec=schedule_spec,
        action=action,
        description=description,
        enabled=enabled,
        **parameters,
    )


def task_to_dict(task: Task) -> dict[str, Any]:
    """
    Convert a Task to a dictionary representation.

    Args:
        task: Task to convert.

    Returns:
        Dictionary representation of the task.
    """
    return {
        "name": task.name,
        "schedule": task.schedule_spec,
        "description": task.description or "",
        "enabled": task.enabled,
        "run_count": task.run_count,
        "last_run": task.last_run.isoformat() if task.last_run else None,
    }


def format_task_info(task: Task) -> str:
    """
    Format task information as a readable string.

    Args:
        task: Task to format.

    Returns:
        Formatted string.
    """
    lines = [
        f"Task: {task.name}",
        f"  Schedule: {task.schedule_spec}",
        f"  Status: {'Enabled' if task.enabled else 'Disabled'}",
        f"  Run Count: {task.run_count}",
    ]

    if task.description:
        lines.insert(1, f"  Description: {task.description}")

    if task.last_run:
        lines.append(f"  Last Run: {task.last_run.strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(lines)


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
