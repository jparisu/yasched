# I — Settings

Dedicated page, accessible from the sidebar or top bar (gear icon).
All settings persisted in `~/.yasched/config.yaml`.

---

## I1 · Appearance — REQUIREMENT

- **Theme:** light / dark toggle. Applied globally, persists across restarts.

## I2 · Schedule Grid — REQUIREMENT

- **Hour window:** start hour and end hour for the Schedule time-grid (default 07:00–22:00).
- **Grid line granularity:** 30 min or 1 hour tick interval.

## I3 · Kanban — REQUIREMENT

- **Noise value:** global slider (0 = perfect grid, 100 = maximum jitter).
  Applied whenever the Sort button is used on any Kanban board.

## I4 · Alerts — REQUIREMENT

Dedicated Alerts section with full management controls:

- Per alert type toggle (active / muted):
  - Overdue tasks
  - Upcoming deadlines
  - Scheduling conflicts
  - Stale event links
  - Stale blocks
- For each type: count of currently dismissed instances + "Reset dismissed" button.
- Changes take effect immediately on the Dashboard.

## I5 · Read-Only Mode — REQUIREMENT

- Global toggle: **Read-only ON / OFF**.
- When ON: all write operations across the entire app are disabled:
  - Layout editor (G3) is hidden or all fields are non-editable.
  - No create / delete layout buttons shown.
  - YAML file is never written from the UI.
  - Any future edit capabilities (tasks, events, topics) are also blocked.
- A visible indicator in the top bar (e.g. a lock icon 🔒) shows when read-only is active.
- Persisted in `~/.yasched/config.yaml`. Useful when sharing the server with others
  or when treating the UI as a pure viewer.

## I6 · Dashboard — DESIRABLE

- **Upcoming deadlines window:** number of days ahead for the deadline panel (default: 7).
- Not a requirement for v1 — the default of 7 days is hardcoded until this is implemented.

---

## Page layout

```
Settings
├── Appearance
│   └── Theme: [Light] [Dark]
├── Schedule
│   ├── Grid start hour: [07:00]
│   ├── Grid end hour:   [22:00]
│   └── Grid lines:      [30 min] [1 h]
├── Kanban
│   └── Sort noise: ────●──── 35
├── General
│   └── Read-only mode: [OFF] [ON]   🔒 shown in top bar when ON
└── Alerts
    ├── [✓] Overdue tasks        0 dismissed  [Reset]
    ├── [✓] Upcoming deadlines   2 dismissed  [Reset]
    ├── [✓] Scheduling conflicts 0 dismissed  [Reset]
    ├── [✓] Stale event links    1 dismissed  [Reset]
    └── [✓] Stale blocks         0 dismissed  [Reset]
```
