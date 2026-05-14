"""Visual style container: BackgroundStyle, BorderStyle, IconStyle, Layout."""

from __future__ import annotations

from dataclasses import dataclass

from yasched.utilizing.coloring.Color import Color


@dataclass(frozen=True)
class BackgroundStyle:
    """Background fill style for a topic, event, or task."""

    type: str
    color: Color | None = None
    colors: list[Color] | None = None


@dataclass(frozen=True)
class BorderStyle:
    """Border drawn around an element."""

    type: str
    width: str
    color: Color


@dataclass(frozen=True)
class IconStyle:
    """Icon decoration shown on an element."""

    type: str
    value: str


@dataclass(frozen=True)
class Layout:
    """Container for optional visual style sub-objects."""

    id: str | None = None
    background: BackgroundStyle | None = None
    border: BorderStyle | None = None
    icon: IconStyle | None = None
