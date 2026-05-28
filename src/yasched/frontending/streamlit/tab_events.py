"""EVENTS tab: monthly calendar with event badges and hover tooltips."""

from __future__ import annotations

import calendar
import datetime
import html as html_lib

import streamlit as st

from yasched.backending import DatabaseInterface, ResolvedEvent
from yasched.frontending.streamlit.helpers import TOPIC_PALETTE, layout_primary_color


def render(iface: DatabaseInterface | None) -> None:
    if iface is None:
        st.info("👈 Load a database file from the sidebar.")
        return

    # Month/year navigation stored in session state
    if "cal_year" not in st.session_state or "cal_month" not in st.session_state:
        today = datetime.date.today()
        st.session_state["cal_year"] = today.year
        st.session_state["cal_month"] = today.month

    year: int = st.session_state["cal_year"]
    month: int = st.session_state["cal_month"]

    # Build topic→color map once
    topics = iface.all_topics()
    topic_color_map = {t.id: TOPIC_PALETTE[i % len(TOPIC_PALETTE)] for i, t in enumerate(topics)}

    # Navigation controls
    col_prev, col_title, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("◀ Prev", use_container_width=True):
            if month == 1:
                st.session_state["cal_month"] = 12
                st.session_state["cal_year"] = year - 1
            else:
                st.session_state["cal_month"] = month - 1
            st.rerun()
    with col_title:
        st.markdown(
            f"<h3 style='text-align:center;margin:0;'>{calendar.month_name[month]} {year}</h3>",
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Next ▶", use_container_width=True):
            if month == 12:
                st.session_state["cal_month"] = 1
                st.session_state["cal_year"] = year + 1
            else:
                st.session_state["cal_month"] = month + 1
            st.rerun()

    # Build day→events mapping
    _, num_days = calendar.monthrange(year, month)
    month_start = datetime.date(year, month, 1)
    month_end = datetime.date(year, month, num_days)
    events_in_month = iface.get_events_in_range(month_start, month_end)

    day_events: dict[int, list[ResolvedEvent]] = {d: [] for d in range(1, num_days + 1)}
    for day in range(1, num_days + 1):
        d = datetime.date(year, month, day)
        day_events[day] = iface.get_events_in_range(d, d)

    # Render calendar HTML
    cal_html = _build_calendar_html(year, month, num_days, day_events, topic_color_map)
    st.html(cal_html)

    # Legend
    st.divider()
    _render_legend(events_in_month, topic_color_map)


def _build_calendar_html(
    year: int,
    month: int,
    num_days: int,
    day_events: dict[int, list[ResolvedEvent]],
    topic_color_map: dict[str, str],
) -> str:
    today = datetime.date.today()
    first_weekday = calendar.monthrange(year, month)[0]  # 0=Mon … 6=Sun

    # Empty cells before day 1
    cells = "".join('<div class="day-cell empty"></div>' for _ in range(first_weekday))

    for day in range(1, num_days + 1):
        d = datetime.date(year, month, day)
        is_today = d == today
        events = day_events.get(day, [])
        cells += _day_cell_html(day, events, is_today, topic_color_map)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #fff; }}
  .calendar {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    padding: 4px;
  }}
  .day-header {{
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    color: #555;
    padding: 6px 0;
    background: #f0f2f6;
    border-radius: 4px;
  }}
  .day-header.weekend {{ color: #d32f2f; }}
  .day-cell {{
    min-height: 90px;
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 5px;
    overflow: hidden;
    vertical-align: top;
  }}
  .day-cell.empty {{ background: transparent; border: none; }}
  .day-cell.today {{ border: 2px solid #1a73e8; background: #e8f0fe; }}
  .day-number {{
    font-size: 12px;
    font-weight: bold;
    color: #333;
    margin-bottom: 4px;
  }}
  .day-cell.today .day-number {{ color: #1a73e8; }}
  .event-badge {{
    position: relative;
    display: block;
    color: white;
    border-radius: 3px;
    padding: 2px 5px;
    font-size: 10px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: default;
  }}
  .tooltip {{
    display: none;
    position: absolute;
    background: #333;
    color: #fff;
    border-radius: 5px;
    padding: 7px 10px;
    font-size: 11px;
    line-height: 1.5;
    z-index: 9999;
    top: calc(100% + 4px);
    left: 0;
    min-width: 170px;
    max-width: 240px;
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    pointer-events: none;
  }}
  .event-badge:hover .tooltip {{ display: block; }}
</style>
</head>
<body>
<div class="calendar">
  <div class="day-header">Mon</div>
  <div class="day-header">Tue</div>
  <div class="day-header">Wed</div>
  <div class="day-header">Thu</div>
  <div class="day-header">Fri</div>
  <div class="day-header weekend">Sat</div>
  <div class="day-header weekend">Sun</div>
  {cells}
</div>
</body>
</html>"""


def _day_cell_html(
    day: int,
    events: list[ResolvedEvent],
    is_today: bool,
    topic_color_map: dict[str, str],
) -> str:
    today_cls = " today" if is_today else ""
    badges = "".join(_event_badge_html(e, topic_color_map) for e in events[:4])
    overflow = (
        f'<div style="font-size:10px;color:#888;">+{len(events) - 4} more</div>'
        if len(events) > 4
        else ""
    )
    return (
        f'<div class="day-cell{today_cls}">'
        f'<div class="day-number">{day}</div>'
        f"{badges}{overflow}"
        f"</div>"
    )


def _event_badge_html(event: ResolvedEvent, topic_color_map: dict[str, str]) -> str:
    color = layout_primary_color(
        event.effective_layout,
        fallback=topic_color_map.get(event.topic.id, "#4285f4"),
    )
    name = html_lib.escape(event.name)

    # Build tooltip text
    lines = [f"📌 {event.name}"]
    if event.location:
        lines.append(f"📍 {event.location}")
    if event.description:
        lines.append(f"📝 {event.description}")
    lines.append(f"📁 {event.topic.id}")
    tooltip = html_lib.escape("\n".join(lines))

    return (
        f'<div class="event-badge" style="background:{color};">'
        f"{name}"
        f'<span class="tooltip">{tooltip}</span>'
        f"</div>"
    )


def _render_legend(events: list[ResolvedEvent], topic_color_map: dict[str, str]) -> None:
    if not events:
        return
    st.caption("**Events this month:**")
    seen_ids: set[str] = set()
    cols = st.columns(min(len(events), 4))
    col_idx = 0
    for e in events:
        if e.id in seen_ids:
            continue
        seen_ids.add(e.id)
        color = layout_primary_color(
            e.effective_layout,
            fallback=topic_color_map.get(e.topic.id, "#4285f4"),
        )
        with cols[col_idx % len(cols)]:
            st.markdown(
                f'<span style="display:inline-block;width:10px;height:10px;'
                f'background:{color};border-radius:2px;margin-right:5px;"></span>'
                f"**{e.name}** _{e.topic.id}_",
                unsafe_allow_html=True,
            )
        col_idx += 1
