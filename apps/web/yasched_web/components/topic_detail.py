"""Topic detail panel component."""

from __future__ import annotations

import reflex as rx

from yasched_web.state import TopicData, TopicState


def _layout_preview(data: TopicData) -> rx.Component:
    """Render a visual swatch for the topic's effective layout."""
    has_layout = data.layout_id != ""

    bg_style = rx.cond(
        data.layout_bg_type == "solid",
        {"background": data.layout_bg_color},
        {"background": "var(--gray-3)"},
    )

    swatch = rx.box(
        rx.cond(
            data.layout_icon_value != "",
            rx.text(data.layout_icon_value, size="5"),
            rx.fragment(),
        ),
        width="64px",
        height="64px",
        border_radius="8px",
        border=rx.cond(
            data.layout_border_type != "",
            data.layout_border_width + " " + data.layout_border_type + " " + data.layout_border_color,
            "1px solid var(--gray-5)",
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        style=bg_style,
    )

    return rx.vstack(
        rx.text("Layout", size="1", weight="medium", color="var(--gray-10)"),
        rx.cond(
            has_layout,
            rx.hstack(
                swatch,
                rx.vstack(
                    rx.text(data.layout_id, size="2", weight="bold"),
                    rx.cond(
                        data.layout_bg_type != "",
                        rx.text("BG: ", data.layout_bg_type, " ", data.layout_bg_color, size="1", color="var(--gray-10)"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        data.layout_border_type != "",
                        rx.text("Border: ", data.layout_border_width, " ", data.layout_border_type, size="1", color="var(--gray-10)"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        data.layout_icon_value != "",
                        rx.text("Icon: ", data.layout_icon_value, size="1", color="var(--gray-10)"),
                        rx.fragment(),
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.text("No layout assigned", size="2", color="var(--gray-8)", font_style="italic"),
        ),
        spacing="1",
        align="start",
        width="100%",
    )


def _tag_badge(tag: str) -> rx.Component:
    return rx.badge(tag, variant="soft", color_scheme="blue", size="1")


def _parent_breadcrumb(data: TopicData) -> rx.Component:
    return rx.cond(
        data.parent_ids.length() > 0,
        rx.vstack(
            rx.text("Parents", size="1", weight="medium", color="var(--gray-10)"),
            rx.hstack(
                rx.foreach(
                    data.parent_ids,
                    lambda pid: rx.tooltip(
                        rx.badge(pid, variant="outline", color_scheme="gray", size="1", cursor="pointer",
                                 on_click=TopicState.select_topic(pid)),
                        content="Navigate to topic: " + pid,
                    ),
                ),
                flex_wrap="wrap",
                spacing="1",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        rx.fragment(),
    )


def topic_detail() -> rx.Component:
    return rx.cond(
        TopicState.selected_topic_id != "",
        rx.cond(
            TopicState.selected_topic != None,  # noqa: E711
            rx.vstack(
                # header
                rx.hstack(
                    rx.icon("folder", size=20, color="var(--accent-9)"),
                    rx.vstack(
                        rx.text(
                            TopicState.selected_topic.name,
                            size="4",
                            weight="bold",
                        ),
                        rx.text(
                            TopicState.selected_topic.id,
                            size="1",
                            color="var(--gray-10)",
                            font_family="monospace",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.separator(width="100%"),
                # description
                rx.cond(
                    TopicState.selected_topic.description != "",
                    rx.vstack(
                        rx.text("Description", size="1", weight="medium", color="var(--gray-10)"),
                        rx.text(TopicState.selected_topic.description, size="2"),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                # parents breadcrumb
                _parent_breadcrumb(TopicState.selected_topic),
                # effective tags
                rx.cond(
                    TopicState.selected_topic.effective_tags.length() > 0,
                    rx.vstack(
                        rx.text("Tags (effective)", size="1", weight="medium", color="var(--gray-10)"),
                        rx.hstack(
                            rx.foreach(TopicState.selected_topic.effective_tags, _tag_badge),
                            flex_wrap="wrap",
                            spacing="1",
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                    ),
                    rx.fragment(),
                ),
                rx.separator(width="100%"),
                # layout preview
                _layout_preview(TopicState.selected_topic),
                spacing="3",
                align="start",
                width="100%",
                padding="1rem",
            ),
            rx.fragment(),
        ),
        rx.box(
            rx.text("Select a topic from the tree to see its details.", size="2", color="var(--gray-9)"),
            padding="1rem",
        ),
    )
