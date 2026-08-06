"""Tests for the coring value objects."""

import pytest

from yasched.coring.AttributeDefinition import NON_INHERITING, ValueType, builtin_definitions
from yasched.coring.Connection import Connection
from yasched.coring.Element import Element
from yasched.coring.ElementType import ElementType
from yasched.coring.Layout import Background, Border, Layout
from yasched.utilizing.coloring.Color import Color


def test_element_type_parsing():
    assert ElementType.from_string("Task") is ElementType.TASK
    assert str(ElementType.SCHEDULE) == "schedule"
    with pytest.raises(ValueError):
        ElementType.from_string("nope")


def test_element_accessors():
    e = Element(id="x", type=ElementType.TASK, attributes={"name": "X", "description": "d"})
    assert e.name == "X"
    assert e.description == "d"
    assert e.is_topic() is False


def test_connection_from_raw():
    assert Connection.from_raw("other") == Connection(to="other", relation="related")
    assert Connection.from_raw({"to": "b", "relation": "has"}) == Connection("b", "has")


def test_element_connections_parse():
    e = Element(
        id="a", type=ElementType.TASK, attributes={"connections": [{"to": "b", "relation": "x"}]}
    )
    assert e.connections() == [Connection("b", "x")]


def test_layout_merged_over_is_per_field():
    top = Layout(shape="diamond")
    base = Layout(shape="ellipse", animation="beep", border=Border(Color.from_hex("#000000")))
    merged = top.merged_over(base)
    assert merged.shape == "diamond"  # own wins
    assert merged.animation == "beep"  # filled from base
    assert merged.border is not None


def test_layout_to_dict_gradient():
    layout = Layout(background=Background(Color.from_hex("#112233"), Color.from_hex("#445566")))
    assert layout.to_dict()["background"] == {"color": "#112233", "gradient_color": "#445566"}


def test_layout_empty():
    assert Layout().is_empty()
    assert not Layout(shape="rectangle").is_empty()


def test_builtins_present_and_scoped():
    defs = builtin_definitions()
    assert defs["name"].value_type is ValueType.STRING
    assert defs["priority"].applies_to == (ElementType.TASK,)
    assert defs["connections"].inherits is False
    assert "connections" in NON_INHERITING
