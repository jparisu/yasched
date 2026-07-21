"""Locate the personal agenda file and the built frontend — all local paths."""

from __future__ import annotations

import os
from pathlib import Path

ENV_AGENDA = "YASCHED_AGENDA"
ENV_WEB_DIST = "YASCHED_WEB_DIST"

DEFAULT_AGENDA = Path.home() / ".yasched" / "agenda.yaml"


def resolve_agenda_path(cli_value: str | None = None) -> Path:
    """Pick the agenda path: CLI arg > ``$YASCHED_AGENDA`` > ``~/.yasched/agenda.yaml``."""
    if cli_value:
        return Path(cli_value).expanduser().resolve()
    env = os.environ.get(ENV_AGENDA)
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_AGENDA


def _walk_up_for(relative: str) -> Path | None:
    """Search this file's ancestors for *relative* (used to find repo resources)."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / relative
        if candidate.exists():
            return candidate
    return None


def find_web_dist() -> Path | None:
    """Locate the built SPA (``apps/web/dist``): env override, then repo layout."""
    env = os.environ.get(ENV_WEB_DIST)
    if env:
        p = Path(env).expanduser().resolve()
        return p if p.is_dir() else None
    found = _walk_up_for("apps/web/dist")
    return found if (found and found.is_dir()) else None


def find_personal_template() -> Path | None:
    return _walk_up_for("resources/personal_template/agenda.yaml")


# Fallback used by `yasched init` if the repo template cannot be located
# (e.g. installed as a wheel without the resources tree).
FALLBACK_TEMPLATE = """\
# Your personal yasched agenda. Edit freely, then run `yasched serve`.
# Full model reference: resources/teacher_example/ in the yasched repo.

default:
  attributes: { priority: 3, status: todo }
  layout:
    shape: { type: rounded, radius: 6px }

traits:
  urgent:
    attributes: { priority: 5 }
    layout: { pin: { color: red, icon: "🔥" } }

topics:
  - id: work
    name: Work
    tags: [work]
    layout: { background: { type: solid, color: "#3b82f6" } }
  - id: personal
    name: Personal
    tags: [personal]
    layout: { background: { type: solid, color: "#10b981" } }

events:
  - id: standup
    name: Daily standup
    topic_ids: [work]
    schedules:
      - { type: weekly, week_days: [monday, tuesday, wednesday, thursday, friday],
          start_time: "09:00", duration: 15m }

tasks:
  - id: welcome
    name: "Welcome to yasched — edit ~/.yasched/agenda.yaml"
    topic_ids: [personal]
    traits: [urgent]
    attributes: { deadline: today }
"""
