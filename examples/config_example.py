#!/usr/bin/env python3
"""
Example demonstrating yasched with YAML configuration.

This script loads tasks from a YAML configuration file and runs them.
"""

import sys
from pathlib import Path

from yasched.utils import create_scheduler_from_config


def main() -> None:
    """Run example using YAML configuration."""
    # Get the configuration file path
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Use the sample configuration by default
        examples_dir = Path(__file__).parent
        config_path = str(examples_dir / "sample_config.yaml")

    print(f"Loading configuration from: {config_path}")

    try:
        # Create scheduler from configuration
        scheduler = create_scheduler_from_config(config_path)

        # Show loaded tasks
        tasks = scheduler.get_tasks()
        print(f"\nLoaded {len(tasks)} task(s):")
        for task in tasks:
            status = "✓" if task.enabled else "✗"
            print(f"  {status} {task.name}: {task.schedule_spec}")
            if task.description:
                print(f"      {task.description}")

        enabled_tasks = [t for t in tasks if t.enabled]
        print(f"\n{len(enabled_tasks)} task(s) are enabled and will run.")
        print("\nPress Ctrl+C to stop...\n")

        # Run the scheduler
        scheduler.run()

    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid configuration: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        print("\nTask execution summary:")
        for task in scheduler.get_tasks():
            if task.run_count > 0:
                print(f"  - {task.name}: {task.run_count} executions")


if __name__ == "__main__":
    main()
