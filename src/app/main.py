"""Main Streamlit application for yasched."""

import logging

import streamlit as st
import yaml

from yasched import Scheduler, Task
from yasched.actions import ACTIONS, get_action
from yasched.config import get_default_config, validate_config
from yasched.utils import create_task_from_dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="yasched - YAML Task Scheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
    st.session_state.config = get_default_config()
    st.session_state.selected_task = None


def render_sidebar() -> None:
    """Render the sidebar navigation."""
    st.sidebar.title("📅 yasched")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation", ["Dashboard", "Tasks", "Configuration", "About"], label_visibility="collapsed"
    )

    st.session_state.current_page = page

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Actions")

    if st.sidebar.button("🔄 Reload Config"):
        reload_configuration()

    if st.sidebar.button("🗑️ Clear All Tasks"):
        st.session_state.scheduler.clear()
        st.session_state.config = {"tasks": []}
        st.rerun()


def render_dashboard() -> None:
    """Render the dashboard page."""
    st.title("📊 Dashboard")

    # Statistics
    tasks = st.session_state.scheduler.get_tasks()
    enabled_tasks = [t for t in tasks if t.enabled]
    disabled_tasks = [t for t in tasks if not t.enabled]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Tasks", len(tasks))

    with col2:
        st.metric("Enabled Tasks", len(enabled_tasks))

    with col3:
        st.metric("Disabled Tasks", len(disabled_tasks))

    with col4:
        total_runs = sum(t.run_count for t in tasks)
        st.metric("Total Runs", total_runs)

    st.markdown("---")

    # Tasks overview
    st.subheader("📋 Tasks Overview")

    if not tasks:
        st.info("No tasks configured. Go to the Tasks page to add some!")
    else:
        for task in tasks:
            with st.expander(f"{'✅' if task.enabled else '❌'} {task.name}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Schedule:** {task.schedule_spec}")
                    if task.description:
                        st.write(f"**Description:** {task.description}")
                    st.write(f"**Runs:** {task.run_count}")
                    if task.last_run:
                        st.write(f"**Last Run:** {task.last_run.strftime('%Y-%m-%d %H:%M:%S')}")

                with col2:
                    if st.button("Run Now", key=f"run_{task.name}"):
                        try:
                            task.execute()
                            st.success(f"Task '{task.name}' executed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")


def render_tasks() -> None:
    """Render the tasks management page."""
    st.title("📝 Task Management")

    tab1, tab2, tab3 = st.tabs(["View Tasks", "Add Task", "Edit Task"])

    with tab1:
        render_tasks_list()

    with tab2:
        render_add_task()

    with tab3:
        render_edit_task()


def render_tasks_list() -> None:
    """Render the list of tasks."""
    tasks = st.session_state.scheduler.get_tasks()

    if not tasks:
        st.info("No tasks available.")
        return

    for task in tasks:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            st.write(f"**{task.name}** - {task.schedule_spec}")
            if task.description:
                st.caption(task.description)

        with col2:
            status = "🟢 Enabled" if task.enabled else "🔴 Disabled"
            st.write(status)

        with col3:
            if task.enabled:
                if st.button("Disable", key=f"disable_{task.name}"):
                    st.session_state.scheduler.disable_task(task.name)
                    st.rerun()
            else:
                if st.button("Enable", key=f"enable_{task.name}"):
                    st.session_state.scheduler.enable_task(task.name)
                    st.rerun()

        with col4:
            if st.button("Delete", key=f"delete_{task.name}"):
                st.session_state.scheduler.remove_task(task.name)
                # Also remove from config
                config_tasks = st.session_state.config.get("tasks", [])
                st.session_state.config["tasks"] = [
                    t for t in config_tasks if t.get("name") != task.name
                ]
                st.rerun()

        st.markdown("---")


def render_add_task() -> None:
    """Render the add task form."""
    st.subheader("➕ Add New Task")

    with st.form("add_task_form"):
        name = st.text_input("Task Name", placeholder="my_task")
        description = st.text_area("Description (optional)", placeholder="What does this task do?")

        col1, col2 = st.columns(2)

        with col1:
            schedule = st.text_input(
                "Schedule",
                placeholder="every 1 hour",
                help="Examples: 'every 1 hour', 'every day at 10:30', 'every monday'",
            )

        with col2:
            action = st.selectbox("Action", list(ACTIONS.keys()))

        # Action parameters
        st.markdown("**Action Parameters**")

        if action == "print":
            message = st.text_input("Message", value="Hello from yasched!")
            parameters = {"message": message}
        elif action == "log":
            message = st.text_input("Message")
            level = st.selectbox("Log Level", ["debug", "info", "warning", "error", "critical"])
            parameters = {"message": message, "level": level}
        else:
            parameters = {}

        enabled = st.checkbox("Enabled", value=True)

        submitted = st.form_submit_button("Add Task")

        if submitted:
            if not name:
                st.error("Task name is required!")
            elif not schedule:
                st.error("Schedule is required!")
            else:
                try:
                    # Create task
                    action_func = get_action(action)
                    task = Task(
                        name=name,
                        schedule_spec=schedule,
                        action=action_func,
                        description=description,
                        enabled=enabled,
                        **parameters,
                    )

                    # Add to scheduler
                    st.session_state.scheduler.add_task(task)

                    # Add to config
                    task_config = {
                        "name": name,
                        "description": description,
                        "schedule": schedule,
                        "action": action,
                        "enabled": enabled,
                        "parameters": parameters,
                    }

                    if "tasks" not in st.session_state.config:
                        st.session_state.config["tasks"] = []
                    st.session_state.config["tasks"].append(task_config)

                    st.success(f"Task '{name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {e}")


