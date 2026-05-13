"""Immutable RGBA color value."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """Immutable RGBA color with channels stored as floats in [0.0, 1.0]."""

    r: float
    g: float
    b: float
    a: float = 1.0

    def __post_init__(self) -> None:
        for name, val in (("r", self.r), ("g", self.g), ("b", self.b), ("a", self.a)):
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Color channel '{name}' must be in [0.0, 1.0], got {val!r}")

    @staticmethod
    def from_name(name: str) -> Color:
        from yasched.utilizing.coloring.SingletonColorRegistry import SingletonColorRegistry

        return SingletonColorRegistry.get_instance().get_color(name.lower())

    @staticmethod
    def from_hex(hex_str: str) -> Color:
        s = hex_str.strip().lstrip("#")
        if len(s) == 3:
            s = s[0] * 2 + s[1] * 2 + s[2] * 2
        if len(s) != 6:
            raise ValueError(f"Invalid hex color: {hex_str!r}")
        try:
            r = int(s[0:2], 16) / 255.0
            g = int(s[2:4], 16) / 255.0
            b = int(s[4:6], 16) / 255.0
        except ValueError as err:
            raise ValueError(f"Invalid hex color: {hex_str!r}") from err
        return Color(r=r, g=g, b=b)

    @staticmethod
    def from_rgb(r: int | float, g: int | float, b: int | float, a: int | float = 1.0) -> Color:
        def _norm(val: int | float, name: str) -> float:
            if isinstance(val, int):
                if not (0 <= val <= 255):
                    raise ValueError(f"Integer channel '{name}' must be in [0, 255], got {val!r}")
                return val / 255.0
            return float(val)

        return Color(r=_norm(r, "r"), g=_norm(g, "g"), b=_norm(b, "b"), a=float(a))

    def to_hex(self) -> str:
        return f"#{round(self.r * 255):02x}{round(self.g * 255):02x}{round(self.b * 255):02x}"

    def to_rgba_tuple(self) -> tuple[float, float, float, float]:
        return (self.r, self.g, self.b, self.a)

    def with_alpha(self, a: float) -> Color:
        return Color(r=self.r, g=self.g, b=self.b, a=a)
