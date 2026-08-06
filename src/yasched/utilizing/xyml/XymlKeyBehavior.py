"""Enum describing what a directive key does when found in a YAML mapping."""

from __future__ import annotations

import enum


class XymlKeyBehavior(enum.Enum):
    """What the loader does when it encounters a directive key."""

    REPLACE = 1
    EXTEND = 2
