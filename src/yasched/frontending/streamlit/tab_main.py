"""MAIN tab: overview, validation results, statistics, and topic tree."""

from __future__ import annotations

import streamlit as st

from yasched.backending import DatabaseInterface
from yasched.backending.managing.ConsistencyError import ConsistencyError
from yasched.frontending.streamlit.helpers import STATUS_EMOJI


def render(iface: DatabaseInterface | None, errors: list[ConsistencyError | str]) -> None:
    if iface is None:
        st.info("👈 Load a database file from the sidebar to get started.")
        _render_help()
        return

    _render_validation(errors)
    st.divider()
    _render_metrics(iface)
    st.divider()

    col_left, col_right = st.columns([3, 2])
    with col_left:
        _render_status_breakdown(iface)
    with col_right:
        _render_topic_tree(iface)


def _render_help() -> None:
    with st.expander("ℹ️ How to use yasched"):
        st.markdown("""
1. Enter the path to your YAML database file in the **sidebar**.
2. Click **Load** — the app validates the file and loads all entities.
3. Navigate the **TASKS** tab to see a Kanban board of all tasks.
4. Navigate the **EVENTS** tab to browse a monthly calendar view.
        """)


def _render_validation(errors: list[ConsistencyError | str]) -> None:
    if not errors:
        st.success("✅ Database validated — no consistency errors found.")
        return
    st.error(f"❌ {len(errors)} validation error(s) found")
    with st.expander("Show errors"):
        for e in errors:
            if isinstance(e, ConsistencyError):
                st.markdown(f"- **{type(e).__name__}**: {e}")
            else:
                st.markdown(f"- {e}")


def _render_metrics(iface: DatabaseInterface) -> None:
    st.subheader("📊 Database Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Layouts", len(iface.all_layouts()))
    c2.metric("Topics", len(iface.all_topics()))
    c3.metric("Events", len(iface.all_events()))
    c4.metric("Tasks", len(iface.all_tasks()))


def _render_status_breakdown(iface: DatabaseInterface) -> None:
    st.subheader("Task Status Breakdown")
    summary = iface.task_status_summary()
    total = sum(summary.values()) or 1
    for status, count in summary.items():
        emoji = STATUS_EMOJI.get(status.value, "")
        label = status.value.replace("_", " ").title()
        col_a, col_b = st.columns([3, 1])
        col_a.markdown(f"**{emoji} {label}**")
        col_b.markdown(f"`{count}`")
        st.progress(count / total)


def _render_topic_tree(iface: DatabaseInterface) -> None:
    st.subheader("Topic Tree")
    task_counts = iface.task_count_by_topic()

    def _node(topic, indent: int = 0) -> None:
        prefix = " " * (indent * 4) + ("└─ " if indent > 0 else "")
        count = task_counts.get(topic.id, 0)
        count_badge = f" `{count} tasks`" if count else ""
        st.markdown(
            f"<div style='font-family:monospace;font-size:13px;padding:1px 0'>"
            f"{prefix}<b>{topic.id}</b>: {topic.name}{count_badge}</div>",
            unsafe_allow_html=True,
        )
        for child in topic.children:
            _node(child, indent + 1)

    for root in iface.get_root_topics():
        _node(root)
