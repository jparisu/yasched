"""Tests for utility functions."""

import tempfile
from pathlib import Path

import pytest

from yasched.config import save_config
from yasched.scheduler import Task
from yasched.utils import (
    create_scheduler_from_config,
    create_task_from_dict,
    task_to_dict,
    format_task_info,
)


def test_create_task_from_dict() -> None:
    """Test creating a task from a dictionary."""
    task_dict = {
        "name": "test_task",
        "description": "Test task",
        "schedule": "every 1 hour",
        "action": "print",
        "enabled": True,
        "parameters": {"message": "test"}
    }
    
    task = create_task_from_dict(task_dict)
    
    assert task.name == "test_task"
    assert task.description == "Test task"
    assert task.schedule_spec == "every 1 hour"
    assert task.enabled is True


def test_create_task_from_dict_minimal() -> None:
    """Test creating a task from a minimal dictionary."""
    task_dict = {
        "name": "test_task",
        "schedule": "every 1 hour",
        "action": "print",
    }
    
    task = create_task_from_dict(task_dict)
    
    assert task.name == "test_task"
    assert task.schedule_spec == "every 1 hour"
    assert task.description == ""
    assert task.enabled is True


def test_task_to_dict() -> None:
    """Test converting a task to a dictionary."""
    def dummy_action() -> None:
        pass
    
    task = Task(
        name="test_task",
        schedule_spec="every 1 hour",
        action=dummy_action,
        description="Test task",
        enabled=True
    )
    task.run_count = 5
    
    task_dict = task_to_dict(task)
    
    assert task_dict["name"] == "test_task"
    assert task_dict["schedule"] == "every 1 hour"
    assert task_dict["description"] == "Test task"
    assert task_dict["enabled"] is True
    assert task_dict["run_count"] == 5


def test_format_task_info() -> None:
    """Test formatting task information."""
    def dummy_action() -> None:
        pass
    
    task = Task(
        name="test_task",
        schedule_spec="every 1 hour",
        action=dummy_action,
        description="Test task",
        enabled=True
    )
    
    info = format_task_info(task)
    
    assert "test_task" in info
    assert "every 1 hour" in info
    assert "Test task" in info
    assert "Enabled" in info


def test_create_scheduler_from_config() -> None:
    """Test creating a scheduler from a configuration file."""
    config = {
        "tasks": [
            {
                "name": "task1",
                "schedule": "every 1 hour",
                "action": "print",
                "parameters": {"message": "test1"}
            },
            {
                "name": "task2",
                "schedule": "every 2 hours",
                "action": "log",
                "parameters": {"message": "test2", "level": "info"}
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        save_config(config, str(config_path))
        
        scheduler = create_scheduler_from_config(str(config_path))
        
        assert len(scheduler.tasks) == 2
        assert "task1" in scheduler.tasks
        assert "task2" in scheduler.tasks


def test_create_scheduler_from_invalid_config() -> None:
    """Test creating a scheduler from an invalid configuration."""
    config = {
        "tasks": [
            {
                "name": "task1",
                # Missing schedule and action
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        save_config(config, str(config_path))
        
        with pytest.raises(ValueError):
            create_scheduler_from_config(str(config_path))
