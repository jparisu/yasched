"""Topic CRUD and query endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from apps.api import state as app_state
from apps.api.schemas.task import TaskSchema
from apps.api.schemas.topic import TopicSchema, TopicWriteSchema
from apps.api.state import AppState
from yasched.backending.managing.ConsistencyError import ConsistencyError

router = APIRouter()


def _state() -> AppState:
    return app_state.get_state()


@router.get("/roots", response_model=list[TopicSchema])
def get_root_topics(st: AppState = Depends(_state)) -> list[TopicSchema]:
    return [TopicSchema.from_resolved(t) for t in st.interface.get_root_topics()]


@router.get("", response_model=list[TopicSchema])
def list_topics(
    tag: str | None = Query(default=None),
    search: str | None = Query(default=None),
    st: AppState = Depends(_state),
) -> list[TopicSchema]:
    if tag is not None:
        topics = st.interface.get_topics_with_tag(tag)
    elif search is not None:
        topics = st.interface.search_topics(search)
    else:
        topics = st.interface.all_topics()
    return [TopicSchema.from_resolved(t) for t in topics]


@router.post("", response_model=TopicSchema, status_code=201)
def create_topic(body: TopicWriteSchema, st: AppState = Depends(_state)) -> TopicSchema:
    if any(t.id == body.id for t in st.raw_db.topics):
        raise HTTPException(status_code=409, detail=f"Topic {body.id!r} already exists")
    try:
        topic = body.to_topic()
        new_db = st.append_topic(topic)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return TopicSchema.from_resolved(st.interface.get_topic(body.id))


@router.get("/{topic_id}", response_model=TopicSchema)
def get_topic(topic_id: str, st: AppState = Depends(_state)) -> TopicSchema:
    try:
        return TopicSchema.from_resolved(st.interface.get_topic(topic_id))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None


@router.patch("/{topic_id}", response_model=TopicSchema)
def update_topic(
    topic_id: str, body: TopicWriteSchema, st: AppState = Depends(_state)
) -> TopicSchema:
    if not any(t.id == topic_id for t in st.raw_db.topics):
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None
    if body.id != topic_id:
        raise HTTPException(status_code=422, detail="Body id must match path topic_id")
    try:
        topic = body.to_topic()
        new_db = st.replace_topic(topic)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return TopicSchema.from_resolved(st.interface.get_topic(topic_id))


@router.delete("/{topic_id}", status_code=204)
def delete_topic(topic_id: str, st: AppState = Depends(_state)) -> Response:
    if not any(t.id == topic_id for t in st.raw_db.topics):
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None
    try:
        new_db = st.remove_topic(topic_id)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return Response(status_code=204)


@router.get("/{topic_id}/children", response_model=list[TopicSchema])
def get_topic_children(topic_id: str, st: AppState = Depends(_state)) -> list[TopicSchema]:
    try:
        return [TopicSchema.from_resolved(t) for t in st.interface.get_topic_children(topic_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None


@router.get("/{topic_id}/subtree", response_model=list[TopicSchema])
def get_topic_subtree(topic_id: str, st: AppState = Depends(_state)) -> list[TopicSchema]:
    try:
        return [TopicSchema.from_resolved(t) for t in st.interface.get_topic_subtree(topic_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None


@router.get("/{topic_id}/ancestors", response_model=list[TopicSchema])
def get_topic_ancestors(topic_id: str, st: AppState = Depends(_state)) -> list[TopicSchema]:
    try:
        return [TopicSchema.from_resolved(t) for t in st.interface.get_topic_ancestors(topic_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None


@router.get("/{topic_id}/tasks", response_model=list[TaskSchema])
def get_topic_tasks(
    topic_id: str,
    include_subtopics: bool = Query(default=False),
    st: AppState = Depends(_state),
) -> list[TaskSchema]:
    try:
        tasks = st.interface.get_tasks_by_topic(topic_id, include_subtopics=include_subtopics)
        return [TaskSchema.from_resolved(t) for t in tasks]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found") from None
