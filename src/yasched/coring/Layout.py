"""Visual style container (the ``layout`` field) and its component styles.

A ``Layout`` is a plain, frozen value object. Every field is optional; an unset
(``None``) field is resolved through the layout hierarchy by ``backending``
(own > attribute-layout > parents-in-order, first-defined-wins per field).

Field-level merge semantics live in ``backending.resolving``; this module only
holds values and knows how to (de)serialize itself.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from yasched.utilizing.coloring.Color import Color


@dataclass(frozen=True)
class Background:
    """Fill of the element. A second color turns the fill into a gradient."""

    color: Color
    gradient_color: Color | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"color": self.color.to_hex()}
        if self.gradient_color is not None:
            out["gradient_color"] = self.gradient_color.to_hex()
        return out


@dataclass(frozen=True)
class Border:
    """Border drawn around the element."""

    color: Color
    width: str = "1px"
    style: str = "solid"  # solid | dashed | dotted

    def to_dict(self) -> dict[str, Any]:
        return {"color": self.color.to_hex(), "width": self.width, "style": self.style}


@dataclass(frozen=True)
class Icon:
    """Icon decoration (an emoji or a named icon)."""

    type: str  # "emoji" | "name"
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "value": self.value}


@dataclass(frozen=True)
class Pin:
    """Map-pin style marker."""

    color: Color

    def to_dict(self) -> dict[str, Any]:
        return {"color": self.color.to_hex()}


@dataclass(frozen=True)
class Format:
    """Text formatting. Applied by default this version."""

    font: str | None = None
    font_size: str | None = None
    font_color: Color | None = None
    text_align: str | None = None  # left | center | right

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.font is not None:
            out["font"] = self.font
        if self.font_size is not None:
            out["font_size"] = self.font_size
        if self.font_color is not None:
            out["font_color"] = self.font_color.to_hex()
        if self.text_align is not None:
            out["text_align"] = self.text_align
        return out


@dataclass(frozen=True)
class Layout:
    """Visual style applied to any element. Every field is independently optional."""

    background: Background | None = None
    border: Border | None = None
    icon: Icon | None = None
    pin: Pin | None = None
    shape: str | None = None  # rectangle | rounded_rectangle | ellipse | diamond
    animation: str | None = None  # none | beep | rumble
    hover_animation: str | None = None  # none | highlight | pulse
    format: Format | None = None

    def is_empty(self) -> bool:
        return all(getattr(self, f.name) is None for f in fields(self))

    def merged_over(self, base: Layout | None) -> Layout:
        """Return a layout where each unset field falls back to *base*.

        ``self`` wins per field; ``base`` fills the fields ``self`` leaves as
        ``None``. This is the per-field first-defined-wins rule used everywhere.
        """
        if base is None:
            return self
        return Layout(
            **{
                f.name: (
                    own if (own := getattr(self, f.name)) is not None else getattr(base, f.name)
                )
                for f in fields(self)
            }
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.background is not None:
            out["background"] = self.background.to_dict()
        if self.border is not None:
            out["border"] = self.border.to_dict()
        if self.icon is not None:
            out["icon"] = self.icon.to_dict()
        if self.pin is not None:
            out["pin"] = self.pin.to_dict()
        if self.shape is not None:
            out["shape"] = self.shape
        if self.animation is not None:
            out["animation"] = self.animation
        if self.hover_animation is not None:
            out["hover_animation"] = self.hover_animation
        if self.format is not None and self.format.to_dict():
            out["format"] = self.format.to_dict()
        return out
