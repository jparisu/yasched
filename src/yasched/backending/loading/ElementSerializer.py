"""Serialize a :class:`Database` back to a single canonical YAML document.

Only real (non-virtual) elements are written. Multi-file xyml sources are
flattened into one file the first time the app saves (per the v4 spec).
"""

from __future__ import annotations

from typing import Any

import yaml

from yasched.backending.Database import ALL_TOPIC_ID, Database
from yasched.coring.AttributeDefinition import AttributeDefinition
from yasched.coring.Element import Element


class ElementSerializer:
    """Turns a Database into YAML text (and elements into plain dicts)."""

    @staticmethod
    def element_to_dict(element: Element) -> dict[str, Any]:
        out: dict[str, Any] = {"id": element.id, "type": element.type.value}
        if element.direct_parents:
            out["directParents"] = list(element.direct_parents)
        if element.attributes:
            out["attributes"] = _plain(element.attributes)
        if element.layout is not None and not element.layout.is_empty():
            out["layout"] = element.layout.to_dict()
        return out

    @staticmethod
    def _def_to_dict(d: AttributeDefinition) -> dict[str, Any]:
        out: dict[str, Any] = {"type": d.value_type.value}
        if d.applies_to:
            out["applies_to"] = [t.value for t in d.applies_to]
        if d.enum_values:
            out["enum_values"] = list(d.enum_values)
        if d.minimum is not None:
            out["min"] = d.minimum
        if d.maximum is not None:
            out["max"] = d.maximum
        if not d.inherits:
            out["inherits"] = False
        if d.layout is not None and not d.layout.is_empty():
            out["layout"] = d.layout.to_dict()
        return out

    @staticmethod
    def to_dict(db: Database) -> dict[str, Any]:
        doc: dict[str, Any] = {}
        user_defs = {n: d for n, d in db.attribute_defs.items() if not d.builtin}
        if user_defs:
            doc["attributes"] = {n: ElementSerializer._def_to_dict(d) for n, d in user_defs.items()}
        doc["elements"] = [
            ElementSerializer.element_to_dict(e) for e in db.elements.values() if _should_persist(e)
        ]
        return doc

    @staticmethod
    def to_yaml(db: Database) -> str:
        return yaml.safe_dump(
            ElementSerializer.to_dict(db),
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )


def _should_persist(element: Element) -> bool:
    """Virtual elements are never written; AllTopic only if the user customized it."""
    if element.virtual:
        return False
    if element.id != ALL_TOPIC_ID:
        return True
    return _root_customized(element)


def _root_customized(root: Element) -> bool:
    """Write AllTopic only if the user gave it more than the default name."""
    attrs = {k: v for k, v in root.attributes.items() if not (k == "name" and v == "All")}
    return bool(attrs) or root.layout is not None or bool(root.direct_parents)


def _plain(value: Any) -> Any:
    """Recursively convert value objects to YAML-friendly primitives."""
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "to_iso"):  # Date
        return value.to_iso()
    return value
