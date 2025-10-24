"""Predefined actions that can be used in task configurations."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def print_action(message: str = "Hello from yasched!", **kwargs: Any) -> None:
    """
    Print a message to stdout.

    Args:
        message: Message to print.
        **kwargs: Additional parameters (ignored).
    """
    print(message)


def log_action(message: str = "", level: str = "info", **kwargs: Any) -> None:
    """
    Log a message using the logging module.

    Args:
        message: Message to log.
        level: Log level (debug, info, warning, error, critical).
        **kwargs: Additional parameters (ignored).
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)


def custom_action(function: str, **kwargs: Any) -> None:
    """
    Execute a custom Python function.

    Args:
        function: Fully qualified function name (e.g., 'module.function').
        **kwargs: Parameters to pass to the function.
    """
    # This is a placeholder for custom action execution
    # In a real implementation, you'd want to import and call the function
    logger.warning(f"Custom action '{function}' called with parameters: {kwargs}")


# Registry of available actions
ACTIONS: dict[str, Any] = {
    "print": print_action,
    "log": log_action,
    "custom": custom_action,
}


def get_action(action_name: str) -> Any:
    """
    Get an action by name.

    Args:
        action_name: Name of the action.

    Returns:
        The action callable.

    Raises:
        ValueError: If the action doesn't exist.
    """
    if action_name not in ACTIONS:
        raise ValueError(f"Unknown action: {action_name}")
    return ACTIONS[action_name]


def register_action(name: str, action: Any) -> None:
    """
    Register a custom action.

    Args:
        name: Name for the action.
        action: Callable to register.
    """
    ACTIONS[name] = action
    logger.info(f"Registered action: {name}")
