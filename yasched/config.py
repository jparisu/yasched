"""Configuration management for yasched."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
        
    Returns:
        Dictionary containing the parsed configuration.
        
    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        yaml.YAMLError: If the YAML is invalid.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config or {}


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate.
        
    Returns:
        True if the configuration is valid.
        
    Raises:
        ValueError: If the configuration is invalid.
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")
    
    tasks = config.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("'tasks' must be a list")
    
    for idx, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValueError(f"Task {idx} must be a dictionary")
        
        if "name" not in task:
            raise ValueError(f"Task {idx} is missing required field: 'name'")
        
        if "schedule" not in task:
            raise ValueError(f"Task {idx} is missing required field: 'schedule'")
        
        if "action" not in task:
            raise ValueError(f"Task {idx} is missing required field: 'action'")
    
    return True


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a YAML file.
    
    Args:
        config: Configuration dictionary to save.
        config_path: Path where to save the configuration file.
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_default_config() -> Dict[str, Any]:
    """
    Get a default configuration example.
    
    Returns:
        Dictionary with a default configuration.
    """
    return {
        "tasks": [
            {
                "name": "example_task",
                "description": "An example task",
                "schedule": "every 1 hour",
                "action": "print",
                "parameters": {
                    "message": "Hello from yasched!"
                }
            }
        ]
    }
