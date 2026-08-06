# yasched

<p align="center">
  <img src="assets/logo.png" alt="yasched" width="520" />
</p>

**yasched** is a local-first, YAML-based personal scheduler. You describe your
topics, tasks, events, and recurring schedules in a plain YAML *agenda* file, and
yasched serves a colorful web app to browse and edit them.

Everything runs entirely on your machine — no accounts, no cloud, no outbound
network calls.

## Highlights

- **One unified model** — everything is an **Element** (`topic`, `event`,
  `task`, or `schedule`). Only `id` and `type` are structural; `name`,
  `description`, dates, `status`, and everything else live in an open
  `attributes` bag, plus a `layout`.
- **One inheritance relation** — `directParents` is an ordered list; the first
  entry is the element's **MainParent** and the first reachable topic becomes its
  **Topic**. Values and layout flow down this chain.
- **Auto-elements** — schedules generate events/tasks, and deadlines/reminders
  generate events, as **virtual** occurrences that become real the moment you
  edit one.
- **Connections** — link any element to any other with an open relation label
  (informational, shown on both ends).
- **Single-file & editable** — the database is one YAML file the app can read
  and write; multi-file [xyml](agenda-format.md#splitting-files-xyml) includes
  are supported on read and flattened on first save.

## Where to go next

- [Getting started](getting-started.md) — install and run.
- [Data model](data-model.md) — elements, inheritance, auto-elements.
- [Agenda format](agenda-format.md) — the YAML reference.
- [Architecture](architecture.md) — how the layers fit together.
- [API reference](api/index.md) — the Python packages.
