# Agenda format

An agenda is a YAML document with up to five top-level keys. All are optional.

```yaml
default:            # lowest-priority layer
  attributes: { priority: 3, status: todo }
  layout:
    shape: { type: rounded, radius: 6px }

traits:             # reusable named bundles
  urgent:
    attributes: { priority: 5 }
    layout: { pin: { color: red, icon: "🔥" } }

topics:
  - id: work
    name: Work
    tags: [work]
    parent_ids: []          # DAG; a topic may list several parents
    layout: { background: { type: solid, color: "#3b82f6" } }

events:
  - id: standup
    name: Daily standup
    topic_ids: [work]
    schedules:
      - { type: weekly, week_days: [monday, wednesday, friday],
          start_time: "09:00", duration: 15m }

tasks:
  - id: report
    name: Quarterly report
    topic_ids: [work]
    traits: [urgent]
    attributes: { deadline: "2026-10-30", priority: 5 }
    relations:
      - { task: gather-data, type: requires }
    event_links:
      - { event: standup, as_context: true }
```

## Value formats

| Type | Examples |
|---|---|
| Color | `#3b82f6` (hex) or a name like `red` |
| Duration | `30m`, `1h`, `1d`, `2w`, `1h30m` |
| Date | `2026-10-20` (ISO), also `today` / `tomorrow` |
| Time | `10:00`, `17:30` (24-hour) |

## Layout

```yaml
layout:
  background:                 # one entry, or a list of layers
    - { type: gradient_bl, color: "#3b82f6" }
    - { type: gradient_tr, color: "#f59e0b" }   # composes with the above
  border: { type: solid, width: 2px, color: red }
  icon:   { type: emoji, value: "📝" }
  pin:    { color: red, icon: "🔥" }
  shape:  { type: rounded, radius: 8px }
```

Background `type`s (`solid`, `gradient_tr`, `gradient_bl`) compose when they
differ and replace when they match a higher layer.

## Relations & event links

```yaml
relations:
  - { task: other, type: requires }     # requires | needs | connected | similar
  - other-task                          # shorthand string → connected

event_links:
  - { event: exam, use_as_deadline: true, as_context: true }
```

## Splitting files (xyml)

Use `__file__` to splice a file in place, and `__ext__` to extend a base file
with overrides:

```yaml
# main.yaml
topics:
  __file__: topics.yaml          # topics.yaml contains the list

events:
  - __ext__: cancel_template.yaml # merge a shared base…
    id: lecture-cancelled         # …then override/extend with these keys
    parent_id: lecture
    schedules: [{ type: single_day, day: "2026-09-23" }]
```

For a complete, working example that uses every feature, see
`resources/teacher_example/` in the repository.
