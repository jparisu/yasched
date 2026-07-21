<p align="center">
  <img src="docs/assets/logo.png" alt="yasched" width="520" />
</p>

# yasched

**yasched** is a local-first, YAML-based personal scheduler. You describe your
topics, tasks, and events in a plain YAML *agenda* file, and yasched serves a
colorful web app to browse them — an agenda, a calendar, a task board, a focus
view, and statistics.

Everything runs **entirely on your machine**. There are no accounts, no cloud,
and no outbound network calls.

## Quick start

One command builds everything and serves your personal agenda locally:

```bash
./run.sh
```

On first run it creates `~/.yasched/agenda.yaml` from a template, builds the
frontend, and opens the server at <http://127.0.0.1:8000>. Edit that YAML file,
refresh the page, and your schedule updates.

Want to explore a fully-featured example first?

```bash
make demo        # serves resources/teacher_example (uses every feature)
```

### With Docker (easy up / down)

```bash
make up          # build image (first time only) + start → http://localhost:8000
make down        # stop and remove it
```

`make up` starts the app detached with a ready-to-use default document, so it is
up in one command and torn down cleanly with `make down`. `make up-demo` instead
serves the bundled comprehensive example. Equivalent without Make:

```bash
docker compose up -d --build     # start
docker compose down              # stop
docker compose logs -f           # watch logs   (or: make logs)
```

Your agenda lives in `./data/agenda.yaml` on the host (created on first run),
so it persists and you can edit it directly. Override the port with
`PORT=9000 make up`. *(The first build pulls base images and installs deps —
needs network once, ~1–2 min. After that, up/down take seconds and the running
container makes no outbound calls.)*

### Command reference

Everything you need to run it locally:

| Command | What it does |
|---|---|
| `./run.sh` | **Do-everything**: create venv, install, build frontend, create `~/.yasched/agenda.yaml` if missing, serve on `:8000` (foreground, Ctrl-C to stop) |
| `./run.sh path/to/agenda.yaml` | Same, against a specific agenda file |
| `./run.sh --daemon` | Serve in the **background**, print the URL, return the terminal |
| `./run.sh --stop` | Stop the background server |
| `./run.sh --status` / `--restart` / `--logs` | Check / restart / follow logs of the background server |
| `./run.sh --reinstall` / `--rebuild` | Reinstall after dependency changes / rebuild the frontend |
| `HOST=0.0.0.0 PORT=9000 ./run.sh` | Override bind host/port (use the same `PORT` for `--stop`/`--status`) |
| `make run` | Alias for `./run.sh` |
| `make demo` | Serve the bundled `resources/teacher_example` (every feature; browse-only) |
| `make serve` | Serve your personal agenda (assumes deps installed + frontend built) |
| `make web-build` | Build the frontend bundle only |
| `make web` | Frontend dev server with hot reload (proxies `/api` → `:8000`) |
| `make up` | **Docker**: build (first time) + start detached on `:8000` with a default document |
| `make up-demo` | Docker: start detached serving the bundled example (browse-only) |
| `make down` | Docker: stop and remove the container |
| `PORT=9000 make up` | Docker on a different port |

After `pip install -e .` (done by `run.sh`/`make install`), the `yasched` CLI is available:

```bash
yasched init                              # create ~/.yasched/agenda.yaml from the template
yasched serve --agenda FILE --port 8000   # run the local server
yasched check --agenda FILE               # load + validate, print a summary
```

`--agenda` defaults to `$YASCHED_AGENDA`, then `~/.yasched/agenda.yaml`. Then
open <http://127.0.0.1:8000>.

## The agenda file

An agenda is a YAML document with up to five top-level keys:

```yaml
default:            # lowest-priority layer, fills anything left unset
traits:             # reusable named bundles of attributes and/or layout
topics:             # organizational categories (a DAG)
events:             # time-bound occurrences, recurring via `schedules`
tasks:              # units of work (deadlines, subtasks, relations)
```

Every topic, task, and event carries two open "bags":

- **`attributes`** — semantic data (`deadline`, `priority`, `difficulty`,
  `kanban`, `status`, …). Fully open: add any key you like.
- **`layout`** — visual style (`background`, `border`, `icon`, `pin`, `shape`).

Both are resolved through one inheritance engine, lowest → highest:

```
default  <  topic(s)  <  traits  <  parent  <  own
```

`tags` accumulate (union) across the chain. Files can be split and composed
with the xyml `__file__` / `__ext__` include directives.

See [`resources/teacher_example/`](resources/teacher_example/) and its
[`FEATURES.md`](resources/teacher_example/FEATURES.md) for a tour of every
capability, and the [documentation](docs/) for the full reference.

## Architecture

```
utilizing   generic value types (color, time, xyml loader)
   ▲
coring      plain data holders: Topic, Task, Event, Schedule, Layout, Trait
   ▲
backending  load (xyml → objects) · resolve (inheritance/traits) · schedule occurrences
   ▲
serving     FastAPI app + view DTOs + `yasched` CLI, serving the React SPA
```

The React frontend (`apps/web`) talks to the API over HTTP and is served as
static files by the same process — one port, no CORS. See
[`devs/v3-architecture.md`](devs/v3-architecture.md).

## Development

```bash
make install     # create .venv and install dev deps
make test        # pytest (Python)
make lint        # ruff + mypy
make web         # frontend dev server with hot reload (proxies /api)
make docs        # build the MkDocs site

cd apps/web && npm run typecheck && npm run lint && npm run build   # frontend checks
```

## License

Licensed under the Apache 2.0 License.
