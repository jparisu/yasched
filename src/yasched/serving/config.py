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
# Your personal yasched agenda (v4). Edit freely, then run `yasched serve`.
# Everything is an Element; `directParents` drives inheritance (first = MainParent).
# Full model reference: resources/example_v4/ in the yasched repo.

elements:
  # AllTopic is the built-in root; customize it to set app-wide defaults.
  - id: AllTopic
    type: topic
    attributes: { name: All }
    layout: { shape: rounded_rectangle }

  - id: work
    type: topic
    directParents: [AllTopic]
    attributes: { name: Work }
    layout: { background: { color: "#3b82f6" } }

  - id: personal
    type: topic
    directParents: [AllTopic]
    attributes: { name: Personal }
    layout: { background: { color: "#10b981" } }

  - id: standup
    type: schedule
    directParents: [work]
    attributes:
      name: Daily standup
      generates: event
      kind: weekly
      weekDays: [mon, tue, wed, thu, fri]
      time: "09:00"
      duration: 15m

  - id: welcome
    type: task
    directParents: [personal]
    attributes:
      name: "Welcome to yasched — edit ~/.yasched/agenda.yaml"
      status: not-started
      priority: 5
      deadline: today
"""
