# yasched v4 — Requirements (ground truth)

> This document supersedes the v3 data model. It incorporates the decisions
> recorded in [`comments-v4.md`](comments-v4.md) and the four follow-up
> decisions (persistence, connections, traits, recurrence). It is the reference
> for building v4. The companion [`data-model.plantuml`](data-model.plantuml)
> mirrors this document.
>
> Sections tagged **DECISION** are design calls made while writing this spec
> (delegated parts, or corner cases not previously covered). They can be vetoed.

---

# Part I — Data model

## 1. The Element

Everything the app manages and renders is an **Element**. There is exactly one
universal entity; the different "kinds" (topic, event, task, schedule) are
element *types* that add type-specific behavior and a type-specific set of valid
attributes — not different data structures.

An Element has only these **structural fields** (everything else is an
attribute):

| Field | Meaning |
|---|---|
| `id` | Unique, immutable identity. The only value that is **not** an attribute. |
| `type` | One of `topic` \| `event` \| `task` \| `schedule`. Determines behavior and which attributes are valid. |
| `directParents` | Ordered list of element ids — the **inheritance** relation only (see §2). |
| `layout` | Structured visual style (see §7). Inheritable, but resolved by its own rule. |
| `attributes` | Open name→value bag holding all semantic values, including `name`, `description`, `focus`, `connections`, dates, `status`, … (see §4). |

**Why so few fields.** `name` and `description` are attributes (so they can be
inherited); `id` is kept separate because identity must not be inherited or
merged. Dates, durations, deadlines, status, priority, etc. are all attributes
too — one bag, one editor, one inheritance engine.

---

## 2. DirectParents · Parents · MainParent

`directParents` is the **only** relation that drives inheritance. It is an
**ordered list of element ids**, understood by the user as a *tag list*: **the**
first entry is the element's intended primary parent, the rest are additional
tags. Any element type can appear in any element's `directParents`.

