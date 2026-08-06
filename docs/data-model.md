# Data model

Everything yasched manages is an **Element**. There is one data structure; the
`type` field (`topic` \| `event` \| `task` \| `schedule`) selects behavior and
which attributes are meaningful.

## The Element

| Field | Meaning |
|---|---|
| `id` | Unique, immutable identity. The only value that is **not** an attribute. |
| `type` | `topic` \| `event` \| `task` \| `schedule`. |
| `directParents` | Ordered inheritance list (see below). |
| `layout` | Visual style (optional; inheritable). |
| `attributes` | Open name→value bag: `name`, `description`, `focus`, dates, `status`, `connections`, … |

`name` and `description` are attributes (so they inherit); only `id` and `type`
are structural.

## directParents, Parents, MainParent

`directParents` is the **only** relation that drives inheritance — an ordered
list of element ids understood as a *tag list*: the first entry is the primary
parent, the rest are extra tags.

From it, yasched computes `Parents` by a pre-order depth-first walk with a single
visited set (a branch is fully expanded before the next sibling), and always
appends the root **AllTopic** last so defaults resolve:

```
directParents:  A:[]  B:[A]  C:[A]  D:[B,A]  E:[C,D]
Parents(E)  =  [C, A, D, B, AllTopic]
MainParent(E) = C          # = directParents[0]
```

- **`Topic(E)`** — the first `topic`-typed element in `Parents(E)`. Used for
  grouping and sorting. Always resolves (AllTopic is a topic).
- **`AllTopic`** — a built-in root topic that is an ancestor of every element and
  holds the app-wide default attributes and layout (so there is no separate
  "default" layer).

## Inheritance

**Attributes** — for each attribute an element does not set, the value comes from
the first element in `Parents` that defines it (own value always wins). A
definition's *applies-to* scopes this, so schedule-only config never leaks into a
generated event, and `connections` never inherits at all.

**Layout** — resolved per field, first-defined wins:

```
element's own  >  attribute-layout  >  Parents (in Parents order)
```

An attribute definition may carry a static `layout` applied whenever the
attribute is present — e.g. a `danger` bool that paints a red border. That beats
topic/parent layout but loses to a value set directly on the element.

## Element types

- **Topic** — an organizational category. Sub-topics are topics whose MainParent
  is another topic, giving the file-tree used throughout the UI.
- **Event** — time-bound. `start` / optional `end` / `duration`, plus
  `location` and `reminders`. A recurring event is produced by a Schedule.
- **Task** — `status`, `priority`, `difficulty`, optional `deadline`,
  `reminders`, and `marked`. A **subtask** has a task MainParent; a parent task
  with marked subtasks derives its completion from them.
- **Schedule** — a generator. It carries `generates` (`event`/`task`), a `kind`
  (`daily` / `weekly` / `monthly` / `yearly`) with the matching day fields, a
  `[startDate, endDate]` window, and optional `time` / `duration`. **The schedule
  *is* the template**: each occurrence inherits its name/attributes/layout.

## Auto-elements (virtual → real)

Three generators produce **virtual** elements within the active date window,
never stored until edited:

| Generator | Produces | Deterministic id |
|---|---|---|
| Schedule | events or tasks | `{schedule}#{date}` |
| A task `deadline` | one `deadline` event | `{task}#deadline` |
| `reminders` | one `reminder` event each | `{host}#reminder-{offset}` |

Each pins its generator as MainParent, so it inherits everything. **Editing a
virtual element promotes it** to a real element with the same id (storing only
the overrides); the real one then suppresses the generated one. To cancel a
single occurrence, promote it and set `cancelled: true`.

## Connections

The built-in `connections` attribute links an element to another via an open
relation label (`follows`, `blocks`, `similar`, …). It is stored once on the
source, surfaced on **both** endpoints, and is informational only — it never
changes another element's computed state and never participates in inheritance.

## Persistence

The database is a single YAML file. Multi-file xyml includes are supported when
reading; the first save from the app flattens everything into that one file.
Only real elements are written — virtual ones are recomputed on load.
