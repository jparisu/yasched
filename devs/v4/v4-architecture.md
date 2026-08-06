# yasched v4 — Architecture (as implemented)

Companion to [`v4-panel-requirements.md`](v4-panel-requirements.md) (the spec)
and [`data-model.plantuml`](data-model.plantuml) (the model diagram). This
records what the Python backend actually implements.

## Layering (imports flow downward only)

```
utilizing   coloring · timing (Date/Time/Duration) · structuring · xyml   (unchanged from v3)
   ▲
coring      the unified model — imports utilizing only
   ▲
backending  load/serialize · resolve · generate · validate
   ▲
serving     FastAPI app · view DTOs · CLI · static SPA mount
```

## coring — the unified model (`src/yasched/coring/`)

| Type | Purpose |
|---|---|
| `ElementType` | enum: `topic` \| `event` \| `task` \| `schedule` |
| `Element` | `id`, `type`, `direct_parents`, `layout`, `attributes` (+ `virtual` flag). Mutable holder; `name`/`description`/… live in `attributes`. |
| `Layout` (+ `Background` with gradient, `Border`, `Icon`, `Pin`, `Format`) | visual bag; every field optional; `merged_over()` does per-field first-defined-wins |
| `Connection` | directed, informational link stored in the `connections` attribute |
| `AttributeDefinition` (+ `ValueType`) | attribute schema: value type, `applies_to`, min/max, enum, optional layout, `inherits`; `builtin_definitions()` seeds the 24 built-ins; `NON_INHERITING` = `{connections}` |

## backending — engine (`src/yasched/backending/`)

- `Database` — flat `elements` dict + `attribute_defs`; guarantees the
  `AllTopic` root exists; type-filtered views (`.topics`, `.events`, …).
- `loading/ElementLoader` — (x)yml → `Database`. Accepts `directParents` or
  `direct_parents`, folds top-level `name`/`description` into attributes, parses
  layout + attribute definitions. Flags multi-file sources.
- `loading/ElementSerializer` — `Database` → single canonical YAML (flatten on
  save). Never writes virtual elements; omits an untouched `AllTopic`.
- `resolving/Resolver` — the heart:
  - `parents(id)` — pre-order DFS over `direct_parents` with one global visited
    set; `AllTopic` appended last. `main_parent` = `Parents[0]`; `topic_of` =
    first topic in `Parents`.
  - attribute resolution: own wins, else first parent that defines it, scoped by
    the definition's `applies_to` (so schedule-only config never leaks into a
    generated event/task) and skipping `NON_INHERITING`.
  - layout resolution: `own > attribute-layout > parents` (per field).
  - returns `ResolvedElement`.
- `generating/Generator` — expands a `[start, end]` window into `virtual`
  elements: schedule occurrences (`daily`/`weekly`/`monthly` with month-end
  clamp/`yearly`), `deadline` events, and `reminder` events. Deterministic ids
  (`{gen}#{date}`, `{task}#deadline`, `{host}#reminder-{offset}`); a real element
  with the same id suppresses the virtual (promotion). Cascade bounded to
  `schedule → task → {deadline, reminder}`.
- `validating/Validator` — unknown/self/cyclic parents, unknown connection
  targets, out-of-range/enum attribute values, detached promoted occurrences.

## serving — API + CLI (`src/yasched/serving/`)

- `views` — pure (FastAPI-free) DTO builders. `build_payload(db, start, end)`
  returns `{window, definitions, elements}` where elements are resolved reals +
  generated virtuals, each with resolved attributes/layout, `parents`,
  `mainParent`, `topic`, outgoing `connections`, and reverse `incoming`.
- `state/AppState` — loads/caches the DB, CRUD, and save-back. v4 is always
  writable; saving flattens any multi-file source to the single file.
  Promotion of a virtual element is an upsert with its deterministic id.
- `api` — FastAPI: `/api/health`, `/api/meta`, `/api/validate`,
  `/api/elements` (GET payload, POST create), `/api/elements/{id}`
  (GET/PUT/DELETE — PUT is also promotion), `/api/reload`. Mounts the SPA.
- `cli` — `yasched init | serve | check`.

## Persistence

One YAML file is the database. xyml includes are read-time only; the first UI
save flattens to a single file. Default path `~/.yasched/agenda.yaml`.

## Testing

`tests/coring`, `tests/backending`, `tests/serving` cover the model, the DFS
linearization example, inheritance/layout resolution, all generator kinds +
promotion + cascade bound, serializer round-trip, validation, view DTOs, and
CRUD/flatten. The FastAPI smoke test `importorskip`s if fastapi is absent.

## Frontend (`apps/web`)

Rebuilt v4-native around the `/api/elements` payload. Layers:

- `types.ts` / `api.ts` — DTOs + fetch client (elements, meta, validate, CRUD).
- `store.tsx` — `DataProvider` + `useData()`; fetches the resolved payload,
  exposes elements/definitions/meta/validation and `save`/`remove` (save is also
  the promote-a-virtual path). `settings.tsx` — theme/style/density.
- `lib/` — `elements.ts` (selectors: topic tree, `whenOf`, `isVisibleTask`,
  `marked` rule), `layout.ts` (resolved `LayoutDTO` → CSS), `format.ts` (dates).
- `ui/` — `ElementView` (card/line/point), `PanelCard`, `ElementDrawer`.
- `app/` — category `Sidebar` (Core/Topic/Event/Schedule/Task), `TopBar`, `App`.
- `panels/` — Main, Stats, Focus, Attributes, Settings, TopicGraph, Calendar,
  Agenda, Taskboard (native drag→status), Timeboard, and a shared
  `ElementManagement` (topic tree + attribute/layout editor) used by the four
  “manage” panels.

Build: `cd apps/web && npm install && npm run build`. Not yet built here (this
environment has no Node runtime); Timeline and the year/day calendar views from
the spec are still TODO. The MkDocs pages under `docs/` still describe v3.