> Other kinds of relations (dependencies, "blocked until", "similar to", "part
> of a meeting", …) are **not** `directParents` — they are `connections` (§5)
> and never affect inheritance.

### 2.1 The Parents list (linearization)

`Parents(E)` is the full, de-duplicated ancestor list, computed by a
**pre-order Depth-First Search** over `directParents` with a single global
visited set:

```
Parents(E):
    result = []           # E itself is NOT included
    visited = set()
    def dfs(x):
        for p in x.directParents:      # in listed order
            if p not in visited:
                visited.add(p)
                result.append(p)
                dfs(p)                 # fully expand p before its siblings
    dfs(E)
    return result
```

**Worked example** — `directParents`:

```
A: []      B: [A]      C: [A]      D: [B, A]      E: [C, D]
```

`Parents(E) = [C, A, D, B]`.

Trace: from `E`, take `C` → expand `C` → `A`; back to `E`, take `D` → expand `D`
→ `B` (`A` already visited, skipped). Note this is **branch-first**, not
breadth-first: `A` (reached through `C`) outranks the direct parent `D`. This is
intentional and is the agreed behavior.

### 2.2 MainParent

`MainParent(E) = Parents(E)[0]` — always the **first** entry of `directParents`.
It is the "the parent" in the tag-list mental model, and it is what auto- and
sub-elements pin (see §6, §8).

### 2.3 Cycles & missing refs

- A `directParents` entry pointing to a non-existent id is ignored (the
  validator warns).
- Cycles cannot loop forever (the visited set stops them) and are reported by
  the validator. A cycle does not corrupt resolution — it just truncates that
  branch.

---

## 3. Topic & AllTopic

### 3.1 Topic of an element

An element may reference several topics (several `topic`-typed entries anywhere
in its `Parents`). Exactly one of them is **the** `Topic` of the element:

> `Topic(E)` = the **first** element of type `topic` found in `Parents(E)`.

It may or may not be the `MainParent`. `Topic` is used for grouping and sorting
(tree views, stats, kanban rows/columns, …).

### 3.2 AllTopic (the root)

`AllTopic` is a single built-in topic that is the ancestor of every element:

- It is the parent of all top-level topics; through the topic chain it ends up
  in **every** element's `Parents`, always **last**.
- Any element with no topic in its `directParents` is treated as a direct child
  of `AllTopic`, so `Topic(E)` and inheritance **always** resolve.
- It carries the app-wide **defaults** (default attributes + default layout),
  which is why v4 has no separate `default` layer and no default-handling code.
- `AllTopic` itself has no parents; its `Topic` is itself.

---

## 4. Attributes

Attributes are name→value pairs. There are two things called "attribute":

1. **Attribute definitions** (the schema) — created by the user and stored in
   the database.
2. **Attribute values** — what an element actually sets, in its `attributes`
   bag.

### 4.1 Attribute definitions

A definition declares:

- **value type**: `string`, `number`, `int`, `bool`, `date`, `time`,
  `datetime`, `duration`, `enum` (with allowed values), `color`, `id-ref`
  (reference to an element), `list<…>`.
- **applies-to**: which element types may carry it (e.g. `status` → `task`
  only). This scoping is important: it means an attribute is only ever inherited
  from an ancestor of a compatible type, so no nonsensical cross-type leakage
  (a topic never has `status`, so a task never inherits `status` from a topic).
- **constraints**: min/max, allowed enum values, etc. (validator enforces).
- **layout** (optional): a static layout applied when the attribute is present.
  See §7.3. **DECISION:** the *conditional* form ("difficulty > 9 → red border")
  is deferred to a later version, as previously agreed; for v4 an attribute's
  layout is applied whenever the attribute is set, unconditionally. The
  resolution *slot* for attribute-layout exists now so the feature slots in
  later without reordering.

Attribute definitions are managed in a dedicated panel (§ "Attributes"
management, Part II).

### 4.2 Built-in attribute definitions

Always present, cannot be deleted (can be extended by user layout, etc.):

**All element types**

| Attribute | Type | Notes |
|---|---|---|
| `name` | string | Inheritable. |
| `description` | string | Inheritable. |
| `focus` | bool | Drives the Focus panel. **Not** inherited — set per element (§6.4). Default `false`. |
| `connections` | list | See §5. **Not inheritable.** |
| `cancelled` | bool | Hides the element / suppresses a generated occurrence from all normal views while keeping it in the DB. Default `false`. See §8.4. |

**Event** (type `event`)

| Attribute | Type | Notes |
|---|---|---|
| `start` | datetime | The instant the event begins. Required for a concrete event. |
| `end` | datetime | Optional. If absent or equal to `start`, the event is a point in time and no end is shown. |
| `duration` | duration | Optional alternative to `end`; if only `duration` is set, `end = start + duration`. If both set and they disagree, `end` wins (validator warns). |
| `location` | string | Free text. |
| `reminders` | list<duration> | Offsets relative to `start` (e.g. `-1d`, `-2h`). Each generates a virtual Reminder event (§8). |
| `class` | enum `normal`\|`reminder`\|`deadline` | Set automatically for auto-generated events; `normal` otherwise. |
| `timeSpent` | duration | Time used on this event. Falls back to `duration` when unset. Aggregated by the Effort panels. |

**Task** (type `task`)

| Attribute | Type | Notes |
|---|---|---|
| `status` | enum `not-started`\|`in-progress`\|`completed`\|`paused` | Workflow state. See §6.3 for roll-up. |
| `priority` | int 0–10 | 0 lowest, 10 highest. |
| `difficulty` | number 0–10 | |
| `deadline` | date | Optional. Generates a virtual Deadline event (§8). |
| `reminders` | list<duration> | Offsets relative to `deadline`. |
| `marked` | bool | Sub-task visibility toggle (§6.2). |
| `location` | string | Optional. |
| `timeSpent` | duration | Time used on this task. Aggregated by the Effort panels. |

> **DECISION** — task cancellation. To keep one mechanism, a task is *cancelled*
> by setting `cancelled: true` (universal, hides it), **not** by a `status`
> value. `status` therefore drops the `cancelled` entry the earlier draft had.
> If you'd rather keep `cancelled` in the workflow enum *and* have it stay
> visible, say so and I'll re-add it.

**Schedule** (type `schedule`) — see §6.5 for the full recurrence config.

### 4.3 What a Topic contributes

Topics rarely set type-specific attributes; they mostly set `name`,
`description`, `layout`, and shared attributes that then flow down to members.

---

## 5. Connections

`connections` is a built-in, **non-inheritable** attribute for relating any
element to any other element **without** affecting inheritance.

- A connection links element **A** to element **B** with an **open relation
  string** (e.g. `has`, `blocks`, `similar`, `follows`).
- **Two-way knowledge, one-way meaning.** Both A and B display the connection in
  their element panels, but the relation label has a *direction*: `A --has--> B`
  reads "A has B" on A's side and shows as an incoming `has` on B's side.
- **Informational only for v4.** Connections are displayed, navigable, and
  filterable; they never change another element's computed state (no auto-pause,
  no auto-status). Behavior may come in a later version.

