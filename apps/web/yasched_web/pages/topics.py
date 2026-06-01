"""Topics page — collapsible tree + radial view + detail panel."""

from __future__ import annotations

import reflex as rx

from yasched_web.components.topic_detail import topic_detail
from yasched_web.components.topic_radial import topic_radial
from yasched_web.components.topic_tree import topic_tree
from yasched_web.state import TopicState


def _view_toggle() -> rx.Component:
    return rx.hstack(
        rx.tooltip(
            rx.button(
                rx.icon("list-tree", size=15),
                " Tree",
                on_click=TopicState.set_view_mode("tree"),
                variant=rx.cond(TopicState.view_mode == "tree", "solid", "soft"),
                size="2",
            ),
            content="Collapsible file-explorer tree view",
        ),
        rx.tooltip(
            rx.button(
                rx.icon("circle-dot", size=15),
                " Radial",
                on_click=TopicState.set_view_mode("radial"),
                variant=rx.cond(TopicState.view_mode == "radial", "solid", "soft"),
                size="2",
            ),
            content="Radial graph showing the full topic hierarchy",
        ),
        spacing="2",
    )


def topics_page() -> rx.Component:
    return rx.hstack(
        # ── left panel: tree / radial ──────────────────────────────────────
        rx.vstack(
            rx.hstack(
                rx.heading("Topics", size="4"),
                rx.spacer(),
                _view_toggle(),
                width="100%",
                align="center",
                padding="1rem 1rem 0.5rem 1rem",
            ),
            rx.box(
                rx.cond(
                    TopicState.view_mode == "tree",
                    topic_tree(),
                    topic_radial(),
                ),
                flex="1",
                overflow="hidden",
                padding="0 0.5rem",
            ),
            spacing="0",
            height="calc(100vh - 56px)",
            width="340px",
            flex_shrink="0",
            border_right="1px solid var(--gray-4)",
        ),
        # ── right panel: detail ────────────────────────────────────────────
        rx.box(
            topic_detail(),
            flex="1",
            height="calc(100vh - 56px)",
            overflow_y="auto",
        ),
        spacing="0",
        align="start",
        width="100%",
        height="calc(100vh - 56px)",
    )
