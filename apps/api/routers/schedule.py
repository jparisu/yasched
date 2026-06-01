"""Schedule view endpoints: daily, weekly, range, conflicts."""

from __future__ import annotations

import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api import state as app_state
from apps.api.schemas.views import DailyViewSchema, EventConflictSchema, WeeklyViewSchema
from apps.api.state import AppState

router = APIRouter()


def _state() -> AppState:
    return app_state.get_state()


@router.get("/daily", response_model=DailyViewSchema)
def get_daily(
    date: datetime.date = Query(default_factory=datetime.date.today),
    st: AppState = Depends(_state),
) -> DailyViewSchema:
    return DailyViewSchema.from_view(st.interface.get_daily_schedule(date))


@router.get("/weekly", response_model=WeeklyViewSchema)
def get_weekly(
    week_start: datetime.date | None = Query(default=None),
    st: AppState = Depends(_state),
) -> WeeklyViewSchema:
    if week_start is None:
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
    return WeeklyViewSchema.from_view(st.interface.get_weekly_schedule(week_start))


@router.get("/range", response_model=list[DailyViewSchema])
def get_range(
    start: datetime.date = Query(...),
    end: datetime.date = Query(...),
    st: AppState = Depends(_state),
) -> list[DailyViewSchema]:
    if start > end:
        raise HTTPException(status_code=422, detail="start must be <= end")
    days = []
    current = start
    while current <= end:
        days.append(DailyViewSchema.from_view(st.interface.get_daily_schedule(current)))
        current += datetime.timedelta(days=1)
    return days


@router.get("/conflicts", response_model=list[EventConflictSchema])
def get_conflicts(
    start: datetime.date | None = Query(default=None),
    end: datetime.date | None = Query(default=None),
    st: AppState = Depends(_state),
) -> list[EventConflictSchema]:
    conflicts = st.interface.get_conflicts(start=start, end=end)
    return [EventConflictSchema.from_conflict(c) for c in conflicts]
