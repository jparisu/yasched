"""Data-quality check endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api import state as app_state
from apps.api.schemas.task import TaskSchema
from apps.api.state import AppState

router = APIRouter()


def _state() -> AppState:
    return app_state.get_state()


@router.get("/stale-links", response_model=list[TaskSchema])
def get_stale_links(st: AppState = Depends(_state)) -> list[TaskSchema]:
    return [TaskSchema.from_resolved(t) for t in st.interface.get_stale_event_links()]


@router.get("/stale-blocks", response_model=list[TaskSchema])
def get_stale_blocks(st: AppState = Depends(_state)) -> list[TaskSchema]:
    return [TaskSchema.from_resolved(t) for t in st.interface.get_stale_blocks()]
