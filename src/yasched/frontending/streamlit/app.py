"""Main Streamlit application for yasched."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from yasched.backending import (
    ConsistencyError,
    DatabaseInterface,
    DatabaseLoader,
    DatabaseManager,
    DatabaseParseError,
)
from yasched.frontending.streamlit import tab_events, tab_main, tab_tasks


def _load_database(path: str) -> None:
    """Load, validate, and resolve a database; update session state."""
    try:
        db = DatabaseLoader.load(path)
    except (DatabaseParseError, FileNotFoundError, Exception) as e:
        st.session_state["db_errors"] = [str(e)]
        st.session_state["iface"] = None
        return

    errors = DatabaseManager.validate(db)
    st.session_state["db_errors"] = errors
    st.session_state["db_path"] = path

    try:
        rdb = DatabaseManager.resolve(db)
        st.session_state["iface"] = DatabaseInterface(rdb)
    except ConsistencyError as e:
        st.session_state["iface"] = None
        if not errors:
            st.session_state["db_errors"] = [str(e)]


def _render_file_browser() -> None:
    """Inline directory browser that sets db_path on .yaml file selection."""
    if "browser_dir" not in st.session_state:
        st.session_state["browser_dir"] = str(Path.cwd())

    current = Path(st.session_state["browser_dir"])

    # Current path display
    st.caption(f"📂 `{current}`")

    # Parent directory button
    if current.parent != current:
        if st.button("⬆ ..", use_container_width=True, key="browser_up"):
            st.session_state["browser_dir"] = str(current.parent)
            st.rerun()

    # List contents: dirs first, then yaml files
    try:
        entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        st.warning("Permission denied.")
        return

    dirs = [e for e in entries if e.is_dir() and not e.name.startswith(".")]
    yaml_files = [e for e in entries if e.is_file() and e.suffix in (".yaml", ".yml")]

    for d in dirs:
        if st.button(f"📁 {d.name}", use_container_width=True, key=f"dir_{d}"):
            st.session_state["browser_dir"] = str(d)
            st.rerun()

    if yaml_files:
        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
        for f in yaml_files:
            if st.button(f"📄 {f.name}", use_container_width=True, key=f"file_{f}"):
                st.session_state["db_path_input"] = str(f)
                st.rerun()
    elif not dirs:
        st.caption("_No YAML files here._")


def _render_sidebar() -> None:
    with st.sidebar:
        st.title("📅 yasched")
        st.markdown("---")

        st.subheader("Database")

        # Path text input (also updated by the file browser)
        db_path = st.text_input(
            "File path",
            value=st.session_state.get("db_path_input", st.session_state.get("db_path", "")),
            placeholder="path/to/main.yaml",
            label_visibility="collapsed",
            key="db_path_text",
        )

        col_load, col_browse = st.columns(2)
        with col_load:
            if st.button("Load", type="primary", use_container_width=True):
                if db_path.strip():
                    _load_database(db_path.strip())
                    st.rerun()
                else:
                    st.warning("Enter a file path first.")
        with col_browse:
            browsing = st.session_state.get("browser_open", False)
            label = "✖ Close" if browsing else "🗂 Browse"
            if st.button(label, use_container_width=True):
                st.session_state["browser_open"] = not browsing
                # Seed browser to the directory of the current path if set
                current_path = db_path.strip()
                if current_path and Path(current_path).exists():
                    seed = str(Path(current_path).parent)
                else:
                    seed = str(Path.cwd())
                if not browsing:
                    st.session_state["browser_dir"] = seed
                st.rerun()

        if st.session_state.get("browser_open"):
            with st.container(border=True):
                _render_file_browser()

        # Status indicator
        iface: DatabaseInterface | None = st.session_state.get("iface")
        errors: list = st.session_state.get("db_errors", [])

        if iface is not None:
            if errors:
                st.warning(f"⚠️ Loaded with {len(errors)} error(s)")
            else:
                st.success("✅ Loaded")
            st.caption(f"Tasks: {len(iface.all_tasks())}  |  Events: {len(iface.all_events())}")
        elif st.session_state.get("db_path"):
            st.error("❌ Failed to load")

        st.markdown("---")
        st.caption("yasched v2.0 — proof of concept")


def main() -> None:
    st.set_page_config(
        page_title="yasched",
        page_icon="📅",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _render_sidebar()

    iface: DatabaseInterface | None = st.session_state.get("iface")
    errors: list = st.session_state.get("db_errors", [])

    tab1, tab2, tab3 = st.tabs(["🏠 MAIN", "📋 TASKS", "📅 EVENTS"])

    with tab1:
        tab_main.render(iface, errors)
    with tab2:
        tab_tasks.render(iface)
    with tab3:
        tab_events.render(iface)
