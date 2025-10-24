"""Tests for configuration management."""

import tempfile
from pathlib import Path

import pytest
import yaml

from yasched.config import (
    load_config,
    validate_config,
    save_config,
    get_default_config,
)


def test_get_default_config() -> None:
    """Test getting default configuration."""
    config = get_default_config()
    
    assert isinstance(config, dict)
    assert "tasks" in config
    assert isinstance(config["tasks"], list)
    assert len(config["tasks"]) > 0


def test_validate_config_valid() -> None:
    """Test validating a valid configuration."""
    config = {
        "tasks": [
            {
                "name": "test_task",
                "schedule": "every 1 hour",
                "action": "print",
            }
        ]
    }
    
    assert validate_config(config) is True


def test_validate_config_invalid_type() -> None:
    """Test validating an invalid configuration type."""
    with pytest.raises(ValueError, match="Configuration must be a dictionary"):
        validate_config("not a dict")  # type: ignore


def test_validate_config_tasks_not_list() -> None:
    """Test validating configuration with tasks not being a list."""
    config = {"tasks": "not a list"}
    
    with pytest.raises(ValueError, match="'tasks' must be a list"):
        validate_config(config)


def test_validate_config_task_missing_name() -> None:
    """Test validating configuration with task missing name."""
    config = {
        "tasks": [
            {
                "schedule": "every 1 hour",
                "action": "print",
            }
        ]
    }
    
    with pytest.raises(ValueError, match="missing required field: 'name'"):
        validate_config(config)


def test_validate_config_task_missing_schedule() -> None:
    """Test validating configuration with task missing schedule."""
    config = {
        "tasks": [
            {
                "name": "test_task",
                "action": "print",
            }
        ]
    }
    
    with pytest.raises(ValueError, match="missing required field: 'schedule'"):
        validate_config(config)


def test_validate_config_task_missing_action() -> None:
    """Test validating configuration with task missing action."""
    config = {
        "tasks": [
            {
                "name": "test_task",
                "schedule": "every 1 hour",
            }
        ]
    }
    
    with pytest.raises(ValueError, match="missing required field: 'action'"):
        validate_config(config)


def test_save_and_load_config() -> None:
    """Test saving and loading configuration."""
    config = {
        "tasks": [
            {
                "name": "test_task",
                "schedule": "every 1 hour",
                "action": "print",
                "parameters": {"message": "test"},
            }
        ]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        
        # Save config
        save_config(config, str(config_path))
        
        # Load config
        loaded_config = load_config(str(config_path))
        
        assert loaded_config == config


def test_load_config_file_not_found() -> None:
    """Test loading configuration from non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_load_config_invalid_yaml() -> None:
    """Test loading invalid YAML configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        f.flush()
        
        with pytest.raises(yaml.YAMLError):
            load_config(f.name)
        
        Path(f.name).unlink()


def test_save_config_creates_directory() -> None:
    """Test that save_config creates parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "subdir" / "config.yaml"
        config = {"tasks": []}
        
        save_config(config, str(config_path))
        
        assert config_path.exists()
        assert config_path.parent.exists()
