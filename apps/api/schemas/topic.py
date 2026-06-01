"""Topic read/write schemas."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from apps.api.schemas.common import LayoutSchema, layout_to_schema, schema_to_layout

if TYPE_CHECKING:
    from yasched.backending.Database import ResolvedTopic


class TopicSchema(BaseModel):
    """Read schema built from ResolvedTopic."""

    id: str
    name: str
    description: str | None
    tags: list[str]
    parent_ids: list[str]
    children_ids: list[str]
    effective_layout: LayoutSchema | None

    @staticmethod
    def from_resolved(topic: ResolvedTopic) -> TopicSchema:
        return TopicSchema(
            id=topic.id,
            name=topic.name,
            description=topic.description,
            tags=topic.effective_tags,
            parent_ids=[p.id for p in topic.parents],
            children_ids=[c.id for c in topic.children],
            effective_layout=layout_to_schema(topic.effective_layout),
        )


class TopicWriteSchema(BaseModel):
    """Write schema for POST (create) and PATCH (replace) operations."""

    id: str
    name: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parent_ids: list[str] = Field(default_factory=list)
    layout: LayoutSchema | str | None = None

    def to_topic(self) -> object:
        from yasched.coring.Topic import Topic

        return Topic(
            id=self.id,
            name=self.name,
            description=self.description,
            tags=self.tags,
            parent_ids=self.parent_ids,
            layout=schema_to_layout(self.layout),
        )
