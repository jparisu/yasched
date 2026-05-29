# E — Time Schedule (Week Time-Grid)

## Overview
A week-level time-grid showing recurring and timed events as positioned blocks,
giving a realistic view of how a typical week is structured.

---

## E1 · Time-Grid Layout — REQUIREMENT

- **Columns:** Mon – Sun (7 columns).
- **Rows:** configurable hour window, default 07:00–22:00. Set in Settings.
  Events outside the window are clipped and shown with a truncation indicator.
- **All-day banner row** at the top of the grid (above the hourly area):
  events without a specific time (SingleDay, MultiDay, Monthly, Yearly schedules)
  appear as horizontal banners spanning their covered day columns.
- Hour labels on the left axis; 30-min or 1-hour grid lines (configurable in Settings).
- Today's column highlighted with a subtle background tint.

## E2 · Timed Event Blocks — REQUIREMENT

- Weekly recurring events (`WeeklySchedule` with `WeeklyAppointment` start/end times)
  are rendered as **positioned blocks** within the grid:
  - Vertical position = start time.
  - Block height = duration (end_time or start + duration).
  - Block color follows `effective_layout`; label shows event name.
- Hovering a block shows a tooltip (name, time range, location, topic).
- Clicking a block opens the event detail drawer (same as Calendar page).

## E3 · Conflict Visualization — REQUIREMENT

- Overlapping timed events (same day, overlapping time range) are rendered
  **side-by-side**, splitting the column width between them.
- Each conflicting block gets a **red border** to make the issue immediately visible.
- Hovering either block shows which other event it conflicts with.

## E4 · Task Deadline Markers — REQUIREMENT

- Reuses the **global deadline toggle** shared with the Calendar page (Group D).
- When ON: deadline markers appear in the all-day banner row on their due day column,
  using the same flag-style badge as the calendar.

## E5 · Navigation — REQUIREMENT

- Prev / Next week buttons.
- "Today" button jumps to the current week.
- Week label shows date range (e.g. "26 May – 1 Jun 2026").

## E6 · Filters — REQUIREMENT

- Local filter bar: topic (subtree), layout, tags.
- Filters hide non-matching event blocks; all-day banners follow the same filter.

---

## Settings knobs (stored in ~/.yasched/config.yaml)
- Grid start hour / end hour (default: 07:00 – 22:00).
- Grid line granularity: 30 min or 1 hour.
