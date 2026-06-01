"""Integration test: load the basic_example resource through XymlLoader."""

from pathlib import Path

import pytest

from yasched.utilizing.xyml.XymlLoader import XymlLoader

BASIC_EXAMPLE = (
    Path(__file__).parents[3] / "resources" / "basic_example" / "basic_example_main.yaml"
)


@pytest.fixture(scope="module")
def doc():
    return XymlLoader.load(BASIC_EXAMPLE)


# ---------------------------------------------------------------------------
# Top-level structure
# ---------------------------------------------------------------------------


def test_top_level_keys_present(doc):
    assert set(doc.keys()) == {"layouts", "topics", "tasks", "events"}


def test_layouts_is_list(doc):
    assert isinstance(doc["layouts"], list)


def test_topics_is_list(doc):
    assert isinstance(doc["topics"], list)


def test_tasks_is_list(doc):
    assert isinstance(doc["tasks"], list)


def test_events_is_list(doc):
    assert isinstance(doc["events"], list)


# ---------------------------------------------------------------------------
# Counts (one entry per item in each resource file)
# ---------------------------------------------------------------------------


def test_layouts_count(doc):
    assert len(doc["layouts"]) == 2


def test_topics_count(doc):
    assert len(doc["topics"]) == 4


def test_tasks_count(doc):
    assert len(doc["tasks"]) == 8


def test_events_count(doc):
    assert len(doc["events"]) == 5


# ---------------------------------------------------------------------------
# Spot-check a few known entries
# ---------------------------------------------------------------------------


def test_layout_ids(doc):
    ids = [entry["id"] for entry in doc["layouts"]]
    assert "my_layout" in ids
    assert "important" in ids


def test_topic_ids(doc):
    ids = [entry["id"] for entry in doc["topics"]]
    assert "uni" in ids
    assert "exams" in ids
    assert "classes" in ids
    assert "my" in ids


def test_task_ids(doc):
    ids = [entry["id"] for entry in doc["tasks"]]
    assert "math_study" in ids
    assert "xmas" in ids
    assert "weekly_review" in ids


def test_event_ids(doc):
    ids = [entry["id"] for entry in doc["events"]]
    assert "math_classes" in ids
    assert "math_exam" in ids
    assert "xmas" in ids
