"""Parse an (x)yml document into a :class:`Database` of v4 ``Element`` objects.

Parsing is lenient: unknown keys are ignored and missing optional keys fall back
to sensible defaults. Reading still supports xyml ``__file__`` / ``__ext__``
includes for authoring; the app flattens to a single file on first save-back.

Document shape::

    attributes:            # optional: user attribute DEFINITIONS
      difficulty: { type: number, min: 0, max: 10, applies_to: [task] }
    elements:              # one flat list; `type` discriminates
      - id: math-101
        type: topic
        directParents: [AllTopic]
        attributes: { name: "Math 101" }
        layout: { background: { color: "#3b82f6" } }
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from yasched.backending.Database import Database
from yasched.coring.AttributeDefinition import AttributeDefinition, ValueType, builtin_definitions
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Background, Border, Format, Icon, Layout, Pin
from yasched.utilizing.coloring.Color import Color
from yasched.utilizing.xyml.XymlLoader import XymlLoader


class DatabaseLoadError(ValueError):
    """Raised when a document cannot be parsed into a Database."""


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_color(value: Any) -> Color:
    if isinstance(value, Color):
        return value
    s = str(value).strip()
    return Color.from_hex(s) if s.startswith("#") else Color.from_name(s)


def _opt_color(value: Any) -> Color | None:
    return None if value is None else _parse_color(value)


class ElementLoader:
    """Loads and parses a v4 database document."""

    @staticmethod
    def load(path: str | Path) -> Database:
        text = Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""
        multi_file = "__file__" in text or "__ext__" in text
        doc = XymlLoader.load(path)
        db = ElementLoader.from_dict(doc)
        db.multi_file = multi_file
        return db

    @staticmethod
    def loads(content: str, base_path: str | Path | None = None) -> Database:
        multi_file = "__file__" in content or "__ext__" in content
        doc = XymlLoader.loads(content, base_path)
        db = ElementLoader.from_dict(doc)
        db.multi_file = multi_file
        return db

    @staticmethod
    def from_dict(doc: Any) -> Database:
        if doc is None:
            db = Database()
            db.all_topic()
            return db
        if not isinstance(doc, dict):
            raise DatabaseLoadError(
                f"Top-level document must be a mapping, got {type(doc).__name__}"
            )

        db = Database(attribute_defs=builtin_definitions())
        for name, raw in (doc.get("attributes") or {}).items():
            db.attribute_defs[name] = ElementLoader._parse_attribute_def(name, raw)

        for raw in _as_list(doc.get("elements")):
            element = ElementLoader.parse_element(raw)
            if element.id in db.elements:
                db.duplicate_ids.append(element.id)
            db.elements[element.id] = element

        db.all_topic()  # guarantee the root exists
        return db

    # ------------------------------------------------------------------
    # Element
    # ------------------------------------------------------------------

    @staticmethod
    def parse_element(raw: Any) -> Element:
        if not isinstance(raw, dict):
            raise DatabaseLoadError(f"Each element must be a mapping, got {type(raw).__name__}")
        if "id" not in raw:
            raise DatabaseLoadError(f"Each element requires an 'id'; got keys {sorted(raw)}")
        if "type" not in raw:
            raise DatabaseLoadError(f"Element {raw['id']!r} requires a 'type'")

        # Accept both `directParents` and `direct_parents`.
        parents_raw = raw.get("directParents", raw.get("direct_parents"))
        attributes = dict(raw.get("attributes") or {})
        # `name`/`description` may be given at top level for convenience.
        if "name" in raw and "name" not in attributes:
            attributes["name"] = raw["name"]
        if "description" in raw and "description" not in attributes:
            attributes["description"] = raw["description"]

        return Element(
            id=str(raw["id"]),
            type=ElementType.from_string(str(raw["type"])),
            direct_parents=[str(p) for p in _as_list(parents_raw)],
            layout=ElementLoader.parse_layout(raw.get("layout")),
            attributes=attributes,
        )

    # ------------------------------------------------------------------
    # Attribute definitions
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_attribute_def(name: str, raw: Any) -> AttributeDefinition:
        raw = raw or {}
        applies = tuple(ElementType.from_string(str(t)) for t in _as_list(raw.get("applies_to")))
        return AttributeDefinition(
            name=name,
            value_type=ValueType.from_string(str(raw.get("type", "string"))),
            applies_to=applies,
            enum_values=tuple(str(v) for v in _as_list(raw.get("enum_values"))),
            minimum=(float(raw["min"]) if raw.get("min") is not None else None),
            maximum=(float(raw["max"]) if raw.get("max") is not None else None),
            layout=ElementLoader.parse_layout(raw.get("layout")),
            inherits=bool(raw.get("inherits", True)),
            builtin=False,
        )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    @staticmethod
    def parse_layout(raw: Any) -> Layout | None:
        if not raw:
            return None
        if not isinstance(raw, dict):
            raise DatabaseLoadError(f"layout must be a mapping, got {type(raw).__name__}")

        background = None
        if raw.get("background"):
            b = raw["background"]
            background = Background(
                color=_parse_color(b.get("color")),
                gradient_color=_opt_color(b.get("gradient_color")),
            )

        border = None
        if raw.get("border"):
            b = raw["border"]
            border = Border(
                color=_parse_color(b.get("color")),
                width=str(b.get("width", "1px")),
                style=str(b.get("style", "solid")),
            )

        icon = None
        if raw.get("icon"):
            i = raw["icon"]
            icon = Icon(type=str(i.get("type", "emoji")), value=str(i.get("value", "")))

        pin = None
        if raw.get("pin"):
            pin = Pin(color=_parse_color(raw["pin"].get("color")))

        fmt = None
        if raw.get("format"):
            f = raw["format"]
            fmt = Format(
                font=(str(f["font"]) if f.get("font") else None),
                font_size=(str(f["font_size"]) if f.get("font_size") else None),
                font_color=_opt_color(f.get("font_color")),
                text_align=(str(f["text_align"]) if f.get("text_align") else None),
            )

        return Layout(
            background=background,
            border=border,
            icon=icon,
            pin=pin,
            shape=(str(raw["shape"]) if raw.get("shape") else None),
            animation=(str(raw["animation"]) if raw.get("animation") else None),
            hover_animation=(str(raw["hover_animation"]) if raw.get("hover_animation") else None),
            format=fmt,
        )
