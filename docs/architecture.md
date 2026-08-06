# Architecture

yasched is layered; imports only ever flow downward.

```
utilizing   coloring · timing (Date/Time/Duration) · structuring · xyml   (generic)
   ▲
coring      the unified model: Element, ElementType, Layout, Connection,
            AttributeDefinition
   ▲
backending  load/serialize (xyml ↔ single file) · resolve (DFS parents,
            inheritance, layout) · generate auto-elements · validate
   ▲
serving     FastAPI app · view DTOs · CLI · static frontend mount
```

## utilizing

Reusable, domain-agnostic building blocks: `Color`, `Date` / `Time` /
`Duration`, generic registries/singletons, and the **xyml** loader (YAML plus
`__file__` / `__ext__` include directives).

## coring

Plain data holders — no resolution, no generation. `Element` (id, type,
`direct_parents`, `layout`, `attributes`), `ElementType`, `Layout` and its
component styles, `Connection`, and `AttributeDefinition` (the attribute schema,
with 24 built-ins).

## backending

- **loading** — `ElementLoader` turns an (x)yml document into a `Database`;
  `ElementSerializer` writes a `Database` back to a single canonical YAML file
  (flattening any includes, never writing virtual elements).
- **resolving** — `Resolver` computes `Parents` (pre-order DFS + AllTopic),
  `MainParent`, `Topic`, effective attributes (own > first defining parent,
  scoped by applies-to), and per-field layout (own > attribute-layout > parents).
- **generating** — `Generator` expands schedules, deadlines, and reminders into
  virtual dated elements in a window, with deterministic ids and
  promotion-suppression.
- **validating** — `Validator` reports unknown/cyclic parents, unknown
  connection targets, out-of-range/enum values, and detached promoted
  occurrences.

## serving

- **views** — pure functions that build the `/api/elements` payload: resolved
  real + virtual elements (each with resolved attributes/layout, `parents`,
  `mainParent`, `topic`, and connections both directions) plus the definitions.
- **api** — a FastAPI app exposing `/api/health`, `/api/meta`, `/api/validate`,
  `/api/elements` (GET payload, POST create), `/api/elements/{id}`
  (GET raw / PUT / DELETE — PUT is also the promote path), `/api/reload`, and
  serving the built SPA.
- **cli** — the `yasched` command (`init`, `check`, `serve`).

## Frontend

`apps/web` is a React + Vite + TypeScript SPA. A data store fetches
`/api/elements` into context; panels (grouped by category) read from it and write
through `POST`/`PUT`/`DELETE`. In production the same FastAPI process serves the
built bundle (one port, no CORS); in development `npm run dev` proxies `/api` to
the running `yasched serve`.

## Local-only guarantee

The API binds to `127.0.0.1` by default and makes no outbound calls. The
frontend bundles all assets — no CDNs, external fonts, or analytics.

See also [`devs/v4/v4-architecture.md`](https://github.com/jparisu/yasched) and
[`devs/v4/v4-panel-requirements.md`](https://github.com/jparisu/yasched) in the
repository.
