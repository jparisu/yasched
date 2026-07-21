# Architecture

yasched is layered; imports only ever flow downward.

```
utilizing   coloring · timing · structuring · xyml     (generic, domain-agnostic)
   ▲
coring      plain data holders: entities + value objects (imports utilizing only)
   ▲
backending  load (xyml → coring) · resolve (inheritance/traits) · schedule occurrences
   ▲
serving     FastAPI app · view DTOs · CLI · static frontend mount
```

## utilizing

Reusable, domain-agnostic building blocks: `Color`, `Date`/`Time`/`Duration`,
generic registries/singletons, and the **xyml** loader (YAML plus `__file__` /
`__ext__` include directives).

## coring

Frozen dataclasses that hold parsed values only — no reference resolution, no
inheritance, no scheduling logic. `Topic`, `Task`, `Event`, `Trait`, the
`Schedule` family, and `Layout` and its component styles.

## backending

- **loading** — `DatabaseLoader` turns an xyml document into a `Database`.
- **resolving** — `Resolver` computes effective `attributes`, `tags`, and
  `layout` by merging layers (`default < topics < traits < parent < own`).
- **scheduling** — `build_event_occurrences` expands `Schedule`s into concrete
  dated occurrences over a window, applying sub-event overrides/cancellations.

## serving

- **views** — the single place that maps the open v3 model to the frontend's
  fixed JSON schema.
- **api** — a FastAPI app exposing `/api/health`, `/api/agenda`,
  `/api/topics|tasks|events`, `/api/reload`, and serving the built SPA.
- **cli** — the `yasched` command (`init`, `check`, `serve`).

## Frontend

`apps/web` is a React + Vite + TypeScript SPA. It fetches `/api/agenda` once
into a data context; pages read from it. In production the same FastAPI process
serves the built bundle (one port, no CORS). In development, `npm run dev`
proxies `/api` to the running `yasched serve`.

## Local-only guarantee

The API binds to `127.0.0.1` by default and makes no outbound calls. The
frontend bundles all assets — no CDNs, external fonts, or analytics.

See also [`devs/v3-architecture.md`](https://github.com/jparisu/yasched) in the
repository.
