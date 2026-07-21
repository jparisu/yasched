"""Tests for the resolution engine (inheritance, traits, merges)."""

from yasched.backending.loading.DatabaseLoader import DatabaseLoader
from yasched.backending.resolving.Resolver import Resolver


def test_dag_multi_parent_tag_union(teacher_resolver):
    ts = teacher_resolver.resolve_topic("thesis-supervision")
    # inherits from both teaching (work) and research (work) + own supervision
    assert set(ts.tags) == {"work", "supervision"}


def test_subtask_inherits_topic_and_parent_tags(teacher_resolver):
    ms = teacher_resolver.resolve_task("make-slides")
    # math-101 topic chain -> work, undergrad ; parent prepare-math101 -> prep
    assert set(ms.tags) == {"work", "undergrad", "prep"}


def test_attributes_precedence_trait_over_default(teacher_resolver):
    gm = teacher_resolver.resolve_task("grade-midterm")
    assert gm.attributes["priority"] == 5  # high-priority trait beats default 1
    assert gm.attributes["kanban"] == "on-focus"  # focus trait


def test_attributes_own_beats_trait_and_default(teacher_resolver):
    sg = teacher_resolver.resolve_task("submit-grades")
    assert sg.attributes["priority"] == 4  # own inline


def test_trait_layering_and_border(teacher_resolver):
    ms = teacher_resolver.resolve_task("make-slides")
    assert ms.layout.border is not None  # from `hard` trait
    assert ms.attributes["difficulty"] == "hard"


def test_layout_backgrounds_compose_by_type(teacher_resolver):
    me = teacher_resolver.resolve_event("midterm-exam")
    types = [b.type for b in me.layout.backgrounds]
    # solid (default + exam-style), gradient_bl (teaching), gradient_tr (math-101)
    assert "gradient_bl" in types
    assert "gradient_tr" in types
    assert "solid" in types
    # each type appears once (composition, not duplication)
    assert len(types) == len(set(types))


def test_layout_shape_from_default(teacher_resolver):
    # nothing overrides shape, so the default `rounded` survives
    assert teacher_resolver.resolve_topic("admin").layout.shape.type == "rounded"


def test_default_fills_unset(teacher_resolver):
    admin = teacher_resolver.resolve_topic("admin")
    assert admin.attributes["priority"] == 1  # from default layer


def test_missing_entity_returns_none(teacher_resolver):
    assert teacher_resolver.resolve_task("does-not-exist") is None


def test_topic_cycle_is_guarded():
    db = DatabaseLoader.loads(
        "topics:\n"
        "  - id: a\n    name: A\n    parent_ids: [b]\n"
        "  - id: b\n    name: B\n    parent_ids: [a]\n"
    )
    r = Resolver(db)
    # Should not recurse infinitely; both resolve.
    assert r.resolve_topic("a") is not None
    assert r.resolve_topic("b") is not None


def test_task_parent_cycle_is_guarded():
    db = DatabaseLoader.loads(
        "tasks:\n"
        "  - id: a\n    name: A\n    parent_id: b\n"
        "  - id: b\n    name: B\n    parent_id: a\n"
    )
    r = Resolver(db)
    assert r.resolve_task("a") is not None


def test_topic_order_last_wins():
    db = DatabaseLoader.loads(
        "topics:\n"
        "  - id: x\n    name: X\n    attributes: {k: from_x}\n"
        "  - id: y\n    name: Y\n    attributes: {k: from_y}\n"
        "tasks:\n"
        "  - id: t\n    name: T\n    topic_ids: [x, y]\n"
    )
    r = Resolver(db)
    assert r.resolve_task("t").attributes["k"] == "from_y"  # later topic wins
