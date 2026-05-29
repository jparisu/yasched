# D — Calendar / Events

## Sub-views

| View | Tier |
|---|---|
| Monthly grid + mini next-month | REQUIREMENT |
| Weekly grid | REQUIREMENT |
| Daily view | REQUIREMENT |
| Yearly heatmap | FUTURE |

---

## D1 · Monthly Grid — REQUIREMENT

- Standard 7-column calendar grid (Mon–Sun header).
- Each day cell shows event badges: colored by `effective_layout` or topic color.
- **Mini next-month panel** on the right: smaller grid showing the following month
  with event density dots (no badges), for quick planning context.
- Today's cell highlighted with a distinct border/background.
- Day cell gets a **red tint** when one or more scheduling conflicts exist on that day.
- Navigate via Prev / Next month buttons and a month+year picker.
- Clicking a day cell navigates to the Daily view for that day.

## D2 · Weekly Grid — REQUIREMENT

- 7-column layout (Mon–Sun), events rendered as **horizontal band spanning their days**.
- Multi-day events stretch across all covered columns.
- Single-day events appear as a full-width badge in their column.
- Today's column highlighted.
- Conflict days: red tint on the column header.
- Navigate via Prev / Next week buttons and a "Today" jump button.

## D3 · Daily View — REQUIREMENT

- Full list of all events occurring on the selected day, with:
  name, location (if set), topic, time range (if weekly appointment), description excerpt.
- Task deadlines section (if deadline toggle is ON): lists tasks due on this day.
- Conflict section: lists conflicting event pairs for this day.
- Navigation: Prev / Next day arrows; click on any day in the monthly mini-calendar
  to jump directly.

## D4 · Yearly Heatmap — FUTURE

- 12-month compact grid, each day a small colored square.
- Color intensity = event count on that day.
- Clicking a day navigates to the Daily view.

---

## D5 · Task Deadline Markers — REQUIREMENT

- A **toggle** (persistent, stored in `~/.yasched/config.yaml`) controls whether
  deadline markers appear on all calendar views.
- When ON: deadline markers appear on the relevant day cell as a small distinct badge
  (different icon/style from event badges — e.g. flag icon, dashed border).
- When OFF: calendar shows only events, no deadline clutter.

## D6 · Event Detail Drawer — REQUIREMENT

- Clicking any event badge opens a **slide-in drawer from the right**
  (consistent with task detail in Group C).
- Drawer content: name, location, description, topic breadcrumb, effective layout,
  schedule breakdown (list of all schedule rules: single-day, weekly recurrence, etc.),
  blocking level, linked tasks (if any task references this event).
- Click outside or Escape to close.

## D7 · Conflict Markers — REQUIREMENT

- Day cells with scheduling conflicts (overlapping `blocking_level`) receive a
  **red tint / red border** on the cell background.
- Hovering a conflict-highlighted day shows a tooltip listing the conflicting event pairs.
- Detail visible in the Daily view's conflict section.

## D8 · Filters — REQUIREMENT

- Each calendar view has a local filter bar: topic (subtree), layout, tags.
- Filters hide non-matching events from the calendar; day cells with only hidden
  events show as empty.

---

## Shared UX notes
- All three views share the same filter bar and deadline toggle state.
- Switching between Monthly / Weekly / Daily preserves the currently selected date.
- Event badges use `effective_layout` color; if no layout, fall back to topic color
  from a consistent palette.
