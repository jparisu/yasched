"""Tests for AppState: load, CRUD, save-back / flatten (no FastAPI)."""

import pytest

from yasched.serving.state import AppState, UnknownEntityError


def _write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_upsert_and_reload_round_trip(tmp_path):
    agenda = tmp_path / "db.yaml"
    _write(agenda, "elements:\n  - id: AllTopic\n    type: topic\n")
    state = AppState(agenda)
    state.upsert({"id": "t", "type": "task", "attributes": {"name": "T", "priority": 5}})

    reloaded = AppState(agenda)
    assert reloaded.db.element("t").attributes["priority"] == 5


def test_delete(tmp_path):
    agenda = tmp_path / "db.yaml"
    _write(agenda, "elements:\n  - id: t\n    type: task\n")
    state = AppState(agenda)
    state.delete("t")
    assert "t" not in state.db.elements
    with pytest.raises(UnknownEntityError):
        state.delete("missing")


def test_promotion_is_upsert_with_deterministic_id(tmp_path):
    agenda = tmp_path / "db.yaml"
    _write(
        agenda,
        "elements:\n"
        "  - id: lec\n"
        "    type: schedule\n"
        "    attributes: {generates: event, kind: daily}\n",
    )
    state = AppState(agenda)
    # Promote the occurrence on 2026-01-01 by saving a real element with its id.
    state.upsert(
        {
            "id": "lec#2026-01-01",
            "type": "event",
            "directParents": ["lec"],
            "attributes": {"cancelled": True},
        }
    )
    assert state.db.element("lec#2026-01-01").attributes["cancelled"] is True


def test_save_flattens_multi_file_source(tmp_path):
    # A base file included via __ext__ makes the source multi-file until first save.
    base = tmp_path / "base.yaml"
    _write(base, "elements:\n  - id: AllTopic\n    type: topic\n")
    agenda = tmp_path / "db.yaml"
    _write(agenda, "__ext__: base.yaml\n")
    state = AppState(agenda)
    assert state.multi_file is True
    state.upsert({"id": "t", "type": "task"})
    # After save, the on-disk file is a single flattened document.
    assert "__ext__" not in agenda.read_text(encoding="utf-8")
    assert AppState(agenda).multi_file is False
