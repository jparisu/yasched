"""Visual style container: background layers, border, icon, shape, pin, and Layout."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from yasched.utilizing.coloring.Color import Color


class BackgroundStyle(ABC):
    """Abstract background layer. Concrete subclasses represent distinct fill modes that
    can coexist independently when merging layouts from different sources."""


@dataclass(frozen=True)
class SolidBackground(BackgroundStyle):
    """Solid fill with a single color."""

    color: Color


@dataclass(frozen=True)
class GradientTopRightBackground(BackgroundStyle):
    """Gradient anchor color for the top-right corner."""

    color: Color


@dataclass(frozen=True)
class GradientBottomLeftBackground(BackgroundStyle):
    """Gradient anchor color for the bottom-left corner."""

    color: Color


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
class ShapeStyle:
    """Shape and corner style for an element."""

    type: str
    radius: str | None = None


@dataclass(frozen=True)
class PinStyle:
    """Point marker shown in spatial / map views."""

    color: Color
    icon: str | None = None


@dataclass(frozen=True)
class Layout:
    """Container for optional visual style layers."""

    id: str | None = None
    backgrounds: list[BackgroundStyle] = field(default_factory=list)
    border: BorderStyle | None = None
    icon: IconStyle | None = None
    shape: ShapeStyle | None = None
    pin: PinStyle | None = None
