# yasched Web — Build Status

## Infrastructure

| Item | Status | Notes |
|---|---|---|
| Reflex project scaffolding (`apps/web/`) | done | rxconfig.py, package structure |
| Config system (`~/.yasched/config.yaml`) | done | read/write, all settings fields |
| AppState (db loading, theme, read-only) | done | |
| Top bar (status badge, open-DB, lock icon) | done | tooltips on all elements |
| Sidebar navigation | done | tooltips on all links |
| Database modal (file browser, recent files, load) | done | Group A complete |
| Settings page (theme + read-only toggle) | done | Group I partial (only A1+A5) |

## Pages

| Page | Status | Notes |
|---|---|---|
| Dashboard (B) | placeholder | not started |
| Tasks (C) | placeholder | not started |
| Calendar (D) | placeholder | not started |
| Schedule (E) | placeholder | not started |
| Topics (F) | **done** | see below |
| Layouts (G) | placeholder | not started |
| Analytics (H) | placeholder | not started |
| Graph (J) | placeholder | not started |
| Settings (I) | partial | theme + read-only only; alerts, grid, noise pending |

## Topics page (F) — detail

| Feature | Status | Notes |
|---|---|---|
| F1 · Collapsible tree | done | expand/collapse, click to select, ID on hover |
| F1 · Radial SVG tree | done | angular layout, click to select node |
| F1 · View mode toggle | done | tree ↔ radial, shared selection state |
| F2 · Detail panel — basic info | done | id, name, description, parent breadcrumb (clickable) |
| F2 · Detail panel — effective tags | done | |
| F2 · Detail panel — layout preview | done | bg color swatch, border, icon |
| F2 · Task breakdown per topic | not started | future per design |
| F2 · Events list per topic | not started | future per design |
| F3 · Cross-page filter | not included | by design decision |

## Settings page (I) — detail

| Feature | Status | Notes |
|---|---|---|
| I1 · Theme toggle (light/dark) | done | persisted to config |
| I2 · Schedule grid hour window | not started | |
| I2 · Grid line granularity | not started | |
| I3 · Kanban noise slider | not started | |
| I4 · Alerts management section | not started | |
| I5 · Read-only mode toggle | done | persisted to config, lock icon in top bar |
| I6 · Upcoming deadlines window | not started | |
