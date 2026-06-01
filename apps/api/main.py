"""FastAPI application entry point for yasched."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api import state as app_state
from apps.api.config import Config
from apps.api.routers import checks, events, health, schedule, tasks, topics
from yasched.backending.managing.ConsistencyError import ConsistencyError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app_state.init_state(Config.db_path)
    yield


app = FastAPI(
    title="yasched API",
    description="Read/write API over the yasched YAML scheduler.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ConsistencyError)
async def consistency_error_handler(request: Request, exc: ConsistencyError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(health.router)
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(topics.router, prefix="/topics", tags=["topics"])
app.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
app.include_router(checks.router, prefix="/checks", tags=["checks"])
