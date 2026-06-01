# API Layer Design

## What Already Exists (nothing needs to change)

| Component | Status | Notes |
|---|---|---|
| `DatabaseInterface` | Complete | Rich read-only query API |
| `DatabaseLoader.load()` | Complete | YAML → `Database` |
| **`DatabaseLoader.save()`** | **Complete** | `Database` → YAML on disk |
| `DatabaseSerializer.to_yaml()` | Complete | Full serialization of all types |
| `DatabaseManager.validate()` | Complete | Returns list of `ConsistencyError` |
| `DatabaseManager.resolve()` | Complete | `Database` → `ResolvedDatabase` |

The library already has a complete load/save round-trip. The API layer wraps it.

---

## Resolved Decisions

### Duration serialization
Use `str(duration)` → `"1h30m"` (same format as YAML input). Parses back with `Duration.from_string()`. Clean round-trip, no unit ambiguity. Do NOT use unix time (that is an absolute timestamp; Duration is a relative span).

### Color serialization
Use `color.to_hex()` → `"#ff5733"`. Already used internally by `DatabaseSerializer`. Standard web format.

### DB loading
Load once at startup. State held in memory. File-watch can be added later without changing the API contract.

### Write support
Full create/update/delete for tasks, events, and topics.

---

## Serialization Reference

| Python type | JSON representation | How |
|---|---|---|
| `datetime.date` | `"2026-06-01"` | `.isoformat()` — native Pydantic |
| `datetime.time` | `"14:30:00"` | `.isoformat()` — native Pydantic |
| `Duration` | `"1h30m"` | `str(duration)` / `Duration.from_string()` |
| `Color` | `"#ff5733"` | `color.to_hex()` |
| `TaskStatus` | `"todo"` | `.value` |
| `RelationType` | `"requires"` | `.value` |
| `Weekday` | `"monday"` | `.value` |
| `Schedule` | discriminated union on `type` field | see below |
| `BackgroundStyle` | discriminated union on `type` field | see below |
| Circular refs (`children`, `parent`) | IDs only | `children_ids: list[str]`, `parent_id: str \| None` |

### Schedule discriminated union

Six concrete types, distinguished by `type` field in the JSON schema:

| `type` value | Class | Key fields |
|---|---|---|
| `"single_day"` | `SingleDaySchedule` | `day`, `start_time?`, `duration?` |
| `"multi_day"` | `MultiDaySchedule` | `start_day`, `end_day` |
| `"weekly"` | `WeeklySchedule` | `appointments[]`, `start_date?`, `end_date?` |
| `"monthly"` | `MonthlySchedule` | `day_of_month`, `start_time`, `duration`, `start_date?`, `end_date?` |
| `"yearly"` | `YearlySchedule` | `month`, `day` |

`SingleDaySchedule` and `MultiDaySchedule` have no `type` field in YAML, but the API always includes one for unambiguous JSON discriminators.

### BackgroundStyle discriminated union

| `type` value | Class |
|---|---|
| `"solid"` | `SolidBackground` |
| `"gradient_tr"` | `GradientTopRightBackground` |
| `"gradient_bl"` | `GradientBottomLeftBackground` |

---

## Write Architecture

### The key insight

The `Database` (raw, unresolved) is the mutable source of truth. All write operations:
1. Mutate the `Database` (creating new frozen dataclass instances — they are `frozen=True`)
2. Run `DatabaseManager.resolve()` — this validates AND resolves in one call
3. If validation passes: `DatabaseLoader.save()` to disk, update in-memory state
4. If validation fails: return `422 Unprocessable Entity` with the `ConsistencyError` details

This means **the YAML file on disk is always valid** — invalid writes are rejected before saving.

### Warning: `__ext__` consolidation

`DatabaseLoader.save()` writes a single consolidated YAML file. If the user loaded from a multi-file database (main file + `__ext__` sub-files), the first write consolidates everything into one file. This is a known limitation. Document it clearly in the API docs.

### Server state

```python
@dataclass
class AppState:
    db_path: Path
    raw_db: Database           # mutable source of truth for writes
    interface: DatabaseInterface  # over the current resolved state
```

On startup:
```
raw_db = DatabaseLoader.load(db_path)          # YAML → Database
resolved = DatabaseManager.resolve(raw_db)     # validate + resolve
interface = DatabaseInterface(resolved)
```

On every write:
```
new_raw_db = <mutated copy of raw_db>
resolved = DatabaseManager.resolve(new_raw_db)  # raises ConsistencyError if invalid
DatabaseLoader.save(new_raw_db, db_path)
state.raw_db = new_raw_db
state.interface = DatabaseInterface(resolved)
```

