# F — Topics

## F1 · Topic Hierarchy Visualization — REQUIREMENT

Two display modes, toggled via a button:

- **Collapsible tree** (default): classic file-explorer style on the left panel.
  Each node shows topic id + name. Click to select; expand/collapse children.
- **Radial tree**: nodes arranged radially from the root(s). Click a node to
  expand/collapse its subtree. Useful for spotting the full structure at a glance.

Both modes share the same selection state — switching layout preserves the
currently selected topic.

## F2 · Topic Detail Panel — REQUIREMENT

Shown on the right when a topic is selected. Contains:

- **Basic info:** id, name, description, effective tags (own + inherited), parent breadcrumb.
- **Inherited layout preview:** visual render of `effective_layout` — background color
  or gradient swatch, border style sample, icon (if set). If no layout is inherited,
  shows a "no layout" placeholder.

Not included in v1 (future):
- Task status breakdown per topic.
- Events list per topic.

## F3 · Cross-page Filtering — NOT INCLUDED

Topics page is standalone. No global topic filter propagated to other pages.
Each page manages its own filters independently.

---

## Layout

```
┌──────────────────┬───────────────────────────────────┐
│  Tree / Radial   │  Topic Detail                     │
│  toggle button   │  ─────────────────────────────    │
│                  │  id · name · description          │
│  [topic tree     │  tags (inherited)                 │
│   or radial      │  parent breadcrumb                │
│   visualization] │  layout preview swatch            │
│                  │                                   │
└──────────────────┴───────────────────────────────────┘
```
