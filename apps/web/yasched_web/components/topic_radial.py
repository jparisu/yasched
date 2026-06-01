"""SVG radial tree component for the Topics page."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import RadialEdge, RadialNode, TopicState

_CANVAS = 600
_NODE_R = 20
_FONT_SIZE = 11


def _edge(e: RadialEdge) -> rx.Component:
    return rx.el.line(
        x1=e.x1,
        y1=e.y1,
        x2=e.x2,
        y2=e.y2,
        stroke="var(--gray-6)",
        stroke_width="1.5",
    )


def _node(n: RadialNode) -> rx.Component:
    return rx.el.g(
        rx.el.circle(
            cx=n.x,
            cy=n.y,
            r=_NODE_R,
            fill=rx.cond(n.is_selected, "var(--accent-9)", "var(--accent-3)"),
            stroke=rx.cond(n.is_selected, "var(--accent-11)", "var(--accent-7)"),
            stroke_width="2",
            style={"cursor": "pointer"},
        ),
        rx.el.text(
            n.name,
            x=n.x,
            y=n.y + _NODE_R + _FONT_SIZE,
            text_anchor="middle",
            font_size=_FONT_SIZE,
            fill="var(--gray-11)",
            style={"pointer-events": "none", "user-select": "none"},
        ),
        on_click=TopicState.select_topic(n.id),
    )


def topic_radial() -> rx.Component:
    return rx.cond(
        TopicState.db_loaded,
        rx.scroll_area(
            rx.el.svg(
                rx.el.g(rx.foreach(TopicState.radial_edges, _edge)),
                rx.el.g(rx.foreach(TopicState.radial_nodes, _node)),
                view_box=f"0 0 {_CANVAS} {_CANVAS}",
                width="100%",
                height="100%",
                style={"min-height": "500px"},
            ),
            height="100%",
            type="hover",
        ),
        rx.box(
            rx.text("Load a database to see the radial view.", size="2", color="var(--gray-9)"),
            padding="1rem",
        ),
    )