Since `Database` fields use `frozen=True` dataclasses, mutations are copies:
```python
from dataclasses import replace

# Replace one task
new_tasks = [t if t.id != updated.id else updated for t in state.raw_db.tasks]
new_raw_db = replace(state.raw_db, tasks=new_tasks)
```

---

## Package Structure

```
apps/api/
  __init__.py
  main.py          # FastAPI app, lifespan (load DB on startup), CORS
  config.py        # env vars: YASCHED_DB_PATH, YASCHED_CORS_ORIGINS
  state.py         # AppState dataclass + get_state() FastAPI dependency
  schemas/
    __init__.py
    common.py      # ColorStr, DurationStr, LayoutSchema, ScheduleSchema (union)
    task.py        # TaskSchema (read), TaskWriteSchema (create/update)
    event.py       # EventSchema, EventWriteSchema
    topic.py       # TopicSchema, TopicWriteSchema
    views.py       # DailyViewSchema, WeeklyViewSchema, EventConflictSchema
    summary.py     # HealthSchema, StatusSummarySchema
  routers/
    __init__.py
    health.py      # GET /health
    tasks.py       # GET + POST + PATCH + DELETE /tasks
    events.py      # GET + POST + PATCH + DELETE /events
    topics.py      # GET + POST + PATCH + DELETE /topics
    schedule.py    # GET /schedule/daily|weekly|range|conflicts
    checks.py      # GET /checks/stale-links|stale-blocks
```

---

## Endpoints

### Health
```
GET  /health
→ { db_loaded, task_count, event_count, topic_count, status_summary, errors[] }
```

### Tasks
```
GET    /tasks                                   → list[TaskSchema]
GET    /tasks/{id}                              → TaskSchema
POST   /tasks                                   → TaskSchema          (create)
PATCH  /tasks/{id}                              → TaskSchema          (update)
DELETE /tasks/{id}                              → 204

GET    /tasks/{id}/children                     → list[TaskSchema]
GET    /tasks/{id}/subtree                      → list[TaskSchema]
GET    /tasks/{id}/events                       → list[EventSchema]
GET    /tasks/{id}/blocking                     → list[TaskSchema]

# Query params on GET /tasks
?status=todo|in_progress|done|cancelled|blocked
?topic_id=xxx[&include_subtopics=true]
?tag=xxx
?search=query
?min_priority=1&max_priority=5

# Special read-only derived lists
GET    /tasks/deadlines?days_ahead=7            → list[TaskSchema]
GET    /tasks/overdue                           → list[TaskSchema]
GET    /tasks/blocked                           → list[TaskSchema]
```

### Events
```
GET    /events                                  → list[EventSchema]
GET    /events/{id}                             → EventSchema
POST   /events                                  → EventSchema
PATCH  /events/{id}                             → EventSchema
DELETE /events/{id}                             → 204

# Query params
?start=2026-06-01&end=2026-06-30
```

### Topics
```
GET    /topics                                  → list[TopicSchema]
GET    /topics/{id}                             → TopicSchema
POST   /topics                                  → TopicSchema
PATCH  /topics/{id}                             → TopicSchema
DELETE /topics/{id}                             → 204

GET    /topics/roots                            → list[TopicSchema]
GET    /topics/{id}/children                    → list[TopicSchema]
GET    /topics/{id}/subtree                     → list[TopicSchema]
GET    /topics/{id}/ancestors                   → list[TopicSchema]
GET    /topics/{id}/tasks                       → list[TaskSchema]

?tag=xxx
?search=query
```

### Schedule
```
GET  /schedule/daily?date=2026-06-01            → DailyViewSchema
GET  /schedule/weekly?week_start=2026-06-01     → WeeklyViewSchema
GET  /schedule/range?start=…&end=…             → list[DailyViewSchema]
GET  /schedule/conflicts?start=…&end=…         → list[EventConflictSchema]
```

### Checks
```
GET  /checks/stale-links                        → list[TaskSchema]
GET  /checks/stale-blocks                       → list[TaskSchema]
```

---

## Error handling

| Situation | HTTP status | Body |
|---|---|---|
| Entity not found | 404 | `{ detail: "task 'xyz' not found" }` |
| Write fails validation | 422 | `{ detail: [{ type, entity, field, message }] }` |
| DB not loaded | 503 | `{ detail: "database not available" }` |

FastAPI generates `422` natively for Pydantic validation. `ConsistencyError` from `DatabaseManager.resolve()` maps to a custom 422 handler.

---

## Configuration (env vars)

| Var | Default | Description |
|---|---|---|
| `YASCHED_DB_PATH` | required | Path to the YAML database file |
| `YASCHED_CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins (comma-separated) |

---

## New dependencies

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
api = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.34.0",
  "pydantic>=2.0.0",
]
```

Install with: `pip install -e ".[api]"`
Run with: `YASCHED_DB_PATH=./data/db.yaml uvicorn apps.api.main:app --reload`
