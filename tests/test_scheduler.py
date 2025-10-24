"""Tests for scheduler functionality."""

import pytest

from yasched.scheduler import Scheduler, Task


def test_task_creation() -> None:
    """Test creating a task."""
    executed = []

    def test_action(value: str) -> None:
        executed.append(value)

    task = Task(
        name="test_task",
        schedule_spec="every 1 second",
        action=test_action,
        description="Test task",
        value="test_value",
    )

    assert task.name == "test_task"
    assert task.schedule_spec == "every 1 second"
    assert task.description == "Test task"
    assert task.enabled is True
    assert task.run_count == 0
    assert task.last_run is None


def test_task_execute() -> None:
    """Test executing a task."""
    executed = []

    def test_action(value: str) -> None:
        executed.append(value)

    task = Task(
        name="test_task", schedule_spec="every 1 hour", action=test_action, value="test_value"
    )

    task.execute()

    assert executed == ["test_value"]
    assert task.run_count == 1
    assert task.last_run is not None


def test_task_execute_disabled() -> None:
    """Test executing a disabled task."""
    executed = []

    def test_action() -> None:
        executed.append("executed")

    task = Task(name="test_task", schedule_spec="every 1 hour", action=test_action, enabled=False)

    task.execute()

    assert executed == []
    assert task.run_count == 0


def test_scheduler_creation() -> None:
    """Test creating a scheduler."""
    scheduler = Scheduler()

    assert len(scheduler.tasks) == 0
    assert scheduler._running is False


def test_scheduler_add_task() -> None:
    """Test adding a task to scheduler."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task = Task(name="test_task", schedule_spec="every 1 hour", action=test_action)

    scheduler.add_task(task)

    assert len(scheduler.tasks) == 1
    assert "test_task" in scheduler.tasks


def test_scheduler_add_duplicate_task() -> None:
    """Test adding a duplicate task to scheduler."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task1 = Task(name="test_task", schedule_spec="every 1 hour", action=test_action)
    task2 = Task(name="test_task", schedule_spec="every 2 hours", action=test_action)

    scheduler.add_task(task1)

    with pytest.raises(ValueError, match="already exists"):
        scheduler.add_task(task2)


def test_scheduler_remove_task() -> None:
    """Test removing a task from scheduler."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task = Task(name="test_task", schedule_spec="every 1 hour", action=test_action)
    scheduler.add_task(task)

    assert len(scheduler.tasks) == 1

    scheduler.remove_task("test_task")

    assert len(scheduler.tasks) == 0


def test_scheduler_remove_nonexistent_task() -> None:
    """Test removing a non-existent task."""
    scheduler = Scheduler()

    with pytest.raises(KeyError, match="not found"):
        scheduler.remove_task("nonexistent")


def test_scheduler_enable_disable_task() -> None:
    """Test enabling and disabling tasks."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task = Task(name="test_task", schedule_spec="every 1 hour", action=test_action)
    scheduler.add_task(task)

    assert scheduler.tasks["test_task"].enabled is True

    scheduler.disable_task("test_task")
    assert scheduler.tasks["test_task"].enabled is False

    scheduler.enable_task("test_task")
    assert scheduler.tasks["test_task"].enabled is True


def test_scheduler_get_tasks() -> None:
    """Test getting all tasks."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task1 = Task(name="task1", schedule_spec="every 1 hour", action=test_action)
    task2 = Task(name="task2", schedule_spec="every 2 hours", action=test_action)

    scheduler.add_task(task1)
    scheduler.add_task(task2)

    tasks = scheduler.get_tasks()

    assert len(tasks) == 2
    assert any(t.name == "task1" for t in tasks)
    assert any(t.name == "task2" for t in tasks)


def test_scheduler_get_task() -> None:
    """Test getting a specific task."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task = Task(name="test_task", schedule_spec="every 1 hour", action=test_action)
    scheduler.add_task(task)

    retrieved_task = scheduler.get_task("test_task")

    assert retrieved_task.name == "test_task"


def test_scheduler_get_nonexistent_task() -> None:
    """Test getting a non-existent task."""
    scheduler = Scheduler()

    with pytest.raises(KeyError, match="not found"):
        scheduler.get_task("nonexistent")


def test_scheduler_clear() -> None:
    """Test clearing all tasks."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task1 = Task(name="task1", schedule_spec="every 1 hour", action=test_action)
    task2 = Task(name="task2", schedule_spec="every 2 hours", action=test_action)

    scheduler.add_task(task1)
    scheduler.add_task(task2)

    assert len(scheduler.tasks) == 2

    scheduler.clear()

    assert len(scheduler.tasks) == 0


def test_schedule_spec_parsing() -> None:
    """Test parsing different schedule specifications."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    # Test various schedule formats
    specs = [
        "every 1 second",
        "every 5 minutes",
        "every 2 hours",
        "every 1 day",
        "every day at 10:30",
        "every monday",
        "every friday at 15:00",
    ]

    for i, spec in enumerate(specs):
        task = Task(name=f"task_{i}", schedule_spec=spec, action=test_action)
        scheduler.add_task(task)

    assert len(scheduler.tasks) == len(specs)


def test_invalid_schedule_spec() -> None:
    """Test invalid schedule specification."""
    scheduler = Scheduler()

    def test_action() -> None:
        pass

    task = Task(name="test_task", schedule_spec="invalid spec", action=test_action)

    with pytest.raises(ValueError, match="Invalid schedule specification"):
        scheduler.add_task(task)
