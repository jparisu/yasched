# Design: Task Relations & Layout System v2

## Motivation

Three limitations in v1 needed addressing:

1. **Tasks had a single topic** — real work often spans multiple topics.
2. **Task dependencies were a single type** (`blocked_by`) — relations between tasks carry richer semantics.
3. **Layouts were monolithic** — a single `background` field prevented independent layers from different sources (topic, parent, task) from composing naturally.

---

## 1. Multiple Topics per Task

### Model change

```
Task.topic_id: str | None   →   Task.topic_ids: list[str]
```

YAML accepts a single string or a list:

```yaml
tasks:
  - id: deploy
    topics: [backend, devops]  # multiple topics
  - id: write_report
    topics: research            # single string shorthand
```

### Resolution

`effective_tags` = union of all assigned topics' tags (in `topic_ids` order).
`effective_layout` base = topics' layouts stacked in `topic_ids` order (last topic = lowest among them, see §3).

If `topic_ids` is empty and the task has no parent, the `__default__` synthetic topic is used.

---

## 2. Task Relations

Replaces `blocked_by: list[BlockedBy]` with a general `relations: list[TaskRelation]`.

### Types

```python
class RelationType(enum.Enum):
    REQUIRES  = "requires"    # hard dependency; source is BLOCKED until done
    NEEDS     = "needs"       # soft dependency; informational
    CONNECTED = "connected"   # related work, no ordering semantics
    SIMILAR   = "similar"     # same kind of task, no ordering semantics
```

`RelationType` is an `Enum` — new relation types can be added by extending it.

### YAML

```yaml
tasks:
  - id: deploy
    relations:
      - task: write_tests
        type: requires
        description: Tests must pass before deploy
      - task: write_docs
        type: needs
      - task: deploy_staging
        type: similar
```

Shorthand (string) defaults to `connected`:

```yaml
relations:
  - task: another_task   # type defaults to "connected"
```

### Resolution

`ResolvedTask.related_tasks: list[ResolvedTaskRelation]` holds all resolved relations.
`ResolvedTask.blocking_tasks` is a computed property returning tasks with `type == REQUIRES`.

---

## 3. Layout System v2

### Background as abstract class

`BackgroundStyle` becomes an abstract base class. Concrete subclasses represent distinct visual layers that can coexist independently:

| Subclass | YAML `type` | Fields | Meaning |
|---|---|---|---|
| `SolidBackground` | `solid` | `color` | Flat fill |
| `GradientTopRightBackground` | `gradient_tr` | `color` | Gradient anchor at top-right corner |
| `GradientBottomLeftBackground` | `gradient_bl` | `color` | Gradient anchor at bottom-left corner |

Since each subclass is a distinct type, one layer can provide the `gradient_tr` color while another independently provides `gradient_bl` — they compose without conflict.

### New layout fields

```python
@dataclass(frozen=True)
class ShapeStyle:
    type: str           # "rectangle" | "rounded" | "pill" | "trapezoid"
    radius: str | None  # e.g. "8px" (for "rounded")

@dataclass(frozen=True)
class PinStyle:
    color: Color
    icon: str | None    # emoji or icon name shown as a map pin
```

`Layout` gains `shape` and `pin` fields; `background: BackgroundStyle | None` becomes `backgrounds: list[BackgroundStyle]`.

### YAML

Single background (shorthand, still works):

```yaml
background:
  type: solid
  color: "#4A90D9"
```

Multiple background layers in one layout definition:

```yaml
background:
  - type: gradient_tr
    color: "#FF5500"
  - type: gradient_bl
    color: "#0055FF"
```

Shape and pin:

```yaml
shape:
  type: rounded
  radius: 8px

pin:
  color: red
  icon: "📌"
```

### Layout layer resolution order

From lowest to highest priority:

```
default_layout  <  topic layouts (topic_ids order)  <  parent layout  <  own layout
```

- **`default_layout`** is an optional database-level layout that fills in any field not set by higher layers. Defined via a top-level `default_layout:` key in YAML.
- **Topic layouts**: stacked in `topic_ids` declaration order; last topic in the list has highest priority among topics.
- **Parent layout**: the resolved parent task's `effective_layout`.
- **Own layout**: the layout declared directly on the entity (highest priority).

### Merge rules per field

| Field | Merge rule |
|---|---|
| `backgrounds` | Group by concrete type; higher-priority layer replaces same type; different types coexist |
| `border` | Higher-priority wins (replace whole border) |
| `icon` | Higher-priority wins |
| `shape` | Higher-priority wins |
| `pin` | Higher-priority wins |

### Example: diagonal gradient from two sources

```yaml
topics:
  - id: work
    layout:
      background:
        type: gradient_bl
        color: "#4A90D9"       # topic provides bottom-left anchor

tasks:
  - id: big_task
    topics: [work]
    layout:
      background:
        type: gradient_tr
        color: "#F5A623"       # task provides top-right anchor
      border:
        type: solid
        width: 2px
        color: gray
```

`effective_layout.backgrounds` = `[GradientBottomLeftBackground(#4A90D9), GradientTopRightBackground(#F5A623)]`

---

## 4. Affected files

| File | Change |
|---|---|
| `coring/Layout.py` | Abstract `BackgroundStyle`; `SolidBackground`, `GradientTopRightBackground`, `GradientBottomLeftBackground`; add `ShapeStyle`, `PinStyle`; `Layout.backgrounds: list` |
| `coring/_shared.py` | Add `RelationType`, `TaskRelation`; remove `BlockedBy` |
| `coring/Task.py` | `topic_ids: list[str]`; `relations: list[TaskRelation]`; remove `topic_id`, `blocked_by` |
| `backending/Database.py` | `ResolvedTask.topics: list[ResolvedTopic]`; `ResolvedTask.related_tasks: list[ResolvedTaskRelation]`; add `ResolvedTaskRelation`; `Database.default_layout` |
| `backending/loading/DatabaseParser.py` | Parse `topics`, `relations`, `backgrounds`, `shape`, `pin`, `default_layout` |
| `backending/loading/DatabaseSerializer.py` | Serialize same |
| `backending/managing/DatabaseManager.py` | `_merge_layouts`; updated validate + resolve |