**DECISION** — storage. A connection is stored **once**, on the source element:

```yaml
connections:
  - to: other-id
    relation: has        # open string
```

Direction is implicit (source → `to`). The app surfaces the reverse view on the
target automatically (shown as an incoming relation). Symmetric relations
(`similar`) simply read the same on both sides. This keeps the YAML free of
duplicated/desyncable entries while still making "both know each other" true in
the UI.

---

## 6. Element types

### 6.1 Topic

Organizational/classification element. Sub-topics are just topics whose
`MainParent` is another topic, giving the file-tree structure used across the
UI. Provides attributes and layout to descendants via inheritance.

### 6.2 Task — sub-tasks and `marked`

A **sub-task** is a task whose `MainParent` is another task (decomposition).
Sub-tasks inherit topic, attributes, and layout from the parent task like any
other child.

`marked` controls sub-task visibility to reduce clutter:

- A task with **no task-parent** (a top-level task) is always shown; its
  effective `marked` is treated as `true`.
- A **sub-task** defaults to `marked: false` and is then *ignored* by
  visualizations and stats — only its (marked) parent shows. The user marks the
  sub-tasks worth surfacing.
- **DECISION** — an unmarked sub-task does not count in stats/progress; a marked
  one does.

### 6.3 Task completion roll-up

**DECISION.** If a task has ≥1 **marked** sub-task, its completion is derived:

- progress = fraction of marked sub-tasks whose `status == completed`;
- `status` becomes `completed` automatically when all marked sub-tasks are
  completed, `in-progress` when some are, `not-started` when none are;
- a manually set `status` on such a parent is overridden by the roll-up.

If a task has no marked sub-tasks, its `status` is fully manual.

### 6.4 Focus

`focus` is set **explicitly per element and does not inherit** — focusing a topic
does not focus its descendants. Toggle it from an element's drawer or its
configuration panel; the Focus panel offers an "unfocus all". Default is `false`
everywhere (including `AllTopic`), so nothing is focused until you say so.

### 6.5 Event

Timing comes from `start` / `end` / `duration` (§4.2). A one-off event is just
an `event`; there is no "single-day / multi-day schedule" type — a date range is
expressed with `start` and `end`. Recurrence is never inline; it comes from a
Schedule element (§6.6).

Events may declare `reminders`; each produces a virtual Reminder event (§8).

### 6.6 Schedule (recurrence generator)

**Recurrence is expressed only through standalone Schedule elements.** A
Schedule is an element that **generates** events or tasks over a time window.

Config attributes:

| Attribute | Type | Notes |
|---|---|---|
| `generates` | enum `event`\|`task` | What kind of element each occurrence is. |
| `startDate` | date | Window start (inclusive). |
| `endDate` | date | Window end (inclusive). May be open-ended. |
| `kind` | enum `daily`\|`weekly`\|`monthly`\|`yearly` | Recurrence family. |
| `weekDays` | list<weekday> | For `weekly`. |
| `monthDays` | list<int 1–31> | For `monthly` (clamped to month end). |
| `yearlyDays` | list<{month, day}> | For `yearly`. |
| `time` | time | Optional time-of-day for generated **events**. If absent → "all-day". |
| `duration` | duration | Optional duration for generated events. |

**DECISION — the Schedule *is* the template.** Rather than a separate template
payload, every generated element pins the Schedule as its `MainParent`, so it
**inherits** `name`, `description`, attributes and `layout` straight from the
Schedule. The Schedule therefore carries the content of what it generates in its
own bag, plus the config above. To make a recurring lecture, you create one
`schedule` element named "Math 101 Lecture" with `generates: event`,
`kind: weekly`, `weekDays: [mon, wed]`, `time: 10:00`, `duration: 1h` — that's
the whole definition.

### 6.7 Auto-generated event classes

`reminder` and `deadline` are not distinct types — they are `event`s with
`class` set accordingly, produced by §8.

