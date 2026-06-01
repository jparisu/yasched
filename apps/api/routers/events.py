"""Event CRUD and query endpoints."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from apps.api import state as app_state
from apps.api.schemas.event import EventSchema, EventWriteSchema
from apps.api.state import AppState
from yasched.backending.managing.ConsistencyError import ConsistencyError

router = APIRouter()


def _state() -> AppState:
    return app_state.get_state()


@router.get("", response_model=list[EventSchema])
def list_events(
    start: datetime.date | None = Query(default=None),
    end: datetime.date | None = Query(default=None),
    st: AppState = Depends(_state),
) -> list[EventSchema]:
    if start is not None and end is not None:
        events = st.interface.get_events_in_range(start, end)
    else:
        events = st.interface.all_events()
    return [EventSchema.from_resolved(e) for e in events]


@router.post("", response_model=EventSchema, status_code=201)
def create_event(body: EventWriteSchema, st: AppState = Depends(_state)) -> EventSchema:
    if any(e.id == body.id for e in st.raw_db.events):
        raise HTTPException(status_code=409, detail=f"Event {body.id!r} already exists")
    try:
        event = body.to_event()
        new_db = st.append_event(event)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return EventSchema.from_resolved(st.interface.get_event(body.id))


@router.get("/{event_id}", response_model=EventSchema)
def get_event(event_id: str, st: AppState = Depends(_state)) -> EventSchema:
    try:
        return EventSchema.from_resolved(st.interface.get_event(event_id))
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Event {event_id!r} not found") from None


@router.patch("/{event_id}", response_model=EventSchema)
def update_event(
    event_id: str, body: EventWriteSchema, st: AppState = Depends(_state)
) -> EventSchema:
    if not any(e.id == event_id for e in st.raw_db.events):
        raise HTTPException(status_code=404, detail=f"Event {event_id!r} not found") from None
    if body.id != event_id:
        raise HTTPException(status_code=422, detail="Body id must match path event_id")
    try:
        event = body.to_event()
        new_db = st.replace_event(event)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return EventSchema.from_resolved(st.interface.get_event(event_id))


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: str, st: AppState = Depends(_state)) -> Response:
    if not any(e.id == event_id for e in st.raw_db.events):
        raise HTTPException(status_code=404, detail=f"Event {event_id!r} not found") from None
    try:
        new_db = st.remove_event(event_id)
        st.commit(new_db)
    except ConsistencyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return Response(status_code=204)
