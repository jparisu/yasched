# Data model

yasched has three persisted entities — **Topic**, **Task**, **Event** — plus two
supporting concepts: **Trait** (reusable bundles) and **Schedule** (recurrence).

## Two open bags, one engine

Every entity carries:

- **`attributes`** — an open map of semantic data. Any key is allowed
  (`deadline`, `priority`, `difficulty`, `kanban`, `status`, `effort`, …).
- **`layout`** — visual style: `background`, `border`, `icon`, `pin`, `shape`.

Both are computed by merging *layers*, lowest → highest priority:

```
default  <  topic(s) (ancestors-first, listed order)  <  traits (listed order)  <  parent  <  own
```

Merge rules per namespace:

| Namespace | Rule |
|---|---|
| `attributes` | replace by key — higher layer wins per key |
| `tags` | union — accumulate across all layers, de-duplicated |
| `layout` | backgrounds compose by concrete `type`; other fields higher-wins |

Because attribute keys inherit and merge automatically, the model stays open:
some tasks have a `difficulty`, others a `deadline`, others a `kanban` column —
all just keys, supplied directly, via a trait, or inherited.

## Topic

An organizational category. Topics form a **DAG** via `parent_ids` (a topic may
have multiple parents). Tags, attributes, and layout flow down to child topics
and to the tasks/events that reference them.

## Task

A unit of work. A task may be:

- **one-off** — carry a `deadline` attribute;
- **recurring** — carry `schedules`;
- **a subtask** — set `parent_id`; it inherits the parent's topics, attributes,
  layout, and tags.

Tasks also carry `relations` (task → task: `requires`, `needs`, `connected`,
`similar`) and `event_links` (task → event, e.g. *use this event as my
deadline*). A task belongs to zero or more topics via `topic_ids`.

## Event

A time-bound occurrence, recurring via one or more `schedules`. A **sub-event**
sets `parent_id` to a recurring parent and **overrides a single occurrence**
(e.g. move a room). If the sub-event's effective `status` is `cancelled`, that
occurrence is removed entirely.

## Trait

A named, reusable bundle of `attributes` and/or `layout`, attached to an entity
via its `traits` list and merged as a layer. A trait with only a `layout` is a
"named layout".

## Schedule

Describes *when* something happens. Five kinds:

| Type | Fields |
|---|---|
| `weekly` | `week_days`, `start_time`, `end_time` \| `duration` |
| `monthly` | `day` (1–31, clamped to month end) |
| `yearly` | `month`, `day` |
| `single_day` | `day` |
| `multi_day` | `start_day`, `end_day` |

`backending` expands schedules into concrete dated occurrences over a window.
