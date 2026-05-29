# C — Tasks

## Sub-views

| View | Tier |
|---|---|
| Kanban board (post-it style) | REQUIREMENT |
| Dependency graph | REQUIREMENT |
| Table / list view | FUTURE |
| Hierarchy tree view | FUTURE |

---

## C1 · Kanban Board — REQUIREMENT

### Axes
- **Vertical axis (fixed):** task status — TODO / IN_PROGRESS / BLOCKED / DONE / CANCELLED.
- **Horizontal axis (configurable):** any task field or derived property. Default: high-level
  topic (root ancestor of the task's topic). Other examples: time horizon/deadline bucket,
  effort tier, tag, priority band. The axis definition is stored per view preset.
- Both axes can be extended with custom grouping logic without changing the board engine.

### View Presets
- Users can create multiple named Kanban configurations (presets).
- Presets are shown as **named tabs above the board**.
- Each preset stores: name, horizontal axis definition, background style, noise override (future).
- Presets saved in `~/.yasched/config.yaml`. Persists across server restarts.
- Users can create, rename, duplicate, and delete presets from a preset management UI.

### Post-it Board
- Tasks are rendered as **post-it cards** on a physical board surface.
- Cards have **free positioning** — not forced into a grid after the initial sort.
- Cards are **draggable**: grab and drop anywhere on the board.
- A **Sort button** snaps all cards back to the axis grid layout.
- **Noise value** (global setting, configured in Settings page): when Sort is applied,
  each card's final position is jittered by a random offset within the noise radius,
  giving the appearance of a real physical board. Noise = 0 means perfect grid.

### Board Background
All three background types supported, configurable per preset:
- **Solid color** — any hex/rgb color.
- **Texture / pattern** — built-in set (cork board, whiteboard, grid, linen, …).
- **Custom image** — user provides a local file path; server serves it as a static asset.

### Card Highlights & Layout Policy
- Card visual style (background, border, icon) follows the task's `effective_layout`.
- **Highlight conditions** are modeled as a layout policy layer applied on top:
  - Overdue tasks: default policy = red border (overrides base layout border).
  - Other conditions (blocked, high priority, …) can be assigned a policy in Settings.
- This keeps highlights decoupled from the base layout system and fully customizable.

### Task Detail Drawer
- Clicking a card opens a **slide-in drawer** from the right.
- Board remains visible and interactive behind the drawer.
- Drawer shows: all task fields, description, effective tags, priority, effort (min–max),
  deadline, status, topic breadcrumb, parent task, children list, blockers list,
  linked events list.
- Click outside or press Escape to close.

---

## C2 · Dependency Graph — REQUIREMENT

- Dedicated sub-tab within the Tasks page.
- DAG visualization of `blocking → blocked` relationships across all tasks.
- Node color / style follows `effective_layout` of each task.
- Clicking a node opens the task detail drawer.
- Configurable depth: show full graph or only N hops from a selected task.
- Distinct from the global Graph page (Page 8), which mixes all entity types.

---

## C3 · Table / List View — FUTURE

- Sortable columns: name, status, priority, deadline, topic, effort.
- Row click opens the task detail drawer.
- Column visibility configurable.

---

## C4 · Hierarchy Tree View — FUTURE

- Parent → children collapsible tree.
- Visual indentation per level.
- Node click opens task detail drawer.

---

## Shared: Filtering & Search
- Each task view has its own **local filter bar**: status, topic (subtree), tags,
  priority range, deadline range, has-blockers toggle.
- Global search bar (from Group B) can navigate directly to a task, which highlights
  it in the current view.
