"""Task CRUD and query endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from apps.api import state as app_state
from apps.api.schemas.event import EventSchema
from apps.api.schemas.task import TaskSchema, TaskWriteSchema
from apps.api.state import AppState
from yasched.backending.managing.ConsistencyError import ConsistencyError

router = APIRouter()


def _state() -> AppState:
    return app_state.get_state()


# ---------------------------------------------------------------------------
# Derived lists (must come before /{task_id} to avoid routing conflicts)
# ---------------------------------------------------------------------------


@router.get("/deadlines", response_model=list[TaskSchema])
def get_deadlines(
    days_ahead: int = Query(default=7, ge=1),
    st: AppState = Depends(_state),
) -> list[TaskSchema]:
    tasks = st.interface.get_upcoming_deadlines(days_ahead=days_ahead)
    return [TaskSchema.from_resolved(t) for t in tasks]


@router.get("/overdue", response_model=list[TaskSchema])
def get_overdue(st: AppState = Depends(_state)) -> list[TaskSchema]:
    return [TaskSchema.from_resolved(t) for t in st.interface.get_overdue_tasks()]


@router.get("/blocked", response_model=list[TaskSchema])
def get_blocked(st: AppState = Depends(_state)) -> list[TaskSchema]:
    return [TaskSchema.from_resolved(t) for t in st.interface.get_blocked_tasks()]


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


@router.get("", response_model=list[TaskSchema])
def list_tasks(
    status: str | None = Query(default=None),
    topic_id: str | None = Query(default=None),
    include_subtopics: bool = Query(default=False),
    tag: str | None = Query(default=None),
    search: str | None = Query(default=None),
    min_priority: int | None = Query(default=None),
    max_priority: int | None = Query(default=None),
    st: AppState = Depends(_state),
) -> list[TaskSchema]:
    from yasched.coring._shared import TaskStatus

    if status is not None:
        try:
            tasks = st.interface.get_tasks_by_status(TaskStatus(status))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Unknown status: {status!r}") from None
    elif topic_id is not None:
        if topic_id not in {t.id for t in st.interface.all_topics()}:
            raise HTTPException(status_code=404, detail=f"Topic {topic_id!r} not found")
        tasks = st.interface.get_tasks_by_topic(topic_id, include_subtopics=include_subtopics)
    elif tag is not None:
        tasks = st.interface.get_tasks_with_tag(tag)
    elif search is not None:
        tasks = st.interface.search_tasks(search)
    elif min_priority is not None or max_priority is not None:
        tasks = st.interface.get_tasks_by_priority(
            min_priority=min_priority, max_priority=max_priority
        )
    else:
        tasks = st.interface.all_tasks()

    return [TaskSchema.from_resolved(t) for t in tasks]


@router.post("", response_model=TaskSchema, status_code=201)
def create_task(body: TaskWriteSchema, st: AppState = Depends(_state)) -> TaskSchema:
    if any(t.id == body.id for t in st.raw_db.tasks):
        raise HTTPException(status_code=409, detail=f"Task {body.id!r} already exists")
    try:
        task = body.to_task()
        new_db = st.append_task(task)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return TaskSchema.from_resolved(st.interface.get_task(body.id))


# ---------------------------------------------------------------------------
# Single entity
# ---------------------------------------------------------------------------


@router.get("/{task_id}", response_model=TaskSchema)
def get_task(task_id: str, st: AppState = Depends(_state)) -> TaskSchema:
    try:
        return TaskSchema.from_resolved(st.interface.get_task(task_id))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None


@router.patch("/{task_id}", response_model=TaskSchema)
def update_task(task_id: str, body: TaskWriteSchema, st: AppState = Depends(_state)) -> TaskSchema:
    if not any(t.id == task_id for t in st.raw_db.tasks):
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None
    if body.id != task_id:
        raise HTTPException(status_code=422, detail="Body id must match path task_id")
    try:
        task = body.to_task()
        new_db = st.replace_task(task)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return TaskSchema.from_resolved(st.interface.get_task(task_id))


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, st: AppState = Depends(_state)) -> Response:
    if not any(t.id == task_id for t in st.raw_db.tasks):
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None
    try:
        new_db = st.remove_task(task_id)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Sub-resources
# ---------------------------------------------------------------------------


@router.get("/{task_id}/children", response_model=list[TaskSchema])
def get_task_children(task_id: str, st: AppState = Depends(_state)) -> list[TaskSchema]:
    try:
        return [TaskSchema.from_resolved(t) for t in st.interface.get_task_children(task_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None


@router.get("/{task_id}/subtree", response_model=list[TaskSchema])
def get_task_subtree(task_id: str, st: AppState = Depends(_state)) -> list[TaskSchema]:
    try:
        return [TaskSchema.from_resolved(t) for t in st.interface.get_task_subtree(task_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None


@router.get("/{task_id}/events", response_model=list[EventSchema])
def get_task_events(task_id: str, st: AppState = Depends(_state)) -> list[EventSchema]:
    try:
        return [EventSchema.from_resolved(e) for e in st.interface.get_task_events(task_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None


@router.get("/{task_id}/blocking", response_model=list[TaskSchema])
def get_blocking_tasks(task_id: str, st: AppState = Depends(_state)) -> list[TaskSchema]:
    try:
        return [TaskSchema.from_resolved(t) for t in st.interface.get_blocking_tasks(task_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task {task_id!r} not found") from None
