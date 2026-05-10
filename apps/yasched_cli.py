"""Default CLI entrypoint for My Yaml Scheduler."""

from __future__ import annotations

import argparse

from yasched import __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the default command-line parser."""
    parser = argparse.ArgumentParser(
        prog="yasched",
        description="My Yaml Scheduler command-line interface.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main() -> int:
    """Run the default CLI entrypoint."""
    build_parser().parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
