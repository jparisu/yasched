"""Tests for the (x)yml loader."""

import pytest

from yasched.backending.Database import ALL_TOPIC_ID
from yasched.backending.loading.ElementLoader import DatabaseLoadError, ElementLoader
from yasched.coring.ElementType import ElementType


def test_from_dict_parses_elements_and_definitions():
    doc = {
        "attributes": {"effort": {"type": "number", "applies_to": ["task"], "min": 0, "max": 40}},
        "elements": [
            {"id": "AllTopic", "type": "topic"},
            {
                "id": "t",
                "type": "task",
                "directParents": ["AllTopic"],
                "attributes": {"name": "T", "effort": 3},
            },
        ],
    }
    db = ElementLoader.from_dict(doc)
    assert db.element("t").type is ElementType.TASK
    assert db.attribute_defs["effort"].maximum == 40
    assert not db.attribute_defs["effort"].builtin


def test_alltopic_created_when_missing():
    db = ElementLoader.from_dict({"elements": []})
    assert ALL_TOPIC_ID in db.elements
    assert db.element(ALL_TOPIC_ID).type is ElementType.TOPIC


def test_accepts_snake_and_camel_parents_and_toplevel_name():
    a = ElementLoader.parse_element(
        {"id": "a", "type": "task", "direct_parents": ["x"], "name": "A"}
    )
    b = ElementLoader.parse_element({"id": "b", "type": "task", "directParents": ["x"]})
    assert a.direct_parents == ["x"] == b.direct_parents
    assert a.attributes["name"] == "A"  # top-level name folded into attributes


def test_missing_id_or_type_raises():
    with pytest.raises(DatabaseLoadError):
        ElementLoader.parse_element({"type": "task"})
    with pytest.raises(DatabaseLoadError):
        ElementLoader.parse_element({"id": "x"})


def test_layout_parsing_full():
    raw = {
        "background": {"color": "#112233", "gradient_color": "#445566"},
        "border": {"color": "red", "width": "2px", "style": "dashed"},
        "icon": {"type": "emoji", "value": "📐"},
        "pin": {"color": "#00ff00"},
        "shape": "diamond",
        "animation": "beep",
        "hover_animation": "pulse",
        "format": {"font": "serif", "text_align": "center"},
    }
    layout = ElementLoader.parse_layout(raw)
    assert layout.background.gradient_color.to_hex() == "#445566"
    assert layout.border.style == "dashed"
    assert layout.shape == "diamond"
    assert layout.format.text_align == "center"


def test_multi_file_flag_detected():
    db = ElementLoader.loads("elements:\n  - id: x\n    type: task\n")
    assert db.multi_file is False
