"""TASKS tab: Kanban board with one column per status, layout-aware card colors."""

from __future__ import annotations

import streamlit as st

from yasched.backending import DatabaseInterface, ResolvedTask
from yasched.coring._shared import TaskStatus
from yasched.frontending.streamlit.helpers import (
    STATUS_BG,
    STATUS_BORDER,
    STATUS_EMOJI,
    STATUS_HEADER_BG,
    layout_bg_css,
    layout_border_css,
    layout_icon,
)

_COLUMN_ORDER = [
    TaskStatus.TODO,
    TaskStatus.IN_PROGRESS,
    TaskStatus.BLOCKED,
    TaskStatus.DONE,
    TaskStatus.CANCELLED,
]


def render(iface: DatabaseInterface | None) -> None:
    if iface is None:
        st.info("👈 Load a database file from the sidebar.")
        return

    tasks_by_status: dict[TaskStatus, list[ResolvedTask]] = {s: [] for s in _COLUMN_ORDER}
    for task in iface.all_tasks():
        if task.status in tasks_by_status:
            tasks_by_status[task.status].append(task)

    html = _build_kanban_html(tasks_by_status)
    st.html(html)


def _build_kanban_html(tasks_by_status: dict[TaskStatus, list[ResolvedTask]]) -> str:
    columns_html = "".join(
        _column_html(status, tasks_by_status[status]) for status in _COLUMN_ORDER
    )
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f0f2f6; }}
  .board {{ display: flex; gap: 10px; padding: 10px; align-items: flex-start; }}
  .column {{ flex: 1; min-width: 0; border-radius: 10px; background: #e8eaed; overflow: hidden; }}
  .col-header {{
    padding: 10px 12px; font-weight: 700; font-size: 13px;
    color: white; display: flex; align-items: center; gap: 6px;
  }}
  .col-body {{ padding: 8px; min-height: 60px; }}
  .card {{
    border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.10); font-size: 13px;
  }}
  .card-title {{ font-weight: 600; margin-bottom: 4px; word-break: break-word; }}
  .card-meta {{ font-size: 11px; color: #555; margin-top: 2px; }}
  .card-deadline {{ font-size: 11px; color: #c62828; margin-top: 2px; }}
  .tag {{
    display: inline-block; background: rgba(0,0,0,0.08);
    border-radius: 3px; padding: 1px 5px; font-size: 10px; margin-right: 3px; margin-top: 3px;
  }}
  .empty {{ color: #aaa; font-size: 12px; text-align: center; padding: 16px 0; }}
</style>
</head>
<body>
  <div class="board">{columns_html}</div>
</body>
</html>"""


def _column_html(status: TaskStatus, tasks: list[ResolvedTask]) -> str:
    sv = status.value
    emoji = STATUS_EMOJI.get(sv, "")
    label = sv.replace("_", " ").upper()
    header_bg = STATUS_HEADER_BG.get(sv, "#555")
    count = len(tasks)

    if tasks:
        cards = "".join(_card_html(t) for t in tasks)
    else:
        cards = '<div class="empty">no tasks</div>'

    return f"""
<div class="column">
  <div class="col-header" style="background:{header_bg};">
    <span>{emoji}</span>
    <span>{label}</span>
    <span style="margin-left:auto;background:rgba(255,255,255,0.25);
                 border-radius:10px;padding:1px 7px;">{count}</span>
  </div>
  <div class="col-body">{cards}</div>
</div>"""


def _card_html(task: ResolvedTask) -> str:
    sv = task.status.value
    bg = layout_bg_css(task.effective_layout) or STATUS_BG.get(sv, "#f5f5f5")
    border = (
        layout_border_css(task.effective_layout)
        if task.effective_layout
        else f"1px solid {STATUS_BORDER.get(sv, '#ddd')}"
    )
    icon = layout_icon(task.effective_layout)

    priority_html = (
        f'<div class="card-meta">⭐ Priority: {task.priority}</div>'
        if task.priority is not None
        else ""
    )
    deadline_html = (
        f'<div class="card-deadline">📅 {task.effective_deadline}</div>'
        if task.effective_deadline
        else ""
    )
    topic_html = f'<div class="card-meta">📁 {task.topic.id}</div>'
    parent_html = f'<div class="card-meta">↳ {task.parent.id}</div>' if task.parent else ""
    tags_html = (
        "".join(f'<span class="tag">{t}</span>' for t in task.effective_tags[:4])
        if task.effective_tags
        else ""
    )
    blockers_html = (
        '<div class="card-meta" style="color:#c62828;">🔒 '
        + ", ".join(b.task_id for b in task.blocked_by)
        + "</div>"
        if task.blocked_by
        else ""
    )

    return f"""
<div class="card" style="background:{bg};border:{border};">
  <div class="card-title">{icon}{task.name}</div>
  {topic_html}
  {parent_html}
  {priority_html}
  {deadline_html}
  {blockers_html}
  <div>{tags_html}</div>
</div>"""
