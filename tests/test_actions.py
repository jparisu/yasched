"""Tests for action functionality."""

import logging

import pytest

from yasched.actions import (
    print_action,
    log_action,
    get_action,
    register_action,
    ACTIONS,
)


def test_print_action(capsys: pytest.CaptureFixture[str]) -> None:
    """Test print action."""
    print_action(message="Test message")
    
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_print_action_default(capsys: pytest.CaptureFixture[str]) -> None:
    """Test print action with default message."""
    print_action()
    
    captured = capsys.readouterr()
    assert "Hello from yasched!" in captured.out


def test_log_action(caplog: pytest.LogCaptureFixture) -> None:
    """Test log action."""
    with caplog.at_level(logging.INFO):
        log_action(message="Test log message", level="info")
    
    assert "Test log message" in caplog.text


def test_log_action_different_levels(caplog: pytest.LogCaptureFixture) -> None:
    """Test log action with different levels."""
    levels = ["debug", "info", "warning", "error", "critical"]
    
    for level in levels:
        caplog.clear()
        with caplog.at_level(logging.DEBUG):
            log_action(message=f"Test {level} message", level=level)
        
        assert f"Test {level} message" in caplog.text


def test_get_action() -> None:
    """Test getting an action by name."""
    action = get_action("print")
    
    assert action == print_action


def test_get_nonexistent_action() -> None:
    """Test getting a non-existent action."""
    with pytest.raises(ValueError, match="Unknown action"):
        get_action("nonexistent_action")


def test_register_action() -> None:
    """Test registering a custom action."""
    def custom_test_action() -> None:
        pass
    
    register_action("custom_test", custom_test_action)
    
    assert "custom_test" in ACTIONS
    assert ACTIONS["custom_test"] == custom_test_action
    
    # Clean up
    del ACTIONS["custom_test"]


def test_actions_registry() -> None:
    """Test that actions registry contains expected actions."""
    assert "print" in ACTIONS
    assert "log" in ACTIONS
    assert "custom" in ACTIONS
