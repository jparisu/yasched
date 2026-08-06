# Agenda format

An agenda is a YAML document with two optional top-level keys: `attributes`
(the attribute *schema*) and `elements` (a flat list; every element has an `id`
and a `type`).

```yaml
attributes:                 # optional: user-defined attribute definitions
  difficulty:
    type: number
    applies_to: [task]
    min: 0
    max: 10
  danger:                   # a definition may carry a static layout
    type: bool
    applies_to: [task, event]
    layout: { border: { color: "#ef4444", width: 2px } }

elements:
  # AllTopic is the built-in root; customize it to set app-wide defaults.
  - id: AllTopic
    type: topic
    attributes: { name: All, priority: 3 }
    layout: { shape: rounded_rectangle, background: { color: "#f4f4f5" } }

  - id: work
    type: topic
    directParents: [AllTopic]
    attributes: { name: Work }
    layout: { background: { color: "#3b82f6" } }

  - id: standup                       # a recurring event via a Schedule
    type: schedule
    directParents: [work]
    attributes:
      name: Daily standup
      generates: event
      kind: weekly
      weekDays: [mon, tue, wed, thu, fri]
      time: "09:00"
      duration: 15m

  - id: report
    type: task
    directParents: [work]
    attributes:
      name: Quarterly report
      status: in-progress
      priority: 5
      difficulty: 6
      deadline: "2026-10-30"
      reminders: ["1w", "1d"]
      connections:
        - { to: standup, relation: follows }
```

## Elements

Only `id` and `type` are structural. `directParents` is the ordered inheritance
list (first = MainParent). Everything else — `name`, `description`, dates,
`status`, `connections`, … — lives in `attributes`. `name` and `description` may
also be given at the top level of an element as a convenience; they are folded
into `attributes`.

## Built-in attributes

Always available (per element type):

| Attribute | Type | Types |
|---|---|---|
| `name`, `description` | string | all |
| `focus` | bool | all — surfaces the element in the Focus panel. Set explicitly per element (does **not** inherit) |
| `cancelled` | bool | all — hides the element / suppresses a generated occurrence |
| `connections` | list | all (never inherits) |
| `start`, `end`, `duration`, `location`, `reminders`, `class`, `timeSpent` | — | event |
| `status`, `priority`, `difficulty`, `deadline`, `reminders`, `marked`, `timeSpent` | — | task |
| `timeSpent` | duration | event, task — time used, aggregated by the Effort panels (events fall back to `duration`) |
| `generates`, `kind`, `startDate`, `endDate`, `weekDays`, `monthDays`, `yearlyDays`, `time`, `duration` | — | schedule |

## Value formats

| Type | Examples |
|---|---|
| Color | `#3b82f6` (hex) or a name like `red` |
| Duration | `30m`, `1h`, `1d`, `2w`, `1h30m` |
| Date | `2026-10-20` (ISO), also `today` / `tomorrow` |
| Time | `10:00`, `17:30` (24-hour) |
| Datetime | `2026-10-20T10:00` (event `start`/`end`) |

## Layout

```yaml
layout:
  background: { color: "#3b82f6", gradient_color: "#1e3a8a" }  # 2nd color ⇒ gradient
  border:     { color: red, width: 2px, style: dashed }        # solid | dashed | dotted
  icon:       { type: emoji, value: "📝" }
  pin:        { color: red }
  shape:      rounded_rectangle    # rectangle | rounded_rectangle | ellipse | diamond
  animation:  beep                 # none | beep | rumble
  hover_animation: pulse           # none | highlight | pulse
```

Every field is optional and independently inherited.

## Schedules

A `schedule` element generates events or tasks over its window:

```yaml
- id: lecture
  type: schedule
  directParents: [math-101]
  attributes:
    name: "Math 101 Lecture"
    generates: event            # event | task
    kind: weekly                # daily | weekly | monthly | yearly
    weekDays: [mon, wed]        # weekly
    # monthDays: [1, 15]        # monthly (clamped to month end)
    # yearlyDays: [{month: 6, day: 15}]   # yearly
    startDate: 2026-09-01
    endDate: 2026-12-18
    time: "10:00"               # omit for an all-day occurrence
    duration: 1h
```

## Connections

```yaml
connections:
  - { to: other-element, relation: follows }   # open label; shown on both ends
  - depends-on-me                               # shorthand string → relation "related"
```

## Splitting files (xyml)

Split an agenda across files with `__file__` (splice in place) and `__ext__`
(extend a base with overrides). These are a **read-time** convenience — the first
time you save from the app, the whole agenda is flattened into the single file.

```yaml
# main.yaml
elements:
  __file__: elements.yaml       # elements.yaml contains the list
```

For a complete, working example that uses every feature, see
[`resources/example_v4/agenda.yaml`](https://github.com/jparisu/yasched) in the
repository.
