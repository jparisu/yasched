"""In-memory container for a parsed v4 database.

The database is a single flat pool of :class:`Element` objects keyed by id, plus
the attribute definitions. This is the raw, *unresolved* view: ``direct_parents``
are still strings and no inheritance or generation has been applied.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from yasched.coring.AttributeDefinition import AttributeDefinition, builtin_definitions
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType

#: Id of the built-in root topic (ancestor of every element, holds defaults).
ALL_TOPIC_ID = "AllTopic"


@dataclass
class Database:
    """Every parsed element keyed by id, plus attribute definitions."""

    elements: dict[str, Element] = field(default_factory=dict)
    attribute_defs: dict[str, AttributeDefinition] = field(default_factory=builtin_definitions)
    #: Ids seen more than once while parsing (later definitions win).
    duplicate_ids: list[str] = field(default_factory=list)
    #: True when the source used xyml includes (so a save-back would flatten it).
    multi_file: bool = False

    def element(self, element_id: str) -> Element | None:
        return self.elements.get(element_id)

    def by_type(self, element_type: ElementType) -> list[Element]:
        return [e for e in self.elements.values() if e.type is element_type]

    @property
    def topics(self) -> list[Element]:
        return self.by_type(ElementType.TOPIC)

    @property
    def events(self) -> list[Element]:
        return self.by_type(ElementType.EVENT)

    @property
    def tasks(self) -> list[Element]:
        return self.by_type(ElementType.TASK)

    @property
    def schedules(self) -> list[Element]:
        return self.by_type(ElementType.SCHEDULE)

    def all_topic(self) -> Element:
        """The root topic. Created on demand if the document omitted it."""
        existing = self.elements.get(ALL_TOPIC_ID)
        if existing is None:
            existing = Element(id=ALL_TOPIC_ID, type=ElementType.TOPIC, attributes={"name": "All"})
            self.elements[ALL_TOPIC_ID] = existing
        return existing
