"""FastAPI application: local API + static frontend, one process, no CORS.

The app binds to localhost by default and makes no outbound network calls.
The API speaks the unified v4 element model.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from yasched.backending.loading.ElementSerializer import ElementSerializer
from yasched.backending.validating.Validator import validate_database
from yasched.serving import config
from yasched.serving.state import AppState, UnknownEntityError
from yasched.serving.views import build_effort, build_payload

_NO_FRONTEND_HTML = """\
<!doctype html><html><head><title>yasched</title></head><body
 style="font-family:system-ui;max-width:40rem;margin:4rem auto;line-height:1.6">
<h1>yasched v4 is running</h1>
<p>The API is live at <a href="/api/elements">/api/elements</a>, but the frontend
has not been built yet.</p>
<pre>make web-build</pre>
<p>Then restart the server.</p>
</body></html>
"""


def _parse_date(value: str | None) -> datetime.date | None:
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=f"Invalid date: {value!r}") from err


def create_app(agenda_path: Path) -> FastAPI:
    """Build the FastAPI app bound to a specific database file."""
    state = AppState(agenda_path)
    app = FastAPI(title="yasched", version="4.0.0")

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "agenda": str(state.agenda_path),
            "exists": state.agenda_path.exists(),
            "multiFile": state.multi_file,
        }

    @app.get("/api/meta")
    def meta() -> dict[str, Any]:
        db = state.db
        return {
            "agenda": str(state.agenda_path),
            "multiFile": db.multi_file,
            "counts": {
                "topics": len(db.topics),
                "events": len(db.events),
                "tasks": len(db.tasks),
                "schedules": len(db.schedules),
            },
        }

    @app.get("/api/validate")
    def validate() -> dict[str, Any]:
        issues = [i.as_dict() for i in validate_database(state.db)]
        errors = sum(1 for i in issues if i["severity"] == "error")
        return {"issues": issues, "errorCount": errors, "warningCount": len(issues) - errors}

    @app.get("/api/elements")
    def elements(
        start: str | None = Query(default=None), end: str | None = Query(default=None)
    ) -> dict[str, Any]:
        return build_payload(state.db, _parse_date(start), _parse_date(end))

    @app.get("/api/effort")
    def effort(
        start: str | None = Query(default=None), end: str | None = Query(default=None)
    ) -> dict[str, Any]:
        return build_effort(state.db, _parse_date(start), _parse_date(end))

    @app.get("/api/elements/{element_id}")
    def get_element(element_id: str) -> dict[str, Any]:
        element = state.db.elements.get(element_id)
        if element is None:
            raise HTTPException(status_code=404, detail=f"No element '{element_id}'")
        return ElementSerializer.element_to_dict(element)

    @app.post("/api/elements")
    def create(spec: dict[str, Any] = Body(...)) -> dict[str, Any]:
        if not spec.get("id"):
            raise HTTPException(status_code=400, detail="An 'id' is required.")
        if spec["id"] in state.db.elements:
            raise HTTPException(status_code=409, detail=f"'{spec['id']}' already exists.")
        return _write(state, spec)

    @app.put("/api/elements/{element_id}")
    def update(element_id: str, spec: dict[str, Any] = Body(...)) -> dict[str, Any]:
        # Path id is authoritative; this is also the virtual -> real promotion path.
        return _write(state, {**spec, "id": element_id})

    @app.delete("/api/elements/{element_id}")
    def delete(element_id: str) -> dict[str, Any]:
        try:
            state.delete(element_id)
        except UnknownEntityError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        return {"ok": True, "id": element_id}

    @app.post("/api/reload")
    def reload() -> dict[str, Any]:
        state.reload()
        return {"reloaded": True, "agenda": str(state.agenda_path)}

    # Static frontend LAST so /api/* routes take precedence.
    dist = config.find_web_dist()
    if dist is not None:
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
    else:

        @app.get("/", response_class=HTMLResponse)
        def index() -> str:
            return _NO_FRONTEND_HTML

    return app


def _write(state: AppState, spec: dict[str, Any]) -> dict[str, Any]:
    try:
        element = state.upsert(spec)
    except (KeyError, ValueError) as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return {"ok": True, "id": element.id, "type": element.type.value}


def create_default_app() -> FastAPI:
    """Entry point for ``uvicorn yasched.serving.api:create_default_app --factory``."""
    return create_app(config.resolve_agenda_path())


def __getattr__(name: str) -> Any:  # pragma: no cover - thin lazy attribute
    if name == "app":
        return create_default_app()
    raise AttributeError(name)
