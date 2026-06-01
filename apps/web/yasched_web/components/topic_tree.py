"""Collapsible topic tree component."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import FlatTopicNode, TopicState

_INDENT_PX = 18


def _tree_node(node: FlatTopicNode) -> rx.Component:
    indent = rx.el.span(
        style={"display": "inline-block", "width": node.depth * _INDENT_PX, "flex-shrink": "0"},
    )

    expand_icon = rx.cond(
        node.has_children,
        rx.icon(
            rx.cond(node.is_expanded, "chevron-down", "chevron-right"),
            size=14,
            color="var(--gray-9)",
            style={"flex-shrink": "0", "cursor": "pointer"},
            on_click=TopicState.toggle_expand(node.id),
        ),
        rx.box(width="14px", flex_shrink="0"),
    )

    return rx.hstack(
        indent,
        expand_icon,
        rx.tooltip(
            rx.hstack(
                rx.icon("hash", size=14, color="var(--accent-9)", flex_shrink="0"),
                rx.text(
                    node.name,
                    size="2",
                    weight=rx.cond(node.is_selected, "bold", "regular"),
                    color=rx.cond(node.is_selected, "var(--accent-11)", "inherit"),
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                ),
                spacing="1",
                align="center",
                flex="1",
                min_width="0",
                padding="3px 6px",
                border_radius="4px",
                background=rx.cond(node.is_selected, "var(--accent-3)", "transparent"),
                cursor="pointer",
                _hover={"background": "var(--accent-3)"},
                on_click=TopicState.select_topic(node.id),
            ),
            content=node.id,
        ),
        spacing="0",
        align="center",
        width="100%",
        padding_y="1px",
    )


def topic_tree() -> rx.Component:
    return rx.cond(
        TopicState.db_loaded,
        rx.scroll_area(
            rx.vstack(
                rx.foreach(TopicState.flat_tree, _tree_node),
                spacing="0",
                align="start",
                width="100%",
            ),
            height="100%",
            type="hover",
        ),
        rx.box(
            rx.text("Load a database to see topics.", size="2", color="var(--gray-9)"),
            padding="1rem",
        ),
    )
