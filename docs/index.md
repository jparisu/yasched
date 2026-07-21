# yasched

<p align="center">
  <img src="assets/logo.png" alt="yasched" width="520" />
</p>

**yasched** is a local-first, YAML-based personal scheduler. You describe your
topics, tasks, and events in a plain YAML *agenda* file, and yasched serves a
colorful web app to browse them.

Everything runs entirely on your machine — no accounts, no cloud, no outbound
network calls.

## Highlights

- **One command to run** — `./run.sh` builds the frontend and serves your
  agenda at <http://127.0.0.1:8000>.
- **Open data model** — every entity carries an open `attributes` bag and a
  `layout` bag, both resolved through one inheritance engine.
- **Reusable traits** — bundle attributes/layout under a name and attach it
  anywhere.
- **Recurrence & overrides** — five schedule types, plus sub-events that
  override or cancel a single occurrence.
- **Composable files** — split an agenda across files with xyml includes.

## Where to go next

- [Getting started](getting-started.md) — install and run.
- [Data model](data-model.md) — topics, tasks, events, traits, inheritance.
- [Agenda format](agenda-format.md) — the YAML reference.
- [Architecture](architecture.md) — how the layers fit together.
- [API reference](api/index.md) — the Python packages.
