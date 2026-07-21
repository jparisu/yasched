# Getting started

## Requirements

- Python 3.12+
- Node.js 18+ (to build the frontend)

Everything runs locally. yasched makes no network calls at runtime.

## Run it (one command)

From a checkout:

```bash
./run.sh
```

This will, in order:

1. create a virtualenv and install yasched (editable),
2. build the frontend (offline, from installed `node_modules`),
3. create `~/.yasched/agenda.yaml` from the template if it does not exist,
4. serve everything at <http://127.0.0.1:8000>.

Serve a specific file, host, or port:

```bash
./run.sh path/to/agenda.yaml
HOST=0.0.0.0 PORT=9000 ./run.sh
```

## Try the example

```bash
make demo
```

Serves [`resources/teacher_example`](https://github.com/jparisu/yasched),
which exercises every feature (see its `FEATURES.md`).

## Using the CLI

```bash
yasched init                    # create ~/.yasched/agenda.yaml
yasched check --agenda FILE     # parse and print a summary
yasched serve --agenda FILE     # run the local server
```

The agenda path resolves as: `--agenda` > `$YASCHED_AGENDA` >
`~/.yasched/agenda.yaml`.

## Docker

```bash
docker compose up --build       # http://localhost:8000
```

Your agenda is stored in `./data/agenda.yaml` on the host. Building the image
pulls base images once; the running container makes no outbound calls.

## Editing from the app

When you serve a **single-file** agenda, the app is fully editable:

- The **New** button (top bar) creates a topic, task, or event.
- Click a card on the **Task Board**, a node in the **Database Graph**, or an
  entry in the **Weekly View** to edit or delete it.
- Changes are written straight back to your agenda YAML.

Agendas that use xyml includes (`__file__` / `__ext__`) are **browse-only** —
serializing them back would flatten the file structure — so the bundled
`make demo` example cannot be edited from the UI. Edit those as YAML.

## Panels

- **Statistics / Agenda / Calendar / Focus** — overviews of your tasks & events.
- **Weekly View** — a class-timetable grid of your recurring weekly events.
- **Task Board** — kanban by stage / priority / topic.
- **Database Graph** — topics as areas, tasks (▭) and events (◆) inside them,
  connected with UML-style arrows (dependency, composition, aggregation,
  generalization).

## Validation

The app continuously checks your agenda for problems (unknown references,
cycles, impossible schedules, duplicate ids) and shows a banner summarizing any
errors/warnings. From the CLI: `yasched check --agenda FILE`.

## Development

```bash
make install     # .venv + dev deps
make test        # pytest
make lint        # ruff + mypy
make web         # frontend dev server (hot reload, proxies /api → :8000)
```
