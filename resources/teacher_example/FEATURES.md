# Teacher example — feature coverage checklist

This example is the v3.0 regression fixture. Entry point: `teacher_main.yaml`.
Each row is a capability to verify once the code is implemented, with where it lives.

## xyml loader

| Capability | Where |
|---|---|
| `__file__` include (REPLACE) | `teacher_main.yaml` → traits / topics / events / tasks |
| `__ext__` include (EXTEND) with sibling overrides | `teacher_events.yaml` → `math101-lecture-cancel` |
| Inline + included sections mixed | `teacher_main.yaml` (`default` inline, rest included) |

## Top-level layers

| Capability | Where |
|---|---|
| `default` layer (attributes + layout) | `teacher_main.yaml` |
| `traits` registry | `teacher_traits.yaml` |
| `topics` / `events` / `tasks` collections | respective files |

## Traits

| Capability | Where |
|---|---|
| attributes-only trait | `easy`, `focus`, `backlog` |
| layout-only trait (== named layout) | `exam-style`, `recurring-style` |
| attributes + layout trait | `hard`, `high-priority` |
| multiple traits on one element (ordered) | `make-slides` [hard, focus]; `grade-midterm` [high-priority, focus] |

## Topic

| Capability | Where |
|---|---|
| root topic | `teaching`, `research`, `admin`, `personal` |
| single parent (`parent_ids`) | `math-101`, `math-201` |
| **multiple parents (DAG)** | `thesis-supervision` [teaching, research] |
| tags inherited + union | `math-101` [work,undergrad]; `personal` isolated (no `work`) |
| attributes | `teaching.color-group` |
| layout | gradient anchors on `teaching` + `math-101` |

## Event

| Capability | Where |
|---|---|
| single topic | `math101-lecture` |
| **multiple topics** | `dept-seminar` [research, teaching] |
| schedule: weekly (duration) | `math101-lecture` |
| schedule: weekly (end_time) | `office-hours` |
| schedule: monthly | `faculty-meeting` |
| schedule: yearly (with time) | — (see all-day below) |
| schedule: yearly (all-day) | `academic-year-start`, `birthday` |
| schedule: single_day | `midterm-exam`, sub-events |
| schedule: multi_day | `research-conference` |
| **sub-event override** (parent_id) | `math101-lecture-move` |
| **sub-event via `__ext__`** | `math101-lecture-cancel` |
| blocking_level (attribute) | `midterm-exam` |
| location (attribute) | `math101-lecture`, `research-conference` |
| traits on event | `midterm-exam`, `faculty-meeting` |
| inline layout on event | `birthday` |
| tags on event (union) | `birthday` [celebration], cancelled events |

## Task

| Capability | Where |
|---|---|
| single topic | most tasks |
| **multiple topics (ordered)** | `submit-grades` [math-101, admin] |
| **subtask decomposition** (parent_id) | `write-syllabus`, `make-slides`, `prepare-exercises` |
| topic inherited from parent task | the three subtasks (no own `topic_ids`) |
| recurring task (`schedules`) | `grade-weekly-quizzes` |
| deadline / priority / status attributes | `grade-midterm`, `submit-grades`, ... |
| effort (min/max) | `write-syllabus`, `make-slides`, `write-paper` |
| difficulty via trait / kanban via trait | `make-slides`, `grade-weekly-quizzes` |
| **arbitrary open attribute** | `write-paper.reviewer` |
| relation: requires | `grade-midterm`, `submit-grades` |
| relation: needs | `grade-midterm` |
| relation: connected | `write-paper` |
| relation: similar | `write-paper` |
| **relation shorthand (bare string)** | `renew-contract` |
| event_link: use_as_deadline + as_context | `grade-midterm` |
| event_link: as_context only | `renew-contract` |
| inline layout on task | `prepare-math101` |
| tags union | `write-paper` [work, writing] |

## Resolution / merge engine (verify computed effective values)

| Rule | Check |
|---|---|
| precedence `default < topic(s) < traits < parent < own` | `grade-midterm` priority: default 1 → trait `high-priority` 5 (wins) |
| attributes replace-by-key | `submit-grades` priority 4 (own) beats default 1 |
| tags **union** across layers | `make-slides` → work + undergrad + prep (parent) |
| layout backgrounds **compose by type** | `midterm-exam`: teaching `gradient_bl` + math-101 `gradient_tr` + trait solid |
| layout non-background **replace** | shape from `default`, border from `hard`, icon from trait/own |

## Value formats exercised

| Type | Values |
|---|---|
| Color | hex `#3b82f6`, named `red` |
| Duration | `30m`, `1h`, `1d`, `3w`, `90m` |
| Date | `2026-10-20` (ISO) |
| Time | `10:00`, `17:00` (HH:MM) |
