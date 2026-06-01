"""Tests for DatabaseLoader: load() and save()."""

from __future__ import annotations

from pathlib import Path

import pytest

from yasched.backending.Database import Database
from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.utilizing.xyml.XymlLoader import XymlFileNotFoundError


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# load — basic
# ---------------------------------------------------------------------------


def test_load_empty_yaml(tmp_path):
    p = _write(tmp_path, "db.yaml", "{}")
    db = DatabaseLoader.load(p)
    assert isinstance(db, Database)
    assert db.layouts == []
    assert db.topics == []
    assert db.events == []
    assert db.tasks == []
    assert db.source_path == p.resolve()


def test_load_topics_section(tmp_path):
    content = "topics:\n  - id: t1\n    name: Topic One\n"
    p = _write(tmp_path, "db.yaml", content)
    db = DatabaseLoader.load(p)
    assert len(db.topics) == 1
    assert db.topics[0].id == "t1"


def test_load_file_not_found_raises(tmp_path):
    with pytest.raises(XymlFileNotFoundError):
        DatabaseLoader.load(tmp_path / "nonexistent.yaml")


def test_load_string_path(tmp_path):
    p = _write(tmp_path, "db.yaml", "{}")
    db = DatabaseLoader.load(str(p))
    assert isinstance(db, Database)


def test_load_xyml_ext_directive(tmp_path):
    _write(tmp_path, "topics.yaml", "- id: t1\n  name: T1\n")
    main = _write(tmp_path, "main.yaml", "topics:\n  __ext__: ./topics.yaml\n")
    db = DatabaseLoader.load(main)
    assert len(db.topics) == 1


def test_load_basic_example(tmp_path):
    resources = Path(__file__).parent.parent.parent.parent / "resources" / "basic_example"
    if not resources.exists():
        pytest.skip("basic_example resources not found")
    db = DatabaseLoader.load(resources / "basic_example_main.yaml")
    assert len(db.topics) > 0
    assert len(db.events) > 0
    assert len(db.tasks) > 0


# ---------------------------------------------------------------------------
# save + round-trip
# ---------------------------------------------------------------------------


def test_save_creates_file(tmp_path):
    from yasched.coring.Topic import Topic

    db = Database(layouts=[], topics=[Topic(id="t1", name="T1")], events=[], tasks=[])
    out = tmp_path / "out.yaml"
    DatabaseLoader.save(db, out)
    assert out.exists()


def test_save_round_trip_topics(tmp_path):
    from yasched.coring.Topic import Topic

    db = Database(
        layouts=[],
        topics=[Topic(id="t1", name="Topic One", description="desc", tags=["a"])],
        events=[],
        tasks=[],
    )
    out = tmp_path / "out.yaml"
    DatabaseLoader.save(db, out)
    db2 = DatabaseLoader.load(out)
    assert len(db2.topics) == 1
    assert db2.topics[0].id == "t1"
    assert db2.topics[0].name == "Topic One"
    assert db2.topics[0].description == "desc"
    assert db2.topics[0].tags == ["a"]
