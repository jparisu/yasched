"""CLI entrypoint for yasched."""

from __future__ import annotations

import argparse
import datetime
import sys

from yasched import __version__
from yasched.backending import (
    ConsistencyError,
    DatabaseInterface,
    DatabaseLoader,
    DatabaseManager,
    DatabaseParseError,
    ResolvedEvent,
    ResolvedTask,
    ResolvedTopic,
)
from yasched.coring._shared import TaskStatus

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_interface(db_path: str) -> DatabaseInterface:
    db = DatabaseLoader.load(db_path)
    rdb = DatabaseManager.resolve(db)
    return DatabaseInterface(rdb)


def _parse_date(s: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid date '{s}'. Use ISO format: YYYY-MM-DD.") from e


def _fmt_date(d: datetime.date | None) -> str:
    return d.isoformat() if d is not None else "-"


def _fmt_task(t: ResolvedTask, indent: int = 0) -> str:
    prefix = "  " * indent
    deadline = f"  deadline={_fmt_date(t.effective_deadline)}" if t.effective_deadline else ""
    priority = f"  priority={t.priority}" if t.priority is not None else ""
    return f"{prefix}[{t.status.value:<11}] {t.id}: {t.name}{priority}{deadline}"


def _fmt_event(e: ResolvedEvent) -> str:
    loc = f"  @ {e.location}" if e.location else ""
    return f"{e.id}: {e.name}{loc}  (topic: {e.topic.id})"


def _fmt_topic(t: ResolvedTopic, indent: int = 0) -> str:
    prefix = "  " * indent
    return f"{prefix}{t.id}: {t.name}"


def _print_topic_tree(topic: ResolvedTopic, indent: int = 0) -> None:
    print(_fmt_topic(topic, indent))
    for child in topic.children:
        _print_topic_tree(child, indent + 1)


# ---------------------------------------------------------------------------
# db commands
# ---------------------------------------------------------------------------


def cmd_db_validate(args: argparse.Namespace) -> int:
    try:
        db = DatabaseLoader.load(args.db)
    except (DatabaseParseError, FileNotFoundError) as e:
        print(f"ERROR loading {args.db}: {e}", file=sys.stderr)
        return 1
    errors = DatabaseManager.validate(db)
    if not errors:
        print("OK — no consistency errors found.")
        return 0
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  {type(e).__name__}: {e}")
    return 1


def cmd_db_info(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    summary = iface.task_status_summary()
    counts = iface.task_count_by_topic()
    print(f"Layouts : {len(iface.all_layouts())}")
    print(f"Topics  : {len(iface.all_topics())}")
    print(f"Events  : {len(iface.all_events())}")
    print(f"Tasks   : {len(iface.all_tasks())}")
    print()
    print("Task status breakdown:")
    for status, count in summary.items():
        print(f"  {status.value:<12}  {count}")
    print()
    print("Tasks per topic:")
    for topic_id, count in sorted(counts.items()):
        print(f"  {topic_id:<30}  {count}")
    return 0


# ---------------------------------------------------------------------------
# schedule commands
# ---------------------------------------------------------------------------


def cmd_schedule_daily(args: argparse.Namespace) -> int:
    date = _parse_date(args.date) if args.date else datetime.date.today()
    iface = _load_interface(args.db)
    view = iface.get_daily_schedule(date)
    print(f"=== Daily schedule: {date} ===")
    print(f"\nEvents ({len(view.events)}):")
    for e in view.events:
        print(f"  {_fmt_event(e)}")
    print(f"\nTasks ({len(view.tasks)}):")
    for t in view.tasks:
        print(f"  {_fmt_task(t)}")
    if view.conflicts:
        print(f"\nConflicts ({len(view.conflicts)}):")
        for c in view.conflicts:
            print(f"  {c.blocker.id} blocks {c.blocked.id}")
    return 0


def cmd_schedule_weekly(args: argparse.Namespace) -> int:
    if args.date:
        date = _parse_date(args.date)
        week_start = date - datetime.timedelta(days=date.weekday())
    else:
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
    iface = _load_interface(args.db)
    view = iface.get_weekly_schedule(week_start)
    week_end = week_start + datetime.timedelta(days=6)
    print(f"=== Weekly schedule: {week_start} to {week_end} ===\n")
    for day in view.days:
        events_str = ", ".join(e.name for e in day.events) or "-"
        tasks_str = ", ".join(t.name for t in day.tasks) or "-"
        conflicts_str = f"  [!{len(day.conflicts)} conflicts]" if day.conflicts else ""
        print(f"  {day.date}  events: {events_str}  |  tasks: {tasks_str}{conflicts_str}")
    return 0


def cmd_schedule_range(args: argparse.Namespace) -> int:
    start = _parse_date(args.start)
    end = _parse_date(args.end)
    iface = _load_interface(args.db)
    events = iface.get_events_in_range(start, end)
    tasks = iface.get_tasks_in_range(start, end)
    print(f"=== Range: {start} to {end} ===")
    print(f"\nEvents ({len(events)}):")
    for e in events:
        print(f"  {_fmt_event(e)}")
    print(f"\nTasks ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 0


# ---------------------------------------------------------------------------
# tasks commands
# ---------------------------------------------------------------------------


def cmd_tasks_list(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.all_tasks()
    if args.status:
        status = TaskStatus(args.status)
        tasks = [t for t in tasks if t.status == status]
    if args.topic:
        tasks = [t for t in tasks if t.topic.id == args.topic]
    if args.tag:
        tasks = [t for t in tasks if args.tag in t.effective_tags]
    if args.priority_min is not None:
        tasks = [t for t in tasks if t.priority is not None and t.priority >= args.priority_min]
    if args.priority_max is not None:
        tasks = [t for t in tasks if t.priority is not None and t.priority <= args.priority_max]
    print(f"Tasks ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 0


def cmd_tasks_show(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    try:
        t = iface.get_task(args.task_id)
    except KeyError:
        print(f"ERROR: task '{args.task_id}' not found.", file=sys.stderr)
        return 1
    print(f"id         : {t.id}")
    print(f"name       : {t.name}")
    print(f"status     : {t.status.value}")
    print(f"topic      : {t.topic.id}")
    print(f"priority   : {t.priority if t.priority is not None else '-'}")
    print(f"deadline   : {_fmt_date(t.effective_deadline)}")
    print(f"tags       : {', '.join(t.effective_tags) or '-'}")
    if t.description:
        print(f"description: {t.description}")
    if t.effort:
        print(f"effort     : {t.effort.min} – {t.effort.max}")
    if t.parent:
        print(f"parent     : {t.parent.id}")
    if t.children:
        print(f"children   : {', '.join(c.id for c in t.children)}")
    if t.blocked_by:
        print(f"blocked_by : {', '.join(b.task_id for b in t.blocked_by)}")
    if t.linked_events:
        print(f"events     : {', '.join(e.id for e in t.linked_events)}")
    return 0


def cmd_tasks_search(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.search_tasks(args.query)
    print(f"Results for '{args.query}' ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 0


def cmd_tasks_deadlines(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.get_upcoming_deadlines(days_ahead=args.days)
    print(f"Upcoming deadlines (next {args.days} days) — {len(tasks)} task(s):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 0


def cmd_tasks_overdue(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.get_overdue_tasks()
    print(f"Overdue tasks ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 0


def cmd_tasks_blocked(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.get_blocked_tasks()
    print(f"Blocked tasks ({len(tasks)}):")
    for t in tasks:
        blockers = ", ".join(b.task_id for b in t.blocked_by)
        print(f"  {_fmt_task(t)}  blocked_by=[{blockers}]")
    return 0


# ---------------------------------------------------------------------------
# events commands
# ---------------------------------------------------------------------------


def cmd_events_list(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    events = iface.all_events()
    print(f"Events ({len(events)}):")
    for e in events:
        print(f"  {_fmt_event(e)}")
    return 0


def cmd_events_show(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    try:
        e = iface.get_event(args.event_id)
    except KeyError:
        print(f"ERROR: event '{args.event_id}' not found.", file=sys.stderr)
        return 1
    print(f"id          : {e.id}")
    print(f"name        : {e.name}")
    print(f"topic       : {e.topic.id}")
    if e.location:
        print(f"location    : {e.location}")
    if e.description:
        print(f"description : {e.description}")
    if e.blocking_level is not None:
        print(f"blocking    : {e.blocking_level}")
    print(f"schedules   : {len(e.raw.schedules)} schedule(s)")
    for s in e.raw.schedules:
        print(f"  {s}")
    return 0


def cmd_events_range(args: argparse.Namespace) -> int:
    start = _parse_date(args.start)
    end = _parse_date(args.end)
    iface = _load_interface(args.db)
    events = iface.get_events_in_range(start, end)
    print(f"Events from {start} to {end} ({len(events)}):")
    for e in events:
        print(f"  {_fmt_event(e)}")
    return 0


# ---------------------------------------------------------------------------
# topics commands
# ---------------------------------------------------------------------------


def cmd_topics_list(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    roots = iface.get_root_topics()
    print("Topics (tree):")
    for r in roots:
        _print_topic_tree(r)
    return 0


def cmd_topics_show(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    try:
        t = iface.get_topic(args.topic_id)
    except KeyError:
        print(f"ERROR: topic '{args.topic_id}' not found.", file=sys.stderr)
        return 1
    counts = iface.task_count_by_topic()
    print(f"id          : {t.id}")
    print(f"name        : {t.name}")
    if t.description:
        print(f"description : {t.description}")
    print(f"tags        : {', '.join(t.effective_tags) or '-'}")
    if t.parents:
        print(f"parents     : {', '.join(p.id for p in t.parents)}")
    if t.children:
        print(f"children    : {', '.join(c.id for c in t.children)}")
    print(f"tasks       : {counts.get(t.id, 0)}")
    return 0


# ---------------------------------------------------------------------------
# check commands
# ---------------------------------------------------------------------------


def cmd_check_conflicts(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    start_s = getattr(args, "start", None)
    end_s = getattr(args, "end", None)
    start = _parse_date(start_s) if start_s else None
    end = _parse_date(end_s) if end_s else None
    conflicts = iface.get_conflicts(start=start, end=end)
    if not conflicts:
        print("No conflicts found.")
        return 0
    print(f"Conflicts ({len(conflicts)}):")
    for c in conflicts:
        print(f"  {c.date}  {c.blocker.id} blocks {c.blocked.id}")
    return 1


def cmd_check_stale_links(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.get_stale_event_links()
    if not tasks:
        print("No stale event links.")
        return 0
    print(f"Tasks with stale event links ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 1


def cmd_check_stale_blocks(args: argparse.Namespace) -> int:
    iface = _load_interface(args.db)
    tasks = iface.get_stale_blocks()
    if not tasks:
        print("No stale blocks.")
        return 0
    print(f"Tasks with stale blocks ({len(tasks)}):")
    for t in tasks:
        print(f"  {_fmt_task(t)}")
    return 1


def cmd_check_all(args: argparse.Namespace) -> int:
    rc = 0
    print("--- conflicts ---")
    rc |= cmd_check_conflicts(args)
    print("\n--- stale event links ---")
    rc |= cmd_check_stale_links(args)
    print("\n--- stale blocks ---")
    rc |= cmd_check_stale_blocks(args)
    return rc


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yasched",
        description="My Yaml Scheduler command-line interface.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--db", required=True, metavar="PATH", help="Path to the YAML database file."
    )

    sub = parser.add_subparsers(dest="group", required=True)

    # --- db ---
    p_db = sub.add_parser("db", help="Database operations.")
    db_sub = p_db.add_subparsers(dest="command", required=True)
    db_sub.add_parser("validate", help="Validate the database and report errors.")
    db_sub.add_parser("info", help="Show database statistics.")

    # --- schedule ---
    p_sched = sub.add_parser("schedule", help="Time-based schedule views.")
    sched_sub = p_sched.add_subparsers(dest="command", required=True)

    p_daily = sched_sub.add_parser("daily", help="Daily schedule view.")
    p_daily.add_argument("date", nargs="?", metavar="DATE", help="ISO date (default: today).")

    p_weekly = sched_sub.add_parser("weekly", help="Weekly schedule view.")
    p_weekly.add_argument(
        "date",
        nargs="?",
        metavar="DATE",
        help="Any ISO date in the desired week (default: this week).",
    )

    p_range = sched_sub.add_parser("range", help="Events and tasks in a date range.")
    p_range.add_argument("start", metavar="START", help="Start date (ISO).")
    p_range.add_argument("end", metavar="END", help="End date (ISO).")

    # --- tasks ---
    p_tasks = sub.add_parser("tasks", help="Task queries.")
    tasks_sub = p_tasks.add_subparsers(dest="command", required=True)

    p_tlist = tasks_sub.add_parser("list", help="List tasks with optional filters.")
    p_tlist.add_argument(
        "--status",
        choices=[s.value for s in TaskStatus],
        metavar="STATUS",
        help="Filter by status.",
    )
    p_tlist.add_argument("--topic", metavar="TOPIC_ID", help="Filter by topic id.")
    p_tlist.add_argument("--tag", metavar="TAG", help="Filter by tag.")
    p_tlist.add_argument(
        "--priority-min", type=int, metavar="N", help="Minimum priority (inclusive)."
    )
    p_tlist.add_argument(
        "--priority-max", type=int, metavar="N", help="Maximum priority (inclusive)."
    )

    p_tshow = tasks_sub.add_parser("show", help="Show full detail for a task.")
    p_tshow.add_argument("task_id", metavar="TASK_ID")

    p_tsearch = tasks_sub.add_parser("search", help="Search tasks by name/description substring.")
    p_tsearch.add_argument("query", metavar="QUERY")

    p_tdead = tasks_sub.add_parser("deadlines", help="List upcoming deadlines.")
    p_tdead.add_argument(
        "--days", type=int, default=7, metavar="N", help="Look-ahead window in days (default: 7)."
    )

    tasks_sub.add_parser("overdue", help="Tasks past their deadline.")
    tasks_sub.add_parser("blocked", help="Tasks in BLOCKED status.")

    # --- events ---
    p_events = sub.add_parser("events", help="Event queries.")
    events_sub = p_events.add_subparsers(dest="command", required=True)
    events_sub.add_parser("list", help="List all events.")

    p_eshow = events_sub.add_parser("show", help="Show full detail for an event.")
    p_eshow.add_argument("event_id", metavar="EVENT_ID")

    p_erange = events_sub.add_parser("range", help="Events occurring in a date range.")
    p_erange.add_argument("start", metavar="START", help="Start date (ISO).")
    p_erange.add_argument("end", metavar="END", help="End date (ISO).")

    # --- topics ---
    p_topics = sub.add_parser("topics", help="Topic hierarchy queries.")
    topics_sub = p_topics.add_subparsers(dest="command", required=True)
    topics_sub.add_parser("list", help="Show full topic tree.")

    p_tpshow = topics_sub.add_parser("show", help="Show detail for a topic.")
    p_tpshow.add_argument("topic_id", metavar="TOPIC_ID")

    # --- check ---
    p_check = sub.add_parser("check", help="Consistency checks.")
    check_sub = p_check.add_subparsers(dest="command", required=True)

    p_conflicts = check_sub.add_parser("conflicts", help="Detect overlapping events.")
    p_conflicts.add_argument("--start", metavar="DATE", help="Range start (ISO). Default: today.")
    p_conflicts.add_argument("--end", metavar="DATE", help="Range end (ISO). Default: no limit.")

    check_sub.add_parser("stale-links", help="Tasks still linked to already-ended events.")
    check_sub.add_parser("stale-blocks", help="Tasks blocked by tasks that are already done.")
    check_sub.add_parser("all", help="Run all checks.")

    return parser


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

_HANDLERS = {
    ("db", "validate"): cmd_db_validate,
    ("db", "info"): cmd_db_info,
    ("schedule", "daily"): cmd_schedule_daily,
    ("schedule", "weekly"): cmd_schedule_weekly,
    ("schedule", "range"): cmd_schedule_range,
    ("tasks", "list"): cmd_tasks_list,
    ("tasks", "show"): cmd_tasks_show,
    ("tasks", "search"): cmd_tasks_search,
    ("tasks", "deadlines"): cmd_tasks_deadlines,
    ("tasks", "overdue"): cmd_tasks_overdue,
    ("tasks", "blocked"): cmd_tasks_blocked,
    ("events", "list"): cmd_events_list,
    ("events", "show"): cmd_events_show,
    ("events", "range"): cmd_events_range,
    ("topics", "list"): cmd_topics_list,
    ("topics", "show"): cmd_topics_show,
    ("check", "conflicts"): cmd_check_conflicts,
    ("check", "stale-links"): cmd_check_stale_links,
    ("check", "stale-blocks"): cmd_check_stale_blocks,
    ("check", "all"): cmd_check_all,
}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handler = _HANDLERS.get((args.group, args.command))
    if handler is None:
        parser.print_help()
        return 1
    try:
        return handler(args)
    except (ConsistencyError, DatabaseParseError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