def render_edit_task() -> None:
    """Render the edit task interface."""
    st.subheader("✏️ Edit Task")

    tasks = st.session_state.scheduler.get_tasks()

    if not tasks:
        st.info("No tasks available to edit.")
        return

    task_names = [t.name for t in tasks]
    selected_name = st.selectbox("Select Task", task_names)

    if selected_name:
        task = st.session_state.scheduler.get_task(selected_name)

        with st.form("edit_task_form"):
            st.text_input("Task Name", value=task.name, disabled=True)
            description = st.text_area("Description", value=task.description or "")
            schedule = st.text_input("Schedule", value=task.schedule_spec)
            enabled = st.checkbox("Enabled", value=task.enabled)

            submitted = st.form_submit_button("Update Task")

            if submitted:
                try:
                    # Update task properties
                    task.description = description
                    task.enabled = enabled

                    # Update in config
                    for task_config in st.session_state.config.get("tasks", []):
                        if task_config.get("name") == task.name:
                            task_config["description"] = description
                            task_config["schedule"] = schedule
                            task_config["enabled"] = enabled
                            break

                    st.success(f"Task '{task.name}' updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating task: {e}")


def render_configuration() -> None:
    """Render the configuration page."""
    st.title("⚙️ Configuration")

    tab1, tab2, tab3 = st.tabs(["View/Edit", "Import", "Export"])

    with tab1:
        render_config_editor()

    with tab2:
        render_config_import()

    with tab3:
        render_config_export()


def render_config_editor() -> None:
    """Render the configuration editor."""
    st.subheader("📝 Edit Configuration")

    config_yaml = yaml.dump(st.session_state.config, default_flow_style=False, sort_keys=False)

    edited_config = st.text_area(
        "Configuration (YAML)",
        value=config_yaml,
        height=400,
        help="Edit the configuration in YAML format",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save & Apply"):
            try:
                new_config = yaml.safe_load(edited_config)
                validate_config(new_config)

                # Clear current scheduler and reload
                st.session_state.scheduler.clear()
                st.session_state.config = new_config

                # Recreate tasks
                for task_config in new_config.get("tasks", []):
                    task = create_task_from_dict(task_config)
                    st.session_state.scheduler.add_task(task)

                st.success("Configuration applied successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error applying configuration: {e}")

    with col2:
        if st.button("🔄 Reset to Default"):
            st.session_state.config = get_default_config()
            st.rerun()


def render_config_import() -> None:
    """Render the configuration import interface."""
    st.subheader("📥 Import Configuration")

    uploaded_file = st.file_uploader("Choose a YAML file", type=["yaml", "yml"])

    if uploaded_file is not None:
        try:
            config = yaml.safe_load(uploaded_file)
            validate_config(config)

            st.success("Configuration file is valid!")

            # Show preview
            st.subheader("Preview")
            st.code(yaml.dump(config, default_flow_style=False, sort_keys=False), language="yaml")

            if st.button("Apply Configuration"):
                st.session_state.scheduler.clear()
                st.session_state.config = config

                for task_config in config.get("tasks", []):
                    task = create_task_from_dict(task_config)
                    st.session_state.scheduler.add_task(task)

                st.success("Configuration imported and applied successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Error importing configuration: {e}")


def render_config_export() -> None:
    """Render the configuration export interface."""
    st.subheader("📤 Export Configuration")

    config_yaml = yaml.dump(st.session_state.config, default_flow_style=False, sort_keys=False)

    st.code(config_yaml, language="yaml")

    st.download_button(
        label="💾 Download Configuration",
        data=config_yaml,
        file_name="yasched_config.yaml",
        mime="application/x-yaml",
    )


def render_about() -> None:
    """Render the about page."""
    st.title("ℹ️ About yasched")

    st.markdown("""
    ## yasched - YAML Task Scheduler

    **yasched** is a simple yet powerful task scheduler that allows you to define and manage
    scheduled tasks using YAML configuration files.

    ### Features

    - 📝 **YAML-based Configuration**: Define tasks in simple, readable YAML format
    - ⏰ **Flexible Scheduling**: Support for various schedule patterns (hourly, daily, weekly, etc.)
    - 🎯 **Action System**: Predefined actions (print, log) with extensibility for custom actions
    - 🖥️ **Web Interface**: Beautiful Streamlit-based UI for managing tasks
    - 📊 **Monitoring**: Track task execution history and statistics

    ### Quick Start

    1. **Add a Task**: Go to the Tasks page and create a new task
    2. **Configure Schedule**: Set when your task should run
    3. **Choose Action**: Select what the task should do
    4. **Enable & Run**: Enable the task and watch it execute on schedule

    ### Configuration Format

    ```yaml
    tasks:
      - name: example_task
        description: An example task
        schedule: every 1 hour
        action: print
        enabled: true
        parameters:
          message: Hello from yasched!
    ```

    ### Available Actions

    - **print**: Print a message to stdout
    - **log**: Log a message with specified level
    - **custom**: Execute custom Python functions

    ### Links

    - 📦 [GitHub Repository](https://github.com/jparisu/yasched)
    - 📚 [Documentation](https://jparisu.github.io/yasched)
    - 🐛 [Report Issues](https://github.com/jparisu/yasched/issues)

    ---

    Version 0.1.0 | Made with ❤️ using Streamlit
    """)


def reload_configuration() -> None:
    """Reload configuration from file."""
    # This is a placeholder for file-based configuration reload
    st.info("Configuration reloaded from session state.")


def main() -> None:
    """Main application entry point."""
    render_sidebar()

    page = st.session_state.get("current_page", "Dashboard")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Tasks":
        render_tasks()
    elif page == "Configuration":
        render_configuration()
    elif page == "About":
        render_about()


if __name__ == "__main__":
    main()