---

## 7. Inheritance & resolution

### 7.1 Attribute resolution

For each attribute of an element:

1. If the element sets it → use that value.
2. Otherwise walk `Parents(E)` in order and use the **first** parent that sets
   it (nearest-in-linearization wins).
3. Otherwise it is unset (falls through to `AllTopic`'s default, if any).

Values are single-valued and replace-whole (no per-key merge of a list value).
**Non-inheriting** attributes: `id` (not an attribute anyway) and `connections`.
Every other attribute inherits, naturally scoped by its *applies-to* type
(§4.1).

### 7.2 Layout resolution

`layout` resolves **per field** (background, border, icon, pin, shape,
animation, hoverAnimation, format) in this fallback order — first defined wins,
so the element's own value always takes precedence:

```
element's own  >  attribute-layout  >  Parents (in Parents order)
```

1. **Element** — the field set directly on the element's `layout`.
2. **Attribute-layout** — the layout bound to the first of the element's present
   attribute definitions that defines this field (§4.1; conditional logic
   deferred).
3. **Parents** — the first element in `Parents(E)` whose *resolved* layout
   defines this field. Because `MainParent` is `Parents[0]` and `Topic` is the
   first topic in `Parents`, both are covered here by their natural position —
   there is no separate MainParent step or Topic step.

This is the agreed simplification of the earlier five-step hierarchy. Notably,
attribute-driven layout now beats topic/parent layout (so danger/priority
styling wins over topic color).

---

## 8. Auto-elements (virtual → real)

Some elements are generated automatically. There are three **generators**:

| Generator | Produces | Class |
|---|---|---|
| Schedule | events or tasks, one per occurrence in its window | `normal` |
| A task's `deadline` | one event at the deadline date | `deadline` |
| An event's / task's `reminders` | one event per offset | `reminder` |

### 8.1 Virtual elements

- Are computed at load time inside the active time window; **never stored** in
  the YAML.
- Pin their generator as `MainParent` (forced `directParents[0]`), so they
  inherit name/description/attributes/layout from it and appear as sub-elements
  of it.
- Have a **deterministic id** so an edit can attach to the right one:
  - schedule occurrence: `"{schedule-id}#{ISO-date}"`
  - deadline: `"{task-id}#deadline"`
  - reminder: `"{host-id}#reminder-{offset}"`

### 8.2 Promotion (virtual → real)

When the user edits any field of a virtual element it becomes **real**:

- written to the YAML with its deterministic id and `directParents: [generator]`;
- only the **overridden** values are stored — everything else keeps inheriting
  from the generator;
- a real element with the same deterministic id **suppresses** the virtual one
  the generator would produce for that slot, so there is never a duplicate.

### 8.3 Orphans (**DECISION**)

If the generator later stops producing that slot (schedule window shrinks, a
weekday is removed, the deadline is deleted…), the promoted real element is kept
as a normal standalone element — user edits are never silently discarded. Its
`MainParent`→generator link remains, and the validator/UI flags it as
"detached from its generator" so the user can keep or delete it.

### 8.4 Cancelling / skipping an occurrence (**DECISION**)

To remove a single generated occurrence, promote it and set `cancelled: true`.
A cancelled element/occurrence is hidden from all normal views and excluded from
counts, but retained in the DB (so you have a record that "this lecture was
cancelled"). This is the uniform replacement for v3's sub-event cancel.

### 8.5 Cascade bound (**DECISION**)

A generated **task** may itself carry `deadline`/`reminders` (inherited from its
Schedule) and thus generate its own deadline/reminder events. To keep generation
finite:

- Schedules are never themselves generated.
- `deadline` and `reminder` events never generate further auto-elements.

So the cascade is at most: `Schedule → task → {deadline, reminder} events`.

---

## 9. Layout (visual model)

`layout` is a structured bag; every field is optional and, when unset, resolves
per §7.2.

| Field | Shape |
|---|---|
| `background` | color + optional second color (present ⇒ gradient) |
| `border` | color, width, style (`solid`/`dashed`/`dotted`) |
| `icon` | emoji or named icon |
| `pin` | color |
| `shape` | `rectangle`/`rounded_rectangle`/`ellipse`/`diamond` |
| `animation` | `none`/`beep`/`rumble` |
| `hoverAnimation` | `none`/`highlight`/`pulse` |
| `format` | font, size, color, text-align — applied by default this version |

### 9.1 Element views

Three render modes, chosen per panel/context:

- **Card view** — name + full information (dates, duration, attributes, icon).
  Cards resize to their content. Uses **all** layout fields.
- **Line view** — one line, name only, uniform size. Uses background, border,
  pin, animations. Hover shows the full card. Panels may add context to the line
  (e.g. the hour in a schedule panel).
- **Point view** — a dot/small block, no text, uniform size. Uses background,
  border, animations. Hover shows the full card.

---

## 10. Persistence (YAML, single file)

- The **database is one YAML file** (its path is shown/changeable in Main and
  Settings).
- **Reading** still supports the xyml `__file__` / `__ext__` includes for
  authoring convenience, so an existing multi-file document loads fine.
- **First UI save-back flattens** the (possibly multi-file) source into that one
  canonical file; from then on the app reads and writes a single file. Includes
  are thus a read-time import, not a persisted structure.
- Only **real** elements are persisted. Virtual auto-elements are never written
  unless promoted (§8.2).
- Attribute **definitions** and layout live in the same file.

### 10.1 File shape (illustrative)

```yaml
# database.yaml
attributes:                     # attribute DEFINITIONS (schema)
  difficulty:
    type: number
    min: 0
    max: 10
    applies_to: [task]
    layout: { border: { color: red } }   # applied when present (static, v4)

elements:                       # one flat list; `type` discriminates
  - id: AllTopic
    type: topic
    attributes: { name: "All" }
    layout: { background: { color: "#f5f5f5" } }

  - id: teaching
    type: topic
    directParents: [AllTopic]
    attributes: { name: "Teaching" }

  - id: math-101
    type: topic
    directParents: [teaching]
    attributes: { name: "Math 101" }

  - id: math-101-lecture
    type: schedule
    directParents: [math-101]
    attributes:
      name: "Math 101 Lecture"
      generates: event
      kind: weekly
      weekDays: [mon, wed]
      startDate: 2026-09-01
      endDate:   2026-12-20
      time: "10:00"
      duration: 1h

  - id: grade-midterm
    type: task
    directParents: [math-101]
    attributes:
      name: "Grade midterm"
      status: in-progress
      priority: 7
      deadline: 2026-10-25
      connections:
        - { to: midterm-exam, relation: follows }
```

---

# Part II — Panels

Panels are the tabs of the interface, listed in a **left-side menu** grouped by
category, categories separated by a divider. Panels can share components and be
interconnected across categories.

Categories:

- **Core** — control the app, stats, manage main information.
- **Topic** — topic management and topic-level stats.
- **Event** — time-related views.
- **Schedule** — recurrence views.
- **Task** — task views.

## Shared: Element management

A reusable layout used by every "… management" panel:

- **Left**: a collapsible **tree** of elements grouped by `Topic` (file-explorer
  style, honoring the topic hierarchy). Collapse-all / expand-all buttons.
- **Center**: the selected element's characteristics, editable — `name`,
  `description`, attributes, dates, etc. (fields vary by element type).
  Collapsible. Includes the element's **connections** list (both directions,
  §5), navigable.
- **Below**: a collapsible **layout** block, editable.

Each type's management panel (Topic / Event / Task / Schedule management) is this
shared component scoped to that type.

## Core panels

### Main

- Shows the current **database file** path with a button to change it.
- Two columns:
  1. **Upcoming events** — line-view list of the most immediate events.
  2. A stacked pair:
     - **Upcoming deadlines** — the most immediate tasks that have a deadline.
     - **Priority tasks** — the most immediate tasks *without* a deadline,
       ordered by `priority`.

### Attributes (definitions)

Manage **attribute definitions** (§4.1): create/edit/delete user attributes,
set value type, applies-to element types, constraints, and the (static) layout
binding. Built-in definitions are shown read-only.

### Stats

- First row: counts of topics, events, tasks, schedules.
- Then stat panels, each a **topic tree view** (main topic, sub-topics
  collapsible; collapse-all / expand-all):
  - **Elements by topic** (split into tasks / events / schedules)
  - **Completion progress by topic**
  - **Planned time by topic** — **DECISION:** since there is no time-tracking,
    "time" = the sum of `duration` of the topic's events (including generated
    occurrences) within the selected window. Labeled "planned time" to avoid
    implying tracked actuals.
