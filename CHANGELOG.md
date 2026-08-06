# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) — pre-1.0, so minor
versions may still break the agenda format.

## [0.4.0] — 2026-08-06

The first release of the unified element model, its HTTP API, and the React
frontend. Supersedes the earlier 3.x prototypes, which were never released.

### Added

- **Unified element model** — everything is an `Element` (`topic`, `event`,
  `task`, `schedule`). Only `id` and `type` are structural; everything else lives
  in an open `attributes` bag plus a `layout`.
- **Single inheritance relation** — `directParents` (ordered; first entry is the
  MainParent, first reachable topic becomes the element's Topic), with per-field
  attribute and layout resolution.
- **Auto-elements** — schedules generate events/tasks and deadlines/reminders
  generate events as *virtual* occurrences that become real when edited.
- **HTTP API** — `/api/elements` (CRUD), `/api/meta`, `/api/validate`,
  `/api/effort`, `/api/reload`, `/api/health`; writes persist to the YAML file.
- **`yasched` CLI** — `init`, `serve`, `check`.
- **React frontend** — 16 panels grouped as Core / Topic / Event / Schedule /
  Task, served as static files by the same process (one port, no CORS).
- **Multi-file agendas** — xyml `__file__` / `__ext__` includes are read and
  flattened into the single canonical file on first save.
- **Self-hosted fonts** — vendored via `apps/web/scripts/fetch-fonts.sh`, so the
  running app makes no outbound network calls. CI fails on any CDN reference.
- **CI** — tests on Python 3.12 and 3.14, lint, coverage, docs, a frontend
  build, and an end-to-end server smoke test.

### Changed

- The *Time elapsed* panel (time used per topic) moved from the Schedule
  category to Topic, where it belongs.

### Known limitations

- **YAML comments are not preserved** when the app saves — the file is rebuilt
  from the model. Keep notes in an element's `description` attribute. Tracked as
  `TODO(comments)` in `ElementSerializer`.
- The Calendar has month and week views only; `day` and `year` are deferred
  (`TODO(v0.5)` in `Calendar.tsx`).
- Flattening a multi-file agenda leaves the now-unused include files on disk.
