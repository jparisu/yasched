# B — Dashboard / Home

## Features

### B1 · Overview metrics — REQUIREMENT
- Top row of metric cards: Layouts · Topics · Events · Tasks (total counts).
- Updates immediately on database load/reload.

### B2 · Task status breakdown chart — REQUIREMENT
- Shows distribution across all 5 statuses: TODO / IN_PROGRESS / BLOCKED / DONE / CANCELLED.
- Two display modes, user-switchable via a toggle:
  - **Donut / pie chart** — proportional, visually compact.
  - **Horizontal bar chart** — shows exact count + percentage per status.
- Both modes use layout-aware / status colors consistent with the Tasks page.

### B3 · Overdue tasks alert — REQUIREMENT
- Lists all tasks past their effective deadline that are not DONE or CANCELLED.
- Shows task name, topic, deadline date, and days overdue.
- See B-Alerts for dismiss/mute behavior.

### B4 · Upcoming deadlines panel — REQUIREMENT
- Lists tasks whose effective deadline falls within the next N days (N configurable in Settings).
- Sorted by deadline ascending.
- Shows task name, topic, deadline date, days remaining.
- See B-Alerts for dismiss/mute behavior.

### B5 · Scheduling conflicts alert — REQUIREMENT
- Detects events with overlapping `blocking_level` on the same day.
- Shows: event A vs event B, the conflicting date, and blocking levels involved.
- See B-Alerts for dismiss/mute behavior.

### B6 · Stale event links alert — REQUIREMENT
- Flags tasks that are still open (not DONE / CANCELLED) but all their linked events
  are entirely in the past.
- Shows task name, topic, and the stale linked event(s).
- See B-Alerts for dismiss/mute behavior.

### B7 · Stale blocks alert — REQUIREMENT
- Flags tasks still marked BLOCKED when every task in their `blocked_by` list is
  already DONE or CANCELLED.
- Shows task name and the resolved blockers.
- See B-Alerts for dismiss/mute behavior.

### B8 · Global search bar — REQUIREMENT
- Persistent in the top bar, accessible from every page.
- Searches across tasks, events, and topics simultaneously.
- Results shown in a dropdown overlay, grouped by entity type with icons.
- Clicking a result navigates to the relevant page and highlights/selects the entity.
- Each page also has its own local filter/sort controls (independent of the global bar).

---

## B-Alerts — Alert Management System

All alerts (B3–B7) share a common management layer:

- Each **alert type** can be individually **muted** (silenced globally for that category)
  without resolving the underlying issue.
- Each **individual alert instance** can be **dismissed** (hidden for that specific item)
  without muting the whole category.
- Dismissed instances and muted categories are stored in `~/.yasched/config.yaml`
  alongside the default database path.
- A small **alert settings panel** (accessible from the dashboard) shows:
  - Toggle per alert type: active / muted.
  - Count of currently dismissed instances per type, with a "Reset dismissed" button.
- The top bar shows a summary badge (e.g. "3 alerts") counting only active,
  non-dismissed, non-muted issues. Clicking navigates to the dashboard.

---

## Layout

```
┌─────────────────────────────────────────────────────────┐
│  [B1] Metric cards: Layouts · Topics · Events · Tasks   │
├───────────────────────┬─────────────────────────────────┤
│  [B2] Status chart    │  [B3] Overdue tasks             │
│  (pie ↔ bar toggle)   │  [B4] Upcoming deadlines        │
├───────────────────────┴─────────────────────────────────┤
│  [B5] Conflicts  │  [B6] Stale links  │  [B7] Stale     │
│                  │                    │  blocks          │
└─────────────────────────────────────────────────────────┘
```

Alert panels collapse to a single header row when empty (no issues detected).
