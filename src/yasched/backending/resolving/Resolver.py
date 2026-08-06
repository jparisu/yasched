"""Resolve the inheritance model into effective values.

Three derived notions drive everything:

* ``Parents(E)`` — pre-order DFS over ``direct_parents`` with one global visited
  set (branch-first: a branch is fully expanded before the next sibling).
  ``AllTopic`` is appended last so defaults always resolve.
* ``MainParent(E)`` — ``Parents(E)[0]`` (the first direct parent).
* ``Topic(E)`` — the first ``topic``-typed element in ``Parents(E)``.

Attribute resolution: own value wins, else the first parent in ``Parents`` that
defines it (skipping non-inheriting attributes such as ``connections``).

Layout resolution, per field, first-defined-wins::

    element's own  >  attribute-layout  >  Parents (in Parents order)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from yasched.backending.Database import ALL_TOPIC_ID, Database
from yasched.coring.AttributeDefinition import NON_INHERITING
from yasched.coring.Connection import Connection
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Layout


@dataclass
class ResolvedElement:
    """An element with its effective (post-inheritance) values."""

    id: str
    type: ElementType
    attributes: dict[str, Any] = field(default_factory=dict)
    layout: Layout = field(default_factory=Layout)
    parents: list[str] = field(default_factory=list)
    main_parent: str | None = None
    topic: str | None = None
    virtual: bool = False

    @property
    def name(self) -> Any:
        return self.attributes.get("name")

    @property
    def description(self) -> Any:
        return self.attributes.get("description")

    def connections(self) -> list[Connection]:
        return [Connection.from_raw(c) for c in (self.attributes.get("connections") or [])]


class Resolver:
    """Computes effective values for every element in a :class:`Database`."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._parents_cache: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    # Linearization
    # ------------------------------------------------------------------

    def parents(self, element_id: str) -> list[str]:
        """Ordered, de-duplicated ancestors of *element_id* (excludes itself)."""
        if element_id in self._parents_cache:
            return self._parents_cache[element_id]

        result: list[str] = []
        visited: set[str] = {element_id}

        def dfs(current_id: str) -> None:
            element = self._db.elements.get(current_id)
            if element is None:
                return
            for parent_id in element.direct_parents:
                if parent_id in visited:
                    continue
                visited.add(parent_id)
                if parent_id in self._db.elements:
                    result.append(parent_id)
                    dfs(parent_id)

        dfs(element_id)

        # AllTopic is the implicit last parent of every element (defaults).
        if element_id != ALL_TOPIC_ID and ALL_TOPIC_ID not in visited:
            if ALL_TOPIC_ID in self._db.elements:
                result.append(ALL_TOPIC_ID)

        self._parents_cache[element_id] = result
        return result

    def main_parent(self, element_id: str) -> str | None:
        parents = self.parents(element_id)
        return parents[0] if parents else None

    def topic_of(self, element_id: str) -> str | None:
        for parent_id in self.parents(element_id):
            parent = self._db.elements.get(parent_id)
            if parent is not None and parent.type is ElementType.TOPIC:
                return parent_id
        return None

    # ------------------------------------------------------------------
    # Value resolution
    # ------------------------------------------------------------------

    def _resolve_attributes(self, element: Element) -> dict[str, Any]:
        merged: dict[str, Any] = dict(element.attributes)  # own values win
        for parent_id in self.parents(element.id):
            parent = self._db.elements.get(parent_id)
            if parent is None:
                continue
            for key, value in parent.attributes.items():
                if key in merged or not self._inheritable_into(key, element.type):
                    continue
                merged[key] = value
        return merged

    def _inheritable_into(self, key: str, into_type: ElementType) -> bool:
        """Whether attribute *key* may be inherited into an element of *into_type*.

        Non-inheriting attributes (e.g. ``connections``) never flow. Otherwise a
        definition's ``applies_to`` scopes inheritance, so schedule-only config
        never leaks into a generated event/task.
        """
        if key in NON_INHERITING:
            return False
        definition = self._db.attribute_defs.get(key)
        if definition is None:
            return True  # open attribute, no schema — allow
        return definition.inherits and definition.applies_to_type(into_type)

    def _attribute_layout(self, attributes: dict[str, Any]) -> Layout | None:
        """Merge the layouts of every present attribute-definition (first wins per field)."""
        layout: Layout | None = None
        for name in attributes:  # element attribute order
            definition = self._db.attribute_defs.get(name)
            if definition is None or definition.layout is None:
                continue
            layout = definition.layout if layout is None else layout.merged_over(definition.layout)
        return layout

    def _resolve_layout(self, element: Element, attributes: dict[str, Any]) -> Layout:
        # own > attribute-layout > parents (in order)
        layout = element.layout or Layout()
        attribute_layout = self._attribute_layout(attributes)
        if attribute_layout is not None:
            layout = layout.merged_over(attribute_layout)
        for parent_id in self.parents(element.id):
            parent = self._db.elements.get(parent_id)
            if parent is not None and parent.layout is not None:
                layout = layout.merged_over(parent.layout)
        return layout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(self, element: Element) -> ResolvedElement:
        attributes = self._resolve_attributes(element)
        return ResolvedElement(
            id=element.id,
            type=element.type,
            attributes=attributes,
            layout=self._resolve_layout(element, attributes),
            parents=self.parents(element.id),
            main_parent=self.main_parent(element.id),
            topic=self.topic_of(element.id),
            virtual=element.virtual,
        )

    def resolve_id(self, element_id: str) -> ResolvedElement | None:
        element = self._db.elements.get(element_id)
        return None if element is None else self.resolve(element)

    def resolve_all(self) -> dict[str, ResolvedElement]:
        return {eid: self.resolve(e) for eid, e in self._db.elements.items()}
