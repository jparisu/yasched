"""Tests for the serializer (write-back / flatten)."""

import datetime

from yasched.backending.Database import ALL_TOPIC_ID
from yasched.backending.generating.Generator import Generator
from yasched.backending.loading.ElementLoader import ElementLoader
from yasched.backending.loading.ElementSerializer import ElementSerializer


def test_round_trip_preserves_attributes_layout_parents():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "t",
                "type": "task",
                "directParents": ["AllTopic"],
                "attributes": {"name": "T", "priority": 3},
                "layout": {"background": {"color": "#123456", "gradient_color": "#654321"}},
            },
        ]
    }
    db = ElementLoader.from_dict(doc)
    db2 = ElementLoader.loads(ElementSerializer.to_yaml(db))
    t = db2.element("t")
    assert t.attributes == {"name": "T", "priority": 3}
    assert t.direct_parents == ["AllTopic"]
    assert t.layout.background.gradient_color.to_hex() == "#654321"


def test_virtual_elements_never_persisted():
    doc = {
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "d",
                "type": "schedule",
                "attributes": {
                    "generates": "event",
                    "kind": "daily",
                    "startDate": "2026-01-01",
                    "endDate": "2026-01-02",
                },
            },
        ]
    }
    db = ElementLoader.from_dict(doc)
    for v in Generator(db).generate(datetime.date(2026, 1, 1), datetime.date(2026, 1, 2)):
        db.elements[v.id] = v  # inject virtuals into the pool
    out = ElementSerializer.to_dict(db)
    ids = {e["id"] for e in out["elements"]}
    assert ids == {"d"}  # only the real schedule survives


def test_default_alltopic_omitted():
    db = ElementLoader.from_dict({"elements": [{"id": "x", "type": "task"}]})
    ids = {e["id"] for e in ElementSerializer.to_dict(db)["elements"]}
    assert ALL_TOPIC_ID not in ids  # untouched root is not written back
    assert "x" in ids


def test_customized_alltopic_persisted():
    db = ElementLoader.from_dict(
        {
            "elements": [
                {"id": "AllTopic", "type": "topic", "layout": {"shape": "rectangle"}},
            ]
        }
    )
    ids = {e["id"] for e in ElementSerializer.to_dict(db)["elements"]}
    assert ALL_TOPIC_ID in ids
