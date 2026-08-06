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

## Installing everything

There are two supported setups. Run `make check-tools` any time to see what you
already have.

### Option A — Docker (simplest; one prerequisite)

Only [Docker](https://docs.docker.com/get-docker/) is required. The image builds
Node + React, Python + the API, and the frontend bundle for you:

```bash
make up      # build (first time, ~1–2 min) + start → http://localhost:8000
make down    # stop and remove it
```

Nothing else to install — not Node, not Python.

### Option B — Local (for development)

You need two system runtimes that a Python virtualenv cannot provide:

| Tool | Version | Check |
|---|---|---|
| Python | ≥ 3.12 | `python3 --version` |
| Node.js + npm | ≥ 20 | `node --version` |

**Don't have Node.js?** Install it one of these ways:

```bash
make install-node                       # installs Node 20 for your user via nvm, then open a new shell
# — or —
sudo apt-get install -y nodejs npm      # Debian/Ubuntu
brew install node                       # macOS (Homebrew)
```

Then install **everything** (Python deps in a venv, web deps, and the SPA build)
in one command:

```bash
make install-all      # = Python .venv + npm install + build the frontend
make demo             # serve the bundled example at http://127.0.0.1:8000
```

`make install-all` stops with clear instructions if Node is missing, so it is
safe to run first.

## Quick start

Once the prerequisites above are in place, one command builds everything and
serves your personal agenda locally:

```bash
./run.sh
```

On first run it creates `~/.yasched/agenda.yaml` from a template, builds the
frontend, and opens the server at <http://127.0.0.1:8000>. Edit that YAML file,
refresh the page, and your schedule updates.

Want to explore a fully-featured example first?

```bash
make demo        # serves resources/example_v4 (uses every feature)
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
| `make check-tools` | Report which prerequisites (python / node / npm / docker) are present |
| `make install-all` | Install **everything** for local dev: Python venv + web deps + build the SPA |
| `make install-node` | Install Node 20 for your user via nvm (only if you don't have Node) |
| `./run.sh` | **Do-everything**: create venv, install, build frontend, create `~/.yasched/agenda.yaml` if missing, serve on `:8000` (foreground, Ctrl-C to stop) |
| `./run.sh path/to/agenda.yaml` | Same, against a specific agenda file |
| `./run.sh --daemon` | Serve in the **background**, print the URL, return the terminal |
| `./run.sh --stop` | Stop the background server |
| `./run.sh --status` / `--restart` / `--logs` | Check / restart / follow logs of the background server |
| `./run.sh --reinstall` / `--rebuild` | Reinstall after dependency changes / rebuild the frontend |
| `HOST=0.0.0.0 PORT=9000 ./run.sh` | Override bind host/port (use the same `PORT` for `--stop`/`--status`) |
| `make run` | Alias for `./run.sh` |
| `make demo` | Serve the bundled `resources/example_v4` (every feature) |
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

## The agenda file (v4)

An agenda is a YAML document with one **flat list of elements** plus optional
attribute definitions:

```yaml
attributes:          # optional: user-defined attribute schema (type, range, ...)
elements:            # one flat list; every element has an `id` and a `type`
  - id: work
    type: topic      # topic | event | task | schedule
    directParents: [AllTopic]
    attributes: { name: Work }
    layout: { background: { color: "#3b82f6" } }
```

Everything is an **Element**. Only `id` and `type` are structural; `name`,
`description`, dates, `status`, `connections`, … all live in the open
`attributes` bag, alongside a `layout`. `directParents` is the single
inheritance relation: an ordered list whose first entry is the element's
**MainParent** and whose first reachable topic becomes the element's **Topic**.
The built-in `AllTopic` root holds app-wide defaults.

Values resolve per attribute (own wins, else the first parent in the linearized
`Parents` list); layout resolves per field as `own > attribute-layout > parents`.
Schedules generate events/tasks, and deadlines/reminders generate events, as
**virtual** elements that become real when you edit them. Files can still be
split with the xyml `__file__` / `__ext__` includes; the app flattens them into
one file on first save.

See [`resources/example_v4/agenda.yaml`](resources/example_v4/agenda.yaml) for a
feature tour and [`devs/v4/v4-panel-requirements.md`](devs/v4/v4-panel-requirements.md)
for the full spec.

## Architecture

```
utilizing   generic value types (color, time, duration, xyml loader)
   ▲
coring      the unified model: Element, ElementType, Layout, Connection,
            AttributeDefinition
   ▲
backending  load/serialize (xyml ↔ single file) · resolve (DFS parents,
            inheritance, layout) · generate auto-elements · validate
   ▲
serving     FastAPI app + view DTOs + `yasched` CLI, serving the React SPA
```

The React frontend (`apps/web`) talks to the API over HTTP and is served as
static files by the same process — one port, no CORS. See
[`devs/v4/v4-architecture.md`](devs/v4/v4-architecture.md).

> **Status:** the v4 backend, HTTP API, CLI, test suite, and a v4-native React
> frontend (category panels over `/api/elements`) are implemented. Build the
> frontend with `cd apps/web && npm install && npm run build`.

## Development

```bash
make check-tools # verify python / node / npm are present
make install-all # one-shot: .venv + Python dev deps + web deps + SPA build
# (or, piecemeal:)
make install     # create .venv and install Python dev deps only
make test        # pytest (Python)
make lint        # ruff + mypy
make web         # frontend dev server with hot reload (proxies /api)
make docs        # build the MkDocs site

cd apps/web && npm run typecheck && npm run lint && npm run build   # frontend checks
```

## License

Licensed under the Apache 2.0 License.