- Layout: two panels share a row, the third on its own row; all collapsible.

### Settings

- Set the database file path.
- Appearance / theme.
- General: font, font-size, density/compactness, etc.

### Focus

Shows only elements whose effective `focus` is `true` (§6.4), laid out like Main.

## Topic panels

### Graph

Topic visualization with two views: **tree** and **graph** (in graph, sub-topics
are nested inside their parent). Each topic shows toggleable stats: number of
events, tasks, sub-topics, schedules.

### Time elapsed

Topic file-tree view of stats: elapsed time (sum of durations of the topic's
**past** events), number of events, number of tasks, etc.

### Topic management

Element management scoped to topics. Because topics *are* the tree, the left
column is the topic hierarchy itself; selecting a node edits that topic. The
centre focuses on what a topic contributes to its descendants — `name`,
`description`, default attributes, and layout — plus **reparenting** via
`directParents`. A **members** summary shows how many tasks / events / schedules
/ sub-topics resolve to this topic, and new-topic creation lives here.

## Event panels

### Calendar

Calendar of events, styled by layout. View selector: day / week / month / year.
Forward / backward / today buttons. Element views: line and point.

### Agenda

Paper-agenda week: Monday–Wednesday on the left, Thursday–Sunday on the right
(weekend stacked in two columns on the right). Shows day numbers and events. All
element views available.

