# J — Graph Explorer (Page 8)

Dynamic ontology-style graph for navigating relationships between all entity types.

---

## J1 · Node Types & Edges — REQUIREMENT

### Nodes
| Entity | Shape | Color |
|---|---|---|
| Topic | Circle | `effective_layout` color, or topic palette fallback |
| Task | Square | `effective_layout` color, or status color fallback |
| Event | Diamond | `effective_layout` color, or topic palette fallback |

### Edges
| Relationship | Source → Target | Style |
|---|---|---|
| Topic hierarchy | parent topic → child topic | solid, thin |
| Task hierarchy | parent task → child task | solid, thin |
| Task dependency | blocking task → blocked task | dashed, red |
| Task → topic | task → its topic | dotted, neutral |
| Event → topic | event → its topic | dotted, neutral |
| Event link | task → linked event | dashed, neutral |

Edge labels are hidden by default; shown on hover.

---

## J2 · Navigation — Ego-Graph Mode — REQUIREMENT

- The graph always shows an **ego-graph** centered on one selected node.
- On page load, the center node defaults to the first root topic.
- **Clicking any visible node re-centers** the graph on that node: the graph
  rebuilds showing only nodes within the configured depth radius from the new center.
- A **breadcrumb / back button** tracks navigation history so the user can go back.
- The center node is visually distinct (larger, glowing ring, or bold border).

## J3 · Depth Radius Slider — REQUIREMENT

- A slider on the graph page controls how many hops from the center are shown.
- Range: 1–5 hops. Default: 2.
- Changing the slider instantly rebuilds the visible subgraph.
- Not persisted — resets to default on page load.

## J4 · Node Detail — REQUIREMENT

- Clicking the **center node** (already centered) opens the entity detail drawer
  (same drawer as Tasks and Calendar pages, adapted for the entity type).
- Single-click on a non-center node re-centers; requires a second click (once centered)
  to open the drawer. This keeps navigation fluid.

## J5 · Filters — REQUIREMENT

- Toggle which node types are visible: Topics / Tasks / Events (independent checkboxes).
- Hiding a type removes those nodes and their edges from the graph.
- Filter state is per-session (not persisted).

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│  [○ Topics] [□ Tasks] [◇ Events]    Depth: ──●── 2  │
│                                                      │
│                                                      │
│              [graph canvas]                          │
│         pan & zoom, ego-graph centered               │
│                                                      │
│                                                      │
│  ← Back    Center: topic:work                        │
└──────────────────────────────────────────────────────┘
```

Node legend shown as a small fixed overlay in a corner of the canvas.
