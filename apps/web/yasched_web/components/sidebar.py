"""Left navigation sidebar."""

from __future__ import annotations

import reflex as rx

_NAV_ITEMS = [
    ("house", "Dashboard", "/", "Overview: alerts, metrics, upcoming deadlines"),
    ("kanban", "Tasks", "/tasks", "Kanban board and task management"),
    ("calendar", "Calendar", "/calendar", "Monthly, weekly and daily event calendar"),
    ("clock", "Schedule", "/schedule", "Weekly time-grid showing recurring events"),
    ("folder-tree", "Topics", "/topics", "Topic hierarchy and detail"),
    ("palette", "Layouts", "/layouts", "Visual layout gallery and editor"),
    ("chart-bar", "Analytics", "/analytics", "Charts: task counts, priorities, deadline density"),
    ("network", "Graph", "/graph", "Relationship graph across topics, tasks and events"),
    ("settings", "Settings", "/settings", "App settings: theme, read-only mode, alerts"),
]


def _nav_link(icon: str, label: str, href: str, tooltip: str) -> rx.Component:
    is_active = rx.State.router.page.path == href
    # rx.box is the tooltip trigger so Radix UI's asChild always receives a
    # forwardRef-capable Radix Box <div> rather than a Next.js Link component
    # (which may not expose its DOM ref in Reflex's generated React code).
    return rx.tooltip(
        rx.box(
            rx.link(
                rx.hstack(
                    rx.icon(
                        icon,
                        size=17,
                        color=rx.cond(is_active, "var(--accent-9)", "var(--gray-9)"),
                    ),
                    rx.text(
                        label,
                        size="2",
                        weight=rx.cond(is_active, "medium", "regular"),
                        color=rx.cond(is_active, "var(--accent-11)", "inherit"),
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                    padding="0.5rem 0.75rem",
                    border_radius="6px",
                    background=rx.cond(is_active, "var(--accent-3)", "transparent"),
                    _hover={"background": "var(--accent-3)"},
                ),
                href=href,
                text_decoration="none",
                color="inherit",
                width="100%",
            ),
            width="100%",
        ),
        content=tooltip,
        side="right",
    )


def sidebar() -> rx.Component:
    return rx.box(
        rx.vstack(
            *[_nav_link(icon, label, href, tip) for icon, label, href, tip in _NAV_ITEMS],
            spacing="1",
            align="start",
            width="100%",
            padding="1rem 0.5rem",
        ),
        width="200px",
        min_height="calc(100vh - 56px)",
        border_right="1px solid var(--gray-4)",
        background="var(--gray-1)",
        flex_shrink="0",
    )
