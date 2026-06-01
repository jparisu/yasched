"""Import-level smoke tests for the yasched_web package."""

import importlib

import pytest

reflex = pytest.importorskip("reflex", reason="reflex not installed; run: pip install -e '.[frontend]'")


def _web_modules():
    return [
        "yasched_web",
        "yasched_web.yasched_web",
        "yasched_web.state",
        "yasched_web.state.config",
        "yasched_web.state.app_state",
        "yasched_web.state.topic_state",
        "yasched_web.components",
        "yasched_web.components.navbar",
        "yasched_web.components.sidebar",
        "yasched_web.components.db_modal",
        "yasched_web.components.topic_tree",
        "yasched_web.components.topic_radial",
        "yasched_web.components.topic_detail",
        "yasched_web.pages",
        "yasched_web.pages.dashboard",
        "yasched_web.pages.tasks",
        "yasched_web.pages.calendar",
        "yasched_web.pages.schedule",
        "yasched_web.pages.topics",
        "yasched_web.pages.layouts",
        "yasched_web.pages.analytics",
        "yasched_web.pages.graph",
        "yasched_web.pages.settings",
    ]


@pytest.mark.parametrize("module_name", _web_modules())
def test_module_importable(module_name: str) -> None:
    importlib.import_module(module_name)


def test_state_public_names() -> None:
    from yasched_web.state import (
        AppState,
        FlatTopicNode,
        RadialEdge,
        RadialNode,
        TopicData,
        TopicState,
        YaschedConfig,
        add_recent_file,
        load_config,
        save_config,
    )
    assert AppState is not None
    assert TopicState is not None
    assert TopicData is not None
    assert FlatTopicNode is not None
    assert RadialNode is not None
    assert RadialEdge is not None
    assert YaschedConfig is not None
    assert load_config is not None
    assert save_config is not None
    assert add_recent_file is not None


def test_components_public_names() -> None:
    from yasched_web.components import (
        db_modal,
        navbar,
        sidebar,
        topic_detail,
        topic_radial,
        topic_tree,
    )
    assert all(callable(f) for f in (navbar, sidebar, db_modal, topic_tree, topic_radial, topic_detail))


def test_pages_public_names() -> None:
    from yasched_web.pages import (
        analytics_page,
        calendar_page,
        dashboard_page,
        graph_page,
        layouts_page,
        schedule_page,
        settings_page,
        tasks_page,
        topics_page,
    )
    assert all(
        callable(f)
        for f in (
            dashboard_page,
            tasks_page,
            calendar_page,
            schedule_page,
            topics_page,
            layouts_page,
            analytics_page,
            graph_page,
            settings_page,
        )
    )
