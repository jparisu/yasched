"""Tests for coring.Topic."""

import pytest

from yasched.coring.Layout import BackgroundStyle, Layout
from yasched.coring.Topic import Topic
from yasched.utilizing.coloring.Color import Color

# ---------------------------------------------------------------------------
# Construction — sweet path
# ---------------------------------------------------------------------------


def test_topic_minimal():
    t = Topic(id="math", name="Mathematics")
    assert t.id == "math"
    assert t.name == "Mathematics"
    assert t.description is None
    assert t.tags == []
    assert t.parent_ids == []
    assert t.layout is None


def test_topic_full_fields():
    t = Topic(
        id="math",
        name="Mathematics",
        description="All math topics",
        tags=["school", "academic"],
        parent_ids=["studies"],
        layout=Layout(id="blue_theme"),
    )
    assert t.description == "All math topics"
    assert t.tags == ["school", "academic"]
    assert t.parent_ids == ["studies"]


def test_topic_is_frozen():
    t = Topic(id="x", name="X")
    with pytest.raises((AttributeError, TypeError)):
        t.id = "y"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Construction — corner cases
# ---------------------------------------------------------------------------


def test_topic_multiple_parents():
    t = Topic(id="overlap", name="Overlap", parent_ids=["math", "physics"])
    assert len(t.parent_ids) == 2


def test_topic_layout_as_string_reference():
    t = Topic(id="art", name="Art", layout="bright_theme")
    assert t.layout == "bright_theme"


def test_topic_layout_inline():
    bg = BackgroundStyle(type="solid", color=Color(r=0.2, g=0.4, b=0.6))
    layout = Layout(background=bg)
    t = Topic(id="science", name="Science", layout=layout)
    assert isinstance(t.layout, Layout)


def test_topic_empty_tags_list_is_mutable_copy():
    t1 = Topic(id="a", name="A")
    t2 = Topic(id="b", name="B")
    # Each instance has its own default list
    assert t1.tags is not t2.tags


def test_topic_empty_parent_ids_list_is_mutable_copy():
    t1 = Topic(id="a", name="A")
    t2 = Topic(id="b", name="B")
    assert t1.parent_ids is not t2.parent_ids


def test_topic_tags_with_single_entry():
    t = Topic(id="x", name="X", tags=["important"])
    assert t.tags == ["important"]


# ---------------------------------------------------------------------------
# Construction — failure cases (none at coring layer; backending validates)
# ---------------------------------------------------------------------------


def test_topic_empty_id_stored():
    # id uniqueness and non-emptiness are enforced by backending
    t = Topic(id="", name="No ID")
    assert t.id == ""
