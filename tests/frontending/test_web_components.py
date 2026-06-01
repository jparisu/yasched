"""Component construction tests for yasched_web.

Each test calls a component builder and asserts it returns a Reflex component
without raising. Static source-pattern checks guard against known f-string anti-
patterns where Python bakes a Var's __str__ into the tree instead of a reactive
binding.
"""

from __future__ import annotations

from pathlib import Path

import pytest

rx = pytest.importorskip("reflex", reason="reflex not installed; run: pip install -e '.[frontend]'")

_APPS_WEB = Path(__file__).parents[2] / "apps" / "web" / "yasched_web"

# ── component smoke tests ─────────────────────────────────────────────────────


def test_navbar_builds() -> None:
    from yasched_web.components.navbar import navbar

    result = navbar()
    assert isinstance(result, rx.Component)


def test_sidebar_builds() -> None:
    from yasched_web.components.sidebar import sidebar

    result = sidebar()
    assert isinstance(result, rx.Component)


def test_db_modal_builds() -> None:
    from yasched_web.components.db_modal import db_modal

    result = db_modal()
    assert isinstance(result, rx.Component)


def test_topic_tree_builds() -> None:
    from yasched_web.components.topic_tree import topic_tree

    result = topic_tree()
    assert isinstance(result, rx.Component)


def test_topic_radial_builds() -> None:
    from yasched_web.components.topic_radial import topic_radial

    result = topic_radial()
    assert isinstance(result, rx.Component)


def test_topic_detail_builds() -> None:
    from yasched_web.components.topic_detail import topic_detail

    result = topic_detail()
    assert isinstance(result, rx.Component)


def test_topics_page_builds() -> None:
    from yasched_web.pages.topics import topics_page

    result = topics_page()
    assert isinstance(result, rx.Component)


def test_settings_page_builds() -> None:
    from yasched_web.pages.settings import settings_page

    result = settings_page()
    assert isinstance(result, rx.Component)


# ── source pattern guards ─────────────────────────────────────────────────────
# These tests fail if a Reflex Var is embedded in an f-string, which produces
# the Var's internal name as a static string instead of a reactive binding.


def _read(relative: str) -> str:
    return (_APPS_WEB / relative).read_text()


def test_navbar_no_fstring_with_db_stats() -> None:
    src = _read("components/navbar.py")
    assert 'f" {AppState.db_stats' not in src, (
        "navbar.py uses f-string with AppState.db_stats Var — "
        "pass the Var as a separate rx.text child instead."
    )


def test_navbar_no_fstring_with_db_errors_length() -> None:
    src = _read("components/navbar.py")
    assert 'f" {AppState.db_errors.length()}' not in src, (
        "navbar.py uses f-string with AppState.db_errors.length() Var — "
        "pass the Var as a separate rx.badge child instead."
    )


def test_topic_tree_no_fstring_indent_width() -> None:
    src = _read("components/topic_tree.py")
    assert 'f"{node.depth' not in src, (
        "topic_tree.py uses f-string for indent width (node.depth is a Var) — "
        "pass node.depth * _INDENT_PX as a numeric style value."
    )


def test_topic_detail_no_fstring_border_css() -> None:
    src = _read("components/topic_detail.py")
    assert 'f"{data.layout_border_width}' not in src, (
        "topic_detail.py uses f-string to build border CSS (Vars) — "
        "use Var string concatenation instead."
    )


def test_topic_detail_no_fstring_bg_text() -> None:
    src = _read("components/topic_detail.py")
    assert 'f"BG: {data.layout_bg_type}' not in src, (
        "topic_detail.py uses f-string in BG text — "
        "pass Vars as separate rx.text children."
    )


def test_topic_detail_no_fstring_border_text() -> None:
    src = _read("components/topic_detail.py")
    assert 'f"Border: {data.layout_border_width}' not in src, (
        "topic_detail.py uses f-string in Border text — "
        "pass Vars as separate rx.text children."
    )


def test_topic_detail_no_fstring_icon_text() -> None:
    src = _read("components/topic_detail.py")
    assert 'f"Icon: {data.layout_icon_value}' not in src, (
        "topic_detail.py uses f-string in Icon text — "
        "pass the Var as a separate rx.text child."
    )


def test_topic_detail_no_fstring_tooltip_content() -> None:
    src = _read("components/topic_detail.py")
    assert 'f"Navigate to topic: {pid}' not in src, (
        "topic_detail.py uses f-string for tooltip content (pid is a Var) — "
        'use "Navigate to topic: " + pid instead.'
    )
