"""Tests for the inheritance resolution engine."""

from yasched.backending.Database import Database
from yasched.backending.loading.ElementLoader import ElementLoader
from yasched.backending.resolving.Resolver import Resolver
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType


def _db(*elements: Element) -> Database:
    db = Database()
    db.elements.update({e.id: e for e in elements})
    db.all_topic()
    return db


def _t(eid, parents=(), attrs=None, layout=None):
    return Element(
        id=eid,
        type=ElementType.TASK,
        direct_parents=list(parents),
        attributes=attrs or {},
        layout=layout,
    )


def test_dfs_linearization_matches_spec():
    db = _db(_t("A"), _t("B", ["A"]), _t("C", ["A"]), _t("D", ["B", "A"]), _t("E", ["C", "D"]))
    r = Resolver(db)
    assert r.parents("E")[:4] == ["C", "A", "D", "B"]
    assert r.parents("E")[-1] == "AllTopic"
    assert r.main_parent("E") == "C"


def test_alltopic_always_last_even_with_no_parents():
    db = _db(_t("solo"))
    assert Resolver(db).parents("solo") == ["AllTopic"]


def test_cycle_is_guarded():
    db = _db(_t("a", ["b"]), _t("b", ["a"]))
    parents = Resolver(db).parents("a")
    assert "b" in parents and "a" not in parents  # itself never appears


def test_own_value_wins_and_inherits_missing():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic", "attributes": {"priority": 1}},
            {
                "id": "top",
                "type": "topic",
                "directParents": ["AllTopic"],
                "attributes": {"location": "Office"},
            },
            {"id": "t", "type": "task", "directParents": ["top"], "attributes": {"priority": 7}},
        ]
    }
    r = Resolver(ElementLoader.from_dict(doc))
    resolved = r.resolve_id("t")
    assert resolved.attributes["priority"] == 7  # own wins
    assert resolved.attributes["location"] == "Office"  # inherited
    assert resolved.topic == "top"


def test_connections_never_inherited():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {"id": "top", "type": "topic", "attributes": {"connections": [{"to": "x"}]}},
            {"id": "t", "type": "task", "directParents": ["top"]},
        ]
    }
    r = Resolver(ElementLoader.from_dict(doc))
    assert "connections" not in r.resolve_id("t").attributes


def test_schedule_config_does_not_leak_into_generated_type():
    # `kind` applies_to schedule only; a task must not inherit it.
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {"id": "s", "type": "schedule", "attributes": {"kind": "weekly", "name": "S"}},
            {"id": "t", "type": "task", "directParents": ["s"]},
        ]
    }
    r = Resolver(ElementLoader.from_dict(doc))
    resolved = r.resolve_id("t")
    assert "kind" not in resolved.attributes
    assert resolved.attributes["name"] == "S"  # name applies to all -> inherited


def test_layout_resolution_own_over_attribute_over_parents():
    doc = {
        "attributes": {
            "difficulty": {
                "type": "number",
                "applies_to": ["task"],
                "layout": {"border": {"color": "#ff0000"}},
            }
        },
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "topic",
                "type": "topic",
                "layout": {"border": {"color": "#00ff00"}, "shape": "ellipse"},
            },
            {
                "id": "task",
                "type": "task",
                "directParents": ["topic"],
                "attributes": {"difficulty": 9},
                "layout": {"shape": "diamond"},
            },
        ],
    }
    layout = Resolver(ElementLoader.from_dict(doc)).resolve_id("task").layout
    assert layout.shape == "diamond"  # own wins
    assert layout.border.color.to_hex() == "#ff0000"  # attribute beats parent