### Timeline

Events as points on a line. Linear or logarithmic scale. Zoomable (zoom decides
whether to show hours / days / months). Hover shows the element card below.

### Event management

Element management scoped to events. The centre leads with **timing** — `start`
(date + time), `end` or `duration`, `location` — and the `reminders` list, with a
**preview** of the reminder occurrences those offsets will generate. Editing a
promoted schedule occurrence shows that it overrides a single date of its
generating schedule; setting `cancelled` skips that occurrence.

## Schedule panels

### Timeboard

Schedules in a timeline view, showing the events/tasks they generate. Month /
week / day view. Shows **only** schedule elements and their generated elements —
a view to organize a generic month/week/day rather than to inspect individual
occurrences. Because different periods run different schedules (semester 1 vs 2),
it allows date selection like the Calendar.

### Effort

Time used per topic. **One panel with two blocks that share the same controls:**

- **Time used by topic** — a collapsible tree; each topic shows a bar split into
  **event time** (mint) and **task time** (lavender). A subtopic's time rolls up
  into its parent.
- **Topics ranked by time used** — the same numbers as a leaderboard.

Shared controls (apply to both blocks):

- **Metric** — total / events / tasks.
- **Scope** — *with subtopics* (rolled up) or *own only* (elements directly in
  the topic, not those under subtopics).
- **Period** — the time window. Default **from the beginning up to today**;
  presets (all time, this/last/next week, this/last/next month) plus editable
  start/end date fields (empty start = the beginning). This lets you ask "how
  much did I work last week" or "how much does my plan say for next week".

Time per element is its `timeSpent` (events fall back to their `duration`); an
element counts toward a period when its anchor date — an event's `start` or a
task's `deadline` — falls in the window. Computed server-side by `/api/effort`.

### Schedule management

Element management scoped to schedules. The centre is the recurrence editor:
`generates` (event/task), `kind` and the matching day fields
(`weekDays`/`monthDays`/`yearlyDays`), the `[startDate, endDate]` window, and
`time`/`duration`. Because the schedule *is* the template, its `name`,
`description`, attributes and layout are what every occurrence inherits. A **live
preview** lists the next generated occurrences so the effect of a change is
immediately visible (the full month/week picture lives in the Timeboard).

## Task panels

### Taskboard

Kanban for tasks. Columns and rows are configurable filters: `Topic`, attributes
(`status`, `priority`, `difficulty`, …), dates (deadline sort). Dragging a task
between cells changes the corresponding attribute (only mutable attributes, not
structural ones like `Topic`).

### Task management

Element management scoped to tasks. The centre exposes `status`, `priority`,
`difficulty`, `deadline`, `reminders`, and `marked`. When the task has subtasks
it shows the **subtask tree** with each child's `marked`/`status` and the derived
completion roll-up (a parent completes when all *marked* subtasks are complete).
Connections (e.g. `blocks`, `requires`) are listed both directions.
