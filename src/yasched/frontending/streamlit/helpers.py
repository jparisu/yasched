"""Color and layout conversion utilities for the Streamlit frontend."""

from __future__ import annotations

from yasched.coring.Layout import Layout
from yasched.utilizing.coloring.Color import Color

# Default colors per task status
STATUS_BG: dict[str, str] = {
    "todo": "#e3f2fd",
    "in_progress": "#fff8e1",
    "done": "#e8f5e9",
    "cancelled": "#f5f5f5",
    "blocked": "#fce4ec",
}
STATUS_BORDER: dict[str, str] = {
    "todo": "#1976d2",
    "in_progress": "#f57c00",
    "done": "#388e3c",
    "cancelled": "#9e9e9e",
    "blocked": "#d32f2f",
}
STATUS_HEADER_BG: dict[str, str] = {
    "todo": "#1976d2",
    "in_progress": "#f57c00",
    "done": "#388e3c",
    "cancelled": "#9e9e9e",
    "blocked": "#d32f2f",
}
STATUS_EMOJI: dict[str, str] = {
    "todo": "📋",
    "in_progress": "⚙️",
    "done": "✅",
    "cancelled": "🚫",
    "blocked": "🔒",
}

# Rotating palette for topic→color mapping when no layout is defined
TOPIC_PALETTE = [
    "#4285f4",
    "#ea4335",
    "#fbbc04",
    "#34a853",
    "#ff6d00",
    "#46bdc6",
    "#7b1fa2",
    "#c2185b",
]


def color_to_css(color: Color) -> str:
    r, g, b = int(color.r * 255), int(color.g * 255), int(color.b * 255)
    return f"rgba({r},{g},{b},{color.a:.2f})"


def layout_bg_css(layout: Layout | None) -> str | None:
    """Return a CSS background value (solid color or gradient), or None."""
    if not layout or not layout.background:
        return None
    bg = layout.background
    if bg.colors and len(bg.colors) >= 2:
        stops = ", ".join(color_to_css(c) for c in bg.colors)
        return f"linear-gradient(135deg, {stops})"
    if bg.color:
        return color_to_css(bg.color)
    if bg.colors:
        return color_to_css(bg.colors[0])
    return None


def layout_border_css(layout: Layout | None) -> str:
    if not layout or not layout.border:
        return "1px solid #ddd"
    b = layout.border
    return f"{b.width} {b.type} {color_to_css(b.color)}"


def layout_icon(layout: Layout | None) -> str:
    if not layout or not layout.icon:
        return ""
    return layout.icon.value + " " if layout.icon.type == "emoji" else ""


def layout_primary_color(layout: Layout | None, fallback: str = "#4a90d9") -> str:
    """Return a single solid CSS color from a layout (ignores gradients)."""
    if not layout or not layout.background:
        return fallback
    bg = layout.background
    if bg.color:
        return color_to_css(bg.color)
    if bg.colors:
        return color_to_css(bg.colors[0])
    return fallback
