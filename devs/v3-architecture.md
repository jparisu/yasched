# yasched v3.0 — Architecture

## Layering (imports flow downward only)

```
utilizing   coloring · timing · structuring · xyml         (generic, domain-agnostic)
   ▲
coring      plain data holders: entities + value objects   (imports utilizing only)
   ▲
backending  load (xyml → coring) · resolve (inheritance/traits/merge) · schedule occurrences
   ▲
serving     FastAPI app · view DTOs · CLI · static frontend mount
```

The React frontend (`apps/web`) talks to `serving` over HTTP and is served as
static files by the same process — one port, no CORS, fully local.

## coring — data holders (`src/yasched/coring/`)

Frozen dataclasses. No cross-reference resolution, no inheritance, no scheduling
logic — they only hold parsed values. Cycle/consistency checks belong to a later
phase (validation is intentionally deferred).

| Type | Purpose |
|---|---|
| `_shared`: `Weekday`, `RelationType`, `TaskRelation`, `EventLink` | small support types |
| `Layout` (+ `Background`, `Border`, `Icon`, `Pin`, `Shape`) | visual bag |
| `Trait` | named bundle: `attributes` (dict) + `layout` |
| `Schedule` (+ `Weekly`/`Monthly`/`Yearly`/`SingleDay`/`MultiDay`) | recurrence/timing value objects |
| `Topic` | id, name, description, tags, `parent_ids` (DAG), traits, attributes, layout |
| `Event` | + `topic_ids`, `parent_id` (occurrence override), `schedules` |
| `Task`  | + `topic_ids`, `parent_id` (subtask), `schedules`, `relations`, `event_links` |

**Two open bags, one engine.** Every entity carries `attributes: dict[str, Any]`
(semantic) and `layout: Layout | None` (visual). `tags` is a first-class list.

## backending — load + resolve (`src/yasched/backending/`)

- `Database` — container: `default_attributes`, `default_layout`, `traits`,
  `topics`, `events`, `tasks` (all keyed by id).
- `loading/DatabaseLoader` — `XymlLoader.load()` → dict → parse into `Database`.
- `resolving/Resolver` — computes the **effective** attributes/layout/tags for
  each entity by merging layers, lowest → highest:

  ```
  default  <  topic(s) (ancestors-first, listed order)  <  traits (listed order)  <  parent  <  own
  ```

  Merge rules: `attributes` replace-by-key; `tags` union; `layout` backgrounds
  compose by concrete type, other layout fields higher-wins. Produces
  `ResolvedTopic` / `ResolvedEvent` / `ResolvedTask`. Cycles are guarded (skipped).
- `scheduling/Occurrences` — expands `Schedule`s into concrete dated
  `Occurrence`s within a `[start, end]` window. A sub-event (an event with
  `parent_id`) overrides its parent's occurrence on the same date; a sub-event
  whose effective `status == "cancelled"` removes that occurrence.

## serving — API + CLI (`src/yasched/serving/`)

- `views` — maps resolved entities + occurrences to the exact JSON shapes the
  frontend expects (topics/tasks/events/deadlines), translating our open model
  to the frontend's fixed fields (priority int→low/med/high, status→todo/doing/done,
  resolved layout→`{backgroundColor,leftColor,shape}`).
- `api` — FastAPI app: `/api/health`, `/api/agenda` (the full payload),
  `/api/topics|tasks|events`. Mounts the built SPA at `/`.
- `cli` — `yasched` command: `init` (create a personal agenda from template),
  `serve` (run uvicorn against a personal agenda yaml).

## Personal agenda

Default location `~/.yasched/agenda.yaml` (override with `--agenda` or
`$YASCHED_AGENDA`). `yasched init` seeds it from `resources/personal_template/`.
`yasched serve` runs everything locally on `127.0.0.1`.

## Non-negotiable: fully local

No runtime network calls anywhere — no CDNs, external fonts, analytics, or cloud.
The frontend bundles all assets; the API is localhost-only by default.
