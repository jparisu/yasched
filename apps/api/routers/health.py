"""GET /health — database status and summary."""

from __future__ import annotations

from fastapi import APIRouter

from apps.api import state as app_state
from apps.api.schemas.summary import HealthSchema, StatusSummarySchema
from yasched.coring._shared import TaskStatus

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthSchema)
def get_health() -> HealthSchema:
    try:
        st = app_state.get_state()
    except RuntimeError:
        return HealthSchema(
            db_loaded=False,
            task_count=0,
            event_count=0,
            topic_count=0,
            status_summary=StatusSummarySchema(
                todo=0, in_progress=0, done=0, cancelled=0, blocked=0
            ),
            errors=["Database not loaded"],
        )

    summary = st.interface.task_status_summary()
    return HealthSchema(
        db_loaded=True,
        task_count=len(st.interface.all_tasks()),
        event_count=len(st.interface.all_events()),
        topic_count=len(st.interface.all_topics()),
        status_summary=StatusSummarySchema(
            todo=summary.get(TaskStatus.TODO, 0),
            in_progress=summary.get(TaskStatus.IN_PROGRESS, 0),
            done=summary.get(TaskStatus.DONE, 0),
            cancelled=summary.get(TaskStatus.CANCELLED, 0),
            blocked=summary.get(TaskStatus.BLOCKED, 0),
        ),
        errors=[],
    )
