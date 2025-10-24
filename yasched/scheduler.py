"""Core scheduler implementation for yasched."""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import schedule

logger = logging.getLogger(__name__)


class Task:
    """Represents a scheduled task."""
    
    def __init__(
        self,
        name: str,
        schedule_spec: str,
        action: Callable[..., None],
        description: Optional[str] = None,
        enabled: bool = True,
        **kwargs: Any
    ):
        """
        Initialize a Task.
        
        Args:
            name: Unique name for the task.
            schedule_spec: Schedule specification (e.g., "every 1 hour", "every day at 10:30").
            action: Callable to execute when task runs.
            description: Optional description of the task.
            enabled: Whether the task is enabled.
            **kwargs: Additional parameters to pass to the action.
        """
        self.name = name
        self.schedule_spec = schedule_spec
        self.action = action
        self.description = description
        self.enabled = enabled
        self.parameters = kwargs
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self._job: Optional[schedule.Job] = None
    
    def execute(self) -> None:
        """Execute the task action."""
        if not self.enabled:
            logger.debug(f"Task '{self.name}' is disabled, skipping execution")
            return
        
        try:
            logger.info(f"Executing task: {self.name}")
            self.action(**self.parameters)
            self.last_run = datetime.now()
            self.run_count += 1
            logger.info(f"Task '{self.name}' completed successfully")
        except Exception as e:
            logger.error(f"Error executing task '{self.name}': {e}")
    
    def __repr__(self) -> str:
        return (f"Task(name={self.name}, schedule={self.schedule_spec}, "
                f"enabled={self.enabled}, runs={self.run_count})")


class Scheduler:
    """Main scheduler class for managing tasks."""
    
    def __init__(self) -> None:
        """Initialize the Scheduler."""
        self.tasks: Dict[str, Task] = {}
        self._running = False
        schedule.clear()
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the scheduler.
        
        Args:
            task: Task to add.
            
        Raises:
            ValueError: If a task with the same name already exists.
        """
        if task.name in self.tasks:
            raise ValueError(f"Task with name '{task.name}' already exists")
        
        # Parse the schedule specification and create a schedule job
        self._schedule_task(task)
        self.tasks[task.name] = task
        logger.info(f"Added task: {task.name}")
    
    def _schedule_task(self, task: Task) -> None:
        """
        Schedule a task using the schedule library.
        
        Args:
            task: Task to schedule.
        """
        spec = task.schedule_spec.lower()
        
        # Parse simple schedule specifications
        # Format: "every <n> <unit>" or "every <unit> at <time>"
        parts = spec.split()
        
        if not parts or parts[0] != "every":
            raise ValueError(f"Invalid schedule specification: {task.schedule_spec}")
        
        if len(parts) >= 3 and parts[1].isdigit():
            # Format: "every <n> <unit>"
            interval = int(parts[1])
            unit = parts[2].rstrip('s')  # Remove trailing 's' if present
            
            if unit == "second":
                task._job = schedule.every(interval).seconds.do(task.execute)
            elif unit == "minute":
                task._job = schedule.every(interval).minutes.do(task.execute)
            elif unit == "hour":
                task._job = schedule.every(interval).hours.do(task.execute)
            elif unit == "day":
                task._job = schedule.every(interval).days.do(task.execute)
            elif unit == "week":
                task._job = schedule.every(interval).weeks.do(task.execute)
            else:
                raise ValueError(f"Unknown time unit: {unit}")
        elif len(parts) >= 2:
            # Format: "every <unit>" or "every <unit> at <time>"
            unit = parts[1].rstrip('s')
            
            if unit == "second":
                task._job = schedule.every().second.do(task.execute)
            elif unit == "minute":
                task._job = schedule.every().minute.do(task.execute)
            elif unit == "hour":
                task._job = schedule.every().hour.do(task.execute)
            elif unit == "day":
                if len(parts) >= 4 and parts[2] == "at":
                    time_spec = parts[3]
                    task._job = schedule.every().day.at(time_spec).do(task.execute)
                else:
                    task._job = schedule.every().day.do(task.execute)
            elif unit in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                job = getattr(schedule.every(), unit)
                if len(parts) >= 4 and parts[2] == "at":
                    time_spec = parts[3]
                    task._job = job.at(time_spec).do(task.execute)
                else:
                    task._job = job.do(task.execute)
            else:
                raise ValueError(f"Unknown schedule unit: {unit}")
        else:
            raise ValueError(f"Invalid schedule specification: {task.schedule_spec}")
    
    def remove_task(self, task_name: str) -> None:
        """
        Remove a task from the scheduler.
        
        Args:
            task_name: Name of the task to remove.
            
        Raises:
            KeyError: If the task doesn't exist.
        """
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' not found")
        
        task = self.tasks[task_name]
        if task._job is not None:
            schedule.cancel_job(task._job)
        
        del self.tasks[task_name]
        logger.info(f"Removed task: {task_name}")
    
    def enable_task(self, task_name: str) -> None:
        """Enable a task."""
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' not found")
        self.tasks[task_name].enabled = True
        logger.info(f"Enabled task: {task_name}")
    
    def disable_task(self, task_name: str) -> None:
        """Disable a task."""
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' not found")
        self.tasks[task_name].enabled = False
        logger.info(f"Disabled task: {task_name}")
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_task(self, task_name: str) -> Task:
        """Get a specific task by name."""
        if task_name not in self.tasks:
            raise KeyError(f"Task '{task_name}' not found")
        return self.tasks[task_name]
    
    def run_pending(self) -> None:
        """Run all pending tasks."""
        schedule.run_pending()
    
    def run(self, interval: float = 1.0) -> None:
        """
        Run the scheduler continuously.
        
        Args:
            interval: Sleep interval between checks in seconds.
        """
        self._running = True
        logger.info("Scheduler started")
        
        try:
            while self._running:
                self.run_pending()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        logger.info("Scheduler stopped")
    
    def clear(self) -> None:
        """Clear all tasks."""
        schedule.clear()
        self.tasks.clear()
        logger.info("All tasks cleared")
