"""FastAPI application: local API + static frontend, one process, no CORS.

The app binds to localhost by default and makes no outbound network calls.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, cast

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer
from yasched.backending.validating.Validator import validate_database
from yasched.serving import config
from yasched.serving.state import AppState, ReadOnlyError, UnknownEntityError
from yasched.serving.views import build_graph, build_payload, build_timetable

_WRITE_KINDS = {"topics", "events", "tasks"}

_NO_FRONTEND_HTML = """\
<!doctype html><html><head><title>yasched</title></head><body
 style="font-family:system-ui;max-width:40rem;margin:4rem auto;line-height:1.6">
<h1>yasched is running</h1>
<p>The API is live at <a href="/api/agenda">/api/agenda</a>, but the frontend
has not been built yet.</p>
<pre>make web-build     # or: cd apps/web &amp;&amp; npm install &amp;&amp; npm run build</pre>
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
    """Build the FastAPI app bound to a specific agenda file."""
    state = AppState(agenda_path)
    app = FastAPI(title="yasched", version="3.0.0")

    def payload(start: str | None, end: str | None) -> dict[str, Any]:
        return build_payload(state.db, _parse_date(start), _parse_date(end))

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "agenda": str(state.agenda_path),
            "exists": state.agenda_path.exists(),
            "readOnly": state.read_only,
        }

    @app.get("/api/meta")
    def meta() -> dict[str, Any]:
        db = state.db
        return {
            "agenda": str(state.agenda_path),
            "readOnly": state.read_only,
            "traits": sorted(db.traits),
            "topics": [{"id": t.id, "name": t.name} for t in db.topics.values()],
            "tasks": [{"id": t.id, "name": t.name} for t in db.tasks.values()],
            "events": [{"id": e.id, "name": e.name} for e in db.events.values()],
        }

    @app.get("/api/validate")
    def validate() -> dict[str, Any]:
        issues = [i.as_dict() for i in validate_database(state.db)]
        errors = sum(1 for i in issues if i["severity"] == "error")
        return {
            "issues": issues,
            "errorCount": errors,
            "warningCount": len(issues) - errors,
        }

    @app.get("/api/timetable")
    def timetable() -> list[dict[str, Any]]:
        return build_timetable(state.db)

    @app.get("/api/graph")
    def graph() -> dict[str, Any]:
        return build_graph(state.db)

    @app.get("/api/agenda")
    def agenda(
        start: str | None = Query(default=None), end: str | None = Query(default=None)
    ) -> dict[str, Any]:
        return payload(start, end)

    @app.get("/api/topics")
    def topics() -> list[dict[str, Any]]:
        return cast("list[dict[str, Any]]", payload(None, None)["topics"])

    @app.get("/api/tasks")
    def tasks() -> list[dict[str, Any]]:
        return cast("list[dict[str, Any]]", payload(None, None)["tasks"])

    @app.get("/api/events")
    def events(
        start: str | None = Query(default=None), end: str | None = Query(default=None)
    ) -> list[dict[str, Any]]:
        return cast("list[dict[str, Any]]", payload(start, end)["events"])

    @app.post("/api/reload")
    def reload() -> dict[str, Any]:
        state.reload()
        return {"reloaded": True, "agenda": str(state.agenda_path)}

    def _check_kind(kind: str) -> None:
        if kind not in _WRITE_KINDS:
            raise HTTPException(status_code=404, detail=f"Unknown kind: {kind!r}")

    @app.get("/api/{kind}/{entity_id}")
    def get_entity(kind: str, entity_id: str) -> dict[str, Any]:
        _check_kind(kind)
        collection = getattr(state.db, kind)
        if entity_id not in collection:
            raise HTTPException(status_code=404, detail=f"No {kind[:-1]} '{entity_id}'")
        return DatabaseSerializer.entity_to_dict(collection[entity_id])

    def _write(kind: str, spec: dict[str, Any]) -> dict[str, Any]:
        try:
            entity = state.upsert(kind, spec)
        except ReadOnlyError as err:
            raise HTTPException(status_code=409, detail=str(err)) from err
        except (KeyError, ValueError) as err:
            raise HTTPException(status_code=400, detail=str(err)) from err
        return {"ok": True, "id": entity.id, "kind": kind}

    @app.post("/api/{kind}")
    def create(kind: str, spec: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _check_kind(kind)
        if not spec.get("id"):
            raise HTTPException(status_code=400, detail="An 'id' is required.")
        if spec["id"] in getattr(state.db, kind):
            raise HTTPException(
                status_code=409, detail=f"{kind[:-1]} '{spec['id']}' already exists."
            )
        return _write(kind, spec)

    @app.put("/api/{kind}/{entity_id}")
    def update(kind: str, entity_id: str, spec: dict[str, Any] = Body(...)) -> dict[str, Any]:
        _check_kind(kind)
        spec = {**spec, "id": entity_id}  # path id is authoritative
        return _write(kind, spec)

    @app.delete("/api/{kind}/{entity_id}")
    def delete(kind: str, entity_id: str) -> dict[str, Any]:
        _check_kind(kind)
        try:
            state.delete(kind, entity_id)
        except ReadOnlyError as err:
            raise HTTPException(status_code=409, detail=str(err)) from err
        except UnknownEntityError as err:
            raise HTTPException(status_code=404, detail=str(err)) from err
        return {"ok": True, "id": entity_id, "kind": kind}

    # Static frontend LAST so /api/* routes take precedence.
    dist = config.find_web_dist()
    if dist is not None:
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
    else:

        @app.get("/", response_class=HTMLResponse)
        def index() -> str:
            return _NO_FRONTEND_HTML

    return app


def create_default_app() -> FastAPI:
    """Entry point for ``uvicorn yasched.serving.api:create_default_app --factory``."""
    return create_app(config.resolve_agenda_path())


# Convenience for `uvicorn yasched.serving.api:app` (uses default agenda).
def __getattr__(name: str) -> Any:  # pragma: no cover - thin lazy attribute
    if name == "app":
        return create_default_app()
    raise AttributeError(name)
