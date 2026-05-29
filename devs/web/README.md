# yasched — Web Frontend Design

## Toolchain

| Layer | Technology |
|---|---|
| Backend logic | Existing `yasched` Python library (`DatabaseInterface`) |
| App state + API | Reflex `State` classes (Python, auto-wired to React) |
| UI components | Reflex component tree (Python → React) |
| Styling | Radix UI + custom CSS via Reflex |
| Build / serve | `reflex run` (dev) / `reflex export` (prod) |

Reflex generates a FastAPI backend and a React frontend from a single Python codebase.
The existing `yasched` library is used as a pure Python dependency — no REST layer to write manually.

---

## Pages

| # | Page | Status |
|---|---|---|
| 1 | Home / Dashboard | design in progress |
| 2 | Tasks (Kanban + List + Tree + Graph) | design in progress |
| 3 | Calendar (Yearly / Monthly / Weekly / Daily) | design in progress |
| 4 | Schedule (week time-grid) | design in progress |
| 5 | Topics | design in progress |
| 6 | Layouts | design in progress |
| 7 | Analytics | design in progress |
| 8 | Graph (ontology / relationship explorer) | design in progress |

---

## Feature Groups

| File | Group | Design status |
|---|---|---|
| [A_data_loading.md](A_data_loading.md) | Data Loading & Database Management | done |
| [B_dashboard.md](B_dashboard.md) | Dashboard / Home | done |
| [C_tasks.md](C_tasks.md) | Tasks | done |
| [D_calendar.md](D_calendar.md) | Calendar / Events | done |
| [E_schedule.md](E_schedule.md) | Time Schedule (week grid) | done |
| [F_topics.md](F_topics.md) | Topics | done |
| [G_layouts.md](G_layouts.md) | Layouts | done |
| [H_analytics.md](H_analytics.md) | Analytics | done |
| [I_settings.md](I_settings.md) | Settings / Preferences | done |
| [J_graph.md](J_graph.md) | Graph explorer | done |
| [K_crud.md](K_crud.md) | Create / Edit / Delete (CRUD) | done |

---

## Key design decisions (accumulated)

### Toolchain
- **Reflex** chosen over Streamlit for professional, customizable UI.
- Layouts must be highly customizable (backgrounds, borders, icons, gradients).

### CRUD — Create / Edit / Delete (Group K)
- All three entity types (topics, events, tasks) are fully creatable, editable, and deletable from the UI.
- Edit: detail drawer switches to edit mode (Edit button in header).
- Create: dedicated creation modal per entity type (+ New button on each page).
- Delete: button in edit mode + inline confirmation + reference warnings.
- Persistence: immediate YAML write via DatabaseSerializer + auto-reload on save.
- Future: background/debounced writes with dirty indicator in top bar.
- Validation: inline, before save — required fields, id uniqueness, schedule completeness, cross-reference checks.
- Read-only mode (I5) blocks all write operations.

### Graph Explorer (Group J)
- All entity types: topics (circle), tasks (square), events (diamond). Color from effective_layout.
- Ego-graph mode: click any node to re-center; depth-radius slider (1–5, default 2) rebuilds subgraph.
- Back button tracks navigation history.
- Center node click opens entity detail drawer.
- Per-session node type filters (Topics / Tasks / Events toggles).

### Settings (Group I)
- Dedicated page (gear icon in top bar / sidebar).
- Requirements: theme toggle, schedule grid hour window + granularity, Kanban noise slider, Alerts management section, Read-only mode.
- Read-only mode: global toggle that disables all write operations; 🔒 indicator in top bar; persisted in config.
- Upcoming deadlines window (N days): desirable, defaults to 7.
- All settings persisted in `~/.yasched/config.yaml`.

### Analytics (Group H)
- Dedicated page (Page 7).
- Requirements: task count by topic (bar), priority distribution (histogram), deadline density (bar/heatmap).
- Effort totals by topic/status: future.
- Shared date-range and status filters across all charts.

### Layouts (Group G)
- Gallery: card grid with live visual previews (background, border, icon).
- Detail: full style breakdown + live mock post-it and event badge.
- Visual editor (v1 requirement): edit background/border/icon, written back to YAML via DatabaseSerializer.
- Create and delete layouts from the UI; warns on delete if layout is referenced.
- Entities using a layout: future.

### Topics (Group F)
- Tree display: collapsible tree + radial tree, toggleable. Shared selection state.
- Detail panel: id, name, description, inherited tags, parent breadcrumb, layout preview swatch.
- No cross-page filtering — each page manages its own filters.

### Schedule (Group E)
- Week time-grid: configurable hour window (default 07:00–22:00), set in Settings.
- All-day events (non-timed schedules) shown as banners above the hourly grid.
- Overlapping events: side-by-side columns + red border on each conflicting block.
- Deadline markers: shared toggle with Calendar (global setting).
- Grid line granularity (30 min / 1 h) configurable in Settings.

### Calendar (Group D)
- Views: Monthly (+ mini next-month panel) + Weekly + Daily are requirements; Yearly heatmap is future.
- Deadline markers: toggleable (stored in config), distinct style from event badges.
- Event detail: slide-in drawer (consistent with task detail).
- Conflicts: red tint on day cell; tooltip lists conflicting pairs; detail in Daily view.
- Shared filter bar per view: topic, layout, tags.

### Tasks (Group C)
- Kanban: vertical = status (fixed), horizontal = any task field (default: high-level topic).
- Multiple named view presets as tabs, saved in `~/.yasched/config.yaml`.
- Tasks rendered as **post-its** with free drag positioning; Sort button re-snaps to grid.
- Noise value (global setting): jitter applied on sort for physical board aesthetic.
- Board background: solid color / built-in texture / custom image path — per preset.
- Card highlights use a **layout policy layer** (e.g. red border for overdue) decoupled from base layout.
- Task detail opens in a **slide-in drawer** from the right.
- Dependency graph sub-tab: DAG of blocking→blocked, configurable depth.
- Table view and hierarchy tree: future.

### Dashboard (Group B)
- All 5 alert types are requirements: overdue, upcoming deadlines, conflicts, stale links, stale blocks.
- Alerts have an **independent management layer**: each type can be muted, each instance dismissed,
  persisted in `~/.yasched/config.yaml`. Top-bar badge counts only active non-dismissed alerts.
- Status chart: both pie and bar, user-switchable toggle.
- Search: global top-bar (all entities, every page) + per-page local filters.

### Data Loading (Group A)
- Database loader lives in a **modal on first load**, re-openable from the top bar.
- Modal is **mandatory on first startup** (cannot dismiss without a loaded DB).
- After loading: compact status indicator in top bar (✅ / ⚠️ N errors / ❌ Failed).
- Errors shown as summary + expandable per-item list; do not block rendering.
- **Recent files** stored in browser local storage — shown in the modal as a clickable list.
- **Server-side default database** stored in `~/.yasched/config.yaml`; on server restart the
  modal opens pre-filled with the last path so the user just clicks Load.
- **Multi-file support** is future; data model must be designed multi-file-ready.
