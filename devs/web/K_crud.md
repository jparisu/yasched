# K — Create / Edit / Delete (CRUD)

Applies to Topics, Events, and Tasks. Layouts are covered in G3.
All write operations are blocked when Read-only mode (I5) is ON.

---

## K1 · Interaction Patterns

### Edit existing entity
- The detail drawer (used across Tasks, Calendar, Topics, Graph pages) has an
  **Edit button** in its header.
- Clicking Edit switches the drawer to **edit mode**: fields become form inputs,
  a Save button and a Cancel button appear at the bottom.
- Cancel reverts the drawer to read-only view with no changes applied.
- Save writes to the YAML file and reloads the database (see K4).

### Create new entity
- Each page that owns an entity type has a **"+ New [Entity]"** button
  (e.g. "+ New Task" on the Tasks page, "+ New Event" on the Calendar page,
  "+ New Topic" on the Topics page).
- Clicking it opens a **creation dialog** (modal) specific to that entity type.
- The dialog contains a full form for all required and optional fields.
- Confirm creates the entity and writes to YAML; Cancel discards without saving.

### Delete entity
- Available only in **edit mode** inside the drawer (not from the creation dialog).
- A **Delete button** (visually distinct, e.g. red / destructive style) appears
  at the bottom of the edit drawer.
- Clicking Delete shows an **inline confirmation prompt** within the drawer:
  "Are you sure? This cannot be undone."
  If the entity is referenced by others (e.g. a topic with tasks, a task with
  children or blockers), the prompt also lists the affected references as a warning.
- Confirmed delete removes the entity from the YAML and reloads.

---

## K2 · Topic Form Fields

| Field | Type | Notes |
|---|---|---|
| id | text input | Required. Must be unique. Immutable after creation (warn if changed). |
| name | text input | Required. |
| description | textarea | Optional. |
| tags | tag input (add/remove) | Optional. |
| parent_ids | multi-select (existing topics) | Optional. Defines DAG parents. |
| layout | select (existing layouts) or none | Optional. |

**Delete warnings:** list all tasks and events that belong to this topic.

---

## K3 · Event Form Fields

| Field | Type | Notes |
|---|---|---|
| id | text input | Required. Unique. |
| name | text input | Required. |
| description | textarea | Optional. |
| location | text input | Optional. |
| topic | select (existing topics) | Required. |
| layout | select (existing layouts) or none | Optional. |
| blocking_level | number input | Optional. |
| schedules | schedule builder (see below) | At least one required. |

**Schedule builder:** supports all schedule types, multiple schedules per event.
- Type selector per schedule entry: Single-day / Multi-day / Weekly / Monthly / Yearly.
- **Single-day:** date picker.
- **Multi-day:** start date + end date pickers.
- **Weekly:** weekday multi-select + start time + end time or duration +
  optional start/end date range for the recurrence.
- **Monthly:** day-of-month number + optional start/end date range.
- **Yearly:** month + day selectors.
- "Add another schedule" button to append additional schedule rules.
- Each schedule entry can be individually removed.

**Delete warnings:** list all tasks that link to this event.

---

## K4 · Task Form Fields

| Field | Type | Notes |
|---|---|---|
| id | text input | Required. Unique. |
| name | text input | Required. |
| description | textarea | Optional. |
| status | dropdown (5 statuses) | Required. Default: TODO. |
| priority | number input | Optional. |
| topic | select (existing topics) | Required. |
| parent | select (existing tasks) or none | Optional. |
| layout | select (existing layouts) or none | Optional. |
| tags | tag input (add/remove) | Optional. |
| deadline | date picker | Optional. |
| effort | dual number input (min / max duration) | Optional. |
| blocked_by | multi-select (existing tasks) + optional description | Optional. |
| event_links | multi-select (existing events) + use_as_deadline + as_context toggles | Optional. |
| schedules | same schedule builder as events | Optional. |

**Delete warnings:** list all child tasks and tasks that are blocked by this task.

---

## K5 · Persistence

### v1 — Immediate save
- On Save (or Confirm in creation dialog): the entity is serialized and the YAML
  file is written immediately via `DatabaseSerializer`.
- The database is reloaded automatically after a successful write.
- If the write fails (permission error, parse error, etc.), an error toast is shown
  and no reload occurs; the drawer stays open in edit mode.

### Future — Background / debounced writes
- To avoid blocking the UI on every keystroke or save, writes can be moved to a
  background worker that batches changes and writes during idle time.
- The data model must be designed so the in-memory `ResolvedDatabase` is the
  source of truth during a session, with the YAML file as the persistence layer.
- A "dirty" indicator in the top bar can signal unsaved in-memory changes.
- This is a planned optimization, not a v1 requirement.

---

## K6 · Validation

- Required fields are validated before Save; missing fields highlighted inline.
- id uniqueness checked against the current database before Save.
- Cross-reference integrity checked on delete (see Delete warnings above).
- Schedule completeness validated (e.g. weekly schedule must have at least one weekday
  and a valid time range).
- Validation errors shown inline in the form, not as separate dialogs.
