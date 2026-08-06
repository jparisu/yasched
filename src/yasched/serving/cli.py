"""``yasched`` command-line entry point: init a personal agenda and serve it."""

from __future__ import annotations

import argparse
import sys

from yasched.serving import config


def _cmd_init(args: argparse.Namespace) -> int:
    path = config.resolve_agenda_path(args.agenda)
    if path.exists() and not args.force:
        print(f"Agenda already exists: {path}\nUse --force to overwrite.")
        return 0
    template = config.find_personal_template()
    content = template.read_text(encoding="utf-8") if template else config.FALLBACK_TEMPLATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"Created personal agenda at: {path}\nEdit it, then run:  yasched serve")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from yasched.serving.api import create_app

    path = config.resolve_agenda_path(args.agenda)
    if not path.exists():
        print(f"No agenda at {path}.\nRun `yasched init` first, or pass --agenda PATH.")
        return 1

    app = create_app(path)
    # These URLs are printed on every start, so they must name endpoints that
    # actually exist (an earlier build advertised /api/agenda, which 404s).
    print(f"Serving {path}\n  API : http://{args.host}:{args.port}/api/elements")
    print(f"  App : http://{args.host}:{args.port}/   (Ctrl+C to stop)")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    from yasched.backending.loading.ElementLoader import ElementLoader
    from yasched.backending.validating.Validator import Severity, validate_database

    path = config.resolve_agenda_path(args.agenda)
    if not path.exists():
        print(f"No agenda at {path}.")
        return 1
    db = ElementLoader.load(path)
    print(
        f"Loaded {path}\n  topics={len(db.topics)} events={len(db.events)} "
        f"tasks={len(db.tasks)} schedules={len(db.schedules)}"
    )
    issues = validate_database(db)
    errors = [i for i in issues if i.severity is Severity.ERROR]
    warnings = [i for i in issues if i.severity is Severity.WARNING]
    for issue in issues:
        mark = "ERROR" if issue.severity is Severity.ERROR else "warn "
        where = f"{issue.entity_kind} '{issue.entity_id}'" if issue.entity_id else ""
        print(f"  [{mark}] {where}: {issue.message}")
    if not issues:
        print("  no issues found ✓")
    else:
        print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    # Shared option so `--agenda` works both before and after the subcommand.
    # default=SUPPRESS prevents the subparser's copy from clobbering a value the
    # top-level parser already set (argparse writes subparser defaults last).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--agenda",
        default=argparse.SUPPRESS,
        help="Path to the agenda file (overrides $YASCHED_AGENDA).",
    )

    parser = argparse.ArgumentParser(
        prog="yasched", description="Local YAML scheduler.", parents=[common]
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser(
        "init", parents=[common], help="Create a personal agenda from template."
    )
    p_init.add_argument("--force", action="store_true", help="Overwrite an existing agenda.")
    p_init.set_defaults(func=_cmd_init)

    p_serve = sub.add_parser("serve", parents=[common], help="Run the local server.")
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1).")
    p_serve.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000).")
    p_serve.set_defaults(func=_cmd_serve)

    p_check = sub.add_parser("check", parents=[common], help="Load the agenda and print a summary.")
    p_check.set_defaults(func=_cmd_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "agenda"):  # SUPPRESS means the attr may be absent
        args.agenda = None
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
