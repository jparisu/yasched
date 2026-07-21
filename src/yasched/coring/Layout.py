"""Visual style container (the ``layout`` bag) and its component styles.

A ``Layout`` is a plain data holder. Field-level merge semantics (composing
backgrounds by type, higher-layer-wins for the rest) live in ``backending``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from yasched.utilizing.coloring.Color import Color


@dataclass(frozen=True)
class Background:
    """One background layer. ``type`` discriminates the visual kind.

    Known types: ``solid``, ``gradient_tr`` (anchor top-right),
    ``gradient_bl`` (anchor bottom-left). Distinct types compose; the same type
    from a higher layer replaces the lower one.
    """

    type: str
    color: Color


@dataclass(frozen=True)
class Border:
    """Border drawn around the element."""

    type: str
    width: str
    color: Color


@dataclass(frozen=True)
class Icon:
    """Icon decoration (emoji or named)."""

    type: str  # "emoji" | "name"
    value: str


@dataclass(frozen=True)
class Pin:
    """Map-pin style marker."""

    color: Color
    icon: str | None = None


@dataclass(frozen=True)
class Shape:
    """Overall card shape."""

    type: str  # "rectangle" | "rounded" | "pill" | "trapezoid"
    radius: str | None = None


@dataclass(frozen=True)
class Layout:
    """Visual style applied to a topic, event, or task.

    All fields optional; an empty ``Layout`` contributes nothing to a merge.
    """

    backgrounds: list[Background] = field(default_factory=list)
    border: Border | None = None
    icon: Icon | None = None
    pin: Pin | None = None
    shape: Shape | None = None

    def is_empty(self) -> bool:
        return (
            not self.backgrounds
            and self.border is None
            and self.icon is None
            and self.pin is None
            and self.shape is None
        )
