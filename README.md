# yasched

`yasched` is a YAML-based personal scheduler. Define tasks, events, and topics
in plain YAML files and query or visualise them through a CLI or a Streamlit UI.

## Installation

From a local checkout (with venv already activated):

```bash
make install-current
```

For a full development setup (creates `.venv`):

```bash
make install
source .venv/bin/activate
```

For the Streamlit frontend, also install the optional frontend dependency:

```bash
pip install -e ".[frontend]"
```

## Apps

### CLI — `yasched`

A command-line interface for querying the database.

```bash
yasched --db path/to/main.yaml <group> <command> [options]
```

Quick reference:

| Command | Description |
|---|---|
| `db validate` | Validate the database and report any errors |
| `db info` | Summary statistics (entity counts, task status breakdown) |
| `schedule daily [DATE]` | Daily schedule view (default: today) |
| `schedule weekly [DATE]` | Weekly schedule view |
| `schedule range START END` | Events and tasks between two ISO dates |
| `tasks list [--status] [--topic] [--tag] [--priority-min/max]` | List tasks with optional filters |
| `tasks show TASK_ID` | Full detail for one task |
| `tasks search QUERY` | Substring search on name and description |
| `tasks deadlines [--days N]` | Upcoming deadlines (default: 7 days) |
| `tasks overdue` | Tasks past their deadline |
| `tasks blocked` | Tasks in BLOCKED status |
| `events list` | List all events |
| `events show EVENT_ID` | Full detail for one event |
| `events range START END` | Events in a date range |
| `topics list` | Topic hierarchy as an indented tree |
| `topics show TOPIC_ID` | Topic detail with children and task count |
| `check conflicts [--start] [--end]` | Detect overlapping events |
| `check stale-links` | Tasks still linked to already-ended events |
| `check stale-blocks` | Tasks blocked by tasks that are already done |
| `check all` | Run all checks at once |

Example:

```bash
DB=resources/basic_example/basic_example_main.yaml

yasched --db $DB db info
yasched --db $DB tasks list --status todo
yasched --db $DB tasks deadlines --days 30
yasched --db $DB schedule daily 2026-01-15
yasched --db $DB check all
```

---

### Streamlit UI

A browser-based proof-of-concept frontend with three tabs:

- **MAIN** — database overview: validation status, entity counts, task status
  breakdown, and topic tree.
- **TASKS** — Kanban board with one column per task status; cards are styled
  with the colours defined in their layout.
- **EVENTS** — Monthly calendar with coloured event badges; hover over a badge
  to see the event name, location, and description.

Run with:

```bash
make streamlit
```

Or directly:

```bash
streamlit run apps/streamlit/yasched_streamlit.py
```

Then open the URL printed by Streamlit (usually `http://localhost:8501`), enter
the path to your YAML file in the sidebar, and click **Load**.

Example database path to try:

```
resources/basic_example/basic_example_main.yaml
```

## Development

```bash
make lint       # ruff + mypy
make format     # auto-fix formatting
make test       # pytest
make docs       # build MkDocs site
```

## License

Licensed under the Apache 2.0 License.
