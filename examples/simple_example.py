#!/usr/bin/env python3
"""
Simple example demonstrating yasched usage.

This script creates a scheduler with a few tasks and runs them.
"""

from yasched import Scheduler, Task
from yasched.actions import get_action


def main() -> None:
    """Run a simple example with yasched."""
    # Create a scheduler
    scheduler = Scheduler()

    # Create tasks
    task1 = Task(
        name="hello_task",
        schedule_spec="every 10 seconds",
        action=get_action("print"),
        description="Print a hello message",
        message="Hello from yasched!",
    )

    task2 = Task(
        name="counter_task",
        schedule_spec="every 15 seconds",
        action=get_action("log"),
        description="Log a counter message",
        message="Counter task executed",
        level="info",
    )

    # Add tasks to scheduler
    scheduler.add_task(task1)
    scheduler.add_task(task2)

    print("Scheduler started with 2 tasks:")
    print(f"  - {task1.name}: {task1.schedule_spec}")
    print(f"  - {task2.name}: {task2.schedule_spec}")
    print("\nPress Ctrl+C to stop...\n")

    # Run the scheduler
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        print("\nTask execution summary:")
        for task in scheduler.get_tasks():
            print(f"  - {task.name}: {task.run_count} executions")


if __name__ == "__main__":
    main()
