# Getting started

## Requirements

- **Python ≥ 3.12**
- **Node.js ≥ 20** + npm (to build the frontend)

Everything runs locally; yasched makes no network calls at runtime. Run
`make check-tools` to see what you already have.

## Install everything

**Docker (simplest — only Docker needed):**

```bash
make up      # builds Node + React + Python into an image, serves :8000
make down
```

**Local (for development):**

```bash
# don't have Node? one of:
make install-node                    # Node 20 for your user via nvm
sudo apt-get install -y nodejs npm   # Debian/Ubuntu
brew install node                    # macOS

make install-all     # Python venv + web deps + build the SPA
make demo            # serve the bundled example at http://127.0.0.1:8000
```

`./run.sh` is the one-command path once prerequisites are in place: it creates a
venv, builds the frontend, creates `~/.yasched/agenda.yaml` from the template if
missing, and serves at <http://127.0.0.1:8000>.

## Using the CLI

```bash
yasched init                    # create ~/.yasched/agenda.yaml from the template
yasched check --agenda FILE     # load, validate, and print a summary
yasched serve --agenda FILE     # run the local server
```

The agenda path resolves as: `--agenda` > `$YASCHED_AGENDA` >
`~/.yasched/agenda.yaml`.

## Editing from the app

The database is a single YAML file that the app reads **and writes**:

- Every "… management" panel (Topic / Event / Task / Schedule) has an editor for
  the selected element's attributes and layout.
- The **Task board** lets you drag a card between columns to change its
  `status` (or `priority`).
- Editing an auto-generated occurrence (a scheduled event, a deadline, a
  reminder) **promotes** it to a real element, storing only your overrides.

Agendas that use xyml includes (`__file__` / `__ext__`) load fine; the first save
from the app flattens them into the single file.

## Panels

Grouped in the left sidebar by category:

- **Core** — *Main* (upcoming events, deadlines, priority tasks), *Stats*,
  *Focus* (focused elements), *Attributes* (the attribute schema), *Settings*.
- **Topic** — *Graph* (nested/tree topic map), *Topics* (management).
- **Event** — *Calendar* (month/week), *Agenda* (paper-week), *Events*
  (management).
- **Schedule** — *Timeboard* (schedules + their generated occurrences), *Effort*
  (time used per topic, by period), *Schedules* (management).
- **Task** — *Task board* (kanban), *Tasks* (management).

## Validation

The app continuously checks your agenda (unknown references, cycles, out-of-range
values, detached occurrences) and shows the error/warning count in the top bar.
From the CLI: `yasched check --agenda FILE`.

## Development

```bash
make install-all # .venv + Python deps + web deps + SPA build
make test        # pytest
make lint        # ruff + mypy
make web         # frontend dev server (hot reload, proxies /api → :8000)
make docs        # build these docs
```
