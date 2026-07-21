"""Tests for DatabaseSerializer (round-trip fidelity)."""

from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.loading.DatabaseSerializer import DatabaseSerializer
from yasched.backending.resolving.Resolver import Resolver


def test_roundtrip_counts(teacher_db):
    text = DatabaseSerializer.to_yaml(teacher_db)
    db2 = DatabaseLoader.loads(text)
    assert len(db2.topics) == len(teacher_db.topics)
    assert len(db2.events) == len(teacher_db.events)
    assert len(db2.tasks) == len(teacher_db.tasks)
    assert len(db2.traits) == len(teacher_db.traits)


def test_roundtrip_resolved_equivalence(teacher_db):
    db2 = DatabaseLoader.loads(DatabaseSerializer.to_yaml(teacher_db))
    r1, r2 = Resolver(teacher_db), Resolver(db2)
    for tid in teacher_db.tasks:
        a, b = r1.resolve_task(tid), r2.resolve_task(tid)
        assert a.attributes == b.attributes
        assert set(a.tags) == set(b.tags)
        assert [x.type for x in a.layout.backgrounds] == [x.type for x in b.layout.backgrounds]


def test_multiple_backgrounds_serialized_as_list():
    text = (
        "tasks:\n"
        "  - id: t\n"
        "    layout:\n"
        "      background:\n"
        "        - {type: gradient_bl, color: '#111111'}\n"
        "        - {type: gradient_tr, color: '#222222'}\n"
    )
    db = DatabaseLoader.loads(text)
    doc = DatabaseSerializer.to_dict(db)
    bg = doc["tasks"][0]["layout"]["background"]
    assert isinstance(bg, list) and len(bg) == 2


def test_single_background_serialized_as_mapping():
    db = DatabaseLoader.loads(
        "tasks:\n  - id: t\n    layout: {background: {type: solid, color: red}}\n"
    )
    bg = DatabaseSerializer.to_dict(db)["tasks"][0]["layout"]["background"]
    assert isinstance(bg, dict) and bg["type"] == "solid"


def test_schedules_and_relations_roundtrip():
    text = (
        "tasks:\n"
        "  - id: a\n"
        "    schedules: [{type: weekly, week_days: [friday], start_time: '16:00', duration: 30m}]\n"
        "    relations: [{task: b, type: requires, description: first}]\n"
        "    event_links: [{event: e, use_as_deadline: true}]\n"
        "  - id: b\n"
    )
    db = DatabaseLoader.loads(text)
    db2 = DatabaseLoader.loads(DatabaseSerializer.to_yaml(db))
    a = db2.tasks["a"]
    assert a.schedules and a.relations[0].task_id == "b"
    assert a.relations[0].description == "first"
    assert a.event_links[0].use_as_deadline is True


def test_empty_sections_pruned():
    doc = DatabaseSerializer.to_dict(DatabaseLoader.loads(""))
    assert doc == {}
